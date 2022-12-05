
from git import Repo
import os



repo = Repo.init(r"C:\Repositories\test-repo")
git = repo.git
git.add(".")
remote = repo.remote() #通过repo对象获取remote对象
if repo.is_dirty():
    print("dirty")
    git.commit("-m", "add some file")
    remote.push()
else:
    print("not dirty")
remote.pull()

print(git.log())