import os
import sys
import subprocess
import playsound # Make sure to install this library: pip install playsound

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox,
    QProgressBar, QCheckBox, QTabWidget, QFrame, QToolButton
)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject

from .gui_widgets import DragDropWidget, PasswordInput
from .crypto_worker import CryptoWorker

class CryptoGUI(QWidget):
    """
    Main GUI class for the Secure Folder Encryptor/Decryptor application.
    Manages the overall layout, tabs, and interactions with crypto operations.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Folder Encryptor/Decryptor")
        self.setMinimumSize(600, 600)
        self.setWindowIcon(QIcon("images/encry.png"))
        self.dark_mode = False

        self.tabs = QTabWidget()
        self.encrypt_tab = QWidget()
        self.decrypt_tab = QWidget()
        
        self.tabs.addTab(self.encrypt_tab, "Encrypt")
        self.tabs.addTab(self.decrypt_tab, "Decrypt")

        self.init_encrypt_ui()
        self.init_decrypt_ui()

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Light", "Dark"])
        self.theme_dropdown.setMaximumWidth(100)
        self.theme_dropdown.currentTextChanged.connect(self.apply_theme)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        header_layout.addWidget(self.theme_dropdown)

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        
    def play_sound(self, filename: str):
        """Plays a sound file located in the 'sounds' directory."""
        sound_path = os.path.join(os.path.dirname(__file__), "sounds", filename)
        if os.path.exists(sound_path):
            try:
                # The 'playsound' library can be buggy on some systems, 
                # so it's good practice to wrap it in a try-except block.
                playsound.playsound(sound_path, False) # False prevents blocking
            except playsound.PlaysoundException as e:
                print(f"Error playing sound {filename}: {e}")
        else:
            print(f"Sound file not found: {sound_path}")

    def apply_theme(self, mode: str):
        """Applies the selected theme (Light or Dark) to the GUI."""
        if mode == "Dark":
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QPushButton { background-color: #444; color: #fff; border: none; border-radius: 6px; padding: 8px 20px; font-weight: bold; }
                QPushButton:hover { background-color: #666; }
                QProgressBar { border: 1px solid #444; border-radius: 5px; text-align: center; }
                QProgressBar::chunk { background-color: #05B8CC; width: 20px; }
                QLineEdit, QComboBox {
                    background-color: #3b3b3b;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 4px;
                }
                /* Tab Widget Styling - Dark Mode */
                QTabWidget::pane { /* The tab widget frame */
                    border-top: 2px solid #555;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background: #444;
                    color: #fff;
                    border: 1px solid #555;
                    border-bottom-color: #444; /* Same as pane color to make it look seamless */
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 8ex;
                    padding: 8px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #2b2b2b; /* Matches pane background */
                    border-bottom-color: #2b2b2b; /* Matches pane background */
                    color: #05B8CC; /* Highlight color for selected tab */
                }
                QTabBar::tab:hover {
                    background: #666;
                }
                QTabBar::tab:selected:hover {
                    background: #2b2b2b; /* Keep selected tab background same on hover */
                }
            """)
            self.dark_mode = True
            self.drag_widget.setStyleSheet("""
                QFrame {
                    border: 2px dashed #aaa;
                    border-radius: 10px;
                    background-color: #3b3b3b;
                }
                QLabel { color: #ccc; }
                QPushButton { background-color: #0078D4; }
                QPushButton:hover { background-color: #005ea6; }
            """)
            self.file_drop_widget.setStyleSheet("""
                QFrame {
                    border: 2px dashed #aaa;
                    border-radius: 10px;
                    background-color: #3b3b3b;
                }
                QLabel { color: #ccc; }
                QPushButton { background-color: #0078D4; }
                QPushButton:hover { background-color: #005ea6; }
            """)
        else:
            self.setStyleSheet("""
                /* Tab Widget Styling - Light Mode */
                QTabWidget::pane { /* The tab widget frame */
                    border-top: 2px solid #ccc;
                    background-color: #f0f0f0;
                }
                QTabBar::tab {
                    background: #e0e0e0;
                    color: #333;
                    border: 1px solid #ccc;
                    border-bottom-color: #e0e0e0; /* Same as pane color to make it look seamless */
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 8ex;
                    padding: 8px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #f0f0f0; /* Matches pane background */
                    border-bottom-color: #f0f0f0; /* Matches pane background */
                    color: #0078D4; /* Highlight color for selected tab */
                }
                QTabBar::tab:hover {
                    background: #d0d0d0;
                }
                QTabBar::tab:selected:hover {
                    background: #f0f0f0; /* Keep selected tab background same on hover */
                }
            """)
            self.dark_mode = False
            self.drag_widget.setStyleSheet("""
                QFrame {
                    border: 2px dashed #aaa;
                    border-radius: 10px;
                    background-color: #f8f8f8;
                }
                QLabel { color: #666; }
                QPushButton { background-color: #0078D4; }
                QPushButton:hover { background-color: #005ea6; }
            """)
            self.file_drop_widget.setStyleSheet("""
                QFrame {
                    border: 2px dashed #aaa;
                    border-radius: 10px;
                    background-color: #f8f8f8;
                }
                QLabel { color: #666; }
                QPushButton { background-color: #0078D4; }
                QPushButton:hover { background-color: #005ea6; }
            """)

    def init_encrypt_ui(self):
        """Initializes the UI elements for the encryption tab."""
        layout = QVBoxLayout()
        self.input_path = ""
        self.drag_widget = DragDropWidget(callback=self.set_input_path, is_file_mode=False)
        layout.addWidget(self.drag_widget)

        self.password_enc_input = PasswordInput("Password")
        layout.addLayout(self.password_enc_input)
        self.confirm_password_enc_input = PasswordInput("Confirm Password")
        layout.addLayout(self.confirm_password_enc_input)

        self.delete_source = QCheckBox("Delete source after encryption")
        self.export_hash = QCheckBox("Export password salt file (.salt)")
        layout.addWidget(self.delete_source)
        layout.addWidget(self.export_hash)

        self.progress_enc = QProgressBar()
        self.progress_enc.setStyleSheet("""
            QProgressBar { border: 1px solid #aaa; border-radius: 5px; text-align: center; height: 20px; }
            QProgressBar::chunk { background-color: #0078D4; }
        """)
        self.btn_encrypt = QPushButton("Encrypt")
        self.btn_encrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_encrypt.setStyleSheet("""
            QPushButton {
                width:30%;
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005ea6;
            }
        """)
        self.btn_encrypt.clicked.connect(self.encrypt)

        layout.addWidget(self.progress_enc)
        layout.addWidget(self.btn_encrypt)
        self.encrypt_tab.setLayout(layout)

    def init_decrypt_ui(self):
        """Initializes the UI elements for the decryption tab."""
        layout = QVBoxLayout()
        self.enc_file_path = ""
        self.file_drop_widget = DragDropWidget(callback=self.set_enc_path, is_file_mode=True)
        layout.addWidget(self.file_drop_widget)

        self.password_dec_input = PasswordInput("Password")
        layout.addLayout(self.password_dec_input)

        self.import_hash = QCheckBox("Import password salt file (.salt)")
        layout.addWidget(self.import_hash)
        
        self.progress_dec = QProgressBar()
        self.progress_dec.setStyleSheet("""
            QProgressBar { border: 1px solid #aaa; border-radius: 5px; text-align: center; height: 20px; }
            QProgressBar::chunk { background-color: #0078D4; }
        """)
        self.btn_decrypt = QPushButton("Decrypt")
        self.btn_decrypt.setStyleSheet("""
            QPushButton {
                width:30%;
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005ea6;
            }
        """)
        self.btn_decrypt.clicked.connect(self.decrypt)

        layout.addWidget(self.progress_dec)
        layout.addWidget(self.btn_decrypt)
        self.decrypt_tab.setLayout(layout)

    def set_input_path(self, path: str):
        """Sets the input path for encryption."""
        self.input_path = path

    def set_enc_path(self, path: str):
        """Sets the input path for decryption."""
        self.enc_file_path = path

    def encrypt(self):
        """Initiates the encryption process."""
        if not self.input_path or not os.path.isdir(self.input_path):
            QMessageBox.warning(self, "Error", "Please select a valid folder.")
            return

        pwd = self.password_enc_input.text()
        confirm_pwd = self.confirm_password_enc_input.text()

        if not pwd:
            QMessageBox.critical(self, "Error", "Password cannot be empty.")
            return

        if pwd != confirm_pwd:
            QMessageBox.critical(self, "Error", "Passwords do not match.")
            return

        folder_name = os.path.basename(self.input_path)
        out_file = os.path.join(os.path.dirname(self.input_path), f"{folder_name}.enc")

        self.progress_enc.setValue(0)
        self.btn_encrypt.setEnabled(False)
        self.progress_enc.setFormat("Encrypting... %p%")
        self.progress_enc.setTextVisible(True)
        
        # Play the initializing sound
        self.play_sound("initializing.mp3")

        self.thread = QThread()
        self.worker = CryptoWorker(
            mode="encrypt",
            path=self.input_path,
            password=pwd,
            output_path=out_file,
            delete_source=self.delete_source.isChecked(),
            export_hashes=self.export_hash.isChecked()
        )
        self.worker.moveToThread(self.thread)
        self.worker.progress_updated.connect(self.progress_enc.setValue)
        self.worker.encryption_finished.connect(self.on_encryption_finished)
        self.worker.error_occurred.connect(self.on_error_occurred)
        
        # Connect a new signal from the worker to play the 'encrypting' sound
        self.worker.encryption_started.connect(lambda: self.play_sound("encrypting.mp3"))

        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_encryption_finished(self, message: str, out_path: str):
        """Handles actions upon successful encryption completion."""
        # Play the finishing sound
        self.play_sound("finishing.mp3")
        
        QMessageBox.information(self, "Success", message)
        self.thread.quit()
        self.thread.wait()
        self.progress_enc.setValue(0)
        self.progress_enc.setFormat("")
        self.progress_enc.setTextVisible(False)
        self.btn_encrypt.setEnabled(True)
        
        self.password_enc_input.clear()
        self.confirm_password_enc_input.clear()
        self.delete_source.setChecked(False)
        self.export_hash.setChecked(False)
        self.drag_widget.reset()
        self.input_path = ""
        
        self.open_explorer_and_highlight(out_path)

    def decrypt(self):
        """Initiates the decryption process."""
        in_path = self.enc_file_path
        if not in_path or not os.path.isfile(in_path):
            QMessageBox.warning(self, "Error", "Please select a valid encrypted file.")
            return

        pwd = self.password_dec_input.text()
        if not pwd:
            QMessageBox.critical(self, "Error", "Password cannot be empty.")
            return

        self.progress_dec.setValue(0)
        self.btn_decrypt.setEnabled(False)
        self.progress_dec.setFormat("Decrypting... %p%")
        self.progress_dec.setTextVisible(True)

        self.thread = QThread()
        self.worker = CryptoWorker(
            mode="decrypt",
            path=in_path,
            password=pwd,
            import_hashes=self.import_hash.isChecked(),
        )
        self.worker.moveToThread(self.thread)
        self.worker.progress_updated.connect(self.progress_dec.setValue)
        self.worker.decryption_finished.connect(self.on_decryption_finished)
        self.worker.error_occurred.connect(self.on_error_occurred)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_decryption_finished(self, message: str, out_path: str):
        """Handles actions upon successful decryption completion."""
        QMessageBox.information(self, "Success", message)
        self.thread.quit()
        self.thread.wait()
        self.progress_dec.setValue(0)
        self.progress_dec.setFormat("")
        self.progress_dec.setTextVisible(False)
        self.btn_decrypt.setEnabled(True)
        
        self.password_dec_input.clear()
        self.import_hash.setChecked(False)
        
        self.file_drop_widget.reset()
        self.enc_file_path = ""

        self.open_explorer_and_highlight(out_path)

    def on_error_occurred(self, error_message: str):
        """Handles and displays error messages from the worker thread."""
        QMessageBox.critical(self, "Error", error_message)
        self.progress_enc.setValue(0)
        self.progress_dec.setValue(0)
        self.progress_enc.setFormat("")
        self.progress_dec.setFormat("")
        self.progress_enc.setTextVisible(False)
        self.progress_dec.setTextVisible(False)
        self.btn_encrypt.setEnabled(True)
        self.btn_decrypt.setEnabled(True)
        self.thread.quit()
        self.thread.wait()

    def open_explorer_and_highlight(self, file_path: str):
        """Opens the file explorer and highlights the specified file or folder."""
        if os.name == 'nt':  # For Windows
            subprocess.Popen(f'explorer /select,"{os.path.normpath(file_path)}"')
        elif os.name == 'posix': # For macOS and Linux
            if sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', file_path])
            else:
                subprocess.Popen(['xdg-open', os.path.dirname(file_path)])


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set a global font for the application
    font = QFont()
    # Prioritize 'Segoe UI' for Windows, 'Roboto' if available, otherwise 'Sans Serif'
    if sys.platform.startswith('win'):
        font.setFamily("Segoe UI")
    elif sys.platform == 'darwin':
        font.setFamily("SF Pro Text") # macOS default system font
    else: # Linux and other Unix-like systems
        font.setFamily("Roboto") # Popular choice, but might need to be installed
        # Fallback to a generic sans-serif if Roboto isn't found
        if not QFontDatabase.hasFont("Roboto"):
            font.setFamily("Sans Serif")

    font.setPointSize(10) # Adjust font size as needed
    app.setFont(font)

    window = CryptoGUI()
    window.show()
    sys.exit(app.exec())