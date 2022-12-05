import sys
import pygame
from pygame.locals import *
import os
import random
import tkinter
from tkinter import filedialog


# 绘制上一首按钮
def draw_last_button(color):
    pygame.draw.line(screen, color, [140, 100], [120, 120], 4)
    pygame.draw.line(screen, color, [120, 120], [140, 140], 4)


# 绘制播放暂停按钮
def draw_play_or_pause_button(color, is_pause):
    if not is_pause:
        pygame.draw.line(screen, color, [190, 100], [190, 140], 4)
        pygame.draw.line(screen, color, [210, 100], [210, 140], 4)
    else:
        pygame.draw.lines(screen, color, True, [[190, 100], [190, 140], [210, 120]], 4)


# 绘制下一首按钮
def draw_next_button(color):
    pygame.draw.line(screen, color, [260, 100], [280, 120], 4)
    pygame.draw.line(screen, color, [280, 120], [260, 140], 4)


# 制作info按钮
def make_info_button(content, location, color):
    font_size = 18
    font = pygame.font.SysFont('SimHei', font_size)
    text = font.render(content, True, color, color_white)
    rect = text.get_rect()
    rect.topleft = location
    while rect.right + 5 > screen_width:
        font_size -= 1
        font = pygame.font.SysFont('SimHei', font_size)
        text = font.render(content, True, color, color_white)
        rect = text.get_rect()
        rect.topleft = location
    return text, rect


# 绘制info按钮
def draw_info_button(text, rect, line_color):
    screen.blit(text, rect)
    pygame.draw.lines(screen, line_color, True, [[rect.left - 5, rect.top - 5], [rect.right + 3, rect.top - 5],
                                                  [rect.right + 3, rect.bottom + 3], [rect.left - 5, rect.bottom + 3]],
                      2)


# 绘制进度条
def draw_play_bar(music_time, played_time):
    played_percent = played_time / 1000 / music_time
    pygame.draw.rect(screen, color_red, ((120, 160), (int(160 * played_percent), 10)))
    pygame.draw.rect(screen, color_white,
                     ((120 + 160 * played_percent + 1, 160), (int(160 * (1 - played_percent)), 10)))


# 搜集音乐
def collect_music(file_path):
    musics = []
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('mp3') or file.endswith('flac') or file.endswith('wav'):
                full_file = os.path.join(root, file)
                musics.append(full_file)
    if musics:
        return musics
    else:
        raise Exception("no music")


# 播放音乐
def play_music(musics, index):
    pygame.mixer.music.unload()
    pygame.mixer.music.load(musics[index])
    pygame.mixer.music.play()
    sound = pygame.mixer.Sound(musics[index])
    music_time = sound.get_length()
    return music_time


# 暂停音乐
def pause_music():
    pygame.mixer.music.pause()


# 继续播放
def unpause_music():
    pygame.mixer.music.unpause()


# 停止播放
def stop_music():
    pygame.mixer.music.stop()


# 获取下一个播放索引
def get_next_index(index, play_mode, numbers):
    if play_mode == sequence_play:
        new_index = index + 1
        if new_index > len(musics) - 1:
            new_index = 0
    elif play_mode == random_play:
        new_index = index
        while new_index == index:
            new_index = random.randint(0, numbers - 1)
    else:
        new_index = index
    return new_index


# 获取上一个播放索引
def get_last_index(index, play_mode, numbers):
    if play_mode == sequence_play:
        new_index = index - 1
        if new_index < 0:
            new_index = len(musics) - 1
    elif play_mode == random_play:
        new_index = index
        while new_index == index:
            new_index = random.randint(0, numbers - 1)
    else:
        new_index = index
    return new_index


# 获取音乐名
def get_music_name(musics, index):
    new_music_name = musics[index].split("\\")[-1]
    return new_music_name


# 颜色定义
color_red = (255, 0, 0)
color_green = (0, 255, 0)
color_blue = (0, 0, 255)
color_white = (255, 255, 255)
color_black = (0, 0, 0)

# 播放模式
sequence_play = "顺序播放"
loop_play = "循环播放"
random_play = "随机播放"

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 设置界面
screen_width = 400
screen_height = 320
screen = pygame.display.set_mode([screen_width, screen_height])

# 图标图片
launcher_img = pygame.image.load("resources/image/icon.ico").convert_alpha()
launcher_img = pygame.transform.smoothscale(launcher_img, (32, 32))

# 背景图片
bg_img = pygame.image.load("resources/image/bg4.jpg").convert_alpha()
bg_img = pygame.transform.smoothscale(bg_img, (screen_width, screen_height))

# 音乐旋转图片
music_img = pygame.image.load("resources/image/music.png").convert_alpha()
music_img_rect = music_img.get_rect()
music_img_rect.center = [200, 250]

# 设置标题及图标
pygame.display.set_caption("music player")
pygame.display.set_icon(launcher_img)

# 控制帧率
clock = pygame.time.Clock()

music_path = "./resources/music"
musics = collect_music(music_path)
music_is_pause = True
music_index = 0
music_name = "无音乐在播放"
music_numbers = len(musics)
sound = pygame.mixer.Sound(musics[music_index])
music_time = sound.get_length()
music_is_first_play = True
music_play_mode = sequence_play
music_info_location = [100, 50]
folder_info_location = [100, 10]
play_mode_button_location = [10, 50]
file_open_button_location = [10, 10]

play_mode_button_text, play_mode_button_rect = make_info_button(music_play_mode, play_mode_button_location, color_black)
file_open_button_text, file_open_button_rect = make_info_button("选取目录", file_open_button_location, color_black)
music_info_text, music_info_rect = make_info_button(music_name, music_info_location, color_black)
folder_info_text, folder_info_rect = make_info_button(music_path, folder_info_location, color_black)

tkinter.Tk().withdraw()
count = 0
file_button_color = color_green
mode_button_color = color_green
delta_time = 0

# 主循环
while True:
    clock.tick(30)
    screen.blit(bg_img, (0, 0))
    screen.blit(music_img, music_img_rect)
    count += 1
    if count >= 30 and pygame.mixer.music.get_busy() and not music_is_pause:
        music_img = pygame.transform.rotate(music_img, 90)
        count = 0
    draw_last_button(color_red)
    draw_play_or_pause_button(color_red, music_is_pause)
    draw_next_button(color_red)
    draw_info_button(play_mode_button_text, play_mode_button_rect, mode_button_color)
    draw_info_button(music_info_text, music_info_rect, color_green)
    draw_info_button(file_open_button_text, file_open_button_rect, file_button_color)
    draw_info_button(folder_info_text, folder_info_rect, color_green)
    played_time = pygame.mixer.music.get_pos() + delta_time * 1000
    draw_play_bar(music_time, played_time)

    # 播放完自动播放下一首
    if not pygame.mixer.music.get_busy() and not music_is_first_play:
        music_index = get_next_index(music_index, music_play_mode, music_numbers)
        music_time = play_music(musics, music_index)
        music_is_pause = False
        music_name = get_music_name(musics, music_index)
        music_info_text, music_info_rect = make_info_button(music_name, music_info_location, color_black)
        delta_time = 0

    pygame.display.update()
    # 检测事件
    for event in pygame.event.get():
        # 退出
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            if 120 <= event.pos[0] <= 280 and 160 <= event.pos[1] <= 170:
                if pygame.mixer.music.get_busy():
                    delta_time = ((event.pos[0] - 120) / 160) * music_time
                    pygame.mixer.music.play(start=delta_time)
                    music_is_pause = False

            # 播放暂停
            elif 190 <= event.pos[0] <= 210 and 100 <= event.pos[1] <= 140:
                print("pause")
                if not pygame.mixer.music.get_busy():
                    music_time = play_music(musics, music_index)
                    music_is_pause = False
                elif pygame.mixer.music.get_busy() and music_is_pause:
                    unpause_music()
                    music_is_pause = False
                elif pygame.mixer.music.get_busy() and not music_is_pause:
                    pause_music()
                    music_is_pause = True
                music_is_first_play = False

                music_name = get_music_name(musics, music_index)
                music_info_text, music_info_rect = make_info_button(music_name, music_info_location, color_black)

            # 上一首
            elif 120 <= event.pos[0] <= 140 and 100 <= event.pos[1] <= 140:
                music_index = get_last_index(music_index, music_play_mode, music_numbers)
                music_time = play_music(musics, music_index)
                music_is_pause = False
                music_is_first_play = False
                music_name = get_music_name(musics, music_index)
                music_info_text, music_info_rect = make_info_button(music_name, music_info_location, color_black)
                delta_time = 0

            # 下一首
            elif 260 <= event.pos[0] <= 280 and 100 <= event.pos[1] <= 140:
                music_index = get_next_index(music_index, music_play_mode, music_numbers)
                music_time = play_music(musics, music_index)
                music_is_pause = False
                music_is_first_play = False
                music_name = get_music_name(musics, music_index)
                music_info_text, music_info_rect = make_info_button(music_name, music_info_location, color_black)
                delta_time = 0

            # 播放模式切换
            elif play_mode_button_rect.left <= event.pos[0] <= play_mode_button_rect.right \
                    and play_mode_button_rect.top <= event.pos[1] <= play_mode_button_rect.bottom:
                mode_button_color = color_red
                if music_play_mode == sequence_play:
                    music_play_mode = random_play
                elif music_play_mode == random_play:
                    music_play_mode = loop_play
                elif music_play_mode == loop_play:
                    music_play_mode = sequence_play
                play_mode_button_text, play_mode_button_rect = make_info_button(music_play_mode,
                                                                                play_mode_button_location, color_black)

            # 选取目录
            elif file_open_button_rect.left <= event.pos[0] <= file_open_button_rect.right \
                    and file_open_button_rect.top <= event.pos[1] <= file_open_button_rect.bottom:
                file_button_color = color_red

        if event.type == MOUSEBUTTONUP:
            # 播放模式切换
            if play_mode_button_rect.left <= event.pos[0] <= play_mode_button_rect.right \
                    and play_mode_button_rect.top <= event.pos[1] <= play_mode_button_rect.bottom:
                mode_button_color = color_green

            # 选取目录
            elif file_open_button_rect.left <= event.pos[0] <= file_open_button_rect.right \
                    and file_open_button_rect.top <= event.pos[1] <= file_open_button_rect.bottom:
                file_button_color = color_green
                file_path = filedialog.askdirectory(title="选择音乐文件夹")  # 选择目录，返回目录名
                if file_path != "":
                    try:
                        musics = collect_music(file_path)
                        music_numbers = len(musics)
                        music_path = file_path
                        stop_music()
                        music_name = "无音乐在播放"
                        music_info_text, music_info_rect = make_info_button(music_name, music_info_location,
                                                                            color_black)
                        folder_info_text, folder_info_rect = make_info_button(music_path, folder_info_location,
                                                                              color_black)
                        music_is_first_play = True
                        music_is_pause = True
                        delta_time = 0
                    except:
                        pass
