import json
import time
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, \
    QHBoxLayout, QMessageBox, QInputDialog, QFileDialog, QSlider
import threading
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QMouseEvent, QIcon, QPen
from PySide6.QtCore import Qt, QTimer, QRect
import random

class LoginWindow(QWidget):
    window_width = 1000
    window_height = 800

    CONFIG_FILE = "config.json"

    def __init__(self):
        super().__init__()
        self.error_label = QLabel(self)
        self.game_display = GameWidget(self)
        self.instruction_label = QLabel(self)
        self.new_game_button = None
        self.save_game_button = None
        self.load_game_button = None
        self.exit_button = None
        self.last_saved_filename = None
        self.load_config()
        self.difficulty_slider = None
        self.setup()


    def save_config(self):
        # Save the last saved file name to the configuration file
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump({"last_saved_filename": self.last_saved_filename}, f)
    def load_config(self):
        # Load last saved filename to the configuration file
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.last_saved_filename = config.get("last_saved_filename")
        except FileNotFoundError:
            pass
        # Ignore if the config file does not exist

    def exit_app(self):
        reply = QMessageBox.question(self, 'Quit Application',
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()

    def setup(self):
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        button_size = (120, 40)

        self.new_game_button = QPushButton("New game", self)
        self.new_game_button.setFixedSize(*button_size)
        self.new_game_button.clicked.connect(self.start_game)
        left_layout.addWidget(self.new_game_button)

        self.save_game_button = QPushButton("Save game", self)
        self.save_game_button.setFixedSize(*button_size)
        self.save_game_button.setEnabled(False)  # Initially inactive
        self.save_game_button.clicked.connect(self.save_game)
        left_layout.addWidget(self.save_game_button)

        self.load_game_button = QPushButton("Load game", self)
        self.load_game_button.setFixedSize(*button_size)
        self.load_game_button.clicked.connect(self.load_game)
        left_layout.addWidget(self.load_game_button)

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.setFixedSize(*button_size)
        self.exit_button.clicked.connect(self.exit_app)
        left_layout.addWidget(self.exit_button)

        self.difficulty_slider = QSlider(Qt.Horizontal, self)  # Tworzenie slidera
        self.difficulty_slider.setMinimum(1)  # Minimalna wartość
        self.difficulty_slider.setMaximum(3)  # Maksymalna wartość
        self.difficulty_slider.setValue(1)  # Domyślna wartość
        self.difficulty_slider.setTickInterval(1)  # Odstęp między tickami
        self.difficulty_slider.setTickPosition(QSlider.TicksBelow)
        # # Ustawianie fiksowanego rozmiaru dla slidera
        # Ustawianie fiksowanego rozmiaru dla slidera
        self.difficulty_slider.setFixedWidth(200)
        self.difficulty_slider.setFixedHeight(20)

        # Dodawanie tytułu do slidera
        slider_title = QLabel("Difficulty Level", self)
        slider_title.setAlignment(Qt.AlignCenter)

        # Dodawanie znaczeń cyfrowych
        self.slider_value_label = QLabel(f"Current Value: {self.difficulty_slider.value()}", self)
        self.slider_value_label.setAlignment(Qt.AlignCenter)

        # Aktualizacja wartości cyfrowej przy zmianie slidera
        self.difficulty_slider.valueChanged.connect(self.update_difficulty)  # Połączenie sygnału
        self.difficulty_slider.valueChanged.connect(lambda value: self.slider_value_label.setText(f"Current Value: {value}"))

        self.instructions_label.setText(
            "Instructions:\n"
            "- Use arrow keys to move around the grid.\n"
            "- Press numbers 1-9 to fill in the cells.\n"
            "- Press 'R' to reset the game.\n"
            "- Press 'Delete' or 'Backspace' to clear a cell.\n"
            "- Press 'Enter' to demonstrate solving the puzzle.\n"
        )
        self.instructions_label.setStyleSheet("QLabel { font-size: 16px; }")
        left_layout.addWidget(self.instructions_label)

        left_layout.addWidget(slider_title)
        left_layout.addWidget(self.difficulty_slider)
        left_layout.addWidget(self.slider_value_label)
        left_layout.addWidget(self.error_label)
        left_layout.addStretch(1)  # Add a stretch to push everything to the top

        main_layout.addLayout(left_layout)
        right_layout.addWidget(self.game_display)

        right_layout.addWidget(self.game_display)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        self.game_display.setVisible(False)  # Initially hide the game display

        self.setFixedSize(self.window_width, self.window_height)
        self.setWindowTitle("Sudoku Game - Dariusz Szypka")
        self.show()

    def start_game(self):
        self.error_label.clear()  # Clear any previous error messages
        self.game_display.start_game()
        self.game_display.setVisible(True)  # Show the game display
        self.save_game_button.setEnabled(True)  # Enable the save game button
        self.game_display.setFocus()  # Give focus to the GameWidget after starting the game

    def save_game(self):
        self.error_label.clear()  # Clear any previous error messages

        # Generate the suggested filename
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        suggested_filename = f"{current_time}.json"

        # Prompt the user for the filename
        filename, ok = QInputDialog.getText(self, "Save Game", "Enter filename:", text=suggested_filename)

        if ok and filename:
            self.game_display.save_game(filename)
            self.last_saved_filename = filename
            self.save_config()

    def load_game(self):
        self.error_label.clear()  # Clear any previous error messages

        # Suggest the last saved file name
        suggested_filename = self.last_saved_filename if self.last_saved_filename else "default_filename.json"

        # Open a file dialog to select the file to load
        filename, _ = QFileDialog.getOpenFileName(self, "Load game", suggested_filename,
                                                  "JSON Files (*.json);;All Files (*)")
        if filename:
            # Load the selected file
            self.game_display.load_game(filename)
            self.save_game_button.setEnabled(True)  # Enable the save game button
            self.game_display.setVisible(True)  # Show the game display
            self.game_display.setFocus()  # Give focus to the GameWidget after starting the game

    def update_difficulty(self, value):
        self.game_display.difficulty = value

class GameWidget(QWidget):
    square = 3
    dimension = square * square
    side = LoginWindow.window_width - 400
    cell_length = side // dimension
    thick_line = 8
    thin_line = 2