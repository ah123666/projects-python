import os
import filecmp
import re
from win32com.shell import shell, shellcon


def del_to_recyclebin(filename):
    """
    删除文件到回收站
    """
    res = shell.SHFileOperation((0, shellcon.FO_DELETE, filename, None, shellcon.FOF_SILENT | shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION, None, None))  # 删除文件到回收站
    if not res[1]:
        os.system('del ' + filename)


def remove_duplicate(root_path, recursively=False, permanent=False):
    """
    删除当前目录下的重复文件, 返回被删除文件的列表
    """
    removed_list = []
    __remove_duplicate(root_path, recursively, permanent, removed_list)
    return removed_list


def __remove_duplicate(root_path, recursively, permanent, removed_list):
    """
    删除当前目录下的重复文件
    """
    file_path_list = []
    folder_path_list = []

    for file_name in os.listdir(root_path):
        path = root_path + "/" + file_name
        if os.path.isfile(path):
            file_path_list.append(path)
        if os.path.isdir(path):
            folder_path_list.append(path)
    __remove_duplicate_in_list(file_path_list, permanent, removed_list)
    if recursively:
        if len(folder_path_list) == 0:
            return
        for folder_path in folder_path_list:
            __remove_duplicate(folder_path, recursively, permanent, removed_list)


def __remove_duplicate_in_list(file_path_list, permanent, removed_list):
    """
    删除文件列表中的重复文件
    """
    if len(file_path_list) < 2:
        return
    for i in range(0, len(file_path_list) - 1):
        for j in range(i + 1, len(file_path_list)):
            file1 = file_path_list[i]
            file2 = file_path_list[j]
            if file1 != file2 and os.path.exists(file1) and os.path.exists(file2):
                if filecmp.cmp(file1, file2):
                    if permanent:
                        os.remove(file1)
                    else:
                        del_to_recyclebin(file1)
                    removed_list.append(file1)


def remove_number(root_path, recursively=False):
    """
    去除文件名后面的数字
    如 test(1).txt ==> test.txt
    """
    modified_list = []
    __remove_number(root_path, recursively, modified_list)
    return modified_list


def __remove_number(root_path, recursively, modified_list):
    file_path_list = []
    folder_path_list = []

    for file_name in os.listdir(root_path):
        path = root_path + "/" + file_name
        if os.path.isfile(path):
            file_path_list.append(path)
        if os.path.isdir(path):
            folder_path_list.append(path)
    __remove_number_in_list(file_path_list, modified_list)
    if recursively:
        if len(folder_path_list) == 0:
            return
        for folder_path in folder_path_list:
            __remove_number(folder_path, recursively, modified_list)


def __remove_number_in_list(file_path_list, modified_list):
    pattern = r"[(（{\[【]{1,}[-]{0,1}[0-9]+[)）}\]】]{1,}$"
    for file_path in file_path_list:
        file_name, ext = os.path.splitext(file_path)
        if re.search(pattern, file_name) is not None:
            new_file_name = re.sub(pattern, "", file_name)
            new_file_path = new_file_name + ext
            if not os.path.exists(new_file_path):
                os.rename(file_path, new_file_path)
                modified_list.append([file_path, new_file_path])
