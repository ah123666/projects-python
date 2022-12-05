import sys
import pygame
from pygame.locals import *
import os
import random
import tkinter
from tkinter import filedialog

# 颜色定义
color_red = (255, 0, 0)
color_green = (0, 255, 0)
color_blue = (0, 0, 255)
color_white = (255, 255, 255)

# 播放模式
sequence_play = 0
loop_play = 1
random_play = 2


class Text:
    """
    文本类
    """

    def __init__(self, src_rect, button_rect, content, k):
        self.content = content
        self.line_gap = 1
        self.line_width = 2
        self.k = k
        self.update(src_rect, button_rect)

    def draw(self, scr, color):
        scr.blit(self.text, self.rect)
        pygame.draw.line(scr, color, (self.rect.left - self.line_gap, self.rect.top - self.line_gap),
                         (self.rect.right + self.line_gap, self.rect.top - self.line_gap), self.line_width)
        pygame.draw.line(scr, color, (self.rect.right + self.line_gap, self.rect.top - self.line_gap),
                         (self.rect.right + self.line_gap, self.rect.bottom + self.line_gap), self.line_width)
        pygame.draw.line(scr, color, (self.rect.right + self.line_gap, self.rect.bottom + self.line_gap),
                         (self.rect.left - self.line_gap, self.rect.bottom + self.line_gap), self.line_width)
        pygame.draw.line(scr, color, (self.rect.left - self.line_gap, self.rect.bottom + self.line_gap),
                         (self.rect.left - self.line_gap, self.rect.top - self.line_gap), self.line_width)

    def update(self, src_rect, button_rect):
        self.font_size = int(0.02 * (src_rect.width + src_rect.height))
        self.font = pygame.font.SysFont('SimHei', self.font_size)
        self.text = self.font.render(self.content, True, color_blue, color_white)
        self.rect = self.text.get_rect()
        while (self.rect.width + self.line_gap + self.line_width) >= (screen_rect.width - button_rect.left):
            self.font_size -= 1
            self.font = pygame.font.SysFont('SimHei', self.font_size)
            self.text = self.font.render(self.content, True, color_blue, color_white)
            self.rect = self.text.get_rect()
        self.rect.bottomleft = [button_rect.left, button_rect.top + self.k * button_rect.height]


class Button:
    """
    按钮控件类
    """

    def __init__(self, rect, image, x_pos, k):
        self.x_pos = x_pos
        self.k = k
        self.line_draw = False
        self.update(rect, image)

    def draw(self, scr):
        scr.blit(self.image, self.rect)
        if self.line_draw:
            self.draw_line(scr, color_red)

    def draw_line(self, scr, color):
        pygame.draw.line(scr, color, (self.rect.left - self.line_gap, self.rect.top - self.line_gap),
                         (self.rect.right + self.line_gap, self.rect.top - self.line_gap), self.line_width)
        pygame.draw.line(scr, color, (self.rect.right + self.line_gap, self.rect.top - self.line_gap),
                         (self.rect.right + self.line_gap, self.rect.bottom + self.line_gap), self.line_width)
        pygame.draw.line(scr, color, (self.rect.right + self.line_gap, self.rect.bottom + self.line_gap),
                         (self.rect.left - self.line_gap, self.rect.bottom + self.line_gap), self.line_width)
        pygame.draw.line(scr, color, (self.rect.left - self.line_gap, self.rect.bottom + self.line_gap),
                         (self.rect.left - self.line_gap, self.rect.top - self.line_gap), self.line_width)

    def get_range(self):
        self.range_x = list(range(self.rect.left, self.rect.right + 1))
        self.range_y = list(range(self.rect.top, self.rect.bottom + 1))

    def update(self, rect, image):
        self.image = pygame.transform.smoothscale(image, (int(0.05 * rect.width), int(0.05 * rect.height)))
        self.rect = self.image.get_rect()
        self.rect.topleft = [int(self.x_pos * rect.width), rect.centery + self.k * self.rect.height]
        self.line_gap = int(0.02 * (self.rect.width + self.rect.height))
        self.line_width = int(0.05 * (self.rect.width + self.rect.height))
        self.get_range()


class Music:
    """
    音乐类
    """

    def __init__(self):
        self.play_mode = sequence_play
        self.is_pause = False
        self.first_play = True
        self.folder_is_empty = False
        self.played_time = 0
        self.user_change = False
        self.collect_music("./resources/music")

    def collect_music(self, file_path):
        self.play_index = 0
        musics = []
        for root, dirs, files in os.walk(file_path):
            for file in files:
                if file.endswith('mp3') or file.endswith('flac') or file.endswith('wav'):
                    full_file = os.path.join(root, file)
                    musics.append(full_file)
        if musics:
            self.content = musics
            self.folder_is_empty = False
        else:
            self.folder_is_empty = True

    def play(self):
        pygame.mixer.music.unload()
        pygame.mixer.music.load(self.content[self.play_index])
        pygame.mixer.music.play()
        sound = pygame.mixer.Sound(self.content[self.play_index])
        self.total_time = sound.get_length()
        self.first_play = False

    def pause(self):
        pygame.mixer.music.pause()
        self.is_pause = True

    def unpause(self):
        pygame.mixer.music.unpause()
        self.is_pause = False

    def stop(self):
        pygame.mixer.music.stop()
        self.first_play = True

    def draw_play_bar(self, src, scr_rect, button_rect1, button_rect2, time):
        # 画进度条
        self.played_time = (pygame.mixer.music.get_pos() + time) / 1000

        self.played_percent = self.played_time / self.total_time

        self.bar_x_length = button_rect2.right - button_rect1.left
        self.bar_y_length = int(scr_rect.height * 0.02)

        pygame.draw.rect(src, color_red, ((button_rect1.left, button_rect1.bottom + button_rect1.height),
                                          (int(self.bar_x_length * self.played_percent), self.bar_y_length)))
        pygame.draw.rect(src, color_white, (((button_rect1.left + int(self.bar_x_length * self.played_percent) + 1,
                                              button_rect1.bottom + button_rect1.height),
                                             (self.bar_x_length - int(self.bar_x_length * self.played_percent),
                                              self.bar_y_length))))

    def get_bar_range(self, scr_rect, button_rect1, button_rect2):
        self.bar_x_length = button_rect2.right - button_rect1.left
        self.bar_y_length = int(scr_rect.height * 0.02)
        self.bar_range_x = list(range(button_rect1.left, button_rect1.left + self.bar_x_length + 1))
        self.bar_range_y = list(range(button_rect1.bottom + button_rect1.height, button_rect1.bottom + button_rect1.height + self.bar_y_length + 1))

    def get_next_index(self):
        if self.play_mode == sequence_play:
            self.play_index += 1
            if self.play_index >= len(self.content):
                self.play_index = 0
        if self.play_mode == random_play:
            while True:
                new_index = random.randint(0, len(self.content) - 1)
                if self.play_index != new_index:
                    self.play_index = new_index
                    break
        if self.play_mode == loop_play:
            pass

    def get_last_index(self):
        if self.play_mode == sequence_play:
            self.play_index -= 1
            if self.play_index < 0:
                self.play_index = len(self.content) - 1
        if self.play_mode == random_play:
            while True:
                new_index = random.randint(0, len(self.content) - 1)
                if self.play_index != new_index:
                    self.play_index = new_index
                    break
        if self.play_mode == loop_play:
            pass

    def play_next_music_with_mode(self):
        if self.play_mode == sequence_play:
            self.play_index += 1
            if self.play_index >= len(self.content):
                self.play_index = 0
            self.play()
        if self.play_mode == random_play:
            while True:
                new_index = random.randint(0, len(self.content) - 1)
                if self.play_index != new_index:
                    self.play_index = new_index
                    break
            self.play()
        if self.play_mode == loop_play:
            self.play()


# 初始化pygame
pygame.init()
pygame.mixer.init()

# 设置界面
screen = pygame.display.set_mode((600, 400), RESIZABLE)
screen_rect = screen.get_rect()

# 图标和背景
launcher_img = pygame.image.load("resources/image/icon.ico").convert_alpha()
launcher_img = pygame.transform.smoothscale(launcher_img, (32, 32))
ori_bg_img = pygame.image.load("resources/image/bg1.jpg").convert_alpha()
ori_file_img = pygame.image.load("resources/image/open_file.png").convert_alpha()
ori_last_img = pygame.image.load("resources/image/last.png").convert_alpha()
ori_play_img = pygame.image.load("resources/image/play.png").convert_alpha()
ori_pause_img = pygame.image.load("resources/image/pause.png").convert_alpha()
ori_next_img = pygame.image.load("resources/image/next.png").convert_alpha()
ori_sequence_img = pygame.image.load("resources/image/sequence.png").convert_alpha()
ori_random_img = pygame.image.load("resources/image/random.png").convert_alpha()
ori_loop_img = pygame.image.load("resources/image/loop.png").convert_alpha()
bg_img = pygame.transform.smoothscale(ori_bg_img, (screen.get_rect().width, screen.get_rect().height))

# 设置标题及图标
pygame.display.set_caption("音乐播放器")
pygame.display.set_icon(launcher_img)

# 建立按钮对象
file_button = Button(screen_rect, ori_file_img, 0.25, -2)
sequence_button = Button(screen_rect, ori_sequence_img, 0.4, -2)
sequence_button.line_draw = True
random_button = Button(screen_rect, ori_random_img, 0.55, -2)
loop_button = Button(screen_rect, ori_loop_img, 0.7, -2)
last_button = Button(screen_rect, ori_last_img, 0.25, 1)
play_button = Button(screen_rect, ori_play_img, 0.4, 1)
pause_button = Button(screen_rect, ori_pause_img, 0.55, 1)
next_button = Button(screen_rect, ori_next_img, 0.7, 1)

# 建立音乐对象
music = Music()

# 建立文本对象
text = Text(screen_rect, file_button.rect, "当前目录：./resources/music", -4)
text_music = Text(screen_rect, file_button.rect, "无音乐在播放", -1.5)

tkinter.Tk().withdraw()

clock = pygame.time.Clock()
time = 0
# 主循环
while True:
    clock.tick(30)
    screen.blit(bg_img, (0, 0))
    file_button.draw(screen)
    sequence_button.draw(screen)
    random_button.draw(screen)
    loop_button.draw(screen)
    last_button.draw(screen)
    play_button.draw(screen)
    pause_button.draw(screen)
    next_button.draw(screen)
    text.draw(screen, color_green)
    text_music.draw(screen, color_green)

    if pygame.mixer.music.get_busy():
        music.draw_play_bar(screen, screen_rect, last_button.rect, next_button.rect, time)

    if not pygame.mixer.music.get_busy() and not music.first_play:
        music.play_next_music_with_mode()
        text_music.content = music.content[music.play_index].split("\\")[-1]
        text_music.update(screen_rect, file_button.rect)

    pygame.display.update()

    for event in pygame.event.get():
        # 退出
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # 改变窗口大小
        if event.type == VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, RESIZABLE)
            bg_img = pygame.transform.smoothscale(ori_bg_img, event.size)
            screen_rect = screen.get_rect()
            file_button.update(screen_rect, ori_file_img)
            sequence_button.update(screen_rect, ori_sequence_img)
            random_button.update(screen_rect, ori_random_img)
            loop_button.update(screen_rect, ori_loop_img)
            last_button.update(screen_rect, ori_last_img)
            play_button.update(screen_rect, ori_play_img)
            pause_button.update(screen_rect, ori_pause_img)
            next_button.update(screen_rect, ori_next_img)
            text.update(screen_rect, file_button.rect)
            text_music.update(screen_rect, file_button.rect)

        # 鼠标单击
        if event.type == MOUSEBUTTONDOWN:

            music.get_bar_range(screen_rect, last_button.rect, next_button.rect)

            # 进度条调整
            if event.pos[0] in music.bar_range_x and event.pos[1] in music.bar_range_y:
                music.stop()
                music.play()
                time = ((event.pos[0] - last_button.rect.left) / music.bar_x_length) * music.total_time
                pygame.mixer.music.set_pos(time)

            # 打开文件夹按钮
            if event.pos[0] in file_button.range_x and event.pos[1] in file_button.range_y:
                file_button.line_draw = True

            # 顺序播放按钮
            if event.pos[0] in sequence_button.range_x and event.pos[1] in sequence_button.range_y:
                sequence_button.line_draw = True
                random_button.line_draw = False
                loop_button.line_draw = False
                music.play_mode = sequence_play

            # 随机播放按钮
            if event.pos[0] in random_button.range_x and event.pos[1] in random_button.range_y:
                sequence_button.line_draw = False
                random_button.line_draw = True
                loop_button.line_draw = False
                music.play_mode = random_play

            # 单曲循环按钮
            if event.pos[0] in loop_button.range_x and event.pos[1] in loop_button.range_y:
                sequence_button.line_draw = False
                random_button.line_draw = False
                loop_button.line_draw = True
                music.play_mode = loop_play

            # 上一首按钮
            if event.pos[0] in last_button.range_x and event.pos[1] in last_button.range_y:
                last_button.line_draw = True
                music.get_last_index()
                music.play()
                text_music.content = music.content[music.play_index].split("\\")[-1]
                text_music.update(screen_rect, file_button.rect)

            # 播放按钮
            if event.pos[0] in play_button.range_x and event.pos[1] in play_button.range_y:
                play_button.line_draw = True
                text_music.content = music.content[music.play_index].split("\\")[-1]
                text_music.update(screen_rect, file_button.rect)
                if not pygame.mixer.music.get_busy():
                    music.play()
                if music.is_pause:
                    music.unpause()

            # 暂停按钮
            if event.pos[0] in pause_button.range_x and event.pos[1] in pause_button.range_y:
                pause_button.line_draw = True
                music.pause()

            # 下一首按钮
            if event.pos[0] in next_button.range_x and event.pos[1] in next_button.range_y:
                next_button.line_draw = True
                music.get_next_index()
                music.play()
                text_music.content = music.content[music.play_index].split("\\")[-1]
                text_music.update(screen_rect, file_button.rect)

        # 鼠标释放
        if event.type == MOUSEBUTTONUP:

            # 打开文件夹按钮
            if event.pos[0] in file_button.range_x and event.pos[1] in file_button.range_y:
                file_button.line_draw = False
                file_path = filedialog.askdirectory(title="选择音乐文件夹")  # 选择目录，返回目录名
                if file_path != "":
                    music.stop()
                    text_music.content = "无音乐在播放"
                    text_music.update(screen_rect, file_button.rect)
                    music.collect_music(file_path)
                    if not music.folder_is_empty:
                        text.content = "当前目录：" + file_path
                        text.update(screen_rect, file_button.rect)

            # 上一首按钮
            if event.pos[0] in last_button.range_x and event.pos[1] in last_button.range_y:
                last_button.line_draw = False
            # 播放按钮
            if event.pos[0] in play_button.range_x and event.pos[1] in play_button.range_y:
                play_button.line_draw = False
            # 暂停按钮
            if event.pos[0] in pause_button.range_x and event.pos[1] in pause_button.range_y:
                pause_button.line_draw = False
            # 下一首按钮
            if event.pos[0] in next_button.range_x and event.pos[1] in next_button.range_y:
                next_button.line_draw = False
