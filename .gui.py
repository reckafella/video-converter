import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QFileDialog, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from conversion import convert_video_to_audio

class ConversionThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, input_file, output_file, output_format):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.output_format = output_format

    def run(self):
        try:
            convert_video_to_audio(self.input_file, self.output_file, self.output_format, self.progress.emit)
            self.finished.emit(True, "Conversion completed successfully!")
        except Exception as e:
            self.finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video to Audio Converter")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Input file selection
        input_layout = QHBoxLayout()
        self.input_file_edit = QLineEdit()
        input_layout.addWidget(QLabel("Input File:"))
        input_layout.addWidget(self.input_file_edit)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_input_file)
        input_layout.addWidget(browse_button)
        layout.addLayout(input_layout)

        # Output format selection
        format_layout = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "wav", "ogg", "flac", "aac"])
        format_layout.addWidget(QLabel("Output Format:"))
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Output file selection
        output_layout = QHBoxLayout()
        self.output_file_edit = QLineEdit()
        output_layout.addWidget(QLabel("Output File:"))
        output_layout.addWidget(self.output_file_edit)
        output_browse_button = QPushButton("Browse")
        output_browse_button.clicked.connect(self.browse_output_file)
        output_layout.addWidget(output_browse_button)
        layout.addLayout(output_layout)

        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.format_combo.currentTextChanged.connect(self.update_output_filename)

    def browse_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mkv *.flv *.mov);;All Files (*)")
        if file_name:
            self.input_file_edit.setText(file_name)
            self.update_output_filename()

    def browse_output_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "", f"Audio Files (*.{self.format_combo.currentText()});;All Files (*)")
        if file_name:
            self.output_file_edit.setText(file_name)

    def update_output_filename(self):
        input_file = self.input_file_edit.text()
        if input_file:
            base_name = os.path.splitext(input_file)[0]
            new_extension = self.format_combo.currentText()
            self.output_file_edit.setText(f"{base_name}.{new_extension}")

    def start_conversion(self):
        input_file = self.input_file_edit.text()
        output_file = self.output_file_edit.text()
        output_format = self.format_combo.currentText()

        if not input_file or not output_file:
            QMessageBox.warning(self, "Error", "Please select input and output files.")
            return

        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Converting...")

        self.conversion_thread = ConversionThread(input_file, output_file, output_format)
        self.conversion_thread.progress.connect(self.update_progress)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def conversion_finished(self, success, message):
        self.convert_button.setEnabled(True)
        self.status_label.setText(message)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)