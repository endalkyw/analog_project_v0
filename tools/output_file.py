import os
import shutil

current_dir = os.path.dirname(__file__)
log_file_path = "../outputs"
f = os.path.join(current_dir, log_file_path)

def clear_output_files():
    for root, dirs, files in os.walk(f, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            os.remove(file_path)  # Remove each file
        for name in dirs:
            dir_path = os.path.join(root, name)
            shutil.rmtree(dir_path)  # Remove each subdirectory


if __name__ =='__main__':
    clear_output_files()