import sys
import pygame
from pygame.locals import *
import os
import random
from enum import Enum


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 320


class Color(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


class PlayMode(Enum):
    SEQUENCE = "顺序播放"
    RANDOM = "随机播放"
    LOOP = "循环播放"


class Music:

    def __init__(self):
        self.root_dir = "./resources/music"
        self.path_list = []
        self.collect_music()
        self.cur_idx = 0
        self.play_mode = PlayMode.SEQUENCE


    def collect_music(self):
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('mp3') or file.endswith('flac') or file.endswith('wav'):
                    full_file = os.path.join(root, file)
                    self.path_list.append(full_file)

    def get_current_music_length(self):
        return pygame.mixer.Sound(self.path_list[self.cur_idx]).get_length()




class Window:

    def __init__(self):

        
        # 图标图片
        launcher_img = pygame.image.load("./resources/image/icon.ico").convert_alpha()
        launcher_img = pygame.transform.smoothscale(launcher_img, (32, 32))

        # 背景图片
        self.bg_img = pygame.image.load("./resources/image/bg4.jpg").convert_alpha()
        self.bg_img = pygame.transform.smoothscale(self.bg_img, (screen_width, screen_height))

        # 音乐旋转图片
        self.music_img = pygame.image.load("resources/image/music.png").convert_alpha()
        self.music_img_rect = self.music_img.get_rect()
        self.music_img_rect.center = [200, 250]


        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        # 设置标题及图标
        pygame.display.set_caption("music player")
        pygame.display.set_icon(launcher_img)

        # 控制帧率
        self.clock = pygame.time.Clock()

        music_name_text_location = [100, 50]
        open_folder_text_location = [100, 10]
        play_mode_text_location = [10, 50]
        file_open_button_location = [10, 10]


    def drwa_text(content, location, color):
        font_size = 18
        font = pygame.font.SysFont('SimHei', font_size)
        text = font.render(content, True, color, Color.WHITE)
        rect = text.get_rect()
        rect.topleft = location
        while rect.right + 5 > screen_width:
            font_size -= 1
            font = pygame.font.SysFont('SimHei', font_size)
            text = font.render(content, True, color, Color.WHITE)
            rect = text.get_rect()
            rect.topleft = location
        return text, rect




