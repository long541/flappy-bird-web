#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('pip install pygame')


# In[3]:


import pygame
import random
import os
import json
import sys
import math

# ========== 全局变量初始化 ==========
global WIDTH, HEIGHT, screen, current_skin_idx, SKINS, SKIN_LIST
global bgm_volume, sfx_volume, volume_slider_dragging
WIDTH, HEIGHT = 600, 800
current_skin_idx = 0
bgm_volume = 0.5
sfx_volume = 0.8
volume_slider_dragging = {"bgm": False, "sfx": False}
panel_alpha = 255
panel_scale = 1.0
preview_bird_y_offset = 0
preview_bird_phase = 0

# 初始化pygame
#os.environ['SDL_VIDEODRIVER'] = 'windib'
pygame.init()
pygame.font.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SHOWN)
pygame.display.set_caption("飞扬小鸟 - 25分解锁皮肤版")
pygame.display.flip()

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
LIGHT_GRAY = (245, 245, 245)
DARK_GRAY = (150, 150, 150)
GREEN = (46, 204, 113)
BROWN = (142, 68, 173)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
LIGHT_BLUE = (240, 248, 255)
YELLOW = (241, 196, 15)
PURPLE = (155, 89, 182)
GOLD = (241, 196, 15)
SILVER = (189, 195, 199)
BRONZE = (205, 127, 50)

# 场景配色
SCENES = {
    "day": {"bg": (189, 236, 253), "pipe": (46, 204, 113), "pipe_detail": (39, 174, 96)},
    "dusk": {"bg": (255, 179, 186), "pipe": (51, 110, 123), "pipe_detail": (33, 67, 75)},
    "starry": {"bg": (17, 17, 34), "pipe": (102, 51, 153), "pipe_detail": (76, 39, 117)},
    "space": {"bg": (0, 0, 15), "pipe": (255, 105, 180), "pipe_detail": (219, 112, 147)}
}

# ========== 皮肤系统配置（25分一段解锁） ==========
SKINS = {
    "classic": {"name": "经典黑鸟", "color": BLACK, "unlock_score": 0, "trail": BLACK, "unlocked": True},
    "rainbow": {"name": "彩虹鸟", "color": (255,0,0), "unlock_score": 25, "trail": (255,105,180), "unlocked": False},
    "machine": {"name": "机械鸟", "color": (100,149,237), "unlock_score": 50, "trail": (100,149,237), "unlocked": False},
    "star": {"name": "星空鸟", "color": (138,43,226), "unlock_score": 75, "trail": (255,255,153), "unlocked": False}
}
SKIN_LIST = list(SKINS.keys())
SKIN_DATA_FILE = "skin_unlock_data.json"

# 解锁皮肤祝福语库
BLESSINGS = [
    "欧气爆棚！新皮肤到手～",
    "太牛啦！解锁专属炫彩皮肤！",
    "颜值加分！这皮肤也太酷了吧！",
    "上分利器！新皮肤助你冲高分！",
    "运气爆棚！解锁隐藏款皮肤！",
    "手感升级！快用新皮肤秀一波！"
]

# 存档路径
SCORE_FILES = {
    "classic_high": "classic_high.txt",
    "entertain_high": "entertain_high.txt",
    "classic_achieve": "classic_achieve.txt",
    "entertain_achieve": "entertain_achieve.txt"
}

# ========== 字体加载 ==========
try:
    title_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 72)
    btn_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 36)
    small_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 26)
    tiny_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 18)
    mini_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 16)
except:
    title_font = pygame.font.SysFont(["SimHei", "Microsoft YaHei"], 72, bold=True)
    btn_font = pygame.font.SysFont(["SimHei", "Microsoft YaHei"], 36, bold=True)
    small_font = pygame.font.SysFont(["SimHei", "Microsoft YaHei"], 26)
    tiny_font = pygame.font.SysFont(["SimHei", "Microsoft YaHei"], 18)
    mini_font = pygame.font.SysFont(["SimHei", "Microsoft YaHei"], 16)

# ========== 音频加载 ==========
AUDIO_FILES = {
    "bgm": "bgm.mp3",
    "jump": "jump.mp3",
    "hit": "hit.wav",
    "score": "score.wav",
    "item": "item.mp3"
}
sound_cache = {}

def load_audio():
    global bgm_volume, sfx_volume
    for name, file in AUDIO_FILES.items():
        if os.path.isfile(file):
            try:
                if name == "bgm":
                    pygame.mixer.music.load(file)
                    pygame.mixer.music.set_volume(bgm_volume)
                else:
                    snd = pygame.mixer.Sound(file)
                    snd.set_volume(sfx_volume)
                    sound_cache[name] = snd
            except Exception as e:
                print(f"⚠️ 音频{file}加载失败：{e}")
        else:
            print(f"⚠️ 音频文件{file}缺失")

def force_play_bgm():
    if os.path.exists("bgm.mp3"):
        try:
            pygame.mixer.music.play(-1)
            return True
        except:
            return False
    return False

def update_volume():
    global bgm_volume, sfx_volume
    pygame.mixer.music.set_volume(bgm_volume)
    for snd in sound_cache.values():
        snd.set_volume(sfx_volume)

load_audio()

# ========== 皮肤存档/加载函数 ==========
def load_skin_data():
    global SKINS, current_skin_idx, SKIN_LIST
    if os.path.exists(SKIN_DATA_FILE):
        with open(SKIN_DATA_FILE, "r") as f:
            data = json.load(f)
            for skin_id in SKINS:
                if skin_id in data:
                    SKINS[skin_id]["unlocked"] = data[skin_id]["unlocked"]
    while not SKINS[SKIN_LIST[current_skin_idx]]["unlocked"]:
        current_skin_idx = (current_skin_idx + 1) % len(SKIN_LIST)

def save_skin_data():
    global SKINS
    data = {skin_id: {"unlocked": SKINS[skin_id]["unlocked"]} for skin_id in SKINS}
    with open(SKIN_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def check_skin_unlock(total_score):
    global SKINS
    unlocked = False
    for skin_id in SKINS:
        if not SKINS[skin_id]["unlocked"] and total_score >= SKINS[skin_id]["unlock_score"]:
            SKINS[skin_id]["unlocked"] = True
            unlocked = True
    if unlocked:
        save_skin_data()
    return unlocked

# ========== 游戏对象类 ==========
class Star:
    def __init__(self, scene):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.randint(1, 3) if scene == "starry" else random.randint(2, 5)
        self.color = WHITE if scene == "starry" else (random.randint(100, 255), random.randint(100, 255), 255)
    def update(self):
        self.x -= self.speed
        if self.x < -self.size:
            self.x = WIDTH + self.size
            self.y = random.randint(0, HEIGHT)
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

class ScorePopup:
    def __init__(self, x, y, score, color=BLACK):
        self.x = x
        self.y = y
        self.score = score
        self.color = color
        self.alpha = 255
        self.font = pygame.font.Font(None, 32)
    def update(self):
        self.y -= 1.5
        self.alpha -= 4
        if self.alpha < 0:
            self.alpha = 0
    def draw(self):
        text = self.font.render(f"+{self.score}", True, self.color)
        text.set_alpha(self.alpha)
        screen.blit(text, (self.x - text.get_width()//2, self.y))
    def is_finished(self):
        return self.alpha <= 0

class Bird:
    def __init__(self):
        self.x = 80
        self.y = HEIGHT // 2
        self.size = 30
        self.vel = 0
        self.gravity = 0.5
        self.jump_force = -12
        self.invincible = False
        self.inv_time = 0
        self.double_score = False
        self.double_time = 0
        self.life = 2
        self.trail = []
    def update(self, mode):
        if self.invincible:
            self.inv_time -= 1
            if self.inv_time <= 0:
                self.invincible = False
        if mode == "entertain" and self.double_score:
            self.double_time -= 1
            if self.double_time <= 0:
                self.double_score = False
        self.vel += self.gravity
        self.y += self.vel
        current_skin = SKINS[SKIN_LIST[current_skin_idx]]
        self.trail.append((self.x, self.y, current_skin["trail"]))
        if len(self.trail) > 10:
            self.trail.pop(0)
    def jump(self):
        self.vel = self.jump_force
        if "jump" in sound_cache:
            sound_cache["jump"].play()
    def draw(self, mode, current_scene, y_offset=0):
        current_skin = SKINS[SKIN_LIST[current_skin_idx]]
        color = current_skin["color"]
        if self.invincible:
            color = YELLOW
        elif mode == "entertain" and self.double_score:
            color = PURPLE
        if current_scene == "space" and SKIN_LIST[current_skin_idx] == "star":
            color = (random.randint(150, 255), random.randint(100, 255), 255)
        for i, (tx, ty, tcolor) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*tcolor, alpha), (self.size, self.size), self.size//2)
            screen.blit(surf, (tx - self.size//2, ty - self.size//2 + y_offset))
        pygame.draw.circle(screen, color, (self.x, self.y + y_offset), self.size)
        pygame.draw.circle(screen, WHITE, (self.x, self.y + y_offset), self.size, 3)
        pygame.draw.circle(screen, WHITE, (self.x + 15, self.y - 12 + y_offset), 8)
        pygame.draw.circle(screen, BLACK, (self.x + 18, self.y - 12 + y_offset), 4)
        pygame.draw.polygon(screen, (255, 165, 0), [(self.x+20, self.y-3 + y_offset), (self.x+35, self.y + y_offset), (self.x+20, self.y+3 + y_offset)])

class Pipe:
    def __init__(self, speed=3, current_scene="day"):
        self.x = WIDTH
        self.width = 70
        self.gap = 220
        self.top_h = random.randint(100, HEIGHT - self.gap - 100)
        self.bottom_y = self.top_h + self.gap
        self.speed = speed
        self.scored = False
        self.extra_scored = False
        self.scene = current_scene
    def update(self, new_scene):
        self.x -= self.speed
        self.scene = new_scene
    def draw(self):
        pipe_color = SCENES[self.scene]["pipe"]
        detail_color = SCENES[self.scene]["pipe_detail"]
        pygame.draw.rect(screen, pipe_color, (self.x, 0, self.width, self.top_h))
        pygame.draw.rect(screen, detail_color, (self.x+8, 0, self.width-16, self.top_h))
        pygame.draw.rect(screen, pipe_color, (self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y))
        pygame.draw.rect(screen, detail_color, (self.x+8, self.bottom_y, self.width-16, HEIGHT - self.bottom_y))
        pygame.draw.rect(screen, BROWN, (self.x-8, self.top_h-35, self.width+16, 35))
        pygame.draw.rect(screen, BROWN, (self.x-8, self.bottom_y, self.width+16, 35))
    def off_screen(self):
        return self.x < -self.width

class Item:
    def __init__(self, pipes, speed=3, mode="classic"):
        self.mode = mode
        self.types = ["invincible", "narrow", "slow"]
        if mode == "entertain":
            self.types += ["double", "life"]
        self.type = random.choice(self.types)
        self.size = 25
        self.speed = speed
        self.x, self.y = self._get_pos(pipes)
    def _get_pos(self, pipes):
        target = None
        for p in pipes:
            if WIDTH <= p.x <= WIDTH + 300:
                target = p
                break
        if not target:
            target = max(pipes, key=lambda x: x.x)
        y = target.top_h + target.gap // 2
        x = target.x + 150
        return x, y
    def get_color(self):
        colors = {"invincible": YELLOW, "narrow": RED, "slow": BLUE, "double": PURPLE, "life": GREEN}
        return colors[self.type]
    def draw(self):
        color = self.get_color()
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)
        pygame.draw.circle(screen, WHITE, (self.x-8, self.y-8), self.size//3)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.size, 3)
    def update(self):
        self.x -= self.speed
    def off_screen(self):
        return self.x < -self.size

class Button:
    def __init__(self, x, y, w, h, text, font=btn_font, color=BLACK, bg=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = color
        self.bg = bg
        self.hover = False
    def draw(self):
        pygame.draw.rect(screen, LIGHT_GRAY if self.hover else self.bg, self.rect, border_radius=15)
        pygame.draw.rect(screen, self.color, self.rect, 3, border_radius=15)
        text = self.font.render(self.text, True, self.color)
        screen.blit(text, (self.rect.x + (self.rect.w - text.get_width())//2, self.rect.y + (self.rect.h - text.get_height())//2))
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
    def click(self, pos):
        return self.rect.collidepoint(pos)

# ========== 面板绘制函数 ==========
def draw_rule_panel():
    rule_w = 520
    rule_h = 500
    rule_x = WIDTH // 2 - rule_w // 2
    rule_y = HEIGHT // 2 - rule_h // 2 - 30

    mask_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mask_surf.fill((0, 0, 0, 150))
    screen.blit(mask_surf, (0, 0))

    panel_surf = pygame.Surface((rule_w, rule_h), pygame.SRCALPHA)
    panel_surf.fill((240, 248, 255, 255))
    screen.blit(panel_surf, (rule_x, rule_y))
    pygame.draw.rect(screen, (200, 200, 200), (rule_x-5, rule_y-5, rule_w+10, rule_h+10), border_radius=25)
    pygame.draw.rect(screen, WHITE, (rule_x, rule_y, rule_w, rule_h), 5, border_radius=20)

    title_text = btn_font.render("📖 操作说明", True, (25, 118, 210))
    screen.blit(title_text, (rule_x + 20, rule_y + 20))
    pygame.draw.line(screen, (220, 220, 220), (rule_x + 20, rule_y + 70), (rule_x + rule_w - 20, rule_y + 70), 3)

    rules = [
        ("基础操作", (25, 118, 210), 22),
        ("空格键：小鸟跳跃", (51, 51, 51), 18),
        ("ESC键：暂停游戏", (51, 51, 51), 18),
        ("←→键：切换皮肤", (51, 51, 51), 18),
        ("M键：控制BGM播放/暂停", (51, 51, 51), 18),
        ("", (0,0,0), 18),
        ("游戏模式", (76, 175, 80), 22),
        ("经典模式：无道具无生命，碰撞即结束", (51, 51, 51), 18),
        ("娱乐模式：含5种道具，初始2条生命", (51, 51, 51), 18),
        ("", (0,0,0), 18),
        ("道具效果", (156, 39, 176), 22),
        ("黄球=无敌", (51, 51, 51), 18),
        ("红球=缩缝+1分", (51, 51, 51), 18),
        ("蓝球=减速", (51, 51, 51), 18),
        ("紫球=双倍得分", (51, 51, 51), 18),
        ("绿球=增加生命", (51, 51, 51), 18),
        ("", (0,0,0), 18),
        ("场景&皮肤", (255, 152, 0), 22),
        ("场景：0-49=白天 | 50-99=黄昏", (51, 51, 51), 18),
        ("场景：100-199=星空 | 200+=太空", (51, 51, 51), 18),
        ("皮肤：25分=彩虹鸟 | 50分=机械鸟 | 75分=星空鸟", (51, 51, 51), 18),
    ]

    y = rule_y + 80
    line_spacing = 28
    for text, color, font_size in rules:
        if text == "":
            y += line_spacing // 2
            continue
        rule_font = pygame.font.SysFont(["SimHei", "Microsoft YaHei"], font_size)
        rule_text = rule_font.render(text, True, color)
        screen.blit(rule_text, (rule_x + 30, y))
        y += line_spacing

    close_btn = pygame.Rect(rule_x + rule_w - 60, rule_y + 10, 40, 40)
    pygame.draw.circle(screen, RED, close_btn.center, 20)
    close_text = small_font.render("×", True, WHITE)
    screen.blit(close_text, (close_btn.x + 8, close_btn.y + 2))

    return close_btn

def draw_volume_panel():
    vol_w = 450
    vol_h = 280
    vol_x = WIDTH // 2 - vol_w // 2
    vol_y = HEIGHT // 2 - vol_h // 2 + 30
    slider_w = 220

    mask_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mask_surf.fill((0, 0, 0, 150))
    screen.blit(mask_surf, (0, 0))

    panel_surf = pygame.Surface((vol_w, vol_h), pygame.SRCALPHA)
    panel_surf.fill((245, 245, 247, 255))
    screen.blit(panel_surf, (vol_x, vol_y))
    pygame.draw.rect(screen, (200, 200, 200), (vol_x-5, vol_y-5, vol_w+10, vol_h+10), border_radius=25)
    pygame.draw.rect(screen, WHITE, (vol_x, vol_y, vol_w, vol_h), 5, border_radius=20)

    title_text = btn_font.render("🔊 音量调节", True, (25, 118, 210))
    screen.blit(title_text, (vol_x + 20, vol_y + 20))
    pygame.draw.line(screen, (220, 220, 220), (vol_x + 20, vol_y + 70), (vol_x + vol_w - 20, vol_y + 70), 3)

    # BGM滑块
    bgm_label = small_font.render("背景音乐", True, BLACK)
    screen.blit(bgm_label, (vol_x + 30, vol_y + 80))
    pygame.draw.rect(screen, DARK_GRAY, (vol_x + 150, vol_y + 85, slider_w, 18), border_radius=10)
    bgm_fill_width = int(slider_w * bgm_volume)
    pygame.draw.rect(screen, BLUE, (vol_x + 150, vol_y + 85, bgm_fill_width, 18), border_radius=10)
    bgm_slider_x = vol_x + 150 + bgm_fill_width - 10
    bgm_slider = pygame.Rect(bgm_slider_x, vol_y + 78, 25, 30)
    pygame.draw.rect(screen, WHITE, bgm_slider, border_radius=8)
    pygame.draw.rect(screen, BLUE, bgm_slider, 2, border_radius=8)
    bgm_percent = small_font.render(f"{int(bgm_volume*100)}%", True, BLUE)
    screen.blit(bgm_percent, (vol_x + 150 + slider_w + 20, vol_y + 80))

    # 音效滑块
    sfx_label = small_font.render("游戏音效", True, BLACK)
    screen.blit(sfx_label, (vol_x + 30, vol_y + 150))
    pygame.draw.rect(screen, DARK_GRAY, (vol_x + 150, vol_y + 155, slider_w, 18), border_radius=10)
    sfx_fill_width = int(slider_w * sfx_volume)
    pygame.draw.rect(screen, PURPLE, (vol_x + 150, vol_y + 155, sfx_fill_width, 18), border_radius=10)
    sfx_slider_x = vol_x + 150 + sfx_fill_width - 10
    sfx_slider = pygame.Rect(sfx_slider_x, vol_y + 148, 25, 30)
    pygame.draw.rect(screen, WHITE, sfx_slider, border_radius=8)
    pygame.draw.rect(screen, PURPLE, sfx_slider, 2, border_radius=8)
    sfx_percent = small_font.render(f"{int(sfx_volume*100)}%", True, PURPLE)
    screen.blit(sfx_percent, (vol_x + 150 + slider_w + 20, vol_y + 150))

    # 关闭按钮
    close_btn = pygame.Rect(vol_x + vol_w - 60, vol_y + 10, 40, 40)
    pygame.draw.circle(screen, RED, close_btn.center, 20)
    close_text = small_font.render("×", True, WHITE)
    screen.blit(close_text, (close_btn.x + 8, close_btn.y + 2))

    return {
        "bgm_slider": bgm_slider, 
        "sfx_slider": sfx_slider, 
        "close_btn": close_btn, 
        "slider_w": slider_w,
        "scaled_x": vol_x
    }

# ========== 皮肤解锁提示（彩色弹窗+随机祝福语） ==========
def draw_skin_unlock_popup(skin_name, skin_color):
    pop_w = 400
    pop_h = 250
    pop_x = WIDTH // 2 - pop_w // 2
    pop_y = HEIGHT // 2 - pop_h // 2
    
    # 彩色背景（和皮肤同色系）
    pygame.draw.rect(screen, skin_color, (pop_x-5, pop_y-5, pop_w+10, pop_h+10), border_radius=20)
    pygame.draw.rect(screen, WHITE, (pop_x, pop_y, pop_w, pop_h), border_radius=20)
    
    # 皮肤预览（画个小鸟）
    bird_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(bird_surf, skin_color, (40, 40), 30)
    pygame.draw.circle(bird_surf, BLACK, (55, 35), 5)
    screen.blit(bird_surf, (pop_x + 160, pop_y + 30))
    
    # 随机祝福语
    blessing = random.choice(BLESSINGS)
    bless_text = small_font.render(blessing, True, (255, 152, 0))
    screen.blit(bless_text, (pop_x + 50, pop_y + 120))
    
    # 皮肤名称
    skin_text = btn_font.render(f"{skin_name}", True, BLACK)
    screen.blit(skin_text, (pop_x + 120, pop_y + 170))
    
    # 关闭提示
    tip = tiny_font.render("按任意键关闭", True, DARK_GRAY)
    screen.blit(tip, (pop_x + 140, pop_y + 210))
    
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# ========== 工具函数 ==========
def load_file(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_file(path, value):
    with open(path, "w") as f:
        f.write(str(value))

def check_collision(bird, pipes, mode):
    if bird.invincible:
        return False
    if bird.y < 0 or bird.y > HEIGHT:
        if "hit" in sound_cache:
            sound_cache["hit"].play()
            return True
    for p in pipes:
        if (bird.x + bird.size > p.x and bird.x - bird.size < p.x + p.width):
            if bird.y - bird.size < p.top_h or bird.y + bird.size > p.bottom_y:
                if mode == "classic":
                    if "hit" in sound_cache:
                        sound_cache["hit"].play()
                        return True
                else:
                    bird.life -= 1
                    bird.invincible = True
                    bird.inv_time = 120
                    if bird.life <= 0:
                        if "hit" in sound_cache:
                            sound_cache["hit"].play()
                            return True
                    return False
    return False

def check_item(bird, items):
    for i in items[:]:
        if abs(bird.x - i.x) < bird.size + i.size and abs(bird.y - i.y) < bird.size + i.size:
            items.remove(i)
            if "item" in sound_cache:
                sound_cache["item"].play()
            return i.type
    return None

# ========== 主游戏循环 ==========
def main():
    global WIDTH, HEIGHT, screen, current_skin_idx
    global bgm_volume, sfx_volume, volume_slider_dragging
    global panel_alpha, panel_scale, preview_bird_y_offset, preview_bird_phase
    
    classic_high = load_file(SCORE_FILES["classic_high"])
    entertain_high = load_file(SCORE_FILES["entertain_high"])
    classic_achieve = load_file(SCORE_FILES["classic_achieve"])
    entertain_achieve = load_file(SCORE_FILES["entertain_achieve"])
    load_skin_data()

    state = "menu"
    current_mode = None
    show_rule = False
    show_volume = False
    frame_count = 0
    current_scene = "day"
    stars = []
    total_score = 0
    last_skin_score = 0

    bird = Bird()
    pipes = [Pipe(3, current_scene)]
    items = []
    score_pop = []
    score = 0
    pipe_speed = 3
    has_red_buff = False

    def init_buttons():
        return [
            Button(WIDTH//2 - 200, 200, 400, 70, "经典模式"),
            Button(WIDTH//2 - 200, 300, 400, 70, "娱乐模式"),
            Button(WIDTH//2 - 150, 400, 300, 50, "操作说明", small_font),
            Button(WIDTH//2 - 150, 480, 300, 50, "音量调节", small_font),
            Button(WIDTH//2 - 160, HEIGHT//2 - 40, 320, 60, "继续游戏"),
            Button(WIDTH//2 - 160, HEIGHT//2 + 30, 320, 60, "返回菜单"),
            Button(WIDTH//2 - 160, HEIGHT//2 + 100, 320, 60, "重新开始")
        ]
    classic_btn, entertain_btn, rule_btn, volume_btn, continue_btn, quit_btn, restart_btn = init_buttons()

    clock = pygame.time.Clock()
    running = True
    force_play_bgm()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        preview_bird_phase += 0.05
        preview_bird_y_offset = int(math.sin(preview_bird_phase) * 15)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_skin_data()
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_handled = False  # 标记点击是否被面板处理
                    if state == "menu":
                        # 第一步：优先处理面板关闭按钮
                        if show_rule:
                            rule_close_btn = draw_rule_panel()
                            if rule_close_btn.collidepoint(mouse_pos):
                                show_rule = False
                                click_handled = True
                        if show_volume and not click_handled:
                            vol_panels = draw_volume_panel()
                            if vol_panels["close_btn"].collidepoint(mouse_pos):
                                show_volume = False
                                click_handled = True
                            # 处理滑块点击
                            elif vol_panels["bgm_slider"].collidepoint(mouse_pos):
                                volume_slider_dragging["bgm"] = True
                                click_handled = True
                            elif vol_panels["sfx_slider"].collidepoint(mouse_pos):
                                volume_slider_dragging["sfx"] = True
                                click_handled = True

                        # 第二步：仅当点击未被处理时，才处理其他按钮
                        if not click_handled:
                            # 处理面板打开和空白处关闭
                            if show_rule or show_volume:
                                rule_close_btn = draw_rule_panel() if show_rule else None
                                vol_panels = draw_volume_panel() if show_volume else None
                                if show_rule and not rule_close_btn.collidepoint(mouse_pos):
                                    show_rule = False
                                elif show_volume and not vol_panels["close_btn"].collidepoint(mouse_pos) and not vol_panels["bgm_slider"].collidepoint(mouse_pos) and not vol_panels["sfx_slider"].collidepoint(mouse_pos):
                                    show_volume = False
                            # 处理面板打开按钮
                            if rule_btn.click(mouse_pos):
                                show_rule = not show_rule
                                show_volume = False
                            elif volume_btn.click(mouse_pos):
                                show_volume = not show_volume
                                show_rule = False
                            # 处理游戏模式按钮
                            elif classic_btn.click(mouse_pos):
                                state = "playing"
                                current_mode = "classic"
                                current_scene = "day"
                                stars.clear()
                                bird = Bird()
                                pipes = [Pipe(3, current_scene)]
                                items = []
                                score_pop = []
                                score = 0
                                pipe_speed = 3
                                has_red_buff = False
                                show_rule = False
                                show_volume = False
                            elif entertain_btn.click(mouse_pos):
                                state = "playing"
                                current_mode = "entertain"
                                current_scene = "day"
                                stars.clear()
                                bird = Bird()
                                pipes = [Pipe(3, current_scene)]
                                items = []
                                score_pop = []
                                score = 0
                                pipe_speed = 3
                                has_red_buff = False
                                show_rule = False
                                show_volume = False

                    # 暂停和游戏结束的点击逻辑
                    if not click_handled:
                        if state == "paused":
                            if continue_btn.click(mouse_pos):
                                state = "playing"
                                pygame.mixer.music.unpause()
                            if quit_btn.click(mouse_pos):
                                state = "menu"
                                pygame.mixer.music.unpause()
                        elif state == "game_over":
                            if restart_btn.click(mouse_pos):
                                state = "playing"
                                current_scene = "day"
                                stars.clear()
                                bird = Bird()
                                pipe_speed = 3
                                pipes = [Pipe(pipe_speed, current_scene)]
                                items = []
                                score_pop = []
                                score = 0
                                has_red_buff = False
                            if quit_btn.click(mouse_pos):
                                state = "menu"
            
            # 滑块拖动逻辑
            if event.type == pygame.MOUSEMOTION:
                global bgm_volume, sfx_volume
                if volume_slider_dragging["bgm"]:
                    vol_panels = draw_volume_panel()
                    new_volume = (mouse_pos[0] - (vol_panels["scaled_x"] + 150)) / vol_panels["slider_w"]
                    bgm_volume = max(0.0, min(1.0, new_volume))
                    update_volume()
                if volume_slider_dragging["sfx"]:
                    vol_panels = draw_volume_panel()
                    new_volume = (mouse_pos[0] - (vol_panels["scaled_x"] + 150)) / vol_panels["slider_w"]
                    sfx_volume = max(0.0, min(1.0, new_volume))
                    update_volume()
            
            # 滑块拖动结束
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    volume_slider_dragging["bgm"] = False
                    volume_slider_dragging["sfx"] = False
            
            # 键盘事件
            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_LEFT:
                        current_skin_idx = (current_skin_idx - 1) % len(SKIN_LIST)
                        while not SKINS[SKIN_LIST[current_skin_idx]]["unlocked"]:
                            current_skin_idx = (current_skin_idx + 1) % len(SKIN_LIST)
                    if event.key == pygame.K_RIGHT:
                        current_skin_idx = (current_skin_idx + 1) % len(SKIN_LIST)
                        while not SKINS[SKIN_LIST[current_skin_idx]]["unlocked"]:
                            current_skin_idx = (current_skin_idx + 1) % len(SKIN_LIST)
                if state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        state = "paused"
                        pygame.mixer.music.pause()
                    if event.key == pygame.K_SPACE:
                        bird.jump()
                    if event.key == pygame.K_m:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()

        # 场景切换
        if state == "playing":
            current_scene = "day" if score < 50 else "dusk" if score < 100 else "starry" if score < 200 else "space"
            if current_scene in ["starry", "space"] and len(stars) == 0:
                stars = [Star(current_scene) for _ in range(40 if current_scene == "starry" else 60)]

        # 绘制背景
        screen.fill(SCENES[current_scene]["bg"])
        for star in stars:
            star.update()
            star.draw()

        # 菜单状态
        if state == "menu":
            title = title_font.render("飞扬小鸟", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
            # 皮肤预览
            preview_bird = Bird()
            preview_bird.x = WIDTH//2
            preview_bird.y = 600
            preview_bird.draw("classic", current_scene, preview_bird_y_offset)
            skin_name = small_font.render(f"当前皮肤：{SKINS[SKIN_LIST[current_skin_idx]]['name']}", True, BLACK)
            screen.blit(skin_name, (WIDTH//2 - skin_name.get_width()//2, 680 + preview_bird_y_offset))
            # 绘制按钮
            for btn in [classic_btn, entertain_btn, rule_btn, volume_btn]:
                btn.check_hover(mouse_pos)
                btn.draw()
            # 绘制面板
            if show_rule:
                draw_rule_panel()
            if show_volume:
                draw_volume_panel()

        # 游戏运行状态
        elif state == "playing":
            frame_count += 1
            # 生成道具
            if current_mode == "entertain" and frame_count % 200 == 0 and pipes:
                items.append(Item(pipes, pipe_speed, "entertain"))
            # 更新小鸟
            bird.update(current_mode)
            # 更新分数弹窗
            for pop in score_pop[:]:
                pop.update()
                if pop.is_finished():
                    score_pop.remove(pop)
            # 管道逻辑
            add_pipe = False
            for p in pipes[:]:
                p.update(current_scene)
                # 得分判定
                if p.x + p.width < bird.x and not p.scored:
                    base_score = 2 if (current_mode == "entertain" and bird.double_score) else 1
                    score += base_score
                    p.scored = True
                    score_pop.append(ScorePopup(bird.x, bird.y, base_score))
                    if "score" in sound_cache:
                        sound_cache["score"].play()
                # 红球buff判定
                if has_red_buff and p.x + p.width < bird.x and not p.extra_scored:
                    extra_score = 2 if (current_mode == "entertain" and bird.double_score) else 1
                    score += extra_score
                    p.extra_scored = True
                    has_red_buff = False
                    score_pop.append(ScorePopup(bird.x, bird.y-30, extra_score, RED))
                    if "score" in sound_cache:
                        sound_cache["score"].play()
                # 管道移出屏幕
                if p.off_screen():
                    pipes.remove(p)
                    add_pipe = True
            if add_pipe:
                pipes.append(Pipe(pipe_speed, current_scene))
            # 道具逻辑
            for i in items[:]:
                i.update()
                if i.off_screen():
                    items.remove(i)
            item_type = check_item(bird, items)
            if item_type and current_mode == "entertain":
                if item_type == "invincible":
                    bird.invincible = True
                    bird.inv_time = 300
                elif item_type == "narrow":
                    for p in pipes:
                        p.gap = max(150, p.gap - 30)
                    has_red_buff = True
                elif item_type == "slow":
                    pipe_speed = max(2, pipe_speed - 1)
                elif item_type == "double":
                    bird.double_score = True
                    bird.double_time = 600
                elif item_type == "life":
                    bird.life = min(3, bird.life + 1)
            # 碰撞检测
            if check_collision(bird, pipes, current_mode):
                state = "game_over"
                # 更新最高分
                if current_mode == "classic":
                    if score > classic_high:
                        classic_high = score
                        save_file(SCORE_FILES["classic_high"], classic_high)
                    if (score // 10) > classic_achieve:
                        save_file(SCORE_FILES["classic_achieve"], score // 10)
                else:
                    if score > entertain_high:
                        entertain_high = score
                        save_file(SCORE_FILES["entertain_high"], entertain_high)
                    if (score // 10) > entertain_achieve:
                        save_file(SCORE_FILES["entertain_achieve"], score // 10)
                # 解锁皮肤
                total_score += score
                if total_score > last_skin_score:
                    last_skin_score = total_score
                    unlocked = check_skin_unlock(total_score)
                    if unlocked:
                        for skin_id in SKINS:
                            if SKINS[skin_id]["unlocked"] and SKINS[skin_id]["unlock_score"] <= total_score:
                                # 调用带祝福语的弹窗
                                draw_skin_unlock_popup(SKINS[skin_id]["name"], SKINS[skin_id]["color"])
            # 难度加速
            if score % 5 == 0 and score != 0:
                pipe_speed = min(8, pipe_speed + 0.1)
            # 绘制元素
            for p in pipes:
                p.draw()
            for i in items:
                i.draw()
            bird.draw(current_mode, current_scene)
            for pop in score_pop:
                pop.draw()
            # 信息面板
            pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 100))
            pygame.draw.line(screen, DARK_GRAY, (0, 100), (WIDTH, 100), 3)
            screen.blit(small_font.render(f"得分：{score}", True, BLACK), (30, 30))
            screen.blit(small_font.render(f"{'经典' if current_mode == 'classic' else '娱乐'}最高分：{classic_high if current_mode == 'classic' else entertain_high}", True, BLACK), (30, 60))
            if current_mode == "entertain":
                screen.blit(small_font.render(f"生命：{bird.life}", True, GREEN), (350, 30))
                if has_red_buff:
                    screen.blit(small_font.render("红球buff：下根管道+1分", True, RED), (350, 60))
                elif bird.double_score:
                    screen.blit(small_font.render(f"双倍得分剩余：{bird.double_time//60}s", True, PURPLE), (350, 60))
            screen.blit(small_font.render(f"场景：{current_scene}", True, BLACK), (WIDTH - 180, 60))

        # 暂停状态
        elif state == "paused":
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            screen.blit(title_font.render("游戏暂停", True, WHITE), (WIDTH//2 - 150, 200))
            for btn in [continue_btn, quit_btn]:
                btn.check_hover(mouse_pos)
                btn.draw()

        # 游戏结束状态
        elif state == "game_over":
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            screen.blit(title_font.render("游戏结束", True, WHITE), (WIDTH//2 - 150, 150))
            screen.blit(btn_font.render(f"最终得分：{score}", True, WHITE), (WIDTH//2 - 120, 280))
            for btn in [restart_btn, quit_btn]:
                btn.check_hover(mouse_pos)
                btn.draw()

        # 更新屏幕
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()


# In[15]:


print(os.getcwd())


# In[ ]:




