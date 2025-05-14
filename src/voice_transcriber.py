import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from datetime import datetime
import threading
import whisper
import os

# Default Configuration (can be overridden during class instantiation)
DEFAULT_SAMPLERATE = 44100  # Hz
DEFAULT_CHANNELS = 1  # Mono
DEFAULT_FILENAME_BASE = "module_speech_capture"  # Base for temporary files
DEFAULT_SILENCE_THRESHOLD = 0.01  # RMS amplitude for silence detection
DEFAULT_MIN_SPEECH_DURATION_SECONDS = 0.5  # Min speech length
DEFAULT_TRAILING_SILENCE_SECONDS = 2.0  # Silence after speech to stop
DEFAULT_CHUNK_SIZE = 1024  # Frames per buffer
DEFAULT_WHISPER_MODEL_NAME = "turbo"


class AudioTranscriber:
    def __init__(self,
                 samplerate=DEFAULT_SAMPLERATE,
                 channels=DEFAULT_CHANNELS,
                 filename_base=DEFAULT_FILENAME_BASE,
                 silence_threshold=DEFAULT_SILENCE_THRESHOLD,
                 min_speech_duration_seconds=DEFAULT_MIN_SPEECH_DURATION_SECONDS,
                 trailing_silence_seconds=DEFAULT_TRAILING_SILENCE_SECONDS,
                 chunk_size=DEFAULT_CHUNK_SIZE,
                 whisper_model_name=DEFAULT_WHISPER_MODEL_NAME,
                 device=None,
                 verbose=True):

        self.samplerate = samplerate
        self.channels = channels
        self.filename_base = filename_base
        self.silence_threshold = silence_threshold
        self.min_speech_duration_seconds = min_speech_duration_seconds
        self.trailing_silence_seconds = trailing_silence_seconds
        self.chunk_size = chunk_size
        self.whisper_model_name = whisper_model_name
        self.device = device  # Can be None (for default), an int (ID), or str (name substring)
        self.verbose = verbose

        # Calculated Configuration
        self.frames_per_chunk = self.chunk_size
        self.chunks_per_second = self.samplerate / self.frames_per_chunk
        self.min_speech_chunks = int(self.chunks_per_second * self.min_speech_duration_seconds)
        self.trailing_silent_chunks_limit = int(self.chunks_per_second * self.trailing_silence_seconds)

        # State Variables - initialized by _reset_state
        self.final_recorded_audio_chunks = None
        self.current_utterance_chunks = None
        self.has_speech_started_in_utterance = None
        self.silent_chunks_after_speech_count = None
        self.stop_recording_event = None
        self.initial_listening_message_printed = None
        self._saved_audio_filepath_internal = None  # Internal tracking of the saved file

        self.whisper_model = None  # Loaded on demand

        self._reset_state()  # Initialize state variables

    def _print(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

    def _reset_state(self):
        """Resets the recording state variables for a new session."""
        self.final_recorded_audio_chunks = []
        self.current_utterance_chunks = []
        self.has_speech_started_in_utterance = False
        self.silent_chunks_after_speech_count = 0
        self.stop_recording_event = threading.Event()
        self.initial_listening_message_printed = False
        self._saved_audio_filepath_internal = None

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status: sd.CallbackFlags):
        """Callback function for the sounddevice InputStream."""
        if self.stop_recording_event.is_set():
            return

        if status:
            self._print(f"Audio callback status: {status}", flush=True)

        rms_energy = np.sqrt(np.mean(indata ** 2))

        if rms_energy > self.silence_threshold:  # Speech detected
            if not self.has_speech_started_in_utterance:
                self._print("\nSpeech detected, recording starts...", flush=True)
                self.has_speech_started_in_utterance = True
                self.current_utterance_chunks.clear()  # Start fresh for this utterance

            self.current_utterance_chunks.append(indata.copy())
            self.silent_chunks_after_speech_count = 0
            self.initial_listening_message_printed = False

        else:  # Silence detected
            if self.has_speech_started_in_utterance:
                # Recording was active, now it's silent
                self.current_utterance_chunks.append(indata.copy())  # Continue recording silence for a bit
                self.silent_chunks_after_speech_count += 1

                if self.verbose and self.silent_chunks_after_speech_count > 0 and \
                        self.silent_chunks_after_speech_count % int(self.chunks_per_second / 4) == 0:
                    print(".", end="", flush=True)  # Progress indicator for trailing silence

                if self.silent_chunks_after_speech_count > self.trailing_silent_chunks_limit:
                    # Enough trailing silence, process the utterance
                    actual_speech_chunk_count = len(self.current_utterance_chunks) - self.trailing_silent_chunks_limit
                    duration_speech_s = max(0, actual_speech_chunk_count) * self.frames_per_chunk / self.samplerate

                    if actual_speech_chunk_count >= self.min_speech_chunks:
                        duration_total_s = len(self.current_utterance_chunks) * self.frames_per_chunk / self.samplerate
                        self._print(
                            f"\nSufficient silence after speech. Valid utterance captured ({duration_total_s:.2f}s total, {duration_speech_s:.2f}s speech).",
                            flush=True)
                        self.final_recorded_audio_chunks.extend(self.current_utterance_chunks)
                        self.current_utterance_chunks.clear()
                        self.has_speech_started_in_utterance = False  # Reset for next potential utterance
                        self.stop_recording_event.set()  # Signal to stop the main recording loop
                    else:
                        self._print(
                            f"\nDetected sound was too short ({duration_speech_s:.2f}s of speech). Discarding and continuing to listen.",
                            flush=True)
                        self.current_utterance_chunks.clear()
                        self.has_speech_started_in_utterance = False
                        self.silent_chunks_after_speech_count = 0
                        self.initial_listening_message_printed = False  # Allow "Listening..." to print again
            elif not self.initial_listening_message_printed and self.verbose:
                # No speech started yet, and "Listening..." message not printed
                print("Listening for speech...", end="\r", flush=True)
                self.initial_listening_message_printed = True

    def _process_and_save_audio(self):
        """
        Processes the recorded audio chunks, saves them to a file,
        and returns the filepath. Returns None if saving fails or audio is too short.
        """
        self._saved_audio_filepath_internal = None  # Ensure it's reset
        if not self.final_recorded_audio_chunks:
            self._print("No substantial speech was recorded to save.", flush=True)
            return None

        full_audio_data_np = np.concatenate(self.final_recorded_audio_chunks, axis=0)
        duration_seconds = len(full_audio_data_np) / self.samplerate

        # This check ensures that even if interrupted, the saved audio has a minimum sensible length.
        # The callback already ensures `min_speech_duration_seconds` for speech part of normal utterances.
        if duration_seconds < self.min_speech_duration_seconds:
            self._print(
                f"Final recorded audio too short ({duration_seconds:.2f}s), not saving. Min required: {self.min_speech_duration_seconds}s.",
                flush=True)
            return None

        self._print(f"Total recorded audio duration: {duration_seconds:.2f} seconds. Processing...", flush=True)
        audio_data_int16 = (full_audio_data_np * 32767).astype(np.int16)
        audio_segment = AudioSegment(
            data=audio_data_int16.tobytes(),
            sample_width=audio_data_int16.dtype.itemsize,
            frame_rate=self.samplerate,
            channels=self.channels
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename_mp3 = f"{self.filename_base}_{timestamp}.mp3"
        output_filename_wav = f"{self.filename_base}_{timestamp}.wav"

        try:
            self._print(f"Saving audio to {output_filename_mp3}...", flush=True)
            audio_segment.export(output_filename_mp3, format="mp3")
            self._print(f"Audio successfully saved as {output_filename_mp3}", flush=True)
            self._saved_audio_filepath_internal = output_filename_mp3
        except Exception as e_export_mp3:
            self._print(f"\nError exporting to MP3: {e_export_mp3}", flush=True)
            self._print("This commonly occurs if FFmpeg is not installed or not found in your system's PATH.")
            self._print("Attempting to save as WAV file instead as a fallback...", flush=True)
            try:
                audio_segment.export(output_filename_wav, format="wav")
                self._print(f"Audio successfully saved as WAV (fallback): {output_filename_wav}", flush=True)
                self._saved_audio_filepath_internal = output_filename_wav
            except Exception as e_export_wav:
                self._print(f"Error exporting to WAV: {e_export_wav}", flush=True)
                self._print("Failed to save audio in any format.")
                return None
        return self._saved_audio_filepath_internal

    def _transcribe_audio(self, audio_filepath: str):
        """
        Transcribes the audio file using Whisper.
        Deletes the audio file ONLY if transcription is successful.
        Returns the transcribed text or None.
        """
        if not audio_filepath or not os.path.exists(audio_filepath):
            self._print(f"Error: Audio file '{audio_filepath}' not found for transcription.", flush=True)
            return None

        transcribed_text = None
        try:
            self._print(
                f"\nAttempting to transcribe '{audio_filepath}' using Whisper model '{self.whisper_model_name}'...",
                flush=True)
            if self.whisper_model is None:
                self._print(f"Loading Whisper model '{self.whisper_model_name}'... (This may take a moment)",
                            flush=True)
                # Note: "turbo" was in the original script, which isn't a standard Whisper model size.
                # Common sizes: "tiny", "base", "small", "medium", "large".
                # User can pass any valid model name or path.
                self.whisper_model = whisper.load_model(self.whisper_model_name)
                self._print("Whisper model loaded.", flush=True)

            self._print("Transcribing audio...", flush=True)
            result = self.whisper_model.transcribe(audio_filepath, fp16=False)  # fp16=False for wider CPU compatibility
            transcribed_text = result["text"].strip()

            self._print("\n--- Transcription Result ---")
            self._print(transcribed_text)
            self._print("--------------------------")

            # Delete the file ONLY after successful transcription and obtaining the text
            try:
                os.remove(audio_filepath)
                self._print(f"Successfully deleted audio file after transcription: {audio_filepath}", flush=True)
            except Exception as e_delete:
                self._print(f"Error deleting audio file {audio_filepath} after successful transcription: {e_delete}",
                            flush=True)

            # Clear internal path reference as the file (should be) gone or processed
            if self._saved_audio_filepath_internal == audio_filepath:
                self._saved_audio_filepath_internal = None

            return transcribed_text

        except FileNotFoundError:  # Should ideally be caught by the os.path.exists check earlier
            self._print(f"Error: The audio file '{audio_filepath}' was not found during transcription process.",
                        flush=True)
            if self._saved_audio_filepath_internal == audio_filepath:
                self._saved_audio_filepath_internal = None
            return None
        except Exception as e_whisper:
            self._print(f"\nAn error occurred during transcription with Whisper: {e_whisper}", flush=True)
            self._print("Ensure 'openai-whisper' is installed correctly and the model name is valid.", flush=True)
            self._print(f"Audio file '{audio_filepath}' was NOT deleted due to transcription error.")
            # Do not delete the file if transcription fails, so it can be inspected.
            return None

    def record_and_transcribe(self, print_initial_summary=True):
        """
        Main method to start recording based on speech, then transcribe the speech.
        Returns the transcribed text, or None if an error occurs or no valid speech is transcribed.
        """
        self._reset_state()  # Prepare for a new recording session

        if print_initial_summary and self.verbose:
            self._print_operational_summary()

        try:
            # Check and display device info
            device_info = sd.query_devices(self.device, kind='input')
            if not device_info:  # query_devices returns None if device is not found by index/name
                self._print(
                    f"Error: Input audio device not found or invalid: {self.device}. Using default if possible.")
                # sd.InputStream will raise an error if default is also unavailable or self.device is bad string
            device_name = device_info['name'] if isinstance(device_info,
                                                            dict) else "default"  # sd.query_devices() (no args) gives default
            self._print(f"\nUsing audio input device: {device_name}")
        except Exception as e_dev:
            self._print(f"Could not query audio device: {e_dev}. Attempting to proceed with specified/default device.")

        try:
            with sd.InputStream(
                    samplerate=self.samplerate,
                    channels=self.channels,
                    dtype='float32',
                    blocksize=self.frames_per_chunk,
                    callback=self._audio_callback,
                    device=self.device):  # Pass configured device

                if not self.verbose:  # If not verbose, give a minimal start cue.
                    print("Listening...")

                while not self.stop_recording_event.is_set():
                    sd.sleep(100)  # Wait for the callback to signal completion

        except KeyboardInterrupt:
            self._print("\nRecording interrupted by user.", flush=True)
            if self.has_speech_started_in_utterance and self.current_utterance_chunks:
                # If interrupted mid-speech, try to salvage what was recorded
                self.final_recorded_audio_chunks.extend(self.current_utterance_chunks)
                self._print("Attempting to process partially recorded audio...", flush=True)
            self.stop_recording_event.set()  # Ensure loop termination

        except Exception as e_rec:
            self._print(f"\nAn unexpected error occurred during recording: {e_rec}", flush=True)
            self.stop_recording_event.set()  # Ensure no further processing attempts
            return None  # Critical error during recording phase
        finally:
            self._print("\nAudio stream processing finished.", flush=True)

        # --- Process and save the recorded audio ---
        audio_file_to_transcribe = self._process_and_save_audio()

        # --- Transcription Step (includes deletion on success) ---
        transcribed_text = None
        if audio_file_to_transcribe:
            transcribed_text = self._transcribe_audio(audio_file_to_transcribe)
        else:
            self._print("\nNo audio file was saved (or audio was too short), skipping transcription.", flush=True)

        return transcribed_text

    def _print_operational_summary(self):
        """Prints a summary of the transcriber's settings."""
        self._print("--- Audio Transcriber Initialized ---")
        self._print(f"  Mode: Records on speech, transcribes on silence.")
        self._print(f"  Sample Rate: {self.samplerate}Hz, Channels: {self.channels}")
        self._print(f"  Silence Threshold (RMS): {self.silence_threshold:.3f}")
        self._print(
            f"  Min. Speech: {self.min_speech_duration_seconds}s, Trailing Silence: {self.trailing_silence_seconds}s")
        self._print(f"  Whisper Model: '{self.whisper_model_name}'")
        self._print("------------------------------------")

    @staticmethod
    def list_audio_devices():
        """Prints a list of available audio input devices."""
        print("Available audio input devices:")
        try:
            devices = sd.query_devices()
            input_devices_list = [device for device in devices if device['max_input_channels'] > 0]
            if not input_devices_list:
                print("  No input audio devices found. Please check microphone.")
                return

            default_input_device_info = sd.query_devices(kind='input')  # This is a dict
            default_input_device_idx = default_input_device_info['index'] if isinstance(default_input_device_info,
                                                                                        dict) else -1

            for i, device in enumerate(input_devices_list):
                default_indicator = " (default)" if device['index'] == default_input_device_idx else ""
                print(f"  ID {device['index']}: {device['name']}{default_indicator}")
        except Exception as e:
            print(f"Could not query audio devices: {e}")