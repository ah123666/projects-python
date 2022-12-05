
import os
import re


def add_number(root_dir):

    file_path_list = []

    for name in os.listdir(root_dir):
        path = os.path.join(root_dir, name)
        if os.path.isdir(path):
            for name2 in os.listdir(path):
                path2 = os.path.join(path, name2)
                if os.path.isfile(path2):
                    file_path_list.append(path2)
    idx = 1
    for file_path in file_path_list:
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        if idx < 10:
            before = "00" + str(idx)
        elif 10 <= idx < 100:
            before = "0" + str(idx)
        else:
            before = "" + str(idx)
        new_file_name = before + file_name
        new_file_path = os.path.join(dir_name, new_file_name)
        os.rename(file_path, new_file_path)
        idx += 1

def remove_number(root_dir):

    file_path_list = []

    for name in os.listdir(root_dir):
        path = os.path.join(root_dir, name)
        if os.path.isdir(path):
            for name2 in os.listdir(path):
                path2 = os.path.join(path, name2)
                if os.path.isfile(path2):
                    file_path_list.append(path2)

    pattern = r"^[0-9]{1,}"
    for file_path in file_path_list:
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        if re.search(pattern, file_name) is not None:
            new_file_name = re.sub(pattern, "", file_name)
            new_file_path = os.path.join(dir_name, new_file_name)
            os.rename(file_path, new_file_path)


if __name__ == '__main__':
    root_dir = "C:\\庐剧mp3"
    # remove_number(root_dir)
    add_number(root_dir)
