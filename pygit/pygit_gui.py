from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import datetime
from git import Repo, InvalidGitRepositoryError


class MainWin(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GIT仓库批量操作工具")
        # self.setFixedSize(800, 400)
        self.setMinimumSize(800, 400)
        self.edit = QLineEdit()
        self.cur_dir = os.path.abspath(os.path.dirname(__file__))
        self.edit.setText(self.cur_dir)
        self.edit.setPlaceholderText("请输入根目录路径")
        self.btn_choose = QPushButton("选择根目录")
        self.btn1 = QPushButton("批量推送")
        self.btn1.setFixedWidth(120)
        self.btn2 = QPushButton("批量拉取")
        self.btn2.setFixedWidth(120)
        self.btn3 = QPushButton("清空")
        self.btn3.setFixedWidth(120)
        self.info = QTextEdit()
        self.info.setReadOnly(True)

        self.btn_choose.clicked.connect(self.choose_folder)
        self.btn1.clicked.connect(self.push_all)
        self.btn2.clicked.connect(self.pull_all)
        self.btn3.clicked.connect(lambda: self.info.clear())

        layout_h_1 = QHBoxLayout()
        layout_h_1.addWidget(self.edit)
        layout_h_1.addWidget(self.btn_choose)

        layout_h_2 = QHBoxLayout()
        layout_h_2.addWidget(self.btn1)
        layout_h_2.addWidget(self.btn2)
        layout_h_2.addWidget(self.btn3)
        layout_h_2.setAlignment(Qt.AlignLeft)

        layout_v = QVBoxLayout()
        layout_v.addLayout(layout_h_1)
        layout_v.addLayout(layout_h_2)
        layout_v.addWidget(self.info)

        self.setLayout(layout_v)

    def choose_folder(self):
        root_dir = QFileDialog.getExistingDirectory(self, caption="选择文件夹", directory=self.cur_dir)
        if os.path.exists(root_dir):
            self.edit.setText(root_dir)

    def get_all_dir(self, root_dir):
        """
        返回当前目录下的所有文件夹
        """
        dir_list = []
        files = os.listdir(root_dir)
        for file in files:
            cur_path = os.path.join(root_dir, file)
            if os.path.isdir(cur_path):
                dir_list.append(cur_path)
        return dir_list

    def push_all(self):
        root_dir = self.edit.text()
        if os.path.exists(root_dir):
            self.info.clear()
            dir_list = self.get_all_dir(root_dir)
            self.info.append("[====push all====]")
            for dir in dir_list:
                QApplication.processEvents()
                self.info.append("=" * 80)
                self.info.append(f"current dir: {dir}")
                try:
                    repo = Repo(dir)
                except InvalidGitRepositoryError:
                    self.info.append("current dir is not a git repo!")
                else:
                    git = repo.git
                    git.add(".")
                    if repo.is_dirty():
                        git.commit("-m", datetime.datetime.now().strftime("commit at %Y-%m-%d %H:%M:%S"))
                        try:
                            remote = repo.remote(name="github")
                            self.info.append(f"remote_url: {remote.url}")
                            info = remote.push()[0]
                            self.info.append(f"flags: {info.flags}")
                            self.info.append(f"local_ref: {info.local_ref}")
                            self.info.append(f"remote_ref_string: {info.remote_ref_string}")
                            self.info.append(f"remote_ref: {info.remote_ref}")
                            self.info.append(f"old_commit: {info.old_commit}")
                            self.info.append(f"summary: {info.summary}")
                        except Exception as e:
                            self.info.append(str(e))
                    else:
                        self.info.append("nothing to commit")
            self.info.append("done!")
        else:
            self.info.append("目录 {} 不存在！".format(root_dir))

    def pull_all(self):
        root_dir = self.edit.text()
        if os.path.exists(root_dir):
            self.info.clear()
            dir_list = self.get_all_dir(root_dir)
            self.info.append("[====pull all====]")
            for dir in dir_list:
                self.info.append("=" * 80)
                self.info.append(f"current dir: {dir}")
                try:
                    repo = Repo(dir)
                except InvalidGitRepositoryError:
                    self.info.append("current dir is not a git repo!")
                else:
                    try:
                        remote = repo.remote(name="github")
                        self.info.append(f"remote_url: {remote.url}")
                        info = remote.pull()[0]
                        self.info.append(f"flags: {info.flags}")
                        self.info.append(f"ref: {info.ref}")
                        self.info.append(f"note: {info.note}")
                        self.info.append(f"old_commit: {info.old_commit}")
                        self.info.append(f"remote_ref_path: {info.remote_ref_path}")
                    except Exception as e:
                        self.info.append(str(e))
            self.info.append("done!")
        else:
            self.info.append("目录 {} 不存在！".format(root_dir))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWin()
    main_win.show()
    sys.exit(app.exec_())
