
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
        print("current dir: {}".format(dir))
        try:
            repo = Repo(dir)
        except InvalidGitRepositoryError:
            print("current dir is not a git repo!")
        else:
            remote = repo.remote()
            info = remote.pull()
            print(info)


def pushAll(rootDir):
    """
    将当前目录下的所有git仓库进行添加所有文件、提交、推送远程仓库
    """
    dirList = getAllDir(rootDir)
    for dir in dirList:
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
                remote = repo.remote()
                info = remote.push()
                print(info)
            else:
                print("nothing to commit")



if __name__ == "__main__":
    rootDir = os.path.dirname(__file__)
    print("root dir: {}".format(rootDir))
    pushAll(rootDir)