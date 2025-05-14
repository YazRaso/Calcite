# TODO: import self developled modules
import voice_transcriber as vt
from books import ExcelManager
import sys
from PySide6.QtCore import Qt, QDir, QStandardPaths
from PySide6.QtGui import QFont, QPalette, QColor, QFontDatabase # Added QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QFileDialog,
    QStackedWidget,
    QDialog,
    QGridLayout,
    QSpacerItem,
    QSizePolicy,
    QDialogButtonBox,
    QGroupBox
)

FUTURISTIC_FONT_FAMILY = "JetBrains Mono"


class ShareDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Share Receipt")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(20, 20, 20, 20)

        info_icon_label = QLabel("🌐")
        info_icon_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 22))
        info_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_icon_label)

        main_label = QLabel("Share via WhatsApp (Demo)")
        main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 18px;
            color: #00e5ff;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)
        layout.addWidget(main_label)

        self.share_info_label = QLabel("Receipt: [Receipt Name/ID]")
        self.share_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.share_info_label.setStyleSheet(f"""
            font-size: 15px;
            color: #c0c0c0;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)
        layout.addWidget(self.share_info_label)

        instructions_label = QLabel(
            "This is a demonstration feature.\nActual sharing functionality is not implemented."
        )
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_label.setStyleSheet(f"""
            font-size: 13px;
            color: #a0a0a0;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)
        instructions_label.setWordWrap(True)
        layout.addWidget(instructions_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Proceed (Demo)")
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #00bcd4;
                color: #0b0c10;
                border: none;
                padding: 9px 22px;
                border-radius: 2px;
                font-size: 14px;
                font-family: '{FUTURISTIC_FONT_FAMILY}';
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #00acc1;
            }}
            QPushButton:pressed {{
                background-color: #0097a7;
            }}
        """)
        layout.addWidget(buttons)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #121318;
                border: 1px solid #00bcd4;
                border-radius: 4px;
                font-family: '{FUTURISTIC_FONT_FAMILY}';
            }}
            QLabel {{
                color: #e0e0e0;
                font-family: '{FUTURISTIC_FONT_FAMILY}';
            }}
        """)

    def set_receipt_info(self, receipt_name):
        self.share_info_label.setText(f"Preparing to share: {receipt_name}")


class AccountingAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calcite - Accounting AI Agent")
        self.setGeometry(100, 100, 850, 700)

        # Global font setting will happen *after* QFontDatabase has loaded application fonts.
        # This is typically done once the QApplication object exists.
        # See the `if __name__ == "__main__":` block.

        self.apply_global_styles() # This must be called after app.setFont() if we set it globally

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.selected_file_path = ""
        self.current_receipt_name = ""

        self.create_landing_page()
        self.create_file_selection_page()
        self.create_main_interaction_page()

        self.stacked_widget.setCurrentWidget(self.landing_page)

    def apply_global_styles(self):
        self.setStyleSheet(f"""
        QMainWindow {{
            background-color: #0b0c10;
        }}
        QWidget {{
            font-size: 14px;
            color: #e0e0e0;
            font-family: "{FUTURISTIC_FONT_FAMILY}", monospace;
        }}
        QLabel {{
            font-size: 15px;
            color: #e0e0e0;
            font-family: "{FUTURISTIC_FONT_FAMILY}";
        }}
        QPushButton {{
            background-color: #00bcd4;
            color: #0b0c10;
            border: none;
            padding: 10px 18px;
            border-radius: 2px;
            font-size: 14px;
            font-family: "{FUTURISTIC_FONT_FAMILY}";
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: #00acc1;
        }}
        QPushButton:pressed {{
            background-color: #0097a7;
        }}
        QPushButton:disabled {{
            background-color: #37474f;
            color: #78909c;
            border: 1px solid #546e7a;
        }}
        QLineEdit, QTextEdit {{
            background-color: #1c1f26;
            border: 1px solid #00bcd4;
            border-radius: 2px;
            padding: 10px;
            font-size: 14px;
            color: #e0e0e0;
            font-family: "{FUTURISTIC_FONT_FAMILY}";
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border-color: #00e5ff;
        }}
        QGroupBox {{
            font-size: 17px;
            font-weight: bold;
            color: #00e5ff;
            border: 1px solid #2e3b4e;
            border-radius: 4px;
            margin-top: 15px;
            padding: 25px 20px 20px 20px;
            background-color: #121318;
            font-family: "{FUTURISTIC_FONT_FAMILY}";
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 10px 8px 10px;
            left: 15px;
            color: #00e5ff;
            font-family: "{FUTURISTIC_FONT_FAMILY}";
        }}
        QPushButton.secondary {{
            background-color: #455a64;
            color: #e0e0e0;
        }}
        QPushButton.secondary:hover {{
            background-color: #37474f;
        }}
        QPushButton.secondary:pressed {{
            background-color: #263238;
        }}
        QPushButton.success {{
            background-color: #00e676;
            color: #0b0c10;
        }}
        QPushButton.success:hover {{
            background-color: #00c853;
        }}
        QPushButton.success:pressed {{
            background-color: #00bfa5;
        }}
        QPushButton.info {{
            background-color: #00acc1;
            color: #0b0c10;
        }}
        QPushButton.info:hover {{
            background-color: #00838f;
        }}
        QPushButton.info:pressed {{
            background-color: #006064;
        }}
      """)

    def create_landing_page(self):
        self.landing_page = QWidget()
        layout = QVBoxLayout(self.landing_page)
        layout.setContentsMargins(70, 70, 70, 70)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        welcome_label = QLabel("Welcome to Calcite")
        welcome_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 36, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet(f"""
            color: #00e5ff;
            padding-bottom: 15px;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)

        tagline_label = QLabel("Your Futuristic Accounting AI Agent")
        tagline_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16, QFont.Normal))
        tagline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline_label.setStyleSheet(f"""
            color: #a0a0c0;
            padding-bottom: 30px;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)

        start_button = QPushButton("Initialize System")
        start_button.setMinimumHeight(60)
        start_button.setFixedWidth(280)
        start_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 18, QFont.Bold))
        start_button.clicked.connect(self.go_to_file_selection)

        layout.addWidget(welcome_label)
        layout.addWidget(tagline_label)
        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.stacked_widget.addWidget(self.landing_page)

    def create_file_selection_page(self):
        self.file_selection_page = QWidget()
        layout = QVBoxLayout(self.file_selection_page)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(30)

        title_label = QLabel("Load Data Matrix")
        title_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: #00e5ff;
            margin-bottom: 30px;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)

        select_file_button = QPushButton("Browse Data Source")
        select_file_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 15, QFont.DemiBold))
        select_file_button.setMinimumWidth(280)
        select_file_button.clicked.connect(self.open_file_dialog)

        self.selected_file_label = QLabel("No data matrix loaded.")
        self.selected_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_file_label.setStyleSheet(f"""
            font-style: italic;
            color: #888899;
            margin: 20px 0;
            font-size: 15px;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)

        self.proceed_button = QPushButton("Engage Assistant")
        self.proceed_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 15, QFont.DemiBold))
        self.proceed_button.clicked.connect(self.go_to_main_interaction)
        self.proceed_button.setEnabled(False)
        self.proceed_button.setMinimumWidth(280)
        self.proceed_button.setProperty("class", "success")

        back_button = QPushButton("Return to Welcome")
        back_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 15, QFont.DemiBold))
        back_button.clicked.connect(self.go_to_landing_page)
        back_button.setMinimumWidth(280)
        back_button.setProperty("class", "secondary")

        layout.addWidget(title_label)
        layout.addWidget(select_file_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.selected_file_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding))
        layout.addWidget(self.proceed_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)

        self.stacked_widget.addWidget(self.file_selection_page)

    def create_main_interaction_page(self):
        self.main_interaction_page = QWidget()
        main_layout = QVBoxLayout(self.main_interaction_page)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        self.current_file_header_label = QLabel("Data Matrix: Standby")
        self.current_file_header_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 18, QFont.Bold))
        self.current_file_header_label.setStyleSheet(f"""
            color: #00e5ff;
            margin-bottom: 15px;
            padding: 5px;
            border-bottom: 1px solid #2e3b4e;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)
        main_layout.addWidget(self.current_file_header_label, alignment=Qt.AlignmentFlag.AlignCenter)

        input_group = QGroupBox("Command Interface")
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(15)

        command_prompt_label = QLabel("Directive:")
        command_prompt_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 15))
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("e.g., 'Execute transaction: Project Omega'")
        self.command_input.returnPressed.connect(self.submit_command)
        self.command_input.setMinimumHeight(42)

        submit_button = QPushButton("Transmit")
        submit_button.clicked.connect(self.submit_command)
        submit_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14, QFont.Bold))

        speak_button = QPushButton("Voice Input")
        speak_button.clicked.connect(self.activate_voice_input)
        speak_button.setProperty("class", "secondary")
        speak_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14, QFont.Bold))

        input_layout.addWidget(command_prompt_label, 0, 0)
        input_layout.addWidget(self.command_input, 0, 1, 1, 2)
        input_layout.addWidget(submit_button, 1, 1, Qt.AlignmentFlag.AlignRight)
        input_layout.addWidget(speak_button, 1, 2, Qt.AlignmentFlag.AlignLeft)
        input_layout.setColumnStretch(1, 3)
        input_layout.setColumnStretch(2, 1)

        main_layout.addWidget(input_group)

        output_group = QGroupBox("System Output & Logs")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Awaiting directives... System logs and confirmations will appear here.")
        self.output_text.setMinimumHeight(220)
        self.output_text.setFont(QFont(FUTURISTIC_FONT_FAMILY, 13))

        output_layout.addWidget(self.output_text)
        main_layout.addWidget(output_group)

        receipts_group = QGroupBox("Data Output Management")
        receipts_layout = QHBoxLayout(receipts_group)
        receipts_layout.setSpacing(20)
        receipts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.generate_receipt_button = QPushButton("Generate Data Export (PDF)")
        self.generate_receipt_button.clicked.connect(self.generate_receipt)
        self.generate_receipt_button.setProperty("class", "success")
        self.generate_receipt_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14, QFont.Bold))

        self.share_receipt_button = QPushButton("Transmit via Secure Channel (Demo)")
        self.share_receipt_button.clicked.connect(self.share_receipt)
        self.share_receipt_button.setProperty("class", "info")
        self.share_receipt_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14, QFont.Bold))

        receipts_layout.addWidget(self.generate_receipt_button)
        receipts_layout.addWidget(self.share_receipt_button)

        main_layout.addWidget(receipts_group)
        main_layout.addStretch(1)

        back_to_file_select_button = QPushButton("Change/Reload Data Matrix")
        back_to_file_select_button.clicked.connect(self.go_to_file_selection_from_main)
        back_to_file_select_button.setProperty("class", "secondary")
        back_to_file_select_button.setMinimumWidth(300)
        back_to_file_select_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14, QFont.Bold))

        main_layout.addWidget(back_to_file_select_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stacked_widget.addWidget(self.main_interaction_page)

    def go_to_landing_page(self):
        self.stacked_widget.setCurrentWidget(self.landing_page)

    def go_to_file_selection(self):
        self.stacked_widget.setCurrentWidget(self.file_selection_page)

    def go_to_file_selection_from_main(self):
        self.selected_file_path = ""
        self.selected_file_label.setText("No data matrix loaded.")
        self.selected_file_label.setStyleSheet(f"""
            font-style: italic; color: #888899; margin: 20px 0; font-size:15px;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)
        self.proceed_button.setEnabled(False)
        self.output_text.clear()
        self.command_input.clear()
        self.current_file_header_label.setText("Data Matrix: Standby")
        self.stacked_widget.setCurrentWidget(self.file_selection_page)

    def go_to_main_interaction(self):
        if self.selected_file_path:
            filename = self.selected_file_path.split('/')[-1]
            self.current_file_header_label.setText(f"Data Matrix Active: {filename}")
            self.output_text.append(f"[SYSTEM] Data Matrix '{self.selected_file_path}' loaded successfully.\n" + "="*40 + "\nSystem ready for directives.\n")
            self.stacked_widget.setCurrentWidget(self.main_interaction_page)
        else:
            self.selected_file_label.setText("ALERT: No Data Matrix selected. Load a source to proceed.")
            self.selected_file_label.setStyleSheet(f"""
                color: #ff4d4d;
                font-weight: bold; margin-top: 15px; font-size:15px;
                font-family: '{FUTURISTIC_FONT_FAMILY}';
            """)

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setStyleSheet(f"""
            QFileDialog {{
                background-color: #121318;
                color: #e0e0e0;
                font-family: '{FUTURISTIC_FONT_FAMILY}';
            }}
            QFileDialog QLabel, QFileDialog QTreeView, QFileDialog QListView,
            QFileDialog QPushButton, QFileDialog QLineEdit {{
                background-color: #1c1f26;
                color: #e0e0e0;
                font-family: '{FUTURISTIC_FONT_FAMILY}';
            }}
            QFileDialog QPushButton {{
                 background-color: #00bcd4; color: #0b0c10; padding: 8px 15px; border-radius: 2px;
            }}
             QFileDialog QPushButton:hover {{ background-color: #00acc1; }}
        """)
        file_dialog.setWindowTitle("Select Data Matrix Source (Excel Workbook)")
        file_dialog.setNameFilter("Excel Workbooks (*.xlsx *.xls)")
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        documents_path = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DocumentsLocation)[0]
        file_dialog.setDirectory(documents_path)

        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            # print(filenames)  returns list
            # print(filenames[0])  returns file path as str
            if filenames:
                self.selected_file_path = filenames[0]
                short_filename = self.selected_file_path.split('/')[-1]
                if len(short_filename) > 45:
                    short_filename = "..." + short_filename[-42:]
                self.selected_file_label.setText(f"Matrix Loaded: {short_filename}")
                self.selected_file_label.setStyleSheet(f"""
                    color: #00e676;
                    font-weight: bold; margin: 20px 0; font-size:15px;
                    font-family: '{FUTURISTIC_FONT_FAMILY}';
                """)
                self.proceed_button.setEnabled(True)
                self.output_text.clear()
                #todo
                self.workbook = ExcelManager(filepath=self.selected_file_path)
            else:
                self.selected_file_path = ""
                self.selected_file_label.setText("No data matrix loaded.")
                self.selected_file_label.setStyleSheet(f"""
                    font-style: italic; color: #888899; margin: 20px 0; font-size:15px;
                    font-family: '{FUTURISTIC_FONT_FAMILY}';
                """)
                self.proceed_button.setEnabled(False)


    def submit_command(self) -> None:
        command_text = self.command_input.text().strip()
        if command_text:
            self.output_text.append(f"User: {command_text}")
        return


    # def submit_command(self):
    #     command_text = self.command_input.text().strip()
    #     if command_text:
    #         self.output_text.append(f"> DIRECTIVE: '{command_text}'")
    #         if "transaction" in command_text.lower():
    #             self.output_text.append("✔️ CALCITE: Transaction directive acknowledged. (Simulated Processing)")
    #         elif "receipt" in command_text.lower() or "export" in command_text.lower():
    #             self.output_text.append("✔️ CALCITE: Data export directive recognized. Use 'Generate Data Export (PDF)' for output. (Simulated)")
    #             self.generate_receipt(command_text)
    #         elif "hello" in command_text.lower() or "status" in command_text.lower():
    #             self.output_text.append("✔️ CALCITE: System online. Awaiting directives.")
    #         else:
    #             self.output_text.append("⚠️ CALCITE: Directive not fully parsed. Rephrase or consult command lexicon. (Simulated)")
    #         self.command_input.clear()
    #         self.output_text.append("----------------------------------------")
    #     else:
    #         self.output_text.append("ℹ️ CALCITE: No directive entered. Please input a command.")
    # todo: flag2
    # activate_voice_input retrieves the command from audio instead of text
    def activate_voice_input(self) -> None:
        voice = vt.AudioTranscriber()
        command_text = voice.record_and_transcribe()
        if not command_text:
            self.output_text.append("No audio detected, perhaps you could type it instead?")
            return
        else:
            self.output_text.append(f"User: {command_text}") # todo change later, personalize
        # todo: send to model
    # def activate_voice_input(self):
    #     self.output_text.append("🎙️ CALCITE: Voice input channel active... (Simulation)")
    #     simulated_voice_command = "compile fiscal report for q4"
    #     self.output_text.append(f"🎤 CALCITE: Voice directive (simulated): '{simulated_voice_command}'")
    #     self.command_input.setText(simulated_voice_command)
    #     self.output_text.append("----------------------------------------")

    def generate_receipt(self, command_context="Button click"):
        if not self.selected_file_path:
            self.output_text.append("❌ ALERT: No Data Matrix loaded. Cannot generate export.")
            self.output_text.append("----------------------------------------")
            return

        self.current_receipt_name = f"DataExport_ID{QDir().currentMSecsSinceEpoch() % 100000}.pdf"
        self.output_text.append(f"📄 CALCITE: Generating data export: '{self.current_receipt_name}' from '{self.selected_file_path.split('/')[-1]}'. (Simulated)")
        self.output_text.append(f"   Source Directive: {command_context}")
        self.output_text.append("   (PDF generation protocol is a simulation for this UI demo.)")
        self.output_text.append("----------------------------------------")

    def share_receipt(self):
        if hasattr(self, 'current_receipt_name') and self.current_receipt_name:
            dialog = ShareDialog(self)
            dialog.set_receipt_info(self.current_receipt_name)
            dialog.exec()
            self.output_text.append(f"📲 CALCITE: Initiating secure transmission for '{self.current_receipt_name}'. (Placeholder UI)")
        else:
            self.output_text.append("⚠️ CALCITE: No data export generated in current session. Generate an export first.")
        self.output_text.append("----------------------------------------")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # --- Load custom fonts from application directory ---
    font_dir_path = QDir.cleanPath(QDir.currentPath() + "/fonts/ttf/") # Use QDir.currentPath() for broader compatibility
    # For PyInstaller or similar, QDir.appDirPath() might be better if fonts are bundled next to executable
    # font_dir_path = QDir.appDirPath() + "/fonts/ttf/"

    font_dir = QDir(font_dir_path)
    if not font_dir.exists():
        print(f"Warning: Font directory does not exist: {font_dir_path}")
        print("Ensure your 'fonts/ttf' directory is correctly placed relative to your script or executable.")
    else:
        print(f"Attempting to load fonts from: {font_dir_path}")

    loaded_font_families = []
    for font_file in font_dir.entryList(["*.ttf", "*.otf"], QDir.Filter.Files): # Also check for .otf
        font_path = font_dir.filePath(font_file)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families_for_id = QFontDatabase.applicationFontFamilies(font_id)
            if font_families_for_id:
                print(f"Successfully loaded: {font_file} (ID: {font_id}) -> Families: {font_families_for_id}")
                loaded_font_families.extend(font_families_for_id)
            else:
                print(f"Warning: Loaded {font_file} (ID: {font_id}) but no font families found by QFontDatabase.")
        else:
            print(f"Warning: Failed to load font: {font_path}")

    # Verify if "JetBrains Mono" was loaded and is available
    if FUTURISTIC_FONT_FAMILY not in loaded_font_families and loaded_font_families:
        print(f"Warning: '{FUTURISTIC_FONT_FAMILY}' not found in loaded families: {list(set(loaded_font_families))}")
        print(f"Consider updating FUTURISTIC_FONT_FAMILY at the top of the script to one of the detected names if available.")
        # Optionally, pick the first loaded JetBrains-like font if any
        # for family in loaded_font_families:
        #     if "jetbrains" in family.lower() or "mono" in family.lower():
        #         print(f"Suggestion: Try setting FUTURISTIC_FONT_FAMILY = \"{family}\"")
        #         break
    elif not loaded_font_families:
        print("No custom fonts were loaded. Application will rely on system fonts.")
    else:
        print(f"'{FUTURISTIC_FONT_FAMILY}' is available from custom loaded fonts.")
    # --- End of font loading ---

    # Set the global application font AFTER loading custom fonts
    # and potentially adjusting FUTURISTIC_FONT_FAMILY based on diagnostic prints.
    default_font = QFont(FUTURISTIC_FONT_FAMILY, 10) # Base size for JetBrains Mono
    app.setFont(default_font)

    window = AccountingAssistantUI()
    window.show()
    sys.exit(app.exec())
