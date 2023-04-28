import argparse
import datetime
from git import Repo, InvalidGitRepositoryError
import os


parser = argparse.ArgumentParser(description='pygit args')
parser.add_argument('--push', action='store_true', default=False, help='git push')
parser.add_argument('--pull', action='store_true', default=False, help='git pull')
parser.add_argument('--root_dir', type=str, default=None, help='root dir')
args = parser.parse_args()


def getAllDir(rootDir):
    """
    返回当前目录下的所有文件夹
    """
    dirList = []
    allFile = os.listdir(rootDir)
    for file in allFile:
        curPath = os.path.join(rootDir, file)
        if os.path.isdir(curPath):
            dirList.append(curPath)
    return dirList


def pullAll(rootDir):
    """
    将当前目录下的所有git仓库拉取远程仓库
    """
    dirList = getAllDir(rootDir)
    for idx, dir in enumerate(dirList):
        title = " [" + str(idx + 1) + "] " + dir + " "
        print("=" * 25 + title + "=" * max(0, 75 - len(title)))
        try:
            repo = Repo(dir)
            remote = repo.remote(name="github")
            print("remote_url: ", remote.url)
            print("[pull]")
            info = remote.pull()[0]
            print("flags: ", info.flags)
            print("ref: ", info.ref)
            print("note: ", info.note)
            print("old_commit: ", info.old_commit)
            print("remote_ref_path: ", info.remote_ref_path)
        except InvalidGitRepositoryError:
            print("[!error]: current dir is not a git repo!")
        except Exception as e:
            print("[!error]: {}".format(e))
        print("\n")


def pushAll(rootDir):
    """
    将当前目录下的所有git仓库进行添加所有文件、提交、推送远程仓库
    """
    dirList = getAllDir(rootDir)
    for idx, dir in enumerate(dirList):
        title = " [" + str(idx + 1) + "] " + dir + " "
        print("=" * 25 + title + "=" * max(0, 75 - len(title)))
        try:
            repo = Repo(dir)
            git = repo.git
            print("[add]")
            git.add(".")
            if repo.is_dirty():
                msg = datetime.datetime.now().strftime("commit at %Y-%m-%d %H:%M:%S")
                print("[commit]: {}".format(msg))
                git.commit("-m", msg)
            else:
                print("[nothing to commit]")
            remote = repo.remote(name="github")
            print("[push]")
            print("remote_url: ", remote.url)
            info = remote.push()[0]
            print("flags: ", info.flags)
            print("local_ref: ", info.local_ref)
            print("remote_ref_string: ", info.remote_ref_string)
            print("remote_ref: ", info.remote_ref)
            print("old_commit: ", info.old_commit)
            print("summary: ", info.summary)
        except InvalidGitRepositoryError:
            print("[!error]: current dir is not a git repo!")
        except Exception as e:
            print("[!error]: {}".format(e))
        print("\n")


if __name__ == "__main__":
    if args.root_dir is None:
        rootDir = os.path.dirname(os.path.realpath(__file__))
    else:
        rootDir = args.root_dir
    print("root dir: {}".format(rootDir))

    if args.push:
        pushAll(rootDir)
    elif args.pull:
        pullAll(rootDir)
    else:
        print("nothing to do, please use '--push' or '--pull'.")
