from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import sys
from PIL import Image
import pytesseract

"""
need to install Tesseract OCR first (https://github.com/tesseract-ocr/tesseract#installing-tesseract)
and add it to PATH
or specify like bellow
"""


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


# class ShowImageWin(QMainWindow):
#     def __init__(self):
#         super(ShowImageWin, self).__init__()
#         self.initUI()

#     def initUI(self):
#         mainWidget = QWidget()
#         self.setCentralWidget(mainWidget)
#         self.imageLabel = QLabel()
#         self.imageLabel.setScaledContents(True)
#         self.imageLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
#         layout = QVBoxLayout()
#         layout.setAlignment(Qt.AlignCenter)
#         layout.addWidget(self.imageLabel)
#         mainWidget.setLayout(layout)

#     def showImage(self, path):
#         self.imageLabel.setPixmap(QPixmap(path))
#         self.show()


class ShowImageThread(QThread):
    def __init__(self):
        super().__init__()
        self.imagePath = None

    def setImagePath(self, path):
        self.imagePath = path

    def run(self):
        image = Image.open(self.imagePath)
        image.show()


class MainWin(QMainWindow):
    """docstring for MainWin"""

    def __init__(self):
        super(MainWin, self).__init__()
        self.initUI()
        # self.showImageWin = ShowImageWin()
        self.showImageThread = ShowImageThread()
        self.currentImageName = None

    def initUI(self):
        self.setWindowTitle('OCR识别图片')
        self.resize(800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        self.status = self.statusBar()
        self.status.showMessage('欢迎!', 3000)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('文件')
        addImageAct = QAction('添加图片', self)
        addImageAct.triggered.connect(self.openImage)
        fileMenu.addAction(addImageAct)

        self.imageList = QListWidget()
        self.imageList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.imageList.customContextMenuRequested[QPoint].connect(self.showRightClickMenu)
        self.imageList.itemDoubleClicked.connect(self.showImage)

        self.imageListRightClickMenu = QMenu()
        showImageAct = QAction('查看', self)
        showImageAct.triggered.connect(self.showImage)
        deleteImageAct = QAction('删除', self)
        deleteImageAct.triggered.connect(self.deleteImage)
        ocrImageAct = QAction('识别', self)
        ocrImageAct.triggered.connect(self.ocrImage)
        self.imageListRightClickMenu.addAction(addImageAct)
        self.imageListRightClickMenu.addAction(showImageAct)
        self.imageListRightClickMenu.addAction(deleteImageAct)
        self.imageListRightClickMenu.addAction(ocrImageAct)

        self.imageText = QTextEdit()
        # self.imageText.setReadOnly(True)

        self.hideButton = QPushButton('隐藏列表')
        # self.hideButton.setFixedWidth(100)
        self.hideButton.clicked.connect(self.hideList)

        self.saveButton = QPushButton('保存文字')
        self.saveButton.clicked.connect(self.saveText)

        self.ocrButton = QPushButton('识别图片')
        self.ocrButton.clicked.connect(self.ocrImage)

        layoutH = QHBoxLayout()
        layoutH.addWidget(self.imageList)
        layoutH.addWidget(self.imageText)
        layoutH.setStretch(0, 1)
        layoutH.setStretch(1, 1)

        layoutH_2 = QHBoxLayout()
        layoutH_2.addWidget(self.hideButton)
        layoutH_2.addWidget(QLabel())
        layoutH_2.addWidget(self.ocrButton)
        layoutH_2.addWidget(QLabel())
        layoutH_2.addWidget(self.saveButton)
        layoutH_2.setStretch(0, 1)
        layoutH_2.setStretch(1, 4)
        layoutH_2.setStretch(2, 1)
        layoutH_2.setStretch(3, 4)
        layoutH_2.setStretch(4, 1)

        layoutV = QVBoxLayout()
        layoutV.setAlignment(Qt.AlignCenter)
        layoutV.addLayout(layoutH)
        layoutV.addLayout(layoutH_2)
        main_widget.setLayout(layoutV)

    def openImage(self):
        file_path = QFileDialog.getOpenFileName(self, '选择图片', '.', '图片文件(*.jpg *.png)')[0]
        if not os.path.exists(file_path):
            return
        self.imageList.addItem(QListWidgetItem(file_path))
        self.status.showMessage('文件已加载!', 2000)

    def showImage(self):
        if self.imageList.count() == 0:
            return
        if self.showImageThread.isRunning():
            self.showImageThread.terminate()
        imagePath = self.imageList.item(self.imageList.currentRow()).text()
        self.showImageThread.setImagePath(imagePath)
        self.showImageThread.start()

    def deleteImage(self):
        if self.imageList.count() == 0:
            return
        reply = QMessageBox.question(self, '消息', '确定删除选中文件吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            imagePath = self.imageList.item(self.imageList.currentRow()).text()
            imageName = os.path.split(imagePath)[-1].split('.')[0]
            if imageName == self.currentImageName:
                self.imageText.clear()
                self.currentImageName = None
            self.imageList.takeItem(self.imageList.currentRow())
            self.status.showMessage('文件已删除!', 2000)

    def ocrImage(self):
        if self.imageList.count() == 0:
            return
        if self.imageList.currentRow() == -1:
            return
        self.imageText.clear()
        imagePath = self.imageList.item(self.imageList.currentRow()).text()
        # print(os.path.split(imagePath)[-1].split('.')[0])
        self.currentImageName = os.path.split(imagePath)[-1].split('.')[0]
        text = pytesseract.image_to_string(Image.open(imagePath), lang='chi_sim')
        text = text.strip()
        # print(text)
        self.imageText.append(text)
        self.status.showMessage('识别完成!', 2000)

    def hideList(self):
        if not self.imageList.isHidden():
            self.imageList.hide()
            self.hideButton.setText('显示列表')
        else:
            self.imageList.show()
            self.hideButton.setText('隐藏列表')

    def saveText(self):
        # print(self.imageText.toPlainText())
        if self.currentImageName is None:
            return
        path = 'test/result/'
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + self.currentImageName + '.txt', 'w') as writer:
            text = self.imageText.toPlainText()
            writer.write(text)
        self.status.showMessage('已保存!', 2000)

    def showRightClickMenu(self):
        self.imageListRightClickMenu.exec_(QCursor.pos())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWin()
    mainWin.show()
    sys.exit(app.exec_())
