import os
import magic

def is_valid_video_file(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    return file_type.startswith('video/')

def get_file_size(file_path):
    return os.path.getsize(file_path)

def estimate_conversion_time(file_size):
    # This is a very rough estimate and should be adjusted based on actual performance
    return file_size / (5 * 1024 * 1024)  # Assume 5 MB/s conversion rate