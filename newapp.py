import requests
import os
import sys
import json
from pathlib import Path
import platform
import subprocess
from core.books import ExcelManager
from utils import server
from PySide6.QtCore import Qt, QDir, QStandardPaths, QSize, Slot, QTimer
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
    QProgressBar,
    QInputDialog
)

FUTURISTIC_FONT_FAMILY = "JetBrains Mono"
CORE_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"
ACTIONS_SERVER_URL = "http://localhost:5055/"
CORE_SERVER_HEALTH_URL = "http://localhost:5005/status"
ACTIONS_SERVER_HEALTH_URL = "http://localhost:5055/health"
CONFIG_FILE_PATH = (Path(__file__).parent / "config" / "config.json").resolve()

# Styles
COLORS = {
    "light": {
        "primary": "#2DD4BF",
        "primary disabled": "#a9efe7",
        "text": "#0F4C75",
        "bg": "#F8F9FA",
        "card": "#FFFFFF",
        "border": "#E9ECEF",
        "success": "#4AD66D",
        "warning": "#FF9F1C"
    },
    "dark": {
        "primary": "#2DD4BF",  # Keep teal as accent in dark mode
        "primary disabled": "#a9efe7",
        "text": "#E9ECEF",
        "bg": "#121212",
        "card": "#1E1E1E",
        "border": "#2D2D2D",
        "success": "#4AD66D",
        "warning": "#FF9F1C"
    }
}


class AccountingAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calcite - No Code Accounting")
        self.setGeometry(100, 100, 850, 700)
        self.file_path = None
        self.file_abs_path = None
        self.current_theme = "light"
        self.selected_signature_path = ""
        # self.apply_global_styles()

        self.setup_theme_system()
        self.toggle_theme()
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.create_loading_screen()
        self.create_error_page()
        self.create_landing_page()
        self.create_file_selection_page()
        self.create_main_interaction_page()
        self.create_setup_page()
        self.stacked_widget.addWidget(self.loading_page)
        self.initialize_system()

    def setup_theme_system(self):
        """Initialize theme toggle and signal connections"""
        # Add toggle button to a persistent area (e.g., status bar)
        self.theme_toggle = QPushButton("🌙 Dark Mode")
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setFixedSize(145, 40)
        self.theme_toggle.clicked.connect(self.toggle_theme)
        
        # Add to status bar (or your app's header/navigation)
        self.statusBar().addPermanentWidget(self.theme_toggle)

    def on_server_response(self):
        if True or (server.check_server_health(
                    ACTIONS_SERVER_HEALTH_URL) and server.check_server_health(
                    CORE_SERVER_HEALTH_URL)):
            self.stacked_widget.setCurrentWidget(self.landing_page)
        else:
            self.stacked_widget.setCurrentWidget(self.error_page)

    def initialize_system(self):
        # Show loading screen
        self.stacked_widget.setCurrentWidget(self.loading_page)
        # Boot up servers
        server.start_server()
        with open(CONFIG_FILE_PATH, "r") as f:
            config = json.load(f)
            if config['user']['firstTime']:
                self.stacked_widget.setCurrentWidget(self.setup_page)
            else:
                self.on_server_response()

    @Slot()
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.update_theme()
        
        # Update button text
        icon = "☀️" if self.current_theme == "light" else "🌙"
        self.theme_toggle.setText(f"{icon} {'Dark' if self.current_theme == 'dark' else 'Light'} Mode")

    def update_theme(self):
        """Update all styles based on current theme"""
        colors = COLORS[self.current_theme]
        stylesheet = f"""
            QWidget {{
                background-color: {colors['bg']};
                color: {colors['text']};
                font-family: "{FUTURISTIC_FONT_FAMILY}";
            }}
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:disabled {{
                background-color: {colors['primary disabled']};
            }}
            QPushButton:hover {{
                background-color: #25B9A6;
            }}
            QPushButton.secondary {{
                background-color: {colors['text']};
            }}
            QPushButton.success {{
                background-color: {colors['success']};
            }}
            QFrame.data-card, QWidget.dashboard-widget {{
                background-color: {colors['card']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
            }}
            QLabel.header {{
                font-size: 18px;
                font-weight: bold;
                color: {colors['primary']};
            }}
            QGroupBox {{
                border: 1px solid {colors['primary']};
                padding: 2px
            }}
        """
        
        self.setStyleSheet(stylesheet)
        
        # Update toggle button style to stand out
        self.theme_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['card']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
            }}
        """)

    def create_loading_screen(self):
        self.loading_page = QWidget()
        layout = QVBoxLayout(self.loading_page)

        label = QLabel("Loading Calcite...")
        label.setAlignment(Qt.AlignCenter)

        with open(CONFIG_FILE_PATH, 'r') as f:
            data = json.load(f)
            name = data['user']['name']
            first_time = data['user']['firstTime']

        if not first_time:
            name = QLabel(f"{name}")
            name.setAlignment(Qt.AlignCenter)
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate
        progress.setFixedHeight(30)

        layout.addStretch()
        layout.addWidget(label)
        if not first_time:
            layout.addWidget(name)
        layout.addWidget(progress)
        layout.addStretch()

    def create_error_page(self):
        self.error_page = QWidget()
        layout = QVBoxLayout(self.error_page)

        label = QLabel("⚠️ System failed to load server!")
        label.setAlignment(Qt.AlignCenter)

        retry_button = QPushButton("Retry")
        retry_button.clicked.connect(self.initialize_system)

        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(retry_button, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.stacked_widget.addWidget(self.error_page)

    def create_landing_page(self):
        self.landing_page = QWidget()
        layout = QVBoxLayout(self.landing_page)
        layout.setSpacing(5)
        description_label = QLabel(
            "Calcite AI: Your personal accountant — on your desktop, 24/7"
        )

        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        start_button = QPushButton("Get Started")
        start_button.setFixedSize(200, 75)
        start_button.clicked.connect(self.go_to_file_selection_page)
        layout.addWidget(start_button, alignment=Qt.AlignCenter)
        self.stacked_widget.addWidget(self.landing_page)

    def create_file_selection_page(self):
        self.file_selection_page = QWidget()
        layout = QVBoxLayout(self.file_selection_page)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignCenter)
        # Create title label
        title_label = QLabel("Select spreadsheet")
        title_label.setAlignment(Qt.AlignCenter)
        # Create select button
        select_button = QPushButton("Browse spreadsheets")
        select_button.clicked.connect(self.on_select_file_button_clicked)
        # Create label to show selected file
        self.selected_file_label = QLabel("Please select a file to get started")
        self.selected_file_label.setAlignment(Qt.AlignCenter)
        # Create next button
        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.go_to_main_interaction_page)
        # Create back button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_to_landing_page)
        # Layout created widgets
        layout.addWidget(title_label)
        layout.addWidget(select_button)
        layout.addWidget(self.selected_file_label)
        layout.addWidget(self.next_button)
        layout.addWidget(self.back_button)
        self.stacked_widget.addWidget(self.file_selection_page)

    def create_main_interaction_page(self):
        self.main_interaction_page = QWidget()
        main_layout = QVBoxLayout(self.main_interaction_page)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(25)

        self.current_file_header_label = QLabel("Spreadsheet")
        main_layout.addWidget(self.current_file_header_label, alignment=Qt.AlignCenter)

        input_group = QGroupBox("")
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(15)

        prompt_label = QLabel("Prompt")
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Add a transaction of 30 AED, reference 200, for today at rate of 2.7")
        self.prompt_input.setMinimumHeight(42)
        self.prompt_input.returnPressed.connect(self.submit_AI_request)

        submit_button = QPushButton("Send")
        submit_button.clicked.connect(self.submit_AI_request)

        input_layout.addWidget(prompt_label, 0, 0)
        input_layout.addWidget(self.prompt_input, 0, 1)
        input_layout.addWidget(submit_button, 0, 2, Qt.AlignRight)

        main_layout.addWidget(input_group)

        output_group = QGroupBox("")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(15)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Ready when you are - Calcite")

        output_layout.addWidget(self.output_text)
        main_layout.addWidget(output_group)

        receipts_group = QGroupBox("")
        receipts_layout = QHBoxLayout(receipts_group)
        receipts_layout.setSpacing(15)

        self.generate_receipt_button = QPushButton("Generate Receipt")
        self.generate_receipt_button.clicked.connect(self.on_generate_receipt_button_clicked)

        self.past_receipts_button = QPushButton("Past Receipts")
        self.past_receipts_button.clicked.connect(self.on_past_receipts_button_clicked)

        receipts_layout.addWidget(self.generate_receipt_button)
        receipts_layout.addWidget(self.past_receipts_button)

        main_layout.addWidget(receipts_group)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_to_file_selection_page)

        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        self.stacked_widget.addWidget(self.main_interaction_page)

    def go_to_landing_page(self):
        self.stacked_widget.setCurrentWidget(self.landing_page)
    
    def go_to_file_selection_page(self):
        self.stacked_widget.setCurrentWidget(self.file_selection_page)

    def go_to_main_interaction_page(self):
        self.stacked_widget.setCurrentWidget(self.main_interaction_page)

    def on_select_file_button_clicked(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Spreadsheet")
        file_dialog.setNameFilter("Excel Files (*.xlsx *.xls *xlsm)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        sheet_data_path = Path(__file__).parent / "sheet_data"
        file_dialog.setDirectory(str(sheet_data_path))

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # Get the file from the dialoge
                self.file_path = selected_files[0]
                self.file_abs_path = self.file_path = Path(self.file_path).resolve()
                # Check if file is a child of sheet data
                try:
                    self.file_path = self.file_path.relative_to(sheet_data_path)
                except ValueError:
                    QMessageBox.warning(self, "Invalid Selection", "You must select a file inside the 'sheet_data' folder.")
                    return
                # Display file path name
                self.selected_file_label.setText(f"Selected file: {self.file_path}")
                self.next_button.setEnabled(True)
            else:
                self.selected_file_label.setText("Please select a file to get started")

    def submit_AI_request(self) -> None:
        prompt = self.prompt_input.text().strip()
        if prompt:
            # Append file path to request
            prompt += f" EXCEL_FILE_PATH{self.file_path}"
            # Attempt to get hold of server
            try:
                response = requests.post(url=CORE_SERVER_URL,
                                         json={"sender": "user1",
                                               "message": prompt})
                # Check if response was accepted
                if response.status_code == requests.codes.ok:
                    self.output_text.append(f"User: {prompt}")
                    messages = response.json()
                    for msg in messages:
                        if 'text' in msg:
                            self.output_text.append(f"Calcite: {msg['text']}")
            # Give warnings incase of exception
            except Exception as e:
                QMessageBox.warning(self, "Error", "The server was unable to accept your request, no changes made")
            finally:
                # Prepare for next message
                self.prompt_input.clear()

    def on_generate_receipt_button_clicked(self):
        receipt_client = ExcelManager(self.file_abs_path)
        received_by, confirmed = QInputDialog.getText(self, "Assign receipt", "Who is receiving this receipt?")
        if confirmed:
            receipt_name = receipt_client.generate_receipt(received_by=received_by)
            QMessageBox.information(self, "Receipt Generated", f"Receipt for latest transaction added at {receipt_name}")

    def on_past_receipts_button_clicked(self):
        receipts_path = (Path(__file__).parent / "receipts").resolve()

        if platform.system() == "Windows":
            os.startfile(receipts_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(receipts_path)])
        else:
            subprocess.Popen(["xdg-open", str(receipts_path)])

    def create_setup_page(self):
        self.setup_page = QWidget()
        layout = QVBoxLayout(self.setup_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(70, 50, 70, 50)
        layout.setSpacing(30)

        title_label = QLabel("First time setup")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)

        subtitle_label = QLabel("Connect. Configure. Done.")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(subtitle_label)

        setup_group = QGroupBox("Let's get Calcite set up for you")
        setup_group_layout = QFormLayout(setup_group)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Yaz Raso")
        
        name_label = QLabel("Full Name:")
        name_label.setAutoFillBackground(False)
        setup_group_layout.addRow(name_label, self.name_input)

        signature_field_layout = QHBoxLayout()
        self.select_signature_button = QPushButton("Upload signature")
        self.select_signature_button.clicked.connect(self.select_signature_file)
        signature_field_layout.addWidget(self.select_signature_button)

        self.signature_path_label = QLabel("No signature image selected.")
        sig_label = QLabel("Signature Image:")
        sig_label.setAutoFillBackground(False)
        setup_group_layout.addRow(sig_label, signature_field_layout)

        layout.addWidget(setup_group)

        self.save_setup_button = QPushButton("Save and continue")
        self.save_setup_button.clicked.connect(self.save_first_time_setup)

        layout.addWidget(self.save_setup_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.stacked_widget.addWidget(self.setup_page)

    def select_signature_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Signature File")
        file_dialog.setNameFilter("JPEG and PNG only (*.jpg *.png)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            self.selected_signature_path = file_dialog.selectedFiles()

    def save_first_time_setup(self):
        user_name = self.name_input.text().strip()
        if not user_name:
            QMessageBox.warning(self, "Input Required", "Please enter your full name.")
            return
        if not self.selected_signature_path:
            QMessageBox.warning(self, "Input Required", "Please select a signature image.")
            return

        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)

            config["user"]["name"] = user_name
            config["user"]["signaturePath"] = self.selected_signature_path
            config["user"]["firstTime"] = False

            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", "Unable to save configuration")

        else:
            # Check server
           self.on_server_response() 


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
    window.showFullScreen()
    # Start the event loop
    sys.exit(app.exec())
