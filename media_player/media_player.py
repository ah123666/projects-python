"""
music and video player
author: xyym
e-mail: 1920376753@qq.com
date: 2020.12.22
"""
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QUrl, QDirIterator
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPalette, QColor, QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QMenu, QSizePolicy, QLabel, QPushButton, \
    QComboBox, QDoubleSpinBox, QSlider, QListWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog

import sys
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from os import mkdir
from os.path import exists
from mutagen import File
from mutagen.mp4 import MP4

"""
need to install LAVFilters (https://github.com/Nevcairiel/LAVFilters/releases)
"""


# 重写QVideoWidget类的鼠标双击和单击事件
class MyVideoWidget(QVideoWidget):

    doubleClickedItem = pyqtSignal(str)  # 创建双击信号
    singleClickedItem = pyqtSignal(str)
    leftArrowKeyPressedItem = pyqtSignal(str)
    rightArrowKeyPressedItem = pyqtSignal(str)
    spaceKeyPressedItem = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def mouseDoubleClickEvent(self, QMouseEvent):  # 双击事件
        self.doubleClickedItem.emit("double clicked")

    def mousePressEvent(self, QMouseEvent):  # 单击事件
        self.singleClickedItem.emit("single clicked")

    def keyPressEvent(self, event):
        if self.isFullScreen():
            if event.key() == Qt.Key_Escape:
                self.setFullScreen(False)
            elif event.key() == Qt.Key_Left:
                self.leftArrowKeyPressedItem.emit('left arrow pressed')
            elif event.key() == Qt.Key_Right:
                self.rightArrowKeyPressedItem.emit('right arrow pressed')
            elif event.key() == Qt.Key_Space:
                self.spaceKeyPressedItem.emit('space pressed')


# 程序主窗口
class MyMainWin(QMainWindow):

    def __init__(self):
        super().__init__()
        if not exists('./history'):
            mkdir('./history')
        self.music_list_file = './history/music_list.txt'
        self.video_list_file = './history/video_list.txt'
        self.default_cover = './images/default_cover.jpg'
        self.song_cover = self.default_cover
        self.music_types = ['default', 'mp3', 'flac', 'ogg', 'wav', 'm4a', 'ape']
        self.video_types = ['mp4', 'flv', 'mkv', 'avi']
        self.file_types = self.music_types[1:] + self.video_types
        self.current_file_name = ''
        self.current_file_type = 'default'
        self.music_numbers = 0
        self.video_numbers = 0
        self.initUI()
        self.change_display_widget_layout()
        self.change_theme()
        self.get_list(self.music_list_file)
        self.get_list(self.video_list_file)
        self.update_switch_list_button_text()

    # 关闭窗口询问
    def closeEvent(self, QCloseEvent):
        reply = QMessageBox.question(self, '消息', '确定退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()

    # 初始化UI
    def initUI(self):
        self.setWindowTitle('媒体播放器')
        self.setWindowIcon(QIcon('./images/icon.ico'))
        self.resize(1000, 750)
        self.set_dark_theme = True

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        self.status = self.statusBar()
        self.status.showMessage('欢迎来到媒体播放器！', 5000)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        setting_menu = menubar.addMenu('设置')
        file_act = QAction('添加文件', self)
        folder_act = QAction('添加文件夹', self)
        theme_act = QAction('切换主题', self)
        clear_act = QAction('清空列表', self)

        file_act.setShortcut('Ctrl+O')
        folder_act.setShortcut('Ctrl+D')
        theme_act.setShortcut('Ctrl+T')
        clear_act.setShortcut('Ctrl+Shift+C')

        file_menu.addAction(file_act)
        file_menu.addAction(folder_act)
        setting_menu.addAction(theme_act)
        setting_menu.addAction(clear_act)

        file_act.triggered.connect(self.open_file)
        folder_act.triggered.connect(self.open_folder)
        theme_act.triggered.connect(self.change_theme)
        clear_act.triggered.connect(self.clear_current_list)

        self.list_pop_menu = QMenu()
        list_pop_menu_add_file_act = QAction('添加文件', self)
        list_pop_menu_add_folder_act = QAction('添加文件夹', self)
        list_pop_menu_play_act = QAction('播放', self)
        list_pop_menu_delete_act = QAction('删除', self)
        list_pop_menu_clear_act = QAction('清空', self)

        self.list_pop_menu.addAction(list_pop_menu_add_file_act)
        self.list_pop_menu.addAction(list_pop_menu_add_folder_act)
        self.list_pop_menu.addAction(list_pop_menu_play_act)
        self.list_pop_menu.addAction(list_pop_menu_delete_act)
        self.list_pop_menu.addAction(list_pop_menu_clear_act)

        list_pop_menu_add_file_act.triggered.connect(self.open_file)
        list_pop_menu_add_folder_act.triggered.connect(self.open_folder)
        list_pop_menu_play_act.triggered.connect(self.play)
        list_pop_menu_delete_act.triggered.connect(self.delete_select_file)
        list_pop_menu_clear_act.triggered.connect(self.clear_current_list)

        self.player = QMediaPlayer()
        self.play_list = QMediaPlaylist()
        self.play_list.setPlaybackMode(3)
        self.player.setPlaylist(self.play_list)

        self.video_widget = MyVideoWidget()
        self.video_widget.setStyleSheet('background-color: gray')
        self.video_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.player.setVideoOutput(self.video_widget)

        self.picture_widget = QLabel()
        self.picture_widget.setScaledContents(True)
        self.picture_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        play_button = QPushButton('播放')
        pause_button = QPushButton('暂停')
        next_button = QPushButton('下一个')
        last_button = QPushButton('上一个')
        play_mode_button = QComboBox()
        play_mode_button.addItem('单曲播放')
        play_mode_button.addItem('单曲循环')
        play_mode_button.addItem('列表播放')
        play_mode_button.addItem('列表循环')
        play_mode_button.addItem('列表随机')
        play_mode_button.setCurrentIndex(3)
        mode_text = QLabel('模式')
        change_speed_button = QDoubleSpinBox()
        change_speed_button.setRange(0.25, 2)
        change_speed_button.setSingleStep(0.25)
        change_speed_button.setDecimals(2)
        change_speed_button.setValue(1)
        change_speed_button.setWrapping(True)
        speed_text = QLabel('倍速')
        video_full_screen_button = QPushButton('全屏')
        delete_button = QPushButton('删除')
        quit_button = QPushButton('退出')
        self.hide_list_button = QPushButton('隐藏')
        self.hide_list_flag = False

        self.play_slider = QSlider(Qt.Horizontal, self)
        self.play_slider.setRange(0, 0)
        self.play_slider.setSingleStep(1)

        volume_slider = QSlider(Qt.Horizontal, self)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(50)
        volume_slider.setSingleStep(1)

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont('Microsoft YaHei', 8))
        self.list_widget.setContextMenuPolicy(3)
        self.switch_list_button = QComboBox()
        self.switch_list_button.addItem('')
        self.switch_list_button.addItem('')
        self.switch_list_button.addItem('')
        self.switch_list_button.setCurrentIndex(0)

        self.play_label_1 = QLabel('00:00:00')
        self.play_label_2 = QLabel('00:00:00')
        self.volume_value_label = QLabel(' 50')
        volume_text = QLabel('音量')

        layout_h_1 = QHBoxLayout()
        layout_h_2 = QHBoxLayout()
        layout_h_3 = QHBoxLayout()
        layout_v_4 = QVBoxLayout()
        self.layout_h_4 = QHBoxLayout()
        main_layout = QVBoxLayout()
        self.display_widget_layout = QHBoxLayout()
        self.display_widget_layout.addWidget(self.picture_widget)

        layout_h_1.addWidget(self.play_label_1)
        layout_h_1.addWidget(self.play_slider)
        layout_h_1.addWidget(self.play_label_2)

        layout_h_2.addWidget(mode_text)
        layout_h_2.addWidget(play_mode_button)
        layout_h_2.addWidget(speed_text)
        layout_h_2.addWidget(change_speed_button)
        layout_h_2.addWidget(QLabel())
        layout_h_2.addWidget(volume_text)
        layout_h_2.addWidget(volume_slider)
        layout_h_2.addWidget(self.volume_value_label)

        layout_h_2.setStretch(1, 2)
        layout_h_2.setStretch(3, 2)
        layout_h_2.setStretch(4, 3)
        layout_h_2.setStretch(6, 4)

        layout_h_3.addWidget(last_button)
        layout_h_3.addWidget(next_button)
        layout_h_3.addWidget(play_button)
        layout_h_3.addWidget(pause_button)
        layout_h_3.addWidget(video_full_screen_button)
        layout_h_3.addWidget(delete_button)
        layout_h_3.addWidget(quit_button)
        layout_h_3.addWidget(self.hide_list_button)

        layout_v_4.addWidget(self.switch_list_button)
        layout_v_4.addWidget(self.list_widget)
        self.layout_h_4.addLayout(self.display_widget_layout)
        self.layout_h_4.addLayout(layout_v_4)
        self.layout_h_4.setStretch(0, 5)
        self.layout_h_4.setStretch(1, 2)

        main_layout.addLayout(self.layout_h_4)
        main_layout.addLayout(layout_h_3)
        main_layout.addLayout(layout_h_2)
        main_layout.addLayout(layout_h_1)

        self.play_list.currentMediaChanged.connect(self.current_media_changed)
        self.list_widget.itemDoubleClicked.connect(self.quickly_play)
        self.list_widget.customContextMenuRequested[QPoint].connect(self.show_right_clicked_menu)
        self.video_widget.doubleClickedItem.connect(self.video_double_clicked)
        self.video_widget.singleClickedItem.connect(self.video_single_clicked)
        self.video_widget.leftArrowKeyPressedItem.connect(self.back_and_forward)
        self.video_widget.rightArrowKeyPressedItem.connect(self.back_and_forward)
        self.video_widget.spaceKeyPressedItem.connect(self.video_single_clicked)
        last_button.clicked.connect(self.play_last)
        play_button.clicked.connect(self.play)
        pause_button.clicked.connect(self.pause)
        next_button.clicked.connect(self.play_next)
        play_mode_button.currentIndexChanged.connect(self.change_play_mode)
        change_speed_button.valueChanged.connect(self.change_play_speed)
        self.switch_list_button.currentIndexChanged.connect(self.change_current_list)
        video_full_screen_button.clicked.connect(self.video_full_screen)
        delete_button.clicked.connect(self.delete_select_file)
        quit_button.clicked.connect(self.quit_app)
        self.hide_list_button.clicked.connect(self.hide_or_show_list)
        self.player.durationChanged.connect(self.change_slider_range)
        self.play_slider.sliderMoved.connect(self.change_play_position)
        self.player.positionChanged.connect(self.change_slider_value)
        volume_slider.valueChanged.connect(self.change_volume)

        main_widget.setLayout(main_layout)

    # 当音乐或视频的数量发生变化时，更新列表上方按钮的显示文字

    def update_switch_list_button_text(self):
        self.switch_list_button.setItemText(0, '全部(' + str(self.music_numbers + self.video_numbers) + ')')
        self.switch_list_button.setItemText(1, '音乐(' + str(self.music_numbers) + ')')
        self.switch_list_button.setItemText(2, '视频(' + str(self.video_numbers) + ')')

    # 隐藏或显示列表栏
    def hide_or_show_list(self):
        if self.list_widget.isVisible():
            self.list_widget.setVisible(False)
            self.switch_list_button.setVisible(False)
            self.layout_h_4.setStretch(0, 1)
            self.layout_h_4.setStretch(1, 0)
            self.hide_list_button.setText('显示')
        else:
            self.list_widget.setVisible(True)
            self.switch_list_button.setVisible(True)
            self.layout_h_4.setStretch(0, 5)
            self.layout_h_4.setStretch(1, 2)
            self.hide_list_button.setText('隐藏')

    # 全屏播放视频时快进或快退
    def back_and_forward(self, signal):
        if signal == 'left arrow pressed':
            self.player.setPosition(self.player.position() - 5000)
        else:
            self.player.setPosition(self.player.position() + 5000)

    # 显示列表栏的右键菜单
    def show_right_clicked_menu(self, point):
        self.list_pop_menu.exec_(QCursor.pos())

    # 切换显示视频或显示图片
    def change_display_widget_layout(self):
        if self.current_file_type in self.music_types:
            self.display_widget_layout.removeWidget(self.video_widget)
            self.display_widget_layout.addWidget(self.picture_widget)
            self.picture_widget.setVisible(True)
            self.picture_widget.setEnabled(True)
            self.video_widget.setVisible(False)
            self.video_widget.setEnabled(False)
            if self.current_file_type == 'default':
                self.picture_widget.setPixmap(QPixmap(self.default_cover))
            else:
                self.picture_widget.setPixmap(QPixmap(self.song_cover).scaled(600, 600))
        else:
            self.display_widget_layout.removeWidget(self.picture_widget)
            self.display_widget_layout.addWidget(self.video_widget)
            self.video_widget.setVisible(True)
            self.picture_widget.setVisible(False)
            self.video_widget.setEnabled(True)
            self.picture_widget.setEnabled(False)

    # 根据列表文件生成播放列表
    def get_list(self, list_file):
        if exists(list_file):
            with open(list_file, 'r', encoding='utf-8') as read_file:
                all_file_paths = read_file.readlines()
                if list_file == self.music_list_file:
                    self.music_numbers = len(all_file_paths)
                if list_file == self.video_list_file:
                    self.video_numbers = len(all_file_paths)
                for item in all_file_paths:
                    file_path = item[:-1]
                    self.list_widget.addItem(file_path.split('/')[-1])
                    self.play_list.addMedia(QMediaContent(QUrl.fromLocalFile(file_path)))

    # 切换播放列表
    def change_current_list(self, index):
        self.play_list.clear()
        self.list_widget.clear()
        self.current_file_type = 'default'
        self.change_display_widget_layout()
        if index == 0:
            self.get_list(self.music_list_file)
            self.get_list(self.video_list_file)
        elif index == 1:
            self.get_list(self.music_list_file)
        elif index == 2:
            self.get_list(self.video_list_file)
        self.status.showMessage('已切换播放列表！', 5000)

    # 清空当前播放列表
    def clear_current_list(self):
        reply = QMessageBox.question(self, '消息', '确定清空当前播放列表吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.play_list.clear()
            self.list_widget.clear()
            self.current_file_type = 'default'
            self.change_display_widget_layout()
            if self.switch_list_button.currentIndex() == 0:
                self.music_numbers = 0
                self.video_numbers = 0
                if exists(self.music_list_file):
                    with open(self.music_list_file, 'w', encoding='utf-8') as _:
                        pass
                if exists(self.video_list_file):
                    with open(self.video_list_file, 'w', encoding='utf-8') as _:
                        pass
            elif self.switch_list_button.currentIndex() == 1:
                if exists(self.music_list_file):
                    self.music_numbers = 0
                    with open(self.music_list_file, 'w', encoding='utf-8') as _:
                        pass
            elif self.switch_list_button.currentIndex() == 2:
                if exists(self.video_list_file):
                    self.video_numbers = 0
                    with open(self.video_list_file, 'w', encoding='utf-8') as _:
                        pass
            self.status.showMessage('当前列表已清空！', 5000)
            self.update_switch_list_button_text()

    # 删除选中文件
    def delete_select_file(self):
        if self.play_list.isEmpty():
            QMessageBox.warning(self, '警告', '没有待删除的文件！', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        reply = QMessageBox.question(self, '消息', '确定删除选中文件吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:

            select_index = self.list_widget.currentRow()
            select_file_name = self.list_widget.currentItem().text()
            select_file_type = self.list_widget.currentItem().text().split('.')[-1]

            if select_file_name == self.current_file_name:
                self.player.stop()
                self.current_file_type = 'default'
                self.change_display_widget_layout()

            self.list_widget.takeItem(select_index)
            self.play_list.removeMedia(select_index)

            self.status.showMessage('已从列表中移除：' + select_file_name + '！', 5000)

            if select_file_type in self.music_types:
                list_file = self.music_list_file
                self.music_numbers -= 1
            else:
                list_file = self.video_list_file
                self.video_numbers -= 1

            with open(list_file, 'r', encoding='utf-8') as read_file:
                all_file_paths = read_file.readlines()
            with open(list_file, 'w', encoding='utf-8') as write_file:
                for item in all_file_paths:
                    file_path = item[:-1]
                    if file_path.split('/')[-1] == select_file_name:
                        continue
                    write_file.write(file_path + '\n')

            self.update_switch_list_button_text()

    # 按钮全屏

    def video_full_screen(self):
        if self.current_file_type in self.video_types:
            self.video_widget.setFullScreen(True)
        else:
            self.status.showMessage('只有视频文件才能全屏哦！', 5000)

    # 视频双击全屏
    def video_double_clicked(self):
        if self.video_widget.isFullScreen():
            self.video_widget.setFullScreen(False)
        else:
            self.video_widget.setFullScreen(True)
        self.play()

    # 视频单击暂停
    def video_single_clicked(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.pause()
        else:
            self.play()

    # 添加文件
    def open_file(self):
        file_path = QFileDialog.getOpenFileName(self, '打开文件', '.', '媒体文件(*.' + ' *.'.join(self.file_types) + ')')[0]
        if not exists(file_path):
            self.status.showMessage('未选择文件！', 5000)
            return

        file_type = file_path.split('.')[-1]

        if file_type in self.music_types:
            list_file = self.music_list_file
        else:
            list_file = self.video_list_file

        if exists(list_file):
            with open(list_file, 'r', encoding='utf-8') as read_file:
                all_file_paths = read_file.readlines()
                if file_path + '\n' in all_file_paths:
                    self.status.showMessage('已存在相同文件！', 5000)
                    return
            with open(list_file, 'a', encoding='utf-8') as write_file:
                write_file.write(file_path + '\n')
        else:
            with open(list_file, 'w', encoding='utf-8') as write_file:
                write_file.write(file_path + '\n')

        if file_type in self.music_types:
            self.list_widget.insertItem(self.music_numbers, file_path.split('/')[-1])
            self.play_list.insertMedia(self.music_numbers, QMediaContent(QUrl.fromLocalFile(file_path)))
            self.music_numbers += 1
        else:
            self.list_widget.addItem(file_path.split('/')[-1])
            self.play_list.addMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.video_numbers += 1

        self.status.showMessage('成功添加至播放列表！', 5000)
        self.update_switch_list_button_text()

    # 添加文件夹
    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '打开文件夹')
        if not exists(folder):
            self.status.showMessage('未选择文件夹！', 5000)
            return
        it = QDirIterator(folder)
        it.next()
        while it.hasNext():
            if it.fileInfo().suffix() in self.file_types:
                file_path = it.filePath()
                file_type = file_path.split('.')[-1]
                if file_type in self.music_types:
                    list_file = self.music_list_file
                else:
                    list_file = self.video_list_file

                if exists(list_file):
                    with open(list_file, 'r', encoding='utf-8') as read_file:
                        all_file_paths = read_file.readlines()
                        if file_path + '\n' in all_file_paths:
                            it.next()
                            continue
                    with open(list_file, 'a', encoding='utf-8') as write_file:
                        write_file.write(file_path + '\n')
                else:
                    with open(list_file, 'w', encoding='utf-8') as write_file:
                        write_file.write(file_path + '\n')
                if file_type in self.music_types:
                    self.list_widget.insertItem(self.music_numbers, file_path.split('/')[-1])
                    self.play_list.insertMedia(self.music_numbers, QMediaContent(QUrl.fromLocalFile(file_path)))
                    self.music_numbers += 1
                else:
                    self.list_widget.addItem(file_path.split('/')[-1])
                    self.play_list.addMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
                    self.video_numbers += 1
                self.status.showMessage('成功添加至播放列表！', 5000)
            it.next()
        self.update_switch_list_button_text()

        if it.fileInfo().suffix() in self.file_types:
            file_path = it.filePath()
            file_type = file_path.split('.')[-1]
            if file_type in self.music_types:
                list_file = self.music_list_file
            else:
                list_file = self.video_list_file

            if exists(list_file):
                with open(list_file, 'r', encoding='utf-8') as read_file:
                    all_file_paths = read_file.readlines()
                    if file_path + '\n' in all_file_paths:
                        return
                with open(list_file, 'a', encoding='utf-8') as write_file:
                    write_file.write(file_path + '\n')
            else:
                with open(list_file, 'w', encoding='utf-8') as write_file:
                    write_file.write(file_path + '\n')

            if file_type in self.music_types:
                self.list_widget.insertItem(self.music_numbers, file_path.split('/')[-1])
                self.play_list.insertMedia(self.music_numbers, QMediaContent(QUrl.fromLocalFile(file_path)))
                self.music_numbers += 1
            else:
                self.list_widget.addItem(file_path.split('/')[-1])
                self.play_list.addMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
                self.video_numbers += 1

            self.status.showMessage('成功添加至播放列表！', 5000)
            self.update_switch_list_button_text()

    # 播放上一个
    def play_last(self):
        self.play_list.previous()
        self.play()

    # 播放
    def play(self):
        if self.play_list.isEmpty():
            QMessageBox.warning(self, '警告', '没有待播放的文件！', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return

        if self.list_widget.currentItem().text().split('.')[-1] in self.music_types:
            list_file = self.music_list_file
        else:
            list_file = self.video_list_file
        flag = 0
        with open(list_file, 'r', encoding='utf-8') as read_file:
            all_file_paths = read_file.readlines()
        with open(list_file, 'w', encoding='utf-8') as write_file:
            for item in all_file_paths:
                file_path = item[:-1]
                if self.list_widget.currentItem().text() == file_path.split('/')[-1] and not exists(file_path):
                    self.player.stop()
                    self.status.showMessage('文件已删除！', 5000)
                    current_index = self.list_widget.currentRow()
                    self.list_widget.takeItem(current_index)
                    self.play_list.removeMedia(current_index)
                    if self.list_widget.currentItem().text().split('.')[-1] in self.music_types:
                        self.music_numbers -= 1
                    else:
                        self.video_numbers -= 1
                    flag = 1
                    continue
                write_file.write(file_path + '\n')

        if flag == 1:
            return

        self.current_file_name = self.list_widget.currentItem().text()
        self.current_file_type = self.list_widget.currentItem().text().split('.')[-1]
        self.play_list.setCurrentIndex(self.list_widget.currentRow())
        self.player.play()
        self.update_switch_list_button_text()

    # 暂停
    def pause(self):
        self.player.pause()

    # 播放下一个
    def play_next(self):
        self.play_list.next()
        self.play()

    # 退出程序
    def quit_app(self):
        reply = QMessageBox.question(self, '消息', '确定退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()  # 退出应用程序

    # 列表双击播放
    def quickly_play(self):
        if self.play_list.isEmpty():
            return
        else:
            self.play()

    # 改变播放模式
    def change_play_mode(self, index):
        self.play_list.setPlaybackMode(index)

    # 改变播放倍速
    def change_play_speed(self, value):
        self.player.setPlaybackRate(value)

    # 当前媒体发生变化
    def current_media_changed(self, media):
        if not media.isNull():
            url = media.canonicalUrl()
            file_path = url.path()[1:]
            file_name = url.path().split('/')[-1]
            file_type = url.path().split('.')[-1]
            self.current_file_name = file_name
            self.current_file_type = file_type
            self.status.showMessage(url.fileName())
            self.list_widget.setCurrentRow(self.play_list.currentIndex())
            if file_type == 'm4a':
                file = MP4(file_path)
                try:
                    cover = file.tags['covr'][0]
                    cover_path = './cover/' + file_name + '.jpg'
                    if not exists('./cover'):
                        mkdir('./cover')
                    if not exists(cover_path):
                        with open(cover_path, 'wb') as write_file:
                            write_file.write(cover)
                    self.song_cover = cover_path
                except:
                    self.song_cover = './images/default_cover.jpg'

            elif file_type == 'mp3':
                file = File(file_path)
                try:
                    cover = file.tags['APIC:'].data
                    cover_path = './cover/' + file_name + '.jpg'
                    if not exists('./cover'):
                        mkdir('./cover')
                    if not exists(cover_path):
                        with open(cover_path, 'wb') as write_file:
                            write_file.write(cover)
                    self.song_cover = cover_path
                except:
                    self.song_cover = './images/default_cover.jpg'
            else:
                self.song_cover = './images/default_cover.jpg'
            self.change_display_widget_layout()

    # 切换主题
    def change_theme(self):
        app.setStyle("Fusion")
        palette = QPalette()
        # 黑暗主题
        if self.set_dark_theme:
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(235, 101, 54))
            palette.setColor(QPalette.Highlight, QColor(235, 101, 54))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.set_dark_theme = not self.set_dark_theme
        # 明亮主题
        else:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, QColor(240, 240, 240))
            palette.setColor(QPalette.AlternateBase, Qt.white)
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, Qt.white)
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(66, 155, 248))
            palette.setColor(QPalette.Highlight, QColor(66, 155, 248))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.set_dark_theme = not self.set_dark_theme

    # 改变声音大小
    def change_volume(self, value):
        self.volume_value_label.setText(str(value) if value == 100 else '{: 3}'.format(value))
        self.player.setVolume(value)

    # 改变进度条范围
    def change_slider_range(self, duration):
        self.play_slider.setRange(0, duration)
        total_time_s = int(duration / 1000)
        hour = total_time_s // 3600
        minute = total_time_s % 3600 // 60
        second = total_time_s % 3600 % 60
        time = [hour, minute, second]
        for i in range(len(time)):
            time[i] = '{:02}'.format(time[i])
        self.play_label_2.setText(':'.join(time))

    # 改变当前进度条的值
    def change_slider_value(self, position):
        self.play_slider.setValue(position)
        total_time_s = int(position / 1000)
        hour = total_time_s // 3600
        minute = total_time_s % 3600 // 60
        second = total_time_s % 3600 % 60
        time = [hour, minute, second]
        for i in range(len(time)):
            time[i] = '{:02}'.format(time[i])
        self.play_label_1.setText(':'.join(time))

    # 改变当前播放位置
    def change_play_position(self, position):
        self.player.setPosition(position)  # 改变播放时刻


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MyMainWin()
    main_win.show()
    sys.exit(app.exec_())
