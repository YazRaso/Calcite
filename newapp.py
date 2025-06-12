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
CONFIG_FILE_PATH = (Path(__file__).parent / "config" / "config.json").resolve()


class AccountingAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calcite - No Code Accounting")
        self.setGeometry(100, 100, 850, 700)
        self.file_name = None
        self.config = {}
        self.selected_signature_path = ""
        # self.apply_global_styles()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.create_loading_screen()
        self.create_landing_page()
        self.create_file_selection_page()
        self.create_main_interaction_page()
        self.load_or_initialize_config()
        self.stacked_widget.setCurrentWidget(self.loading_page)

    def create_loading_screen(self):
        self.loading_page = QWidget()
        layout = QVBoxLayout(self.loading_page)
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_gif = QLabel()
        self.loading_gif.setAlignment(Qt.AlignCenter)
        movie = QMovie("assets/loading.gif")
        self.loading_gif.setMovie(movie)
        movie.start()
        layout.addWidget(self.loading_label)
        layout.addWidget(self.loading_gif)
        self.stacked_widget.addWidget(self.loading_page)

    def create_landing_page(self):
        self.landing_page = QWidget()
        layout = QVBoxLayout(self.landing_page)
        title_label = QLabel("Welcome to Calcite - No Code Accounting")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(FUTURISTIC_FONT_FAMILY, 24, QFont.Bold))
        layout.addWidget(title_label)

        description_label = QLabel(
            "Calcite is a no-code accounting assistant that helps you manage your finances effortlessly."
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        start_button = QPushButton("Get Started")
        start_button.clicked.connect(self.go_to_file_selection_page)
        layout.addWidget(start_button)

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
