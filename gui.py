import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QFileDialog, QProgressBar, QMessageBox, QSlider,
                             QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from conversion import convert_video_to_audio, cut_video, get_video_duration

class ConversionThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, input_file, output_file, output_format, start_time, end_time):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.output_format = output_format
        self.start_time = start_time
        self.end_time = end_time

    def run(self):
        try:
            if self.start_time is not None and self.end_time is not None:
                # Cut the video first
                temp_cut_file = f"temp_cut_{os.path.basename(self.input_file)}"
                cut_video(self.input_file, temp_cut_file, self.start_time, self.end_time)
                
                # Convert the cut video to audio
                convert_video_to_audio(temp_cut_file, self.output_file, self.output_format, self.progress.emit)
                
                # Remove the temporary cut video file
                os.remove(temp_cut_file)
            else:
                # Convert the entire video to audio
                convert_video_to_audio(self.input_file, self.output_file, self.output_format, self.progress.emit)
            
            self.finished.emit(True, "Conversion completed successfully!")
        except Exception as e:
            self.finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Editor and Converter")
        self.setGeometry(100, 100, 800, 600)

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

        # Video player
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Video controls
        controls_layout = QHBoxLayout()
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.clicked.connect(self.play_pause_video)
        controls_layout.addWidget(self.play_pause_button)

        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.sliderMoved.connect(self.set_video_position)
        controls_layout.addWidget(self.video_slider)

        layout.addLayout(controls_layout)

        # Cut controls
        cut_layout = QHBoxLayout()
        cut_layout.addWidget(QLabel("Start Time (s):"))
        self.start_time_spin = QSpinBox()
        self.start_time_spin.setRange(0, 9999)
        cut_layout.addWidget(self.start_time_spin)

        cut_layout.addWidget(QLabel("End Time (s):"))
        self.end_time_spin = QSpinBox()
        self.end_time_spin.setRange(0, 9999)
        cut_layout.addWidget(self.end_time_spin)

        layout.addLayout(cut_layout)

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

        # Connect media player signals
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)

    def browse_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mkv *.flv *.mov);;All Files (*)")
        if file_name:
            self.input_file_edit.setText(file_name)
            self.update_output_filename()
            self.load_video(file_name)

    def load_video(self, filename):
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
        self.play_pause_button.setText("Play")
        self.video_duration = get_video_duration(filename)
        self.end_time_spin.setRange(0, int(self.video_duration))
        self.end_time_spin.setValue(int(self.video_duration))

    def play_pause_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_button.setText("Pause")

    def set_video_position(self, position):
        self.media_player.setPosition(position)

    def update_duration(self, duration):
        self.video_slider.setRange(0, duration)

    def update_position(self, position):
        self.video_slider.setValue(position)

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

    def get_unique_filename(self, file_path):
        directory, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(directory, f"{name} ({counter}){ext}")
            counter += 1
        return file_path

    def start_conversion(self):
        input_file = self.input_file_edit.text()
        output_file = self.output_file_edit.text()
        output_format = self.format_combo.currentText()
        start_time = self.start_time_spin.value()
        end_time = self.end_time_spin.value()

        if not input_file or not output_file:
            QMessageBox.warning(self, "Error", "Please select input and output files.")
            return

        if os.path.exists(output_file):
            reply = QMessageBox.question(self, "File Exists", 
                                         "The output file already exists. Do you want to overwrite it?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                output_file = self.get_unique_filename(output_file)
                self.output_file_edit.setText(output_file)

        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Converting...")

        self.conversion_thread = ConversionThread(input_file, output_file, output_format, start_time, end_time)
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

    def closeEvent(self, event):
        self.media_player.stop()
        event.accept()