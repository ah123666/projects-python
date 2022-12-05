from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import util


class MainWin(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("文件工具")
        self.setFixedSize(800, 400)
        self.edit = QLineEdit()
        # self.edit.setText(os.getcwd())
        self.edit.setPlaceholderText("请选择文件夹")
        self.btn_choose = QPushButton("选择文件夹")
        self.btn1 = QPushButton("删除重复文件")
        self.btn1.setFixedWidth(120)
        self.btn2 = QPushButton("去除数字后缀")
        self.btn2.setFixedWidth(120)
        self.option1 = QCheckBox("递归遍历")
        self.option2 = QCheckBox("永久删除")
        self.option2.setToolTip("仅对删除操作有效")
        self.info = QTextEdit()
        self.info.setReadOnly(True)

        self.btn_choose.clicked.connect(self.choose_folder)
        self.btn1.clicked.connect(self.remove_duplicate)
        self.btn2.clicked.connect(self.remove_number)

        layout_h_1 = QHBoxLayout()
        layout_h_1.addWidget(self.edit)
        layout_h_1.addWidget(self.btn_choose)

        layout_h_2 = QHBoxLayout()
        layout_h_2.addWidget(self.btn1)
        layout_h_2.addWidget(self.btn2)
        layout_h_2.addWidget(self.option1)
        layout_h_2.addWidget(self.option2)
        layout_h_2.setAlignment(Qt.AlignLeft)

        layout_v = QVBoxLayout()
        layout_v.addLayout(layout_h_1)
        layout_v.addLayout(layout_h_2)
        layout_v.addWidget(self.info)

        self.setLayout(layout_v)

    def choose_folder(self):
        root_path = QFileDialog.getExistingDirectory(self, caption="选择文件夹", directory=os.getcwd())
        if os.path.exists(root_path):
            self.edit.setText(root_path)

    def remove_duplicate(self):
        root_path = self.edit.text()
        if os.path.exists(root_path):
            removed_list = util.remove_duplicate(root_path, recursively=self.option1.isChecked(), permanent=self.option2.isChecked())
            self.info.clear()
            if len(removed_list) > 0:
                self.info.append("成功删除以下文件:")
                for path in removed_list:
                    self.info.append(path)
            else:
                self.info.append("未删除任何文件")

    def remove_number(self):
        root_path = self.edit.text()
        if os.path.exists(root_path):
            modified_list = util.remove_number(root_path, recursively=self.option1.isChecked())
            self.info.clear()
            if len(modified_list) > 0:
                self.info.append("成功修改以下文件:")
                for path in modified_list:
                    self.info.append(path[0] + " ===> " + path[1])
            else:
                self.info.append("未修改任何文件")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWin()
    main_win.show()
    sys.exit(app.exec_())
