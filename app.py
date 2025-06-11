import requests
import os
import sys
import json
from pathlib import Path
import platform
import subprocess
from core.books import ExcelManager
from utils import server
from PySide6.QtCore import Qt, QDir, QStandardPaths, QSize, QTimer
from PySide6.QtGui import QFont, QMovie, QFontDatabase
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
    QGridLayout,
    QSpacerItem,
    QSizePolicy,
    QGroupBox,
    QMessageBox,
    QFormLayout,
)

FUTURISTIC_FONT_FAMILY = "JetBrains Mono"
CORE_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"
ACTIONS_SERVER_URL = "http://localhost:5055/"
CORE_SERVER_HEALTH_URL = "http://localhost:5005/status"
ACTIONS_SERVER_HEALTH_URL = "http://localhost:5055/health"
CONFIG_FILE_PATH = "config/config.json"


class AccountingAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calcite - No Code Accounting")
        self.setGeometry(100, 100, 850, 700)
        self.file_name = None
        self.config = {}
        self.selected_signature_path = ""  # For first-time setup

        self.load_or_initialize_config()  # Load or create config.json

        self.apply_global_styles()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.current_receipt_name = ""

        # Create ALL pages that might be needed.
        # The first_time_setup_page is created regardless; its display is conditional.
        self.create_first_time_setup_page()
        self.create_loading_screen()
        self.create_landing_page()
        self.create_file_selection_page()
        self.create_main_interaction_page()

        # Determine initial page and setup based on firstTime status
        if self.config.get("user", {}).get("firstTime", True):
            self.stacked_widget.setCurrentWidget(self.first_time_setup_page)
            # Server startup and health check will be initiated after setup completion.
        else:
            self.stacked_widget.setCurrentWidget(self.loading_page)
            if hasattr(self, 'loading_movie') and self.loading_movie and self.loading_movie.isValid():
                self.loading_movie.start()

            # If not first time, initialize and configure the health check timer immediately
            self.health_check_timer = QTimer(self)
            self.health_check_timer.setInterval(500)  # Check health every 500ms
            self.health_check_timer.timeout.connect(self.check_server_status_and_proceed)

            
            server.start_server()
            self.check_server_status_and_proceed()  # Perform an initial check

    def load_or_initialize_config(self):
        default_config = {
            "user": {
                "firstTime": True,
                "name": "",
                "signaturePath": ""
            }
        }
        try:
            if os.path.exists(CONFIG_FILE_PATH):
                with open(CONFIG_FILE_PATH, 'r') as f:
                    self.config = json.load(f)
                # Basic validation
                if not isinstance(self.config.get("user"), dict) or \
                        not isinstance(self.config.get("user", {}).get("firstTime"), bool):
                    print("Config file 'user' section is malformed. Resetting to default.")
                    self.config = default_config
                    self.save_config_to_file()
            else:
                print("Config file not found. Creating default config.")
                self.config = default_config
                self.save_config_to_file()
        except json.JSONDecodeError:
            print(f"Error decoding {CONFIG_FILE_PATH}. Resetting to default.")
            self.config = default_config
            self.save_config_to_file()
        except Exception as e:
            print(f"An unexpected error occurred while loading config: {e}. Using default.")
            self.config = default_config
            # self.save_config_to_file() # Optionally save default if a generic error occurs

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

    def save_config_to_file(self):
        try:
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Config saved to {CONFIG_FILE_PATH}")
        except Exception as e:
            print(f"Error saving config to {CONFIG_FILE_PATH}: {e}")

    def create_first_time_setup_page(self):
        self.first_time_setup_page = QWidget()
        layout = QVBoxLayout(self.first_time_setup_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(70, 50, 70, 50)  # Adjusted margins
        layout.setSpacing(30)

        title_label = QLabel("Welcome to Calcite!")
        title_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: #00e5ff; padding-bottom: 10px; font-family: '{FUTURISTIC_FONT_FAMILY}';")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Let's get you set up for a seamless experience.")
        subtitle_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16, QFont.Weight.Normal))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"color: #a0a0c0; padding-bottom: 25px; font-family: '{FUTURISTIC_FONT_FAMILY}';")
        layout.addWidget(subtitle_label)

        setup_group = QGroupBox("Your Information")
        setup_group_layout = QFormLayout(setup_group)  # QFormLayout is good for label-field pairs
        setup_group_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)  # Handles smaller screens better
        setup_group_layout.setSpacing(20)
        setup_group_layout.setContentsMargins(25, 35, 25, 25)  # Padding inside groupbox

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setMinimumHeight(40)
        name_label = QLabel("Full Name:")
        name_label.setStyleSheet("padding-top: 5px;")  # Align better with QLineEdit height
        setup_group_layout.addRow(name_label, self.name_input)

        signature_field_layout = QHBoxLayout()
        self.select_signature_button = QPushButton("Browse File...")
        self.select_signature_button.setFixedWidth(150)
        self.select_signature_button.clicked.connect(self.select_signature_file)
        signature_field_layout.addWidget(self.select_signature_button)

        self.signature_path_label = QLabel("No signature image selected.")
        self.signature_path_label.setStyleSheet("color: #888899; font-style: italic; margin-left: 10px;")
        signature_field_layout.addWidget(self.signature_path_label)
        signature_field_layout.addStretch()

        sig_label = QLabel("Signature Image:")
        sig_label.setStyleSheet("padding-top: 5px;")
        setup_group_layout.addRow(sig_label, signature_field_layout)

        layout.addWidget(setup_group)
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.save_setup_button = QPushButton("Save and Continue")
        self.save_setup_button.setMinimumHeight(50)
        self.save_setup_button.setFixedWidth(250)
        self.save_setup_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16, QFont.Weight.Bold))
        self.save_setup_button.setProperty("class", "success")  # Use success styling
        self.save_setup_button.clicked.connect(self.save_first_time_setup)
        layout.addWidget(self.save_setup_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()  # Pushes content upwards if there's extra space

        self.stacked_widget.addWidget(self.first_time_setup_page)

    def select_signature_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Signature Image",
            self.selected_signature_path or os.path.expanduser("~"),  # Start in user's home or last path
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if file_path:
            self.selected_signature_path = file_path
            file_name = os.path.basename(file_path)
            self.signature_path_label.setText(file_name)
            self.signature_path_label.setStyleSheet("color: #e0e0e0; margin-left: 10px;")  # Reset style to normal color
            print(f"Signature file selected: {file_path}")
    # FLAG 1
    def save_first_time_setup(self):
        user_name = self.name_input.text().strip()

        if not user_name:
            self.show_message_dialog("Input Required", "Please enter your full name.", "warning")
            return
        if not self.selected_signature_path:
            self.show_message_dialog("Input Required", "Please select a signature image.", "warning")
            return

        self.config["user"]["name"] = user_name
        self.config["user"]["signaturePath"] = self.selected_signature_path
        self.config["user"]["firstTime"] = False
        self.save_config_to_file()

        print("First-time setup complete. User data saved.")

        # Now, transition to the loading screen and start server health checks
        self.stacked_widget.setCurrentWidget(self.loading_page)
        if hasattr(self, 'loading_movie') and self.loading_movie and self.loading_movie.isValid():
            self.loading_movie.start()

        # Initialize and start health check process
        if not hasattr(self, 'health_check_timer'):
            self.health_check_timer = QTimer(self)
            self.health_check_timer.setInterval(500)
            self.health_check_timer.timeout.connect(self.check_server_status_and_proceed)

        self.health_check_timer.start()
        self.check_server_status_and_proceed()

    def show_message_dialog(self, title, message, icon_type="information"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: #1c1f26;
                font-family: "{FUTURISTIC_FONT_FAMILY}";
            }}
            QLabel {{ /* For the message text */
                color: #e0e0e0;
                font-size: 14px;
                font-family: "{FUTURISTIC_FONT_FAMILY}";
            }}
            QPushButton {{ /* Standard button styling from global styles */
                background-color: #00bcd4; color: #0b0c10; border: none;
                padding: 8px 16px; border-radius: 2px; font-size: 14px;
                font-family: "{FUTURISTIC_FONT_FAMILY}"; font-weight: 500;
            }}
            QPushButton:hover {{ background-color: #00acc1; }}
            QPushButton:pressed {{ background-color: #0097a7; }}
        """)
        if icon_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif icon_type == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)
        else:  # "information"
            msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    def create_loading_screen(self):
        self.loading_page = QWidget()
        layout = QVBoxLayout(self.loading_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)  # Added margins
        layout.setSpacing(30)  # Added spacing

        loading_text_label = QLabel("Initializing Calcite Systems...\nPlease Wait.")
        loading_text_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 24, QFont.Weight.Bold))
        loading_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_text_label.setStyleSheet(f"""
            color: #00e5ff;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)
        layout.addWidget(loading_text_label)

        # Optional: Animated GIF for loading
        # IMPORTANT: You need to provide a 'loading.gif' file in the same directory
        # as your script, or provide the correct path to your GIF.
        self.movie_label = QLabel(self)  # Parent it to self for QMovie to work reliably in some Qt bindings
        self.loading_movie = None  # Initialize to None
        try:
            # Replace "loading.gif" with the path to your actual loading animation
            movie = QMovie("assets/loading.gif")  # Ensure this file exists!
            if movie.isValid():
                self.loading_movie = movie
                self.loading_movie.setScaledSize(QSize(120, 120))  # Adjust size as needed
                self.movie_label.setMovie(self.loading_movie)
            else:
                print("Warning: loading.gif is not valid or not found. Displaying static text.")
                self.movie_label.setText("Loading animation...")  # Fallback text
                self.movie_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
                self.movie_label.setStyleSheet("color: #a0a0c0;")
        except Exception as e:
            print(f"Error loading QMovie: {e}")
            self.movie_label.setText("Loading animation error...")  # Fallback text
            self.movie_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
            self.movie_label.setStyleSheet("color: #a0a0c0;")

        self.movie_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.movie_label)

        self.stacked_widget.addWidget(self.loading_page)

    def check_server_status_and_proceed(self):
        """
        Checks the action server's health. If healthy, stops the timer
        and transitions to the landing page. Otherwise, ensures loading
        animation is running.
        The original request: "the screen must keep being a loading screen while actions_server.check_health() -> bool"
        This is interpreted as:
        - If check_health() is TRUE (server is healthy), THEN WE ARE DONE LOADING.
        - If check_health() is FALSE (server is NOT healthy), THEN WE KEEP LOADING.
        """
        # print(f"Checking server health... Status: {actions_server.check_health()}") # For debugging
        action_server_up, core_server_up = server.check_server_health(url=ACTIONS_SERVER_HEALTH_URL), server.check_server_health(url=CORE_SERVER_HEALTH_URL)
        if True or (action_server_up and core_server_up):  # Server is healthy, proceed
            # REMOVE THE True, it is only here for testing gui
            self.health_check_timer.stop()
            if hasattr(self, 'loading_movie') and self.loading_movie and self.loading_movie.isValid():
                self.loading_movie.stop()
            self.stacked_widget.setCurrentWidget(self.landing_page)
        else:  # Server not healthy yet, keep showing loading screen
            # Ensure loading screen is visible and animation is (re)started if needed
            if self.stacked_widget.currentWidget() != self.loading_page:
                self.stacked_widget.setCurrentWidget(self.loading_page)
            if hasattr(self, 'loading_movie') and self.loading_movie and self.loading_movie.isValid() and \
                    self.loading_movie.state() != QMovie.MovieState.Running:
                self.loading_movie.start()

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

        start_button = QPushButton("Start")
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

        title_label = QLabel("Load spreadsheet")
        title_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: #00e5ff;
            margin-bottom: 30px;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)

        select_file_button = QPushButton("Browse spreadsheets")
        select_file_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 15, QFont.DemiBold))
        select_file_button.setMinimumWidth(280)
        select_file_button.clicked.connect(self.open_file_dialog)

        self.selected_file_label = QLabel("No spreadsheet selected.")
        self.selected_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_file_label.setStyleSheet(f"""
            font-style: italic;
            color: #888899;
            margin: 20px 0;
            font-size: 15px;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)

        self.proceed_button = QPushButton("Next")
        self.proceed_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 15, QFont.DemiBold))
        self.proceed_button.clicked.connect(self.go_to_main_interaction)
        self.proceed_button.setEnabled(False)
        self.proceed_button.setMinimumWidth(280)
        self.proceed_button.setProperty("class", "success")

        back_button = QPushButton("Back")
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

        self.current_file_header_label = QLabel("Spreadsheet")
        self.current_file_header_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 18, QFont.Bold))
        self.current_file_header_label.setStyleSheet(f"""
            color: #00e5ff;
            margin-bottom: 15px;
            padding: 5px;
            border-bottom: 1px solid #2e3b4e;
            font-family: '{FUTURISTIC_FONT_FAMILY}';
        """)
        main_layout.addWidget(self.current_file_header_label, alignment=Qt.AlignmentFlag.AlignCenter)

        input_group = QGroupBox("Chat")
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(15)

        command_prompt_label = QLabel("Prompt:")
        command_prompt_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 15))
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Ready when you are...")
        self.command_input.returnPressed.connect(self.submit_command)
        self.command_input.setMinimumHeight(42)

        submit_button = QPushButton("Send")
        submit_button.clicked.connect(self.submit_command)
        submit_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14, QFont.Bold))

        input_layout.addWidget(command_prompt_label, 0, 0)
        input_layout.addWidget(self.command_input, 0, 1, 1, 2)
        input_layout.addWidget(submit_button, 1, 3, Qt.AlignmentFlag.AlignRight)
        input_layout.setColumnStretch(1, 3)
        input_layout.setColumnStretch(2, 1)

        main_layout.addWidget(input_group)

        output_group = QGroupBox("Calcite AI")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Awaiting Orders")
        self.output_text.setMinimumHeight(220)
        self.output_text.setFont(QFont(FUTURISTIC_FONT_FAMILY, 13))

        output_layout.addWidget(self.output_text)
        main_layout.addWidget(output_group)

        receipts_group = QGroupBox("Receipts")
        receipts_layout = QHBoxLayout(receipts_group)
        receipts_layout.setSpacing(20)
        receipts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.generate_receipt_button = QPushButton("Generate Receipt")
        self.generate_receipt_button.clicked.connect(self.generate_receipt)
        self.generate_receipt_button.setProperty("class", "success")
        self.generate_receipt_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14, QFont.Bold))

        self.past_receipts_button = QPushButton("Past Receipts")
        self.past_receipts_button.clicked.connect(self.past_receipts)
        self.past_receipts_button.setProperty("class", "info")
        self.past_receipts_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14, QFont.Bold))

        receipts_layout.addWidget(self.generate_receipt_button)
        receipts_layout.addWidget(self.past_receipts_button)

        main_layout.addWidget(receipts_group)
        main_layout.addStretch(1)

        back_to_file_select_button = QPushButton("Back")
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
        self.selected_file_label.setText("Please select a spreadsheet to get started.")
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
            self.current_file_header_label.setText(f"Current Spreadsheet: {filename}")
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
            self.selected_file_path = filenames[0]
            # print(filenames)  returns list
            # print(filenames[0])  returns file path as str
            if filenames:
                self.selected_file_path = filenames[0]
                short_filename = self.selected_file_path.split('/')[-1]
                if len(short_filename) > 45:
                    short_filename = "..." + short_filename[-42:]
                self.selected_file_label.setText(f"Selected spreadsheet: {short_filename}")
                self.selected_file_label.setStyleSheet(f"""
                    color: #00e676;
                    font-weight: bold; margin: 20px 0; font-size:15px;
                    font-family: '{FUTURISTIC_FONT_FAMILY}';
                """)
                self.proceed_button.setEnabled(True)
                self.output_text.clear()
                #todo
            else:
                self.selected_file_path = ""
                self.selected_file_label.setText("No spreadsheet loaded.")
                self.selected_file_label.setStyleSheet(f"""
                    font-style: italic; color: #888899; margin: 20px 0; font-size:15px;
                    font-family: '{FUTURISTIC_FONT_FAMILY}';
                """)
                self.proceed_button.setEnabled(False)

    def submit_command(self) -> None:
        command_text = self.command_input.text().strip()
        if command_text:
            self.output_text.append(f"User: {command_text}")
            command_text += f"to EXCEL_FILE_PATH:{self.selected_file_path}"
            # Now we have to make a call to the api
            response = requests.post(url=CORE_SERVER_URL,
                                     json={"sender": "user1",
                                     "message": command_text})
            print(response.text)
            if response.status_code == requests.codes.ok:
                messages = response.json()
                for msg in messages:
                    if 'text' in msg:
                        self.output_text.append(f"Assistant: {msg['text']}")
            else:
                print("Error:", response.status_code, response.text)
        self.command_input.clear()
        return

    def generate_receipt(self, command_context="Button click"):
        if not self.selected_file_path:
            self.output_text.append("❌ ALERT: No Data Matrix loaded. Cannot generate export.")
            self.output_text.append("----------------------------------------")
            return
        self.wb = ExcelManager(self.selected_file_path)
        self.wb.generate_receipt()
        self.output_text.append(f"Receipts saved in: {Path('receipts').resolve()}")
        self.output_text.append("----------------------------------------")

    @staticmethod
    def past_receipts(self):
        receipts_path = Path("receipts").resolve()

        if not receipts_path.exists():
            print("Receipts folder does not exist.")
            return

        if platform.system() == "Windows":
            os.startfile(receipts_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", str(receipts_path)])
        else:  # Linux
            subprocess.Popen(["xdg-open", str(receipts_path)])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load fonts
    font_dir_path = QDir.cleanPath(QDir.currentPath() + "/fonts/ttf/")
    font_dir = QDir(font_dir_path)
    
    # Add font loading
    if font_dir.exists():
        for font_file in font_dir.entryList(["*.ttf"], QDir.Filter.Files):
            font_path = font_dir.absoluteFilePath(font_file)
            QFontDatabase.addApplicationFont(font_path)
    
    # Create and show the main window
    window = AccountingAssistantUI()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())
