import os


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_file(path, content):
    with open(path, "w") as file:
        file.write(content)
