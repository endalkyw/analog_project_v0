import os
import shutil

current_dir = os.path.dirname(__file__)
log_file_path = "../log_files"
f = os.path.join(current_dir, log_file_path)

def clear_log_files():
    for root, dirs, files in os.walk(f, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            os.remove(file_path)  # Remove each file
        for name in dirs:
            dir_path = os.path.join(root, name)
            shutil.rmtree(dir_path)  # Remove each subdirectory



def write_log_file(file_name: str, text: str, app = 'w'):
    file = os.path.join(f, file_name)
    with open(file, app) as file:
        file.write(text+"\n")


if __name__ =='__main__':
    clear_log_files()
    write_log_file("trial.log", "Endalk is the best")

