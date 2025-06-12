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
    QProgressBar
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
        self.file_name = None
        self.current_theme = "light"
        self.config = {}
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
        self.load_or_initialize_config()
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

    def initialize_system(self):
        # Show loading screenn
        self.stacked_widget.setCurrentWidget(self.loading_page)
        # Boot up servers
        server.start_server()
        # Check if the servers are up
        # TODO: Remove short circuit true once done testing
       # if False and (server.check_server_health(
        #            ACTIONS_SERVER_HEALTH_URL) and server.check_server_health(
         #           CORE_SERVER_HEALTH_URL)):
          #     self.stacked_widget.setCurrentWidget(self.landing_page)
        if False:
            self.stacked_widget.setCurrentWidget(self.error_page)
        else:
            self.stacked_widget.setCurrentWidget(self.error_page)

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
        label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 20, QFont.Bold))

        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate
        progress.setFixedHeight(30)

        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(progress)
        layout.addStretch()

    def create_error_page(self):
        self.error_page = QWidget()
        layout = QVBoxLayout(self.error_page)

        label = QLabel("⚠️ System failed to load server!")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 20, QFont.Bold))

        retry_button = QPushButton("Retry")
        retry_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
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

        description_label.setFont(QFont(
            FUTURISTIC_FONT_FAMILY, 16, QFont.Bold)
                                  )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        start_button = QPushButton("Get Started")
        start_button.setFixedSize(200, 75)
        start_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
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
        title_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        # Create select button
        select_button = QPushButton("Browse spreadsheets")
        select_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
        select_button.clicked.connect(self.on_select_file_button_clicked)
        # Create label to show selected file
        self.selected_file_label = QLabel("Please select a file to get started")
        self.selected_file_label.setAlignment(Qt.AlignCenter)
        # Create next button
        self.next_button = QPushButton("Next")
        self.next_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.go_to_main_interaction_page)
        # Create back button
        self.back_button = QPushButton("Back")
        self.back_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
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
        self.current_file_header_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 24, QFont.Bold))
        main_layout.addWidget(self.current_file_header_label, alignment=Qt.AlignCenter)

        input_group = QGroupBox("Chat")
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(15)

        prompt_label = QLabel("Prompt")
        prompt_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Add a transaction of 30 AED, reference 200, for today at rate of 2.7")

        submit_button = QPushButton("Send")
        submit_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
        submit_button.clicked.connect(self.on_submit_button_clicked)

        input_layout.addWidget(prompt_label, 0, 0)
        input_layout.addWidget(self.prompt_input, 0, 1)
        input_layout.addWidget(submit_button, 0, 2, Qt.AlignRight)

        main_layout.addWidget(input_group)

        output_group = QGroupBox("Calcite")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(15)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Ready when you are - Calcite")
        self.output_text.setFont(QFont(FUTURISTIC_FONT_FAMILY, 14))

        output_layout.addWidget(self.output_text)
        main_layout.addWidget(output_group)

        receipts_group = QGroupBox("Receipts")
        receipts_layout = QHBoxLayout(receipts_group)
        receipts_layout.setSpacing(15)

        self.generate_receipt_button = QPushButton("Generate Receipt")
        self.generate_receipt_button.clicked.connect(self.on_generate_receipt_button_clicked)
        self.generate_receipt_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))

        self.past_receipts_button = QPushButton("Past Receipts")
        self.past_receipts_button.clicked.connect(self.on_past_receipts_button_clicked)
        self.past_receipts_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))

        receipts_layout.addWidget(self.generate_receipt_button)
        receipts_layout.addWidget(self.past_receipts_button)

        main_layout.addWidget(receipts_group)

        back_button = QPushButton("Back")
        back_button.setFont(QFont(FUTURISTIC_FONT_FAMILY, 16))
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
        documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)[0]
        file_dialog.setDirectory(documents_path)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # Get the short name of the excel file
                self.file_name = selected_files[0]
                display_file_name = selected_files[0].split('/')[-1]
                self.selected_file_label.setText(f"Selected file: {display_file_name}")
                self.next_button.setEnabled(True)
            else:
                self.selected_file_label.setText("Please select a file to get started")

    def on_submit_button_clicked(self):
        pass

    def on_generate_receipt_button_clicked(self):
        pass

    def on_past_receipts_button_clicked(self):
        pass

    def load_or_initialize_config(self):
        pass


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
