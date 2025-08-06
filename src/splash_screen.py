from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QProgressBar, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont, QMovie
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

from .main_gui import CryptoGUI  # Import the main GUI

class SplashScreen(QWidget):
    """
    A splash screen displayed during application startup with a loading animation
    and progress bar.
    """
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #2E8B8B;")

        self.title = QLabel("DATA ENCRYPTION/DECRYPTION SYSTEM")
        self.title.setStyleSheet("color: white;")
        self.title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.design = QLabel("DESIGN BY EZEKIEL JOSEPH")
        self.design.setStyleSheet("color: white;")
        self.design.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.design.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image = QLabel()
        self.movie = QMovie("images/data_encryption.gif")
        self.image.setMovie(self.movie)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie.start()

        gif_layout = QVBoxLayout()
        gif_layout.addSpacing(40)
        gif_layout.addWidget(self.image)

        self.loading_label = QLabel("Loading... 0%")
        self.loading_label.setStyleSheet("color: white; font-size: 14px;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setFixedWidth(560)
        self.progress.setFixedHeight(10)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: #ffffff;
                text-align: center;
                color: black;
            }
            QProgressBar::chunk {
                background-color: #00BFFF;
                width: 20px;
            }
        """)
        self.progress.setTextVisible(False)

        progress_layout = QVBoxLayout()
        progress_layout.addStretch()
        progress_layout.addSpacing(50)
        progress_layout.addWidget(self.loading_label)
        progress_layout.addWidget(self.progress)
        progress_layout.addStretch()

        self.status_label = QLabel("Status: Initializing")
        self.status_label.setStyleSheet("color: white; font-size: 12px;")

        self.author_label = QLabel("Author: Joseph Ezekiel")
        self.author_label.setStyleSheet("color: white; font-size: 12px;")

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.author_label)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 10)
        main_layout.addWidget(self.title)
        main_layout.addWidget(self.design)
        main_layout.addLayout(gif_layout)
        main_layout.addLayout(progress_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        self.progress_value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)

    def update_progress(self):
        """Updates the progress bar and status label on the splash screen."""
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        self.loading_label.setText(f"Loading...  {self.progress_value}%")

        if self.progress_value < 25:
            self.status_label.setText("Status: Initializing")
        elif self.progress_value < 50:
            self.status_label.setText("Status: Starting")
        elif self.progress_value < 75:
            self.status_label.setText("Status: Preparing")
        elif self.progress_value < 90:
            self.status_label.setText("Status: Finishing")
        else:
            self.status_label.setText("Status: Done")

        if self.progress_value >= 100:
            self.timer.stop()
            self.accept_splash()

    def accept_splash(self):
        """Closes the splash screen and opens the main application window."""
        self.close()
        self.main = CryptoGUI()
        self.main.show()