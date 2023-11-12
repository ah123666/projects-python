import pygame
from pygame.locals import *
from sys import exit
import random
import codecs
import math

# 设置屏幕大小
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 设置游戏界面大小
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 设置游戏标题图标
ic_launcher = pygame.image.load("resources/image/ic_launcher.jpeg").convert_alpha()

# 背景图
back_ground = pygame.image.load("resources/image/background.jpg").convert_alpha()

# 结束背景图
game_over = pygame.image.load("resources/image/gameover.png").convert_alpha()

# 子弹图片
player_bullet_img = pygame.image.load("resources/image/bullet.png").convert_alpha()
enemy_bullet_img = pygame.image.load("resources/image/enemy_bullet.png").convert_alpha()

# 飞机图片
player_img1 = pygame.image.load("resources/image/player1.png").convert_alpha()
player_img2 = pygame.image.load("resources/image/player2.png").convert_alpha()
player_img3 = pygame.image.load("resources/image/player_off1.png").convert_alpha()
player_img4 = pygame.image.load("resources/image/player_off2.png").convert_alpha()
player_img5 = pygame.image.load("resources/image/player_off3.png").convert_alpha()

# 敌机图片
enemy_img1 = pygame.image.load("resources/image/enemy1.png").convert_alpha()
enemy_img2 = pygame.image.load("resources/image/enemy2.png").convert_alpha()
enemy_img3 = pygame.image.load("resources/image/enemy3.png").convert_alpha()
enemy_img4 = pygame.image.load("resources/image/enemy4.png").convert_alpha()

pause_image = pygame.image.load("resources/image/pause.png").convert_alpha()
unpause_image = pygame.image.load("resources/image/play.png").convert_alpha()

pause_rect = pause_image.get_rect()
pause_rect.topright = [SCREEN_WIDTH-10, 10]

# 背景音乐
bg_music = "resources/music/bg_music.wav"
pygame.mixer.music.load(bg_music)
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
# music = pygame.mixer.Sound(bg_music)
# music.set_volume(0.2)
# music.play(-1)

# 射击及爆炸音效
shoot_sound = "resources/music/shoot.wav"
boom_sound = "resources/music/enemy_boom.wav"
shoot_sound = pygame.mixer.Sound(shoot_sound)
shoot_sound.set_volume(0.1)
boom_sound = pygame.mixer.Sound(boom_sound)
boom_sound.set_volume(0.5)

# 设置游戏标题及图标
pygame.display.set_caption("彩图飞机大战")
pygame.display.set_icon(ic_launcher)

# 玩家飞机不同状态的图片列表，多张图片展示为动画效果
player_imgs = []
# 玩家飞机飞行图片
player_imgs.append(player_img1)
player_imgs.append(player_img2)
# 玩家飞机爆炸图片
player_imgs.append(player_img3)
player_imgs.append(player_img4)
player_imgs.append(player_img4)
player_imgs.append(player_img5)
player_imgs.append(player_img5)
player_imgs.append(player_img5)
player_rect = player_img1.get_rect()
player_pos = [0.5 * SCREEN_WIDTH, SCREEN_HEIGHT]  # 玩家飞机初始位置

# 敌机不同状态的图片列表，多张图片展示为动画效果
# 正常飞行图片
enemy_img = enemy_img1
enemy_rect = enemy_img.get_rect()
# 爆炸图片
enemy_down_imgs = [enemy_img1, enemy_img2, enemy_img3, enemy_img4]

# 子弹种类
player_main_bullet = 0
player_side_bullet = 1
enemy_main_bullet = 2
enemy_random_bullet = 3

score_path = "resources/score.txt"


class Bullet(pygame.sprite.Sprite):
    """
    子弹类
    """

    def __init__(self, bullet_img, init_pos, speed, bullet_type):
        super(Bullet, self).__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.type = bullet_type

        if self.type == player_main_bullet or self.type == player_side_bullet:
            self.rect.midbottom = init_pos

        if self.type == enemy_main_bullet:
            self.rect.midtop = init_pos

        if self.type == enemy_random_bullet:
            self.rect.midtop = init_pos
            self.angle = random.randint(-90, 90)
            self.image = pygame.transform.rotate(self.image, self.angle)

        self.speed = speed

    def move_up(self):
        self.rect.bottom -= self.speed

    def move_down(self):
        self.rect.top += self.speed

    def move_random(self):
        self.rect.centerx += self.speed * math.sin(math.radians(self.angle))
        self.rect.centery += self.speed * math.cos(math.radians(self.angle))


class Player(pygame.sprite.Sprite):
    """
    玩家类
    """

    def __init__(self, player_imgs, init_pos, speed, shoot_frequency):
        super(Player, self).__init__()
        # 存储玩家飞机图片的列表
        self.image = player_imgs
        self.rect = self.image[0].get_rect()
        self.rect.midbottom = init_pos
        self.speed = speed
        self.bullets = pygame.sprite.Group()
        self.img_index = 0
        self.is_hit = False
        self.down_index = 32
        self.shoot_index = 0
        self.shoot_frequency = shoot_frequency
        self.score = 0

    # 发射子弹
    def shoot(self, bullet_img, init_pos, bullet_speed, bullet_type):
        bullet = Bullet(bullet_img, init_pos, bullet_speed, bullet_type)
        self.bullets.add(bullet)

    # 向上移动，需判断边界
    def moveUp(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        else:
            self.rect.top -= self.speed

    def moveDown(self):
        if self.rect.top >= SCREEN_HEIGHT - self.rect.height:
            self.rect.top = SCREEN_HEIGHT - self.rect.height
        else:
            self.rect.top += self.speed

    def moveLeft(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        else:
            self.rect.left -= self.speed

    def moveRight(self):
        if self.rect.left >= SCREEN_WIDTH - self.rect.width:
            self.rect.left = SCREEN_WIDTH - self.rect.width
        else:
            self.rect.left += self.speed


class Enemy(pygame.sprite.Sprite):
    """
    敌机类
    """

    def __init__(self, enemy_img, enemy_down_imgs, init_pos, speed, shoot_frequency):
        super(Enemy, self).__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.midtop = init_pos
        self.down_imgs = enemy_down_imgs
        self.speed = speed
        self.bullets = pygame.sprite.Group()
        self.down_index = 0
        self.shoot_index = 0
        self.shoot_frequency = shoot_frequency

    # 发射子弹
    def shoot(self, bullet_img, init_pos, bullet_speed, bullet_type):
        bullet = Bullet(bullet_img, init_pos, bullet_speed, bullet_type)
        self.bullets.add(bullet)

    def move(self):
        self.rect.top += self.speed


def start_game():
    """
    开始游戏
    """
    # 参数设置
    player_speed = 8
    player_shoot_frequency = 8
    player_bullet_speed = 8

    enemy_generate_index = 0
    enemy_generate_frequency = 50

    enemy_speed = 1
    enemy_shoot_frequency = 45
    enemy_bullet_speed = 4

    # 游戏循环帧率设置
    clock = pygame.time.Clock()

    # 判断游戏循环退出参数
    running = True

    # 背景音乐暂停及玩家移动标志
    music_pause = False
    can_move = True

    # 初始化玩家飞机
    player = Player(player_imgs, player_pos, player_speed, player_shoot_frequency)  # 建立玩家对象

    # 存储敌机
    enemies = pygame.sprite.Group()

    # 存储被击毁的飞机，用来渲染击毁动画
    enemies_down = pygame.sprite.Group()

    # 游戏暂停标志
    game_pause = False

    """
    游戏主循环
    """
    while running:
        if game_pause:
            font = pygame.font.Font(None, 48)
            text = font.render("Press P Continue!", True, (255, 0, 0))
            text_rect = text.get_rect()
            text_rect.centerx = screen.get_rect().centerx
            text_rect.centery = screen.get_rect().centery + 24
            screen.blit(text, text_rect)

            pygame.display.update()
            # pygame.mixer.pause()
            pygame.mixer.music.pause()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == KEYDOWN:
                    if event.key == K_p:
                        game_pause = not game_pause
                        # pygame.mixer.unpause()
                        pygame.mixer.music.unpause()
            continue

        # 控制游戏最大帧率为60
        clock.tick(60)

        # 绘制背景
        screen.fill(0)
        screen.blit(back_ground, (0, 0))

        # 背景音乐播放控制
        if not music_pause:
            screen.blit(unpause_image, pause_rect)
            # pygame.mixer.unpause()
            pygame.mixer.music.unpause()
        else:
            screen.blit(pause_image, pause_rect)
            # pygame.mixer.pause()
            pygame.mixer.music.pause()

        """
        玩家处理
        """
        # 判断玩家飞机是否被击中
        if not player.is_hit:
            # 更换图片索引，使飞机有动画效果
            # 结果为0或1，显示前两张飞机图片，显示飞机飞行动画
            player.img_index = player.shoot_index // (
                (player.shoot_frequency + 1) // 2)
            screen.blit(player.image[player.img_index], player.rect)

            # 根据频率发射子弹
            player.shoot_index += 1
            if player.shoot_index == player.shoot_frequency:
                player.shoot(player_bullet_img, player.rect.midtop, player_bullet_speed, player_main_bullet)
                # player.shoot(enemy_bullet_img, (player.rect.midtop[0]-40, player.rect.midtop[1]+40), player_bullet_speed+5, player_side_bullet)
                # player.shoot(enemy_bullet_img, (player.rect.midtop[0]+40, player.rect.midtop[1]+40), player_bullet_speed+5, player_side_bullet)
                # player.shoot(enemy_bullet_img, (player.rect.midtop[0]-25, player.rect.midtop[1]+25), player_bullet_speed+3, player_side_bullet)
                # player.shoot(enemy_bullet_img, (player.rect.midtop[0]+25, player.rect.midtop[1]+25), player_bullet_speed+3, player_side_bullet)
                shoot_sound.play()
                player.shoot_index = 0
        else:
            # 玩机飞机被击中后的处理效果
            player.img_index = player.down_index // 16  # 结果为2到7，显示第3张到第8张飞机图片，显示飞机爆炸动画
            screen.blit(player.image[player.img_index], player.rect)
            player.down_index += 1

            if player.down_index > 112:
                # 击中效果处理完后游戏结束
                running = False

        for bullet in player.bullets:
            # 以固定速度移动子弹
            bullet.move_up()
            # 移动出屏幕后删除子弹
            if bullet.rect.bottom < 0:
                player.bullets.remove(bullet)
        # 显示子弹
        player.bullets.draw(screen)

        """
          敌机处理
        """
        # 根据频率生成敌机
        enemy_generate_index += 1
        if enemy_generate_index == enemy_generate_frequency:
            enemy_pos = [random.randint(
                0.5 * player_rect.width, SCREEN_WIDTH - 0.5 * player_rect.width), 0]
            enemy = Enemy(enemy_img, enemy_down_imgs, enemy_pos,
                          enemy_speed, enemy_shoot_frequency)
            enemy.shoot(enemy_bullet_img, enemy.rect.midbottom, enemy_bullet_speed, enemy_main_bullet)
            enemy.shoot(enemy_bullet_img, enemy.rect.midbottom, enemy_bullet_speed, enemy_random_bullet)
            enemies.add(enemy)
            enemy_generate_index = 0

        for enemy in enemies:
            # 移动敌机
            enemy.move()

            # 敌机根据频率发射子弹
            enemy.shoot_index += 1
            if enemy.shoot_index == enemy.shoot_frequency:
                enemy.shoot(enemy_bullet_img, enemy.rect.midbottom, enemy_bullet_speed, enemy_main_bullet)
                enemy.shoot(enemy_bullet_img, enemy.rect.midbottom, enemy_bullet_speed, enemy_random_bullet)
                enemy.shoot_index = 0

            for enemy_bullet in enemy.bullets:
                # 移动敌机子弹
                if enemy_bullet.type == enemy_main_bullet:
                    enemy_bullet.move_down()

                if enemy_bullet.type == enemy_random_bullet:
                    enemy_bullet.move_random()

                # 敌机子弹与玩家飞机碰撞检测
                if pygame.sprite.collide_rect(enemy_bullet, player):
                    boom_sound.play()
                    enemy.bullets.remove(enemy_bullet)
                    player.is_hit = True
                    can_move = False
                    break

                # 移动出屏幕后删除子弹
                if not 0 < enemy_bullet.rect.centerx < SCREEN_WIDTH and 0 < enemy_bullet.rect.centery < SCREEN_HEIGHT:
                    enemy.bullets.remove(enemy_bullet)

            # print("敌机子弹数：", len(enemy.bullets))   
            # 敌机子弹与玩家子弹碰撞检测，子弹碰撞互相消失
            pygame.sprite.groupcollide(
                enemy.bullets, player.bullets, True, True)

            # 显示敌机子弹
            enemy.bullets.draw(screen)

            # 敌机与玩家飞机碰撞检测
            if pygame.sprite.collide_rect(enemy, player):
                enemies_down.add(enemy)  # enemies_down是炸毁的敌机
                boom_sound.play()
                enemies.remove(enemy)
                player.is_hit = True
                can_move = False
                break
            # 移出屏幕后删除飞机
            if enemy.rect.top > SCREEN_HEIGHT:
                enemies.remove(enemy)
        # print("敌机数：", len(enemies))
        # print("玩家子弹数：", len(player.bullets))
        # 方法groupcollide()是检测两个精灵组中精灵们的矩形冲突
        result = pygame.sprite.groupcollide(
            enemies, player.bullets, True, True)  # enemies1_down是被玩家飞机子弹击中的敌机
        # 统计碰撞敌机，遍历字典key值
        for enemy_down in result:
            # 添加销毁的敌机到列表
            enemies_down.add(enemy_down)  # 将击中的敌机添加到炸毁敌机中
            boom_sound.play()

        # 敌机被子弹击中的效果展示
        for enemy_down in enemies_down:
            # 结果为0到3，显示4张敌机照片，显示敌机爆炸动画
            screen.blit(
                enemy_down.down_imgs[enemy_down.down_index // 2], enemy_down.rect)

            enemy_down.down_index += 1
            if enemy_down.down_index > 7:
                enemies_down.remove(enemy_down)
                player.score += 100

        # 显示敌机
        enemies.draw(screen)

        # 绘制当前得分
        score_font = pygame.font.Font(None, 36)
        score_text = score_font.render(str(player.score), True, (225, 0, 0))
        text_rect = score_text.get_rect()
        text_rect.topleft = [10, 10]
        screen.blit(score_text, text_rect)

        # 更新屏幕
        pygame.display.update()

        # 处理游戏退出
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == MOUSEBUTTONDOWN:
                if pause_rect.left <= event.pos[0] <= pause_rect.right \
                        and pause_rect.top <= event.pos[1] <= pause_rect.bottom:
                    music_pause = not music_pause
            if event.type == KEYDOWN:
                if event.key == K_p:
                    game_pause = not game_pause

        # 获取键盘事件
        key_pressed = pygame.key.get_pressed()
        # 处理键盘事件
        if can_move:
            if key_pressed[K_w] or key_pressed[K_UP]:
                player.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                player.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                player.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                player.moveRight()

    # 绘制游戏结束背景
    screen.blit(game_over, (0, 0))
    # 游戏 Game Over 后显示最终得分
    font = pygame.font.Font(None, 48)
    text = font.render('Score: ' + str(player.score), True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery + 24
    screen.blit(text, text_rect)

    # 使用系统字体
    xtfont = pygame.font.SysFont('SimHei', 30)
    # 重新开始按钮
    textstart = xtfont.render('重新开始 ', True, (255, 255, 255))
    text_rect = textstart.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery + 120
    screen.blit(textstart, text_rect)
    # 排行榜按钮
    textstart = xtfont.render('排行榜 ', True, (255, 255, 255))
    text_rect = textstart.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery + 180
    screen.blit(textstart, text_rect)

    # 判断得分更新排行榜
    # 临时的变量在到排行榜的时候使用
    j = 0

    # 获取文件中内容转换成列表使用mr分割开内容
    arrayscore = read_txt(score_path)[0].split('mr')

    # 循环分数列表在列表里排序
    for i in range(0, len(arrayscore)):
        # 判断当前获得的分数是否大于排行榜上的分数
        if player.score > int(arrayscore[i]):
            # 大于排行榜上的内容 把分数和当前分数进行替换
            j = arrayscore[i]
            arrayscore[i] = str(player.score)
            player.score = 0
        # 替换下来的分数下移动一位
        if int(j) > int(arrayscore[i]):
            k = arrayscore[i]
            arrayscore[i] = str(j)
            j = k

    #  循环分数列表 写入文档
    for i in range(0, len(arrayscore)):
        # 判断列表中第一个分数
        if i == 0:
            # 覆盖写入内容追加mr方便分割内容
            write_txt(arrayscore[i] + 'mr', 'w', score_path)
        else:
            # 判断是否为最后一个分数
            if i == 9:
                # 最近添加内容最后一个分数不添加mr
                write_txt(arrayscore[i], 'a', score_path)
            else:
                # 不是最后一个分数，添加的时候添加mr
                write_txt(arrayscore[i] + 'mr', 'a', score_path)


def write_txt(content, strim, path):
    """ 
    对文件的操作
    写入文本:
    传入参数为content，strim，path；content为需要写入的内容，数据类型为字符串。
    path为写入的位置，数据类型为字符串。strim写入方式
    传入的path需如下定义：path= r’ D:\text.txt’
    f = codecs.open(path, strim, 'utf8')中，codecs为包，需要用import引入。
    strim=’a’表示追加写入txt，可以换成’w’，表示覆盖写入。
    'utf8'表述写入的编码，可以换成'utf16'等。
    """
    f = codecs.open(path, strim, 'utf8')
    f.write(str(content))
    f.close()


def read_txt(path):
    """
    读取txt：
    表示按行读取txt文件,utf8表 示读取编码为utf8的文件，可以根据需求改成utf16，或者GBK等。
    返回的为数组，每一个数组的元素代表一行，
    若想返回字符串格式，可以将改写成return ‘\n’.join(lines)
    """
    with open(path, 'r', encoding='utf8') as f:
        lines = f.readlines()
    return lines


# 排行榜
def gameRanking():
    screen2 = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # 绘制背景
    screen2.fill(0)
    screen2.blit(back_ground, (0, 0))
    # 使用系统字体
    xtfont = pygame.font.SysFont('SimHei', 30)

    # 排行榜按钮
    textstart = xtfont.render('排行榜', True, (255, 0, 0))
    text_rect = textstart.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = 50
    screen.blit(textstart, text_rect)

    # 重新开始按钮
    textstart = xtfont.render('重新开始', True, (255, 0, 0))
    text_rect = textstart.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery + 120
    screen2.blit(textstart, text_rect)

    # 获取排行文档内容
    arrayscore = read_txt(score_path)[0].split('mr')
    # 循环排行榜文件显示排行
    for i in range(0, len(arrayscore)):
        # 游戏 Game Over 后显示最终得分
        font = pygame.font.Font(None, 48)
        # 排名重1到10
        k = i + 1
        text = font.render(str(k) + "  " + arrayscore[i], True, (255, 0, 0))
        text_rect = text.get_rect()
        text_rect.centerx = screen2.get_rect().centerx
        text_rect.centery = 80 + 30 * k
        # 绘制分数内容
        screen2.blit(text, text_rect)


def main_game():
    start_game()
    # 判断点击位置以及处理游戏推出
    while True:
        for event in pygame.event.get():
            # 关闭页面游戏退出
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # 鼠标单击
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 判断鼠标单击的位置是否为开始按钮位置范围内
                if screen.get_rect().centerx - 70 <= event.pos[0] <= screen.get_rect().centerx + 50 \
                        and screen.get_rect().centery + 100 <= event.pos[1] <= screen.get_rect().centery + 140:
                    # 重新开始游戏
                    main_game()
                # 判断鼠标是否单击排行榜按钮
                if screen.get_rect().centerx - 70 <= event.pos[0] <= screen.get_rect().centerx + 50 \
                        and screen.get_rect().centery + 160 <= event.pos[1] <= screen.get_rect().centery + 200:
                    # 显示排行榜
                    gameRanking()
        # 更新界面
        pygame.display.update()


if __name__ == '__main__':
    main_game()
