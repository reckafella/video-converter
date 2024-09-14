import os
import subprocess
import shutil

def check_ffmpeg():
    return shutil.which("ffmpeg") is not None

def convert_video_to_audio(input_file, output_file, output_format, progress_callback):
    if not check_ffmpeg():
        raise Exception("FFmpeg is not installed. Please install it using 'sudo apt-get install ffmpeg'.")

    total_duration = get_video_duration(input_file)
    
    command = [
        "ffmpeg",
        "-i", input_file,
        "-vn",
        "-acodec", get_audio_codec(output_format),
        "-y",  # Overwrite output file if it exists
        output_file
    ]

    process = subprocess.Popen(command, stderr=subprocess.PIPE, universal_newlines=True)

    for line in process.stderr:
        if "time=" in line:
            time = line.split("time=")[1].split()[0]
            current_duration = time_to_seconds(time)
            progress = int((current_duration / total_duration) * 100)
            progress_callback(progress)

    process.wait()

    if process.returncode != 0:
        raise Exception("Conversion failed. Check if the input file is valid.")

def get_video_duration(input_file):
    command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return float(result.stdout)

def time_to_seconds(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def get_audio_codec(output_format):
    codec_map = {
        "mp3": "libmp3lame",
        "wav": "pcm_s16le",
        "ogg": "libvorbis",
        "flac": "flac",
        "aac": "aac"
    }
    return codec_map.get(output_format, "copy")