
import datetime
from git import Repo, InvalidGitRepositoryError
import os


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
    for dir in dirList:
        print("=" * 100)
        print("current dir: {}".format(dir))
        try:
            repo = Repo(dir)
        except InvalidGitRepositoryError:
            print("current dir is not a git repo!")
        else:
            try:
                remote = repo.remote(name="github")
                print("remote_url: ", remote.url)
                info = remote.pull()[0]
                print("flags: ", info.flags)
                print("ref: ", info.ref)
                print("note: ", info.note)
                print("old_commit: ", info.old_commit)
                print("remote_ref_path: ", info.remote_ref_path)
            except:
                print("no remote named github")


def pushAll(rootDir):
    """
    将当前目录下的所有git仓库进行添加所有文件、提交、推送远程仓库
    """
    dirList = getAllDir(rootDir)
    for dir in dirList:
        print("=" * 100)
        print("current dir: {}".format(dir))
        try:
            repo = Repo(dir)
        except InvalidGitRepositoryError:
            print("current dir is not a git repo!")
        else:
            git = repo.git
            git.add(".")
            if repo.is_dirty():
                git.commit("-m", datetime.datetime.now().strftime("commit at %Y-%m-%d %H:%M:%S"))
                try:
                    remote = repo.remote(name="github")
                    print("remote_url: ", remote.url)
                    info = remote.push()[0]
                    print("flags: ", info.flags)
                    print("local_ref: ", info.local_ref)
                    print("remote_ref_string: ", info.remote_ref_string)
                    print("remote_ref: ", info.remote_ref)
                    print("old_commit: ", info.old_commit)
                    print("summary: ", info.summary)
                except:
                    print("no remote named github")
            else:
                print("nothing to commit")


if __name__ == "__main__":
    # rootDir = os.path.dirname(__file__)
    rootDir = r"D:\Repositories"
    print("root dir: {}".format(rootDir))
    pushAll(rootDir)
    # pullAll(rootDir)
