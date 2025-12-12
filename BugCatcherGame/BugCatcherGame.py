from tkinter import *
import pygame
import random
import time
import os


# ============================================================
# 게임 기본 설정
# ============================================================
class Setting:
    def __init__(self):
        # 화면 사이즈
        self.CANVAS_WIDTH = 400
        self.CANVAS_HEIGHT = 720
        
        # 키 코드
        self.NOW_KEY_SET = 'arrow'
        
        self.KEY_MAPS = {
            'arrow': {
                'UP': 38,
                'DOWN': 40,
                'LEFT': 37,
                'RIGHT': 39,
            },
            'wasd': {
                'UP': 87,
                'DOWN': 83,
                'LEFT': 65,
                'RIGHT': 68,
            }
        }
        
        self.KEY_SHOOT = 32
        self.KEY_ENTER = 13
        self.KEY_ESC = 27
        
        self.used_keycodes = set()
        self.changeKeySet(self.NOW_KEY_SET)
    
    # 사용 키 세트 업데이트
    def updateUsedKeySet(self):
        self.used_keycodes = {
            self.KEY_UP, self.KEY_LEFT, self.KEY_DOWN, self.KEY_RIGHT,
            self.KEY_SHOOT, self.KEY_ENTER, self.KEY_ESC
        }
    
    # 방향 키 세트 변경
    def changeKeySet(self, key_set):
        self.NOW_KEY_SET = key_set
        
        current_map = self.KEY_MAPS[self.NOW_KEY_SET]
        
        for key, code in current_map.items():
            if key in self.used_keycodes:
                return False, key
        
        self.KEY_UP = current_map['UP']
        self.KEY_DOWN = current_map['DOWN']
        self.KEY_LEFT = current_map['LEFT']
        self.KEY_RIGHT = current_map['RIGHT']
        self.updateUsedKeySet()
        
        return True, key
    
    # 발사 키 변경
    def changeShootKey(self, key):
        temp_used_keys = self.used_keycodes - {self.KEY_SHOOT}
        
        if key in temp_used_keys or not self.asciiChar(key):
            return False, key
        
        self.KEY_SHOOT = key
        self.updateUsedKeySet()
        return True, key

    # 키 코드 -> 문자 변경
    def asciiChar(self, key):
        if 48 <= key <= 57 or 65 <= key <= 90:
            return chr(key)
        else:
            return {8: 'BACK SPACE', 9: 'TAB', 13: 'ENTER', 16: 'SHIFT', 17: 'CTRL', 32: 'SPACE'}.get(key, False)
# ------------------------------------------------------------





# ============================================================
# 엔티티 클래스
# ============================================================
# 플레이어
# ------------------------------------------------------------
class Player:
    def __init__(self, canvas, player_img, cursor_img):
        self.canvas = canvas
        
        self.id = "player"
        self.player_img = player_img
        
        self.cursor_img = cursor_img
        
        self.last_time = time.time()
        
        # 플레이어 스탯
        self.score = 0
        self.hp = 3
        
        self.me = self.canvas.create_image(200, 670, image = self.player_img, tags = self.id)

    # 플레이어 정보 반환
    def getPos(self):
        return self.canvas.coords(self.me)
    
    def getHalfSize(self):
        return self.player_img.width() // 2, self.player_img.height() // 2


    # 플레이어 동작 함수
    def move(self, x, y):
        self.canvas.move(self.me, x, y)

    def shoot(self):
        now = time.time()
        # 발사 텀 제한
        if now - self.last_time > 0.3:
            self.last_time = now
            pos = self.getPos()
            self.canvas.create_image(pos[0], pos[1] - 10, image = self.cursor_img, tags = "cursor")
    
    def tp(self, x, y):
        self.canvas.coords(self.me, x, y)

    
    # 스탯 조작
    def scoreManage(self, amount):
        if self.score + amount > 0:
            self.score += amount
        else:
            self.score = 0
    
    def hpManage(self, amount):
        if self.hp + amount > 0:
            self.hp += amount
        else:
            self.hp = 0
# ------------------------------------------------------------



# 몹
# ------------------------------------------------------------
class Mob:
    def __init__(self, canvas, img, id, mob_type, x_pos):
        self.canvas = canvas
        
        # 에러 코드: e
        # 정답 코드: c
        # 커피: h (c는 정답 코드랑 겹쳐서 hp 할 때 h)
        # 스피드업: d
        # ai 모드: a
        self.id = mob_type[0] + str(id)
        
        self.img = img
        
        self.me = self.canvas.create_image(x_pos, 20, image = self.img, tags = self.id)
    
    # 몹 정보 반환
    def getPos(self):
        return self.canvas.coords(self.me)
    
    def getId(self):
        return self.me
    
    def getHalfSize(self):
        return self.img.width() // 2, self.img.height() // 2
    
    
    # 몹 동작 함수
    def move(self):
        self.canvas.move(self.me, 0, 3)
# ------------------------------------------------------------



# 스파게티전 - 쓸모없는 주석
# ------------------------------------------------------------
class UselessComment:
    def __init__(self, canvas, image, x, y):
        self.canvas = canvas
        
        self.image = image
        
        self.x = x
        self.y = y
        
        self.me = self.canvas.create_image(self.x, self.y, image=self.image)
        
        self.tangle_timer_id = None
        self.is_destroyed = False
    
    # 몹 정보 반환
    def getPos(self):
        return self.canvas.coords(self.me)
    
    def getId(self):
        return self.me
    
    def getHalfSize(self):
        return self.image.width() // 2, self.image.height() // 2
    
    def startTangleIncrease(self, scene_instance):
        def increase_tangle():
            if not self.is_destroyed:
                if scene_instance.is_comment_in:
                    INCREASE_AMOUNT = 3
                else:
                    INCREASE_AMOUNT = 1
                scene_instance.tangle_gauge = min(scene_instance.tangle_gauge + INCREASE_AMOUNT, 100)
                scene_instance.updateTangleDisplay()
                scene_instance.showComment(INCREASE_AMOUNT, spagetti=True)

                if not scene_instance.is_paused:
                    self.tangle_timer_id = scene_instance.window.after(500, increase_tangle)
        
        self.tangle_timer_id = scene_instance.window.after(500, increase_tangle)
    
    def destroy(self, scene_instance):
        if self.tangle_timer_id is not None:
            scene_instance.window.after_cancel(self.tangle_timer_id)
        self.is_destroyed = True
        self.canvas.delete(self.me)
# ------------------------------------------------------------





# ============================================================
# 씬 클래스
# ============================================================
# 기본 씬
# ------------------------------------------------------------
class BaseScene:
    def __init__(self, scene_change):
        self.setting = scene_change.setting
        self.window = scene_change.window
        self.keys = set()
        self.scene_change = scene_change
        
        self.sounds = pygame.mixer
        if not self.sounds.get_init(): 
            self.sounds.init()
        
    def pack(self):
        self.canvas.pack(expand=True, fill=BOTH)
    
    def unpack(self):
        self.canvas.pack_forget()
    
    
    def keyPressHandler(self, event):
        self.keys.add(event.keycode)
    
    def keyReleaseHandler(self, event):
        if event.keycode in self.keys:
            self.keys.remove(event.keycode)
    
    
    def destroy(self):
        self.canvas.destroy()
# ------------------------------------------------------------



# 타이틀
# ------------------------------------------------------------
class TitleScene(BaseScene):
    def __init__(self, scene_change):
        super().__init__(scene_change)
        self.canvas = Canvas(self.window, bg="white")
        
        # 배경 이미지 로드, 설정
        self.bg_img = PhotoImage(file="media/image/backgrounds/title_bg.png")
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw", tags="backgrounds")
        
        # 타이틀 텍스트
        self.canvas.create_text(
            200, 200,
            text="bug_catcher",
            fill='white',
            font=('Consolas', 40, 'bold'),
            anchor='center'
        )
        
        # Press ENTER or Click to play
        self.start_text = self.canvas.create_text(
            200, 285,
            text="",
            fill='white',
            font=('Consolas', 12),
            anchor='center'
        )
        # 깜빡임 관련 변수
        self.is_text_visible = True
        self.blink_id = None
        
        # 버튼 설정
        self.start_btn = Button(self.window, text="게임 시작", font=('Malgun Gothic', 12), command=lambda: self.gotoScene(1))
        self.how2game_btn = Button(self.window, text="게임 방법", font=('Malgun Gothic', 12), command=lambda: self.gotoScene(2))
        self.setting_btn = Button(self.window, text="게임 설정", font=('Malgun Gothic', 12), command=lambda: self.gotoScene(3))
        self.exit_btn = Button(self.window, text="종료하기", font=('Malgun Gothic', 12), command=lambda: self.gotoScene(-1))
        
        self.menu_idx = 1
        self.menu_list = [self.start_btn, self.how2game_btn, self.setting_btn, self.exit_btn]
        
        # 음악 로드
        self.select_sound = self.sounds.Sound("media/music/effect/select.mp3")

        self.updateFocusDisplay()
    
    def run(self):
        pass

    
    def pack(self):
        super().pack()
        
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("media/music/bgm/title_bgm.mp3")
            pygame.mixer.music.play(loops=-1)
        
        self.start_btn.place(x=200, y=350, width=100, height=30, anchor="center")
        self.how2game_btn.place(x=200, y=400, width=100, height=30, anchor="center")
        self.setting_btn.place(x=200, y=450, width=100, height=30, anchor="center")
        self.exit_btn.place(x=200, y=500, width=100, height=30, anchor="center")
        
        self.blinkStartText()
    
    def unpack(self):
        super().unpack()
        
        self.menu_idx = 1
        self.updateFocusDisplay()
        
        self.start_btn.place_forget()
        self.how2game_btn.place_forget()
        self.setting_btn.place_forget()
        self.exit_btn.place_forget()
        
        if self.blink_id is not None:
            self.window.after_cancel(self.blink_id)
            self.blink_id = None
    
    
    def keyPressHandler(self, event):
        if event.keycode == self.setting.KEY_UP:
            self.select_sound.play()
            self.menu_idx = ((self.menu_idx + 2) % 4) + 1
            self.updateFocusDisplay()
        
        elif event.keycode == self.setting.KEY_DOWN:
            self.select_sound.play()
            self.menu_idx = (self.menu_idx % 4) + 1
            self.updateFocusDisplay()
        
        elif event.keycode == self.setting.KEY_ENTER:
            self.gotoScene(-1 if self.menu_idx == 4 else self.menu_idx)
    
    
    def gotoScene(self, idx):
        self.select_sound.play()
        
        if idx == 1 or idx == -1:
            pygame.mixer.music.stop()
        
        if idx == -1:
            self.window.after(500, self.scene_change.onClose)
        elif idx == 1: 
            self.scene_change.sceneChange(idx, x_pos=200, y_pos=670, score=0, hp=3, boss_round=1)
        else:
            self.scene_change.sceneChange(idx)
    
    
    def updateFocusDisplay(self):
        for i, button in enumerate(self.menu_list):
            if i == self.menu_idx - 1:
                button.config(bg='#f0f0f0', fg='#000080', font=('Malgun Gothic', 12, 'bold'))
            else:
                button.config(bg='SystemButtonFace', fg='black', font=('Malgun Gothic', 12))
    
    
    def blinkStartText(self):
        self.canvas.itemconfig(self.start_text, text="") if self.is_text_visible else self.canvas.itemconfig(self.start_text, text="< Press ENTER or Click to play >")
        self.is_text_visible = not self.is_text_visible
        self.blink_id = self.window.after(300, self.blinkStartText)
# ------------------------------------------------------------





# 게임 관련 씬
# ------------------------------------------------------------
# 메인 게임
# ------------------------------------------------------------
class MainGameScene(BaseScene):
    def __init__(self, scene_change):
        super().__init__(scene_change)
        
        self.canvas = Canvas(self.window, bg="white")
        self.last_time = time.time()
        
        # 에셋 로드, 게임 배치
        # 배경
        self.bg_img = PhotoImage(file="media/image/backgrounds/main_bg.png")
        self.canvas.create_image(0,0, image=self.bg_img, anchor="nw", tags="backgrounds")
        
        # 플레이어 생성
        self.player_img = PhotoImage(file="media/image/entities/player/player.png")
        self.cursor_img = PhotoImage(file = "media/image/entities/player/cursor.png")
        self.player = Player(self.canvas, self.player_img, self.cursor_img)
        
        # 엔티티 - 에러 코드
        error_folder_path = "media/image/entities/error_code/"
        self.error_images = [PhotoImage(file = os.path.join(error_folder_path, filename)) for filename in os.listdir(error_folder_path) if filename.endswith(".png")]

        # 엔티티 - 정답 코드
        clean_folder_path = "media/image/entities/clean_code/"
        self.clean_images = [PhotoImage(file = os.path.join(clean_folder_path, filename)) for filename in os.listdir(clean_folder_path) if filename.endswith(".png")]
        
        # 엔티티 - 아이템
        self.coffee_img = PhotoImage(file = "media/image/entities/items/coffee.png")
        self.deadline_img = PhotoImage(file = "media/image/entities/items/deadline.png")
        self.ai_img = PhotoImage(file = "media/image/entities/items/ai.png")
        
        
        # 인터페이스 - 스코어
        self.score_text = self.canvas.create_text(
            380, 60,
            text = f"SCORE: {self.player.score}",
            fill = "white",
            font = ('Consolas', 14),
            anchor = "e"
        )

        # 인터페이스 - hp
        self.hp_full_img = PhotoImage(file = "media/image/ui_elements/hp_bar/hp_full.png")
        self.hp_empty_img = PhotoImage(file = "media/image/ui_elements/hp_bar/hp_empty.png")
        
        
        # 일시정지 관련
        self.pause_btn = Button(self.window, text=" || ", command=self.pause_mode)
        
        self.continue_btn = Button(self.window, text="계속하기", font=('Malgun Gothic', 12), command=self.unpause_mode)
        self.return_btn = Button(self.window, text="돌아가기", font=('Malgun Gothic', 12), command=lambda: self.gotoScene(0))
        
        self.pause_menu_list = [self.continue_btn, self.return_btn]
        
        self.fader_mask = PhotoImage(file="media/image/backgrounds/fader_mask.png")
        
        
        # 효과음 로드
        self.select_sound = self.sounds.Sound("media/music/effect/select.mp3")  # 메뉴 선택
        self.shoot_sound = self.sounds.Sound("media/music/effect/shoot.mp3")    # 발사
        self.death_sound = self.sounds.Sound("media/music/effect/death.mp3")    # 파괴 또는 점수 잃음
        self.buff_sound = self.sounds.Sound("media/music/effect/buff.mp3")      # 버프
        self.debuff_sound = self.sounds.Sound("media/music/effect/debuff.mp3")  # 디버프
        
        # 배경 음악 경로
        self.main_game_bgm_path = "media/music/bgm/main_game_bgm.mp3"
        self.low_hp_bgm_path = "media/music/bgm/low_hp_bgm.mp3"
        
        
        # 초기화 변수
        self.mob_list = []
        self.mob_id = 0
        
        self.create_rate = 70
        
        self.pause_menu_idx = 0
        
        self.speed = 5
        self.speed_timer_id = None
        self.speed_start_time = 0.0
        self.speed_remaining_time = 0
        
        self.is_ai_active = False
        self.ai_timer_id = None
        self.ai_start_time = 0.0
        self.ai_remaining_time = 0
        
        self.is_low_hp_bgm = False
        
        self.BOSS_SCORE = 10000
        self.boss_round = 1
        
        self.is_paused = False
    
    
    def run(self):
        try:
            # 일시정지 모드 제어
            if self.is_paused:
                return
            
            # 보스전 진입
            if self.player.score >= self.BOSS_SCORE * self.boss_round:
                last_player_pos = self.player.getPos()
                self.scene_change.sceneChange(5, x_pos = last_player_pos[0], y_pos = last_player_pos[1], score=self.player.score, hp=self.player.hp)
            
            # 게임 오버 제어
            if self.player.hp <= 0:
                last_player_pos = self.player.getPos()
                self.scene_change.sceneChange(4, x_pos = last_player_pos[0], y_pos = last_player_pos[1])
            
            cursors = self.canvas.find_withtag("cursor")
            self.display(self.speed)
            for cs in cursors:
                self.canvas.move(cs, 0, -10)
                if self.canvas.coords(cs)[1] < 0:
                    self.canvas.delete(cs)
            self.manageMob()
        
        except TclError:
            return
    
    
    def pack(self, player_stat):
        super().pack()
        
        self.player.tp(player_stat['x_pos'], player_stat['y_pos'])
        self.player.score = player_stat['score']
        self.player.hp = player_stat['hp']
        self.boss_round = player_stat['boss_round']
        
        if self.player.hp > 1:
            pygame.mixer.music.load(self.main_game_bgm_path)
            pygame.mixer.music.play(loops=-1)
            self.is_low_hp_bgm = False
        else:
            pygame.mixer.music.load(self.low_hp_bgm_path)
            pygame.mixer.music.play(loops=-1)
            self.is_low_hp_bgm = True
        
        self.updateHpDisplay()
        self.updateScoreDisplay()
        
        self.pause_btn.place(x=360, y=10)
    
    def unpack(self):
        super().unpack()
        self.resetGameState()
        pygame.mixer.music.stop()
        self.pause_btn.place_forget()
    
    
    def keyPressHandler(self, event):
        if event.keycode == self.setting.KEY_ESC:
            if self.is_paused:
                self.unpause_mode()
            else:
                self.pause_mode()
        else:
            self.keys.add(event.keycode)
        
        if self.is_paused:
            if event.keycode == self.setting.KEY_ENTER:
                self.select_sound.play()
                if self.pause_menu_idx == 0:
                    self.unpause_mode()
                elif self.pause_menu_idx == 1:
                    self.gotoScene(0)
                
            elif event.keycode == self.setting.KEY_UP:
                self.select_sound.play()
                self.pause_menu_idx = (self.pause_menu_idx - 1) % 2
                self.updateFocusDisplay()
            elif event.keycode == self.setting.KEY_DOWN:
                self.select_sound.play()
                self.pause_menu_idx = (self.pause_menu_idx + 1) % 2
                self.updateFocusDisplay()
        
        if not self.is_paused:
            if event.keycode == self.setting.KEY_SHOOT:
                self.shoot_sound.play()
                self.player.shoot()
    
    
    def changeBGM(self, is_low_hp):
        # hp가 1 이하이고 현재 low_hp_bgm을 재생중이 아닐 때
        if is_low_hp and not self.is_low_hp_bgm:
            pygame.mixer.music.load(self.low_hp_bgm_path)
            pygame.mixer.music.play(loops=-1)
            self.is_low_hp_bgm = True
        
        # hp가 2 이상이고 low_hp_bgm 재생중일 때
        elif not is_low_hp and self.is_low_hp_bgm:
            pygame.mixer.music.load(self.main_game_bgm_path)
            pygame.mixer.music.play(loops=-1)
            self.is_low_hp_bgm = False
    
    
    # 플레이어 동작
    def display(self, speed):
        for key in self.keys:
            pos = self.player.getPos()
            half_width, half_height = self.player.getHalfSize()
            
            if key == self.setting.KEY_RIGHT and pos[0] + half_width <= self.setting.CANVAS_WIDTH:
                self.player.move(speed, 0)
            if key == self.setting.KEY_LEFT and pos[0] - half_width >= 0:
                self.player.move(-speed, 0)
            if key == self.setting.KEY_UP and pos[1] - half_height >= 0:
                self.player.move(0, -speed)
            if key == self.setting.KEY_DOWN and pos[1] + half_height <= self.setting.CANVAS_HEIGHT:
                self.player.move(0, speed)

    
    # 디스플레이 조작
    def updateScoreDisplay(self):
        self.canvas.itemconfig(self.score_text, text = f"SCORE: {self.player.score}")
        
    def showComment(self, comment, entity):
        entity_pos = entity.getPos()
        entity_width, entity_height = entity.getHalfSize()
        
        x_pos = random.randint(int(entity_pos[0] - entity_width), int(entity_pos[0] + entity_width))
        y_pos = random.randint(int(entity_pos[1] - entity_height), int(entity_pos[1] + entity_height))
        
        text = (f"+{comment}" if comment > 0 else f"{comment}") if isinstance(comment, (int, float)) else comment
        
        comment_text = self.canvas.create_text(
            x_pos, y_pos,
            text = text,
            fill = ("green" if comment > 0 else "red") if isinstance(comment, (int, float)) else "blue",
            font = ('Consolas', 12, "bold"),
            tags = "comment"
        )
        
        self.window.after(500, lambda id_to_delete = comment_text: self.canvas.delete(id_to_delete))
    
    def updateHpDisplay(self):
        start_x = 380
        max_hp = 3
        
        self.canvas.delete("hp")
        
        for i in range(max(max_hp, self.player.hp)):
            x_pos = start_x - i * 15
            if i < self.player.hp:
                self.canvas.create_image(x_pos, 90, image=self.hp_full_img, tags="hp")
            else:
                self.canvas.create_image(x_pos, 90, image=self.hp_empty_img, tags="hp")
        
        if self.player.hp <= 1:
            self.changeBGM(True)
        else:
            self.changeBGM(False)
    
    
    # 일시정지 관련 함수
    def pause_mode(self):
        self.is_paused = True
        pygame.mixer.music.pause()
        self.canvas.create_image(0, 0, image=self.fader_mask, anchor="nw", tags="fader")
        
        # 남은 스피드 업 시간 기록
        if self.speed_timer_id is not None:
            self.window.after_cancel(self.speed_timer_id)
            temp_time = (time.time() - self.speed_start_time)
            self.speed_remaining_time = max(0, 5000 - int(temp_time * 1000))
            self.speed_timer_id = None
        
        # 남은 ai 시간 기록
        if self.ai_timer_id is not None:
            self.window.after_cancel(self.ai_timer_id)
            temp_time = (time.time() - self.ai_start_time)
            self.ai_remaining_time = max(0, 5000 - int(temp_time * 1000))
            self.ai_timer_id = None
        
        self.pause_btn.place_forget()
        
        self.continue_btn.place(x=200, y=330, width=100, height=30, anchor="center")
        self.return_btn.place(x=200, y=390, width=100, height=30, anchor="center")
        
        self.pause_menu_idx = 0
        self.updateFocusDisplay()
    
    def unpause_mode(self):
        self.continue_btn.place_forget()
        self.return_btn.place_forget()
        
        self.canvas.delete("fader")
        
        self.pause_btn.place(x=360, y=10)
        
        # 스피드 타이머 재개
        if self.speed_remaining_time > 0:
            self.decreaseSpeedAfterDelay(self.speed_remaining_time)
            self.speed_remaining_time = 0
        
        # ai 타이머 재개
        if self.ai_remaining_time > 0:
            self.activeAI(remaining_time=self.ai_remaining_time)
            self.ai_remaining_time = 0
        
        pygame.mixer.music.unpause()
        self.is_paused = False
    
    def updateFocusDisplay(self):
        for i, button in enumerate(self.pause_menu_list):
            if i == self.pause_menu_idx:
                button.config(bg='#f0f0f0', fg='#000080', font=('Malgun Gothic', 12, 'bold'))
            else:
                button.config(bg='SystemButtonFace', fg='black', font=('Malgun Gothic', 12))


    # 스피드 관련 함수
    def decreaseSpeed(self):
        self.showComment("스피드 다운!", self.player)
        self.debuff_sound.play()
        self.speed = max(self.speed // 2, 5)
    
    def decreaseSpeedAfterDelay(self, delay_ms):
        self.speed_start_time = time.time()
        self.speed_timer_id = self.window.after(delay_ms, self.decreaseSpeed)

    
    # ai 관련 함수
    def activeAI(self, remaining_time = 5000):
        if self.ai_timer_id is not None:
            self.window.after_cancel(self.ai_timer_id)
        else:
            self.is_ai_active = True
            self.create_rate = 30
        
        self.ai_start_time = time.time()
        self.ai_timer_id = self.window.after(remaining_time, self.deactiveAI)
    
    def deactiveAI(self):
        self.showComment("바이브 코딩 종료!", self.player)
        self.debuff_sound.play()
        self.create_rate = 70
        self.is_ai_active = False
        self.ai_timer_id = None
    
    def aiMode(self):
        if not self.is_ai_active:
            return
        
        AUTO_RANGE = 300
        BASE_SCORE = 100
        SCALING = 3
        player_pos = self.player.getPos()
        
        for i in range(len(self.mob_list) - 1, -1, -1):
            mob = self.mob_list[i]
            mob_pos = mob.getPos()
            
            if abs(player_pos[1] - mob_pos[1]) <= AUTO_RANGE:
                if mob.id[0] == 'e':
                    bonus_score = int((self.setting.CANVAS_HEIGHT - mob_pos[1]) / SCALING)
                    total_score = BASE_SCORE + bonus_score
                    
                    self.death_sound.play()
                    self.player.scoreManage(total_score)
                    self.updateScoreDisplay()
                    self.showComment(total_score, mob)

                elif mob.id[0] == 'h':
                    self.player.hp += 1
                    self.buff_sound.play()
                    self.showComment("체력 회복!", self.player)
                    self.updateHpDisplay()

                elif mob.id[0] == 'd':
                    self.speed *= 2
                    self.buff_sound.play()
                    self.showComment("스피드업!", self.player)
                    self.decreaseSpeedAfterDelay(5000)
                
                elif mob.id[0] == 'a':
                    self.buff_sound.play()
                    self.showComment("바이브 코딩!", self.player)
                    self.activeAI()
                
                else:
                    continue
                
                self.canvas.delete(mob.getId())
                self.mob_list.pop(self.mob_list.index(mob))
    
    
    # 다른 몹과 겹치지 않는 x좌표 생성
    def getSafeX(self, img):
        max_attempts = 20
        img_half_width = img.width() // 2
        Y_CHECK = img.height() + 50
        
        min_x = img_half_width
        max_x = self.setting.CANVAS_WIDTH - img_half_width
        
        for _ in range(max_attempts):
            new_x = random.randint(min_x, max_x)
            
            is_safe = True
            for mob in self.mob_list:
                mob_pos = mob.getPos()
                code_half_width, _ = mob.getHalfSize()
                
                width_spacing = img_half_width + code_half_width
                distance_x = abs(new_x - mob_pos[0])
                
                if mob_pos[1] < Y_CHECK and distance_x < width_spacing:
                    is_safe = False
                    break
            
            if is_safe:
                return new_x
        
        return None
    
    # 몹 관리자
    def manageMob(self):
        self.aiMode()
        
        # 모든 개체 이동
        for mob in self.mob_list:
            mob.move()
        
        # 몹 생성
        create_rand = random.randint(0, self.create_rate)
        if create_rand == 0:
            mob_rand = random.randint(0, 100)
            # 에러 41%
            if 0 <= mob_rand < 41:
                img = random.choice(self.error_images)
                x_pos = self.getSafeX(img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, img, self.mob_id, 'error', x_pos))
                    self.mob_id += 1
            # 클린 41%
            elif 41 <= mob_rand < 82:
                img = random.choice(self.clean_images)
                x_pos = self.getSafeX(img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, img, self.mob_id, 'clean', x_pos))
                    self.mob_id += 1
            # 회복 8%
            elif 82 <= mob_rand < 90:
                x_pos = self.getSafeX(self.coffee_img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, self.coffee_img, self.mob_id, 'heart', x_pos))
                    self.mob_id += 1
            # 스피드업 8%
            elif 90 <= mob_rand < 98:
                x_pos = self.getSafeX(self.deadline_img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, self.deadline_img, self.mob_id, 'deadline', x_pos))
                    self.mob_id += 1
            # ai 2%
            else:
                x_pos = self.getSafeX(self.ai_img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, self.ai_img, self.mob_id, 'ai', x_pos))
                    self.mob_id += 1
        
        
        BASE_SCORE = 100
        SCALING = 3
        
        player_pos = self.player.getPos()
        player_width, player_height = self.player.getHalfSize()
        
        # 커서가 몹에 닿았을 때
        cursors = self.canvas.find_withtag("cursor")
        for cs in cursors:
            cs_pos = self.canvas.coords(cs)
            for mob in self.mob_list:
                mob_pos = mob.getPos()
                mob_width, mob_height = mob.getHalfSize()
                
                if mob_pos[0] - mob_width < cs_pos[0] < mob_pos[0] + mob_width and mob_pos[1] - mob_height < cs_pos[1] < mob_pos[1] + mob_height:
                    # 에러코드 - 점수 획득
                    if mob.id[0] == 'e':
                        bonus_score = int((self.setting.CANVAS_HEIGHT - mob_pos[1]) / SCALING)
                        total_score = BASE_SCORE + bonus_score
                        self.death_sound.play()
                    # 클린코드 - 점수 소실
                    elif mob.id[0] == 'c':
                        total_score = min(-BASE_SCORE, -(self.player.score // 10))
                        self.death_sound.play()
                        
                    # 그 외 - 반응 없음
                    else:
                        continue
                    
                    self.player.scoreManage(total_score)
                    self.updateScoreDisplay()
                    self.showComment(total_score, mob)
                    
                    self.canvas.delete(mob.getId())
                    self.mob_list.pop(self.mob_list.index(mob))
                    self.canvas.delete(cs)
        
        
        # 몹과 플레이어가 충돌했을 때
        for mob in self.mob_list:
            mob_pos = mob.getPos()
            mob_width, mob_height = mob.getHalfSize()
            
            # 히트박스
            x_hit = (
                mob_pos[0] - mob_width < player_pos[0] + player_width and 
                mob_pos[0] + mob_width > player_pos[0] - player_width
            )
            y_hit = (
                mob_pos[1] - mob_height < player_pos[1] + player_height and
                mob_pos[1] + mob_height > player_pos[1] - player_height
            )
            
            if x_hit and y_hit:
                # 에러코드 - hp -1, 점수 소실
                if mob.id[0] == 'e':
                    self.player.hpManage(-1)
                    self.updateHpDisplay()
                    
                    total_score = min(-BASE_SCORE, -(self.player.score // 10))
                    
                    self.player.scoreManage(total_score)
                    self.updateScoreDisplay()
                    self.showComment(total_score, mob)
                    self.death_sound.play()
                # 클린코드 - 점수 획득
                elif mob.id[0] == 'c':
                    bonus_score = int((self.setting.CANVAS_HEIGHT - mob_pos[1]) / SCALING)
                    total_score = BASE_SCORE + bonus_score

                    self.player.scoreManage(total_score)
                    self.updateScoreDisplay()
                    self.showComment(total_score, mob)
                    self.buff_sound.play()      # 효과음 변경 필요
                # 커피 - hp 회복
                elif mob.id[0] == 'h':
                    self.player.hp += 1
                    self.updateHpDisplay()
                    self.showComment("체력 회복!", self.player)
                    self.buff_sound.play()
                # 데드라인 - 5초 스피드업
                elif mob.id[0] == 'd':
                    self.speed *= 2
                    self.decreaseSpeedAfterDelay(5000)
                    self.showComment("스피드업!", self.player)
                    self.buff_sound.play()
                # ai - 5초간 바이브 코딩
                elif mob.id[0] == 'a':
                    self.activeAI()
                    self.showComment("바이브 코딩!", self.player)
                    self.buff_sound.play()
                
                self.canvas.delete(mob.getId())
                self.mob_list.pop(self.mob_list.index(mob))
        
        
        # 몹이 화면을 끝까지 이동했을 때
        for mob in self.mob_list:
            if mob.getPos()[1] > self.setting.CANVAS_HEIGHT:
                # 에러코드 - 점수 소실
                if mob.id[0] == 'e':
                    total_score = min(-BASE_SCORE, -(self.player.score // 10))
                    
                    self.player.scoreManage(total_score)
                    self.updateScoreDisplay()
                    self.showComment(total_score, mob)
                    self.death_sound.play()
                # 정답코드 - 점수 획득
                elif mob.id[0] == 'c':
                    total_score = max(BASE_SCORE, self.player.score // 10)
                    
                    self.player.scoreManage(total_score)
                    self.updateScoreDisplay()
                    self.showComment(total_score, mob)
                    self.buff_sound.play()
                
                self.canvas.delete(mob.getId())
                self.mob_list.pop(self.mob_list.index(mob))
    
    
    def gotoScene(self, idx):
        if self.is_paused:
            self.unpause_mode()
        self.scene_change.sceneChange(idx)
    
    
    def resetGameState(self):
        self.canvas.delete("all")
        
        self.canvas.create_image(0,0, image=self.bg_img, anchor="nw", tags="backgrounds")
        
        self.player = Player(self.canvas, self.player_img, self.cursor_img)
        
        self.score_text = self.canvas.create_text(
            380, 60,
            text = f"SCORE: {self.player.score}",
            fill = "white",
            font = ('Consolas', 14),
            anchor = "e"
        )
        
        self.updateHpDisplay()
        
        self.mob_list = []
        self.mob_id = 0
        
        self.create_rate = 70

        self.speed = 5
        if self.speed_timer_id is not None:
            self.window.after_cancel(self.speed_timer_id)
            self.speed_timer_id = None
        self.speed_start_time = 0.0
        self.speed_remaining_time = 0
        
        
        self.is_ai_active = False
        if self.ai_timer_id is not None:
            self.window.after_cancel(self.ai_timer_id)
            self.ai_timer_id = None
        self.ai_start_time = 0.0
        self.ai_remaining_time = 0
        
        
        self.is_paused = False
        
        self.is_low_hp_bgm = False
        
        self.boss_round = 1
        
        self.keys.clear()
# ------------------------------------------------------------



# 게임 오버
# ------------------------------------------------------------
class GameOverScene(BaseScene):
    def __init__(self, scene_change):
        super().__init__(scene_change)
        self.canvas = Canvas(self.window, bg="black")
        
        # 에셋 로드
        self.player_img = PhotoImage(file="media/image/entities/player/player.png")
        
        self.fader_mask_path = "media/image/ui_elements/fader_mask/alpha"
        self.fader_masks = [PhotoImage(file=self.fader_mask_path + str(i) + ".png") for i in range(1, 12)]
        
        self.end_text = "포기하지 마세요!\nA+이 눈앞에 있습니다."
        
        self.press_text = self.canvas.create_text(
            200, 500,
            text="",
            fill='white',
            anchor='center',
            font = ('Consolas', 12)
        )
        
        # 효과음 로드
        self.select_sound = self.sounds.Sound("media/music/effect/select.mp3")  # press ENTER
        # 배경음악 경로
        self.death_sound = "media/music/effect/death.mp3"
        self.bgm_path = "media/music/bgm/game_over_bgm.mp3"
        
        # 초기화 변수
        self.frame_delay = 60
        
        self.current_death_frame = 0
        self.max_death_frame = 16
        self.move_death_dist = -4
        
        self.current_gameover_frame = 0
        self.max_gameover_frame = 11
        
        self.current_endtext_frame = 0
        self.max_endtext_frame = len(self.end_text) + 1
        
        self.is_text_visible = False
        
        self.death_id = None
        self.death_end_id = None
        self.alpha_id = None
        self.alpha_end_id = None
        self.tiping_id = None
        self.tiping_end_id = None 
        self.blink_id = None
    
    
    def run(self):
        pass
    
    
    def pack(self, player_stat):
        super().pack()
        
        self.player_ani = self.canvas.create_image(player_stat['x_pos'], player_stat['y_pos'], image=self.player_img)
        
        pygame.mixer.music.load(self.death_sound)
        pygame.mixer.music.play()
        
        self.runAnimation(player_stat['x_pos'], player_stat['y_pos'])
        self.window.after(1000, self.startGameOverBgm)
    
    def unpack(self):
        super().unpack()
        pygame.mixer.music.stop()
        self.resetSceneState()
    
    
    def keyPressHandler(self, event):
        if event.keycode == self.setting.KEY_ENTER:
            self.select_sound.play()
            self.gotoScene(0)
    
    
    def gotoScene(self, idx):
        self.scene_change.sceneChange(idx)
    
    
    def startGameOverBgm(self):
        pygame.mixer.music.load(self.bgm_path)
        pygame.mixer.music.play(loops=-1)
    
    
    # 애니메이션 구현 함수
    def runAnimation(self, x_pos, y_pos):
        start_x_pos = x_pos + 32
        start_y_pos = y_pos - 32
        
        self.temp_rectangle = self.canvas.create_rectangle(start_x_pos, start_y_pos, start_x_pos + 64, start_y_pos + 64, fill='black')
        
        self.deathPlayerAnimation()
    
    def deathPlayerAnimation(self):
        if self.current_death_frame < self.max_death_frame:
            self.canvas.move(self.temp_rectangle, self.move_death_dist, 0)
            self.current_death_frame += 1
            self.death_id = self.window.after(self.frame_delay, self.deathPlayerAnimation)
        else:
            self.canvas.delete(self.temp_rectangle)
            self.canvas.delete(self.player_ani)
            self.death_end_id = self.window.after(self.frame_delay, self.gameoverTextAnimation)
    
    def gameoverTextAnimation(self):
        self.gameover_text = self.canvas.create_text(
            200, 200,
            text="GAME\nOVER",
            fill='white',
            font=('Consolas', 40, 'bold'),
            anchor='center'
        )
        
        self.temp_mask = self.canvas.create_image(160, 160, image=self.fader_masks[0], anchor='center')
        
        self.gameoverAlphaAnimation()
    
    def gameoverAlphaAnimation(self):
        if self.current_gameover_frame < self.max_gameover_frame:
            self.canvas.itemconfig(self.temp_mask, image=self.fader_masks[self.current_gameover_frame])
            self.current_gameover_frame += 1
            self.alpha_id = self.window.after(self.frame_delay, self.gameoverAlphaAnimation)
        else:
            self.canvas.delete(self.temp_mask)
            self.alpha_end_id = self.window.after(self.frame_delay, self.endAnimation)
    
    def endAnimation(self):
        self.text_animation = self.canvas.create_text(
            200, 400,
            text=self.end_text[0],
            fill='white',
            anchor='center',
            justify='center',
            font=('Malgun Gothic', 16)
        )
        
        self.tipingAnimation()
    
    def tipingAnimation(self):
        if self.current_endtext_frame < self.max_endtext_frame:
            self.canvas.itemconfig(self.text_animation, text=self.end_text[:self.current_endtext_frame])
            self.current_endtext_frame += 1
            self.tiping_id = self.window.after(self.frame_delay, self.tipingAnimation)
        else:
            self.tiping_end_id = self.tiping_end_id = self.window.after(self.frame_delay, self.blinkPressText)
    
    def blinkPressText(self):
        self.canvas.itemconfig(self.press_text, text="") if self.is_text_visible else self.canvas.itemconfig(self.press_text, text="< press ENTER to play >")
        self.is_text_visible = not self.is_text_visible
        self.blink_id = self.window.after(300, self.blinkPressText)
    
    
    def resetSceneState(self):
        self.canvas.delete('all')
        
        self.current_death_frame = 0
        self.current_gameover_frame = 0
        self.current_endtext_frame = 0
        
        self.press_text = self.canvas.create_text(
            200, 500,
            text="",
            fill='white',
            anchor='center',
            font = ('Consolas', 12)
        )
        
        if self.death_id:
            self.window.after_cancel(self.death_id)
            self.death_id = None
            
        if self.death_end_id:
            self.window.after_cancel(self.death_end_id)
            self.death_end_id = None
        
        if self.alpha_id:
            self.window.after_cancel(self.alpha_id)
            self.alpha_id = None
        
        if self.alpha_end_id:
            self.window.after_cancel(self.alpha_end_id)
            self.alpha_end_id = None
            
        if self.tiping_id:
            self.window.after_cancel(self.tiping_id)
            self.tiping_id = None
            
        if self.tiping_end_id:
            self.window.after_cancel(self.tiping_end_id)
            self.tiping_end_id = None
    
        if self.blink_id:
            self.window.after_cancel(self.blink_id)
            self.blink_id = None
        
        self.is_text_visible = False
# ------------------------------------------------------------



# 보스전
# ------------------------------------------------------------
class SpagettiBossScene(BaseScene):
    def __init__(self, scene_change):
        super().__init__(scene_change)
        self.canvas = Canvas(self.window, bg="white")
        
        # 에셋 로드, 게임 배치
        self.bg_img = PhotoImage(file="media/image/backgrounds/main_bg.png")
        self.canvas.create_image(0,0, image=self.bg_img, anchor="nw", tags="backgrounds")
        
        self.fader_mask = PhotoImage(file="media/image/backgrounds/fader_mask.png")
        
        self.player_img = PhotoImage(file="media/image/entities/player/player.png")
        self.cursor_img = PhotoImage(file = "media/image/entities/player/cursor.png")
        self.player = Player(self.canvas, self.player_img, self.cursor_img)
        
        self.spagetti_imgs = [PhotoImage(file="media/image/entities/boss/spagetti/spagetti01.png") for _ in range(20)] + [PhotoImage(file="media/image/entities/boss/spagetti/spagetti02.png") for _ in range(20)]
        self.spagetti = self.canvas.create_image(200, 100, image=self.spagetti_imgs[0], anchor='center', tags="spagetti")
        
        self.meatball_img = PhotoImage(file="media/image/entities/boss/spagetti/meatball.png")
        
        self.coffee_img = PhotoImage(file = "media/image/entities/items/coffee.png")
        self.deadline_img = PhotoImage(file = "media/image/entities/items/deadline.png")
        self.drink_img = PhotoImage(file="media/image/entities/boss/items/drink.png")
        
        comment_forder_path = "media/image/entities/boss/useless_comment/comment_block/"
        self.comment_images = [PhotoImage(file=os.path.join(comment_forder_path, filename)) for filename in sorted(os.listdir(comment_forder_path)) if filename.endswith(".png")]
        
        warning_forder_path = "media/image/entities/boss/useless_comment/warning_block/"
        self.warning_images = [PhotoImage(file=os.path.join(warning_forder_path, filename)) for filename in sorted(os.listdir(warning_forder_path)) if filename.endswith(".png")]
        
        self.score_text = self.canvas.create_text(
            380, 60,
            text="",
            fill = "white",
            font = ('Consolas', 14),
            anchor = "e"
        )

        self.hp_full_img = PhotoImage(file = "media/image/ui_elements/hp_bar/hp_full.png")
        self.hp_empty_img = PhotoImage(file = "media/image/ui_elements/hp_bar/hp_empty.png")
        
        self.tangle_bar_bg = None
        self.tangle_bar_fill = None
        self.tangle_text_value = None


        # 일시정지 관련
        self.pause_btn = Button(self.window, text=" || ", command=self.pause_mode)
        
        self.continue_btn = Button(self.window, text="계속하기", font=('Malgun Gothic', 12), command=self.unpause_mode)
        self.return_btn = Button(self.window, text="돌아가기", font=('Malgun Gothic', 12), command=lambda: self.gotoScene(0))
        
        self.pause_menu_list = [self.continue_btn, self.return_btn]
        
        
        # 효과음 로드
        self.select_sound = self.sounds.Sound("media/music/effect/select.mp3")  # 메뉴 선택
        self.shoot_sound = self.sounds.Sound("media/music/effect/shoot.mp3")    # 발사
        self.death_sound = self.sounds.Sound("media/music/effect/death.mp3")    # 파괴 또는 점수 잃음
        self.buff_sound = self.sounds.Sound("media/music/effect/buff.mp3")      # 버프
        self.debuff_sound = self.sounds.Sound("media/music/effect/debuff.mp3")  # 디버프
        
        # 배경 음악 경로
        self.vs_boss_bgm_path = "media/music/bgm/vs_boss_bgm.mp3"
        self.low_hp_bgm_path = "media/music/bgm/low_hp_bgm.mp3"
        
        
        # 초기화 변수
        self.tangle_gauge = 100
        self.spagetti_img_idx = 0
        
        self.mob_list = []
        self.mob_id = 0
        
        self.comment_list = []
        self.comment_id = 0
        self.comment_len = len(self.comment_images)
        self.is_comment_in = False
        
        self.comment_timer_id = None
        self.comment_start_time = 0.0
        self.comment_remaining_time = 0
        
        self.warning_delay_id = None
        self.warning_start_time = 0.0
        self.warning_remaining_time = 0
        self.paused_warning_info = None
        
        self.create_rate = 70
        
        self.speed = 5
        self.speed_timer_id = None
        self.speed_start_time = 0.0
        self.speed_remaining_time = 0
        
        self.is_drink_boosted = False
        self.drink_timer_id = None
        self.drink_start_time = 0.0
        self.drink_remaining_time = 0
        
        self.is_animation_end = False
        self.frame_delay = 300
        
        self.current_blink_frame = 0
        self.max_blink_frame = 3
        self.blink_id = None
        self.blink_text = None
        
        self.is_low_hp_bgm = False
        
        self.BOSS_SCORE = 10000
        
        self.is_paused = False
        self.pause_menu_idx = 0


    def run(self):
        try:
            if not self.is_animation_end:
                return
            
            if self.is_paused:
                return
            
            # 보스전 격파
            if self.tangle_gauge <= 0:
                last_player_pos = self.player.getPos()
                self.scene_change.sceneChange(6, x_pos=last_player_pos[0], y_pos=last_player_pos[1], score=self.player.score, hp=self.player.hp, boss_round=(self.player.score+self.BOSS_SCORE) // self.BOSS_SCORE)
            
            # 게임 오버 제어
            if self.player.hp <= 0:
                last_player_pos = self.player.getPos()
                self.scene_change.sceneChange(4, x_pos = last_player_pos[0], y_pos = last_player_pos[1], score=self.player.score)
            
            self.canvas.itemconfig(self.spagetti, image=self.spagetti_imgs[self.spagetti_img_idx])
            self.spagetti_img_idx = (self.spagetti_img_idx + 1) % len(self.spagetti_imgs)
            
            cursors = self.canvas.find_withtag("cursor")
            self.display(self.speed)
            for cs in cursors:
                self.canvas.move(cs, 0, -10)
                if self.canvas.coords(cs)[1] < 0:
                    self.canvas.delete(cs)
            self.manageMob()
            self.manageUselessComments()
        
        except TclError:
            return

    
    def pack(self, player_stat):
        super().pack()
        
        self.player.tp(player_stat['x_pos'], player_stat['y_pos'])
        
        self.player.score = player_stat['score']
        self.player.hp = player_stat['hp']
        
        if self.player.hp > 1:
            pygame.mixer.music.load(self.vs_boss_bgm_path)
            pygame.mixer.music.play(loops=-1)
            self.is_low_hp_bgm = False
        else:
            pygame.mixer.music.load(self.low_hp_bgm_path)
            pygame.mixer.music.play(loops=-1)
            self.is_low_hp_bgm = True
        
        self.start_fader = self.canvas.create_image(0, 0, image=self.fader_mask, anchor='nw', tags="fader")
        self.startTextBlinkAnimation()

    
    def unpack(self):
        super().unpack()
        self.resetGameState()
        pygame.mixer.music.stop()
        self.pause_btn.place_forget()
    
    
    def keyPressHandler(self, event):
        if event.keycode == self.setting.KEY_ESC and self.is_animation_end:
            if self.is_paused:
                self.unpause_mode()
            else:
                self.pause_mode()
        else:
            self.keys.add(event.keycode)
        
        if self.is_paused:
            if event.keycode == self.setting.KEY_ENTER:
                self.select_sound.play()
                if self.pause_menu_idx == 0:
                    self.unpause_mode()
                elif self.pause_menu_idx == 1:
                    self.gotoScene(0)
                
            elif event.keycode == self.setting.KEY_UP:
                self.select_sound.play()
                self.pause_menu_idx = (self.pause_menu_idx - 1) % 2
                self.updateFocusDisplay()
            elif event.keycode == self.setting.KEY_DOWN:
                self.select_sound.play()
                self.pause_menu_idx = (self.pause_menu_idx + 1) % 2
                self.updateFocusDisplay()
        
        if not self.is_paused:
            if event.keycode == self.setting.KEY_SHOOT:
                self.shoot_sound.play()
                self.player.shoot()
    
    
    def changeBGM(self, is_low_hp):
        # hp가 1 이하이고 현재 low_hp_bgm을 재생중이 아닐 때
        if is_low_hp and not self.is_low_hp_bgm:
            pygame.mixer.music.load(self.low_hp_bgm_path)
            pygame.mixer.music.play(loops=-1)
            self.is_low_hp_bgm = True
        
        # hp가 2 이상이고 low_hp_bgm 재생중일 때
        elif not is_low_hp and self.is_low_hp_bgm:
            pygame.mixer.music.load(self.vs_boss_bgm_path)
            pygame.mixer.music.play(loops=-1)
            self.is_low_hp_bgm = False
    
    
    # 디스플레이 조작
    def updateScoreDisplay(self):
        self.canvas.itemconfig(self.score_text, text = f"SCORE: {self.player.score}")
    
    def showComment(self, comment, entity=None, spagetti=None):
        x_pos, y_pos = 0, 0
        
        if entity is not None:
            entity_pos = entity.getPos()
            entity_width, entity_height = entity.getHalfSize()
        
        if spagetti is not None:
            entity_pos = self.canvas.coords(self.spagetti)
            entity_width = self.spagetti_imgs[0].width() // 2
            entity_height = self.spagetti_imgs[0].height() // 2
        
        x_pos = random.randint(int(entity_pos[0] - entity_width), int(entity_pos[0] + entity_width))
        y_pos = random.randint(int(entity_pos[1] - entity_height), int(entity_pos[1] + entity_height))
        
        text = (f"+{comment}" if comment > 0 else f"{comment}") if isinstance(comment, (int, float)) else comment
        
        
        if spagetti is not None:
            comment_text = self.canvas.create_text(
                x_pos, y_pos,
                text = text,
                fill = "red" if comment > 0 else "green",
                font = ('Consolas', 20, 'bold'),
                tags = "comment"
            )

        else:
            comment_text = self.canvas.create_text(
                x_pos, y_pos,
                text = text,
                fill = ("green" if comment > 0 else "red") if isinstance(comment, (int, float)) else "blue",
                font = ('Consolas', 12, "bold"),
                tags = "comment"
            )
        
        self.window.after(500, lambda id_to_delete = comment_text: self.canvas.delete(id_to_delete))
    
    def updateHpDisplay(self):
        start_x = 380
        max_hp = 3
        
        self.canvas.delete("hp")
        
        for i in range(max(max_hp, self.player.hp)):
            x_pos = start_x - i * 15
            if i < self.player.hp:
                self.canvas.create_image(x_pos, 90, image=self.hp_full_img, tags="hp")
            else:
                self.canvas.create_image(x_pos, 90, image=self.hp_empty_img, tags="hp")
        
        if self.player.hp <= 1:
            self.changeBGM(True)
        else:
            self.changeBGM(False)
    
    def updateTangleDisplay(self):
        MAX_GAUGE = 100
        MAX_BAR_WIDTH = 300
        
        current_ratio = self.tangle_gauge / MAX_GAUGE
        
        current_bar_width = MAX_BAR_WIDTH * current_ratio
        
        bg_coords = self.canvas.coords(self.tangle_bar_bg)
        x1_bg, y1_bg, x2_bg, y2_bg = bg_coords
        
        new_x2 = x1_bg + current_bar_width
        
        self.canvas.coords(self.tangle_bar_fill, x1_bg, y1_bg, new_x2, y2_bg)
        self.canvas.itemconfig(self.tangle_text_value, text=f"{self.tangle_gauge} / 100")
        
        if self.tangle_gauge > 50:
             self.canvas.itemconfig(self.tangle_bar_fill, fill="green")
        elif self.tangle_gauge > 20:
             self.canvas.itemconfig(self.tangle_bar_fill, fill="yellow")
        else:
             self.canvas.itemconfig(self.tangle_bar_fill, fill="red")
    
    
    # 플레이어 동작
    def display(self, speed):
        for key in self.keys:
            pos = self.player.getPos()
            half_width, half_height = self.player.getHalfSize()
            
            if key == self.setting.KEY_RIGHT and pos[0] + half_width <= self.setting.CANVAS_WIDTH:
                self.player.move(speed, 0)
            if key == self.setting.KEY_LEFT and pos[0] - half_width >= 0:
                self.player.move(-speed, 0)
            if key == self.setting.KEY_UP and pos[1] - half_height >= 0:
                self.player.move(0, -speed)
            if key == self.setting.KEY_DOWN and pos[1] + half_height <= self.setting.CANVAS_HEIGHT:
                self.player.move(0, speed)
    
    
    # 다른 몹과 겹치지 않는 x좌표 생성
    def getSafeX(self, img):
        max_attempts = 20
        
        img_half_width = img.width() // 2
        Y_CHECK = img.height() + 50
        
        min_x = img_half_width
        max_x = self.setting.CANVAS_WIDTH - img_half_width
        
        for _ in range(max_attempts):
            new_x = random.randint(min_x, max_x)
            
            is_safe = True
            for mob in self.mob_list:
                mob_pos = mob.getPos()
                code_half_width, _ = mob.getHalfSize()
                
                width_spacing = img_half_width + code_half_width
                distance_x = abs(new_x - mob_pos[0])
                
                if mob_pos[1] < Y_CHECK and distance_x < width_spacing:
                    is_safe = False
                    break
            
            if is_safe:
                return new_x
        
        return None
    
    # 몹 관리자
    def manageMob(self):
        for mob in self.mob_list:
            mob.move()
        
        create_rand = random.randint(0, self.create_rate)
        if create_rand == 0:
            mob_rand = random.randint(0, 100)
            # 미트볼 76%
            if 0 <= mob_rand < 76:
                x_pos = self.getSafeX(self.meatball_img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, self.meatball_img, self.mob_id, 'meatball', x_pos))
                    self.mob_id += 1
            # 회복 8%
            elif 76 <= mob_rand < 84:
                x_pos = self.getSafeX(self.coffee_img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, self.coffee_img, self.mob_id, 'heart', x_pos))
                    self.mob_id += 1
            # 스피드업 8%
            elif 84 <= mob_rand < 92:
                x_pos = self.getSafeX(self.deadline_img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, self.deadline_img, self.mob_id, 'deadline', x_pos))
                    self.mob_id += 1
            # 에너지 드링크 8%
            else:
                x_pos = self.getSafeX(self.drink_img)
                if x_pos is not None:
                    self.mob_list.append(Mob(self.canvas, self.drink_img, self.mob_id, 'rink', x_pos))
                    self.mob_id += 1
        
        
        BASE_SCORE = 100
        SCALING = 3
        
        player_pos = self.player.getPos()
        player_width, player_height = self.player.getHalfSize()
        
        # 커서가 몹에 닿았을 때
        cursors = self.canvas.find_withtag("cursor")
        for cs in cursors:
            cs_pos = self.canvas.coords(cs)
            for mob in self.mob_list:
                mob_pos = mob.getPos()
                mob_width, mob_height = mob.getHalfSize()
                
                if mob_pos[0] - mob_width < cs_pos[0] < mob_pos[0] + mob_width and mob_pos[1] - mob_height < cs_pos[1] < mob_pos[1] + mob_height:
                    if mob.id[0] != 'm':
                        continue
                    # 미트볼 - 엉킴 게이지 감소
                    bonus_score = int((self.setting.CANVAS_HEIGHT - mob_pos[1]) / SCALING)
                    total_score = BASE_SCORE + bonus_score
                    
                    self.player.scoreManage(total_score)
                    self.updateScoreDisplay()
                    self.showComment(total_score, entity=mob)
                    
                    
                    decrease_amount = random.randint(3, 7)
                    if self.is_drink_boosted:
                        decrease_amount *= 2
                    self.tangle_gauge = max(0, self.tangle_gauge - decrease_amount)
                    
                    self.updateTangleDisplay()
                    self.showComment(-decrease_amount, spagetti=True)
                    
                    self.death_sound.play()
                    
                    self.canvas.delete(mob.getId())
                    self.mob_list.pop(self.mob_list.index(mob))
                    self.canvas.delete(cs)

        # 몹과 클레이어가 충돌했을 때
        for mob in self.mob_list:
            mob_pos = mob.getPos()
            mob_width, mob_height = mob.getHalfSize()
            
            # 히트박스
            x_hit = (
                mob_pos[0] - mob_width < player_pos[0] + player_width and 
                mob_pos[0] + mob_width > player_pos[0] - player_width
            )
            y_hit = (
                mob_pos[1] - mob_height < player_pos[1] + player_height and
                mob_pos[1] + mob_height > player_pos[1] - player_height
            )
            
            if x_hit and y_hit:
                # 미트볼 - hp 소실, 엉킴 게이지 증가
                if mob.id[0] == 'm':
                    self.player.hpManage(-1)
                    self.updateHpDisplay()
                    
                    increase_amount = random.randint(3, 7)
                    self.tangle_gauge = min(self.tangle_gauge + increase_amount, 100)
                    self.showComment(increase_amount, spagetti=True)
                    self.updateTangleDisplay()
                    self.death_sound.play()
                # 커피 - hp 회복
                elif mob.id[0] == 'h':
                    self.player.hp += 1
                    self.updateHpDisplay()
                    self.showComment("체력 회복!", entity=self.player)
                    self.buff_sound.play()
                # 데드라인 - 5초 스피드업
                elif mob.id[0] == 'd':
                    self.speed *= 2
                    self.decreaseSpeedAfterDelay(5000)
                    self.showComment("스피드업!", entity=self.player)
                    self.buff_sound.play()
                # 에너지 드링크 - 5초 엉킴 게이지 감소 업
                elif mob.id[0] == 'r':
                    self.startDrinkBoost()
                    self.showComment("데미지 2배!", self.player)
                    self.buff_sound.play()
                
                self.canvas.delete(mob.getId())
                self.mob_list.pop(self.mob_list.index(mob))
        
        # 몹이 화면을 끝까지 이동했을 때
        for mob in self.mob_list:
            if mob.getPos()[1] > self.setting.CANVAS_HEIGHT:
                self.canvas.delete(mob.getId())
                self.mob_list.pop(self.mob_list.index(mob))
    
    
    # 쓸모 없는 주석
    def startCommentTimer(self, warning_remaining_time=3000, comment_remaining_time=7000):
        if self.comment_timer_id is not None:
            self.window.after_cancel(self.comment_timer_id)
        
        if self.warning_delay_id is not None:
            self.window.after_cancel(self.warning_delay_id)
        
        comment_idx = random.randint(0, self.comment_len-1)
        
        x_pos = random.randint(0, 400)
        y_pos = random.randint(300, 720 - self.warning_images[comment_idx].height() // 2 - 30)
        
        warning = self.canvas.create_image(x_pos, y_pos, image=self.warning_images[comment_idx], tags="warning")
        
        self.current_warning_info = {'id': warning, 'x': x_pos, 'y': y_pos, 'idx': comment_idx}
        
        self.warning_start_time = time.time()
        self.warning_delay_id = self.window.after(warning_remaining_time, lambda x=x_pos, y=y_pos, warning=warning, idx=comment_idx: self.createUselessComment(x, y, warning, idx))
        
        self.comment_start_time = time.time()
        self.comment_timer_id = self.window.after(comment_remaining_time, self.startCommentTimer)
    
    def createUselessComment(self, x_pos, y_pos, warning, idx):
        self.canvas.delete(warning)
        new_comment = UselessComment(self.canvas, self.comment_images[idx], x_pos, y_pos)
        self.comment_list.append(new_comment)
        new_comment.startTangleIncrease(self)
    
    def manageUselessComments(self):
        player_pos = self.player.getPos()
        player_width, player_height = self.player.getHalfSize()
        
        for comment in self.comment_list:
            comment_pos = comment.getPos()
            comment_width, comment_height = comment.getHalfSize()
            
            # 히트박스
            x_hit = (
                comment_pos[0] - comment_width < player_pos[0] + player_width and 
                comment_pos[0] + comment_width > player_pos[0] - player_width
            )
            y_hit = (
                comment_pos[1] - comment_height < player_pos[1] + player_height and
                comment_pos[1] + comment_height > player_pos[1] - player_height
            )

            if x_hit and y_hit:
                self.is_comment_in = True
                if self.speed_timer_id is not None:
                    self.window.after_cancel(self.speed_timer_id)
                    self.speed_timer_id = None
                    self.speed_remaining_time = 0
                self.speed = 2
            else:
                self.is_comment_in = False
            
            cursors = self.canvas.find_withtag("cursor")
            for cs in cursors:
                cs_pos = self.canvas.coords(cs)
                if comment_pos[0] - comment_width < cs_pos[0] < comment_pos[0] + comment_width and comment_pos[1] - comment_height < cs_pos[1] < comment_pos[1] + comment_height:
                    self.death_sound.play()
                    self.comment_list.remove(comment)
                    comment.destroy(self)
                    self.canvas.delete(cs)
        
        if not self.is_comment_in and self.speed == 2:
            self.speed = 5
    
    
    # 스피드 관련 함수
    def decreaseSpeed(self):
        self.showComment("스피드 다운!", self.player)
        self.debuff_sound.play()
        self.speed = max(self.speed // 2, 5)
    
    def decreaseSpeedAfterDelay(self, delay_ms):
        self.speed_start_time = time.time()
        self.speed_timer_id = self.window.after(delay_ms, self.decreaseSpeed)
    
    
    # 에너지 드링크 관련 함수
    def startDrinkBoost(self, remaining_time = 5000):
        if self.drink_timer_id is not None:
            self.window.after_cancel(self.drink_timer_id)
        else:
            self.is_drink_boosted = True
        
        self.drink_start_time = time.time()
        self.drink_timer_id = self.window.after(remaining_time, self.endDrinkBoost)

    def endDrinkBoost(self):
        self.showComment("데미지 감소!", entity=self.player)
        self.is_drink_boosted = False
        self.debuff_sound.play()
        self.drink_timer_id = None
    
    
    # 일시정지 관련 함수
    def pause_mode(self):
        self.is_paused = True
        pygame.mixer.music.pause()
        self.canvas.create_image(0, 0, image=self.fader_mask, anchor="nw", tags="fader")
        
        if self.comment_timer_id is not None:
            self.window.after_cancel(self.comment_timer_id)
            temp_time = time.time() - self.comment_start_time
            self.comment_remaining_time = max(0, 7000 - int(temp_time * 1000))
            self.comment_timer_id = None
        
        if self.warning_delay_id is not None:
            self.window.after_cancel(self.warning_delay_id)
            temp_time = time.time() - self.warning_start_time
            self.warning_remaining_time = max(0, 3000 - int(temp_time * 1000))
            self.warning_delay_id = None
        
        # 남은 스피드 업 시간 기록
        if self.speed_timer_id is not None:
            self.window.after_cancel(self.speed_timer_id)
            temp_time = time.time() - self.speed_start_time
            self.speed_remaining_time = max(0, 5000 - int(temp_time * 1000))
            self.speed_timer_id = None
        
        # 남은 데미지 부스트 시간 기록
        if self.drink_timer_id is not None:
            self.window.after_cancel(self.drink_timer_id)
            temp_time = time.time() - self.drink_start_time
            self.drink_remaining_time = max(0, 5000 - int(temp_time * 1000))
            self.drink_timer_id = None
        
        self.pause_btn.place_forget()
        
        self.continue_btn.place(x=200, y=330, width=100, height=30, anchor="center")
        self.return_btn.place(x=200, y=390, width=100, height=30, anchor="center")
        
        self.pause_menu_idx = 0
        self.updateFocusDisplay()
    
    def unpause_mode(self):
        self.continue_btn.place_forget()
        self.return_btn.place_forget()
        
        self.canvas.delete("fader")
        
        self.pause_btn.place(x=360, y=10)
        
        
        for comment in self.comment_list:
            if not comment.is_destroyed:
                comment.startTangleIncrease(self)
        
        
        if self.warning_remaining_time > 0 and self.current_warning_info is not None:
            info = self.current_warning_info
            
            self.warning_start_time = time.time()
            self.warning_delay_id = self.window.after(self.warning_remaining_time, lambda x=info['x'], y=info['y'], warning=info['id'], idx=info['idx']: self.createUselessComment(x, y, warning, idx))
            self.warning_remaining_time = 0
            
        if self.comment_remaining_time > 0:
            self.comment_timer_id = self.window.after(self.comment_remaining_time, self.startCommentTimer)
            self.comment_remaining_time = 0
        
        elif self.warning_remaining_time == 0 and self.comment_remaining_time == 0 and self.current_warning_info is None:
            self.startCommentTimer()
        
        
        if self.speed_remaining_time > 0:
            self.decreaseSpeedAfterDelay(self.speed_remaining_time)
            self.speed_remaining_time = 0
        
        if self.drink_remaining_time > 0:
            self.startDrinkBoost(self.drink_remaining_time)
            self.drink_remaining_time = 0
        
        pygame.mixer.music.unpause()
        self.is_paused = False
    
    def updateFocusDisplay(self):
        for i, button in enumerate(self.pause_menu_list):
            if i == self.pause_menu_idx:
                button.config(bg='#f0f0f0', fg='#000080', font=('Malgun Gothic', 12, 'bold'))
            else:
                button.config(bg='SystemButtonFace', fg='black', font=('Malgun Gothic', 12))
    
    
    # 애니메이션 관련 함수
    def startTextBlinkAnimation(self):
        if self.current_blink_frame < self.max_blink_frame:
            if self.blink_text is None:
                self.blink_text = self.canvas.create_text(
                    200, 300,
                    text="스파게티 코드\n발생",
                    fill='red',
                    anchor='center',
                    justify='center',
                    font=('Malgun Gothic', 40, 'bold')
                )
                self.current_blink_frame += 1
            else:
                self.canvas.delete(self.blink_text)
                self.blink_text = None
            self.window.after(self.frame_delay, self.startTextBlinkAnimation)
        else:
            self.window.after(self.frame_delay, self.startEndAnimation)
    
    def startEndAnimation(self):
        if self.blink_text is not None:
                self.canvas.delete(self.blink_text)
                self.blink_text = None
        self.canvas.delete(self.start_fader)
        
        self.updateScoreDisplay()
        self.updateHpDisplay()
        self.pause_btn.place(x=360, y=10)
        
        BAR_WIDTH = 300
        BAR_HEIGHT = 20
        CENTER_X = 200
        TOP_Y = 200

        self.tangle_bar_bg = self.canvas.create_rectangle(
            CENTER_X - BAR_WIDTH/2, TOP_Y - BAR_HEIGHT/2,
            CENTER_X + BAR_WIDTH/2, TOP_Y + BAR_HEIGHT/2,
            fill="gray", 
            outline="white", 
            width=2,
            tags="tangle_bar"
        )
        
        self.tangle_bar_fill = self.canvas.create_rectangle(
            CENTER_X - BAR_WIDTH/2, TOP_Y - BAR_HEIGHT/2,
            CENTER_X - BAR_WIDTH/2, TOP_Y + BAR_HEIGHT/2,
            fill="red", 
            tags="tangle_bar"
        )
        
        self.tangle_text_value = self.canvas.create_text(
            CENTER_X, TOP_Y,
            text="100 / 100",
            fill='white',
            font=('Consolas', 10, 'bold'),
            tags="tangle_bar"
        )
        self.updateTangleDisplay()
        
        self.startCommentTimer()
        
        self.is_animation_end = True
    
    
    def gotoScene(self, idx):
        if self.is_paused:
            self.unpause_mode()
        self.scene_change.sceneChange(idx)
    
    
    def resetGameState(self):
        self.canvas.delete("all")
        
        self.canvas.create_image(0,0, image=self.bg_img, anchor="nw", tags="backgrounds")
        
        self.player = Player(self.canvas, self.player_img, self.cursor_img)
        
        self.spagetti = self.canvas.create_image(200, 100, image=self.spagetti_imgs[0], anchor='center', tags="spagetti")
        
        self.score_text = self.canvas.create_text(
            380, 60,
            text = f"SCORE: {self.player.score}",
            fill = "white",
            font = ('Consolas', 14),
            anchor = "e"
        )
        
        self.updateHpDisplay()
        
        self.tangle_gauge = 100
        self.spagetti_img_idx = 0
        
        
        self.mob_list = []
        self.mob_id = 0
        
        for comment in self.comment_list:
            comment.destroy(self)
        self.comment_list = []
        self.canvas.delete("warning")
        
        if self.comment_timer_id is not None:
            self.window.after_cancel(self.comment_timer_id)
            self.comment_timer_id = None
        self.comment_start_time = 0.0
        self.comment_remaining_time = 0
        
        if self.warning_delay_id is not None:
            self.window.after_cancel(self.warning_delay_id)
            self.warning_delay_id = None
        self.warning_start_time = 0.0
        self.warning_remaining_time = 0
        self.paused_warning_info = None
        
        self.tangle_bar_bg = None
        self.tangle_bar_fill = None
        self.tangle_text_value = None

        self.create_rate = 70
        
        self.speed = 5
        if self.speed_timer_id is not None:
            self.window.after_cancel(self.speed_timer_id)
            self.speed_timer_id = None
        self.speed_start_time = 0.0
        self.speed_remaining_time = 0
        
        self.is_drink_boosted = False
        if self.drink_timer_id is not None:
            self.window.after_cancel(self.drink_timer_id)
            self.drink_timer_id = None
        
        self.is_animation_end = False
        
        self.current_blink_frame = 0
        if self.blink_id is not None:
            self.window.after_cancel(self.blink_id)
            self.blink_id = None
        self.blink_text = None
        
        self.is_paused = False
        self.pause_menu_idx = 0
        
        self.is_low_hp_bgm = False
        
        self.keys.clear()
# ------------------------------------------------------------



# 클리어 애니메이션
# ------------------------------------------------------------
class VsBossClearScene(BaseScene):
    def __init__(self, scene_change):
        super().__init__(scene_change)
        self.canvas = Canvas(self.window, bg="white")
        
        # 에셋 로드, 게임 배치
        self.bg_img = PhotoImage(file="media/image/backgrounds/main_bg.png")
        self.canvas.create_image(0,0, image=self.bg_img, anchor="nw", tags="backgrounds")
        
        self.player_img = PhotoImage(file="media/image/entities/player/player.png")
        
        self.spagetti_img = PhotoImage(file="media/image/entities/boss/spagetti/spagetti01.png")
        self.spagetti = self.canvas.create_image(200, 100, image=self.spagetti_img, anchor='center')
        
        self.fader_mask = PhotoImage(file="media/image/backgrounds/fader_mask.png")
        
        self.chat = "...고무적이군."
        
        # 효과음 로드
        self.select_sound = self.sounds.Sound("media/music/effect/select.mp3")  # press ENTER
        self.death_sound = self.sounds.Sound("media/music/effect/death.mp3")    # spagetti 0/100
        
        # 초기화 변수
        self.frame_delay = 120
        
        self.current_chat_frame = 0
        self.max_chat_frame = len(self.chat) + 1
        self.chat_id = None
    
    def run(self):
        pass

    
    def pack(self, player_stat):
        super().pack()
        
        self.death_sound.play()
        
        self.player_stat = player_stat
        self.canvas.create_image(self.player_stat['x_pos'], self.player_stat['y_pos'], image=self.player_img)
        
        self.canvas.create_image(0,0, image=self.fader_mask, anchor="nw", tags="backgrounds")
        
        self.canvas.create_image(270, 550, image=self.spagetti_img, anchor="center")
        
        self.chat_window = PhotoImage(file="media/image/ui_elements/interface_panels/chat_window.png")
        self.canvas.create_image(200, 630, image=self.chat_window, anchor="center")
        self.canvas.create_text(
            30, 580,
            text="스파게티 코드",
            fill="white",
            anchor='nw',
            font=('Malgun Gothic', 12, 'bold')
        )
        
        self.chat_animation = self.canvas.create_text(
            30, 615,
            text=self.chat[0],
            fill='black',
            anchor='nw',
            font=('Malgun Gothic', 12)
        )
        
        self.window.after(self.frame_delay, self.tipingAnimation())

    def unpack(self):
        super().unpack()
        
        if self.chat_id is not None:
            self.window.after_cancel(self.chat_id)
            self.chat_id = None
        
        self.resetSceneState()
    
    
    def keyPressHandler(self, event):
        if event.keycode == self.setting.KEY_ENTER:
            self.select_sound.play()
            self.scene_change.sceneChange(1, x_pos=self.player_stat['x_pos'], y_pos=self.player_stat['y_pos'], score=self.player_stat['score'], hp=self.player_stat['hp'], boss_round=self.player_stat['boss_round'])
    
    
    def tipingAnimation(self):
        if self.current_chat_frame < self.max_chat_frame:
            self.canvas.itemconfig(self.chat_animation, text=self.chat[:self.current_chat_frame])
            self.current_chat_frame += 1
            self.chat_id = self.window.after(self.frame_delay, self.tipingAnimation)
    
    
    def gotoScene(self, idx):
        if self.is_paused:
            self.unpause_mode()
        self.scene_change.sceneChange(idx)
        
    
    def resetSceneState(self):
        self.canvas.delete('all')
        
        self.canvas.create_image(0,0, image=self.bg_img, anchor="nw", tags="backgrounds")
        self.canvas.create_image(200, 100, image=self.spagetti_img, anchor='center')
        
        self.current_chat_frame = 0
# ------------------------------------------------------------





# 게임 방법
# ------------------------------------------------------------
class HowToGameScene(BaseScene):
    def __init__(self, scene_change):
        super().__init__(scene_change)
        self.canvas = Canvas(self.window, bg="white")
        
        # 배경 이미지 로드, 설정
        self.bg_img = PhotoImage(file="media/image/backgrounds/title_bg.png")
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw", tags="backgrounds")
        
        # 인터페이스 로드, 설정
        self.interface_img = PhotoImage(file="media/image/ui_elements/interface_panels/interface.png")
        self.canvas.create_image(20, 80, image=self.interface_img, anchor="nw", tags="interface")
        
        # 효과음
        self.select_sound = self.sounds.Sound("media/music/effect/select.mp3")  # 선택
        
        # 메뉴
        self.head_text_list = [
            "게임 방법", 
            "아이템",
            "보스 - 스파게티 코드"
        ]
        self.body_text_list = [
            "버그를 잡으세요!\n\n에러 코드가 맨 아래에 도달하지 못하도록 \n막아야 합니다.\n에러 코드를 찾아 공격을 가해 버그를 \n잡으세요!\n에러 코드에 닿으면 체력이 깎이니\n조심하세요.\n\n옳은 코드는 없애면 안됩니다!\n닿거나 맨 아래까지 도달시켜 점수를\n얻으세요!\n\n정답 코드는 공격하면 안됩니다.\n원래 제대로 작동하는 코드는 건드는 거\n아닙니다!",
            "세 가지의 아이템이 있습니다.\n아이템은 공격으로는 없앨 수 없으며\n닿으면 효과가 발동됩니다.\n\n커피를 먹으면 HP를 1 회복합니다.\n잠 깨려고 커피 먹는 여러분들처럼요.\n\n달력 뭔가요?\n마감 기간입니다! 마감이 다가오면\n타이핑이 빨라집니다.\n연구에 따르면 바퀴벌레는 위기 상황에서\n일시적으로 아이큐가 340 이상으로\n상승한다고 합니다.\n\n바이브 코딩을 해봅시다!\nAI가 버그를 잡아주네요. 모두는\n아니지만요.\n실력은 안 늘겠지만 점수는 늘어요!",
            "10000점마다 스파게티 코드가 발생합니다.\n\n스파게티 코드는 엉킴 게이지라는\n특별한 수치를 갖고 있습니다.\n100%부터 시작하며 0%에 도달하면\n승리할 수 있습니다.\n\n미트볼을 생성할 것입니다.\n미트볼을 없애면 엉킴 게이지를 줄일 수\n있습니다. 먹어서 없애지 마세요.\n\n새로운 아이템, 에너지 드링크입니다.\n에너지 드링크는 일정 시간동안\n엉킴 게이지를 더 많이 줄여줍니다.\n\n뭐 이딴 주석이 다 있죠?\n주석이 나타나면 엉킴 게이지가 천천히\n늘어납니다. 주석 내부로 들어가지\n않도록 조심하세요!"
        ]
        
        self.head_text = self.canvas.create_text(
            40, 110,
            fill='white',
            font=('Malgun Gothic', 16, 'bold'),
            anchor="w",
            text=self.head_text_list[0]
        )
        self.body_text = self.canvas.create_text(
            40, 140,
            fill='black',
            font=('Malgun Gothic', 12),
            anchor="nw",
            text=self.body_text_list[0]
        )
        
        # 버튼 설정
        self.close_btn = Button(self.window, text="X", font=('Consolas', 10), command=lambda: self.gotoScene(0))
        self.about_game_btn = Button(self.window, text="게임 방법", font=('Malgun Gothic', 12), command=lambda: self.btnFunc(0))
        self.about_item_btn = Button(self.window, text="아이템", font=('Malgun Gothic', 12), command=lambda:self.btnFunc(1))
        self.about_boss_btn = Button(self.window, text="보스", font=('Malgun Gothic', 12), command=lambda:self.btnFunc(2))
        
        self.menu_idx = 0
        self.menu_list = [self.about_game_btn, self.about_item_btn, self.about_boss_btn, self.close_btn]
        
        self.updateFocusDisplay()


    def run(self):
        pass
    
    
    def pack(self):
        super().pack()
        
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("media/music/bgm/title_bgm.mp3")
            pygame.mixer.music.play(loops=-1)
        
        self.close_btn.place(x=345, y=100, width=20, height=20)
        self.about_game_btn.place(x=40, y=595, width=100, height=40)
        self.about_item_btn.place(x=150, y=595, width=100, height=40)
        self.about_boss_btn.place(x=260, y=595, width=100, height=40)
    
    def unpack(self):
        super().unpack()
        
        self.menu_idx = 0
        self.btnFunc(self.menu_idx)
        
        self.close_btn.place_forget()
        self.about_game_btn.place_forget()
        self.about_item_btn.place_forget()
        self.about_boss_btn.place_forget()
    
    
    def keyPressHandler(self, event):
        if event.keycode == self.setting.KEY_ESC:
            self.gotoScene(0)
            
        elif event.keycode == self.setting.KEY_LEFT:
            self.select_sound.play()
            self.menu_idx = (self.menu_idx - 1) % 4
            self.updateFocusDisplay()
        
        elif event.keycode == self.setting.KEY_RIGHT:
            self.select_sound.play()
            self.menu_idx = (self.menu_idx + 1) % 4
            self.updateFocusDisplay()
        
        elif event.keycode == self.setting.KEY_ENTER:
            if self.menu_idx == 3:
                self.gotoScene(0)
            else:
                self.btnFunc(self.menu_idx)
    
    
    def gotoScene(self, idx):
        self.select_sound.play()
        self.scene_change.sceneChange(idx)
    
    
    def updateFocusDisplay(self):
        for i, button in enumerate(self.menu_list):
            size = 10 if i == 3 else 12
            font = 'Consolas' if i == 3 else 'Malgun Gothic'
            if i == self.menu_idx:
                button.config(bg='#f0f0f0', fg='#000080', font=(font, size, 'bold'))
            else:
                button.config(bg='SystemButtonFace', fg='black', font=(font, size))
    
    
    def btnFunc(self, idx):
        self.select_sound.play()
        self.canvas.itemconfig(self.head_text, text=self.head_text_list[idx])
        self.canvas.itemconfig(self.body_text, text=self.body_text_list[idx])
        self.menu_idx = idx
        self.updateFocusDisplay()
# ------------------------------------------------------------



# 게임 설정
# ------------------------------------------------------------
class SettingScene(BaseScene):
    def __init__(self, scene_change):
        super().__init__(scene_change)
        self.canvas = Canvas(self.window, bg="white")
        
        # 배경 이미지 로드, 설정
        self.bg_img = PhotoImage(file="media/image/backgrounds/main_bg.png")
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw", tags="backgrounds")
        
        # 인터페이스 이미지 로드, 설정
        self.interface_img = PhotoImage(file="media/image/ui_elements/interface_panels/interface.png")
        self.canvas.create_image(20, 80, image=self.interface_img, anchor="nw", tags="interface")
        
        # 에셋 로드
        self.arrow_selected_img = PhotoImage(file="media/image/ui_elements/key_selection/arrow_selected.png")
        self.arrow_unselected_img = PhotoImage(file="media/image/ui_elements/key_selection/arrow_unselected.png")
        
        self.wasd_selected_img = PhotoImage(file="media/image/ui_elements/key_selection/wasd_selected.png")
        self.wasd_unselected_img = PhotoImage(file="media/image/ui_elements/key_selection/wasd_unselected.png")
        
        # 효과음
        self.select_sound = self.sounds.Sound("media/music/effect/select.mp3")  # 선택
        self.error_sound = self.sounds.Sound("media/music/effect/debuff.mp3")   # 오류 - 변경 필요
        
        
        # 방향키 설정 구현
        self.canvas.create_text(
            40, 110,
            fill='white',
            font=('Malgun Gothic', 16, 'bold'),
            anchor="w",
            text="게임 설정"
        )
        
        self.canvas.create_text(
            40, 140, 
            text="▶ 방향키 설정", 
            fill='black',
            anchor='nw',
            font=('Malgun Gothic', 12, 'bold'),
        )
        
        self.close_btn = Button(self.window, text="X", font=('Consolas', 10), command=lambda: self.gotoScene(0))
        self.arrow_btn = Button(self.window, image=self.arrow_selected_img, command=lambda: self.keysetChangeBtn('arrow'))
        self.wasd_btn = Button(self.window, image=self.wasd_selected_img, command=lambda: self.keysetChangeBtn('wasd'))
        
        self.key_text = self.canvas.create_text(
            40, 300,
            text="현재 방향키는 ↑, ←, ↓, → 입니다.",
            fill='black',
            anchor='nw',
            font=('Malgun Gothic', 12)
        )
        
        
        # 공격키 설정 구현
        self.canvas.create_text(
            40, 350, 
            text="▶ 공격키 설정", 
            fill='black',
            anchor='nw',
            font=('Malgun Gothic', 12, 'bold'),
        )
        
        self.shoot_text = self.canvas.create_text(
            40, 380,
            text="현재 공격키",
            fill='black',
            anchor='nw',
            font=('Malgun Gothic', 12)
        )
        
        self.shoot_btn = Button(self.window, text=f"{self.setting.asciiChar(self.setting.KEY_SHOOT)}", command=self.startChangeShootKey)
        
        # 초기화 변수
        self.is_binding_shoot = False
    
    
    def run(self):
        pass
    
    
    def pack(self):
        super().pack()
        
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("media/music/bgm/title_bgm.mp3")
            pygame.mixer.music.play(loops=-1)
        
        self.close_btn.place(x=345, y=100, width=20, height=20)
        self.arrow_btn.place(x=40, y=170, anchor='nw', width=150, height=120)
        self.wasd_btn.place(x=210, y=170, anchor="nw", width=150, height=120)
        self.shoot_btn.place(x=250, y=375, anchor="nw", width=100, height=30)
        
        self.updateNowDisplay()
    
    def unpack(self):
        super().unpack()
        
        self.is_binding_shoot = False
        
        self.close_btn.place_forget()
        self.arrow_btn.place_forget()
        self.wasd_btn.place_forget()
        self.shoot_btn.place_forget()
    
    
    def keyPressHandler(self, event):
        if self.is_binding_shoot:
            self.changeShootKey(event.keycode)
        elif event.keycode == self.setting.KEY_ESC:
            self.gotoScene(0)
    
    
    def gotoScene(self, idx):
        self.select_sound.play()
        self.scene_change.sceneChange(idx)
    
    
    def keysetChangeBtn(self, key_set):
        res, key = self.setting.changeKeySet(key_set)
        if res:
            self.select_sound.play()
            self.updateNowDisplay()
        else:
            self.error_sound.play()
            asc = self.setting.asciiChar(key)
            message = f"{asc} 키가 중복되거나 사용 불가능합니다."
            self.canvas.itemconfig(self.key_text, text=message, fill='red')
    
    def updateNowDisplay(self):
        if self.setting.NOW_KEY_SET == 'arrow':
            self.arrow_btn.config(image=self.arrow_selected_img)
            self.wasd_btn.config(image=self.wasd_unselected_img)
            self.canvas.itemconfig(self.key_text, text="현재 방향키는 ↑, ←, ↓, → 입니다.", fill='black')
        
        elif self.setting.NOW_KEY_SET == 'wasd':
            self.arrow_btn.config(image=self.arrow_unselected_img)
            self.wasd_btn.config(image=self.wasd_selected_img)
            self.canvas.itemconfig(self.key_text, text="현재 방향키는 W, A, S, D 입니다.", fill='black')
    
    
    def startChangeShootKey(self):
        self.select_sound.play()
        self.is_binding_shoot = True
        self.shoot_btn.config(text="키 입력 대기중...")
    
    def changeShootKey(self, keycode):
        result, key = self.setting.changeShootKey(keycode)
        
        self.is_binding_shoot = False
        
        asc = self.setting.asciiChar(key)
        
        if result and asc:
            self.select_sound.play()
            self.shoot_btn.config(text=f"{asc}")
        else:
            self.error_sound.play()
            self.temp_shoot_text = self.canvas.create_text(
                40, 410,
                text=f"{asc}가 중복되거나 사용 불가능합니다.",
                fill='red',
                font=('Malgun Gothic', 12, 'bold'),
                anchor="nw",
                tags="temp_shoot"
            )
        
        self.window.after(500, self.endChangeShootKey)
    
    def endChangeShootKey(self):
        self.shoot_btn.config(text=f"{self.setting.asciiChar(self.setting.KEY_SHOOT)}")
        self.canvas.delete("temp_shoot")
# ------------------------------------------------------------






# ============================================================
# 제어 클래스
# ============================================================
class SceneChange:
    def __init__(self):
        self.setting = Setting()
        
        self.window = Tk()
        self.window.title("BugCatcher")
        self.window.geometry(f"{self.setting.CANVAS_WIDTH}x{self.setting.CANVAS_HEIGHT}")
        self.window.resizable(0,0)
        
        self.window.bind("<KeyPress>", self.keyPressHandler)
        self.window.bind("<KeyRelease>", self.keyReleaseHandler)
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)
        
        self.title_scene = TitleScene(self)                     # 0
        self.game_scene = MainGameScene(self)                   # 1
        self.how_scene = HowToGameScene(self)                   # 2
        self.setting_scene = SettingScene(self)                 # 3
        self.over_scene = GameOverScene(self)                   # 4
        self.boss_spagetti_scene = SpagettiBossScene(self)      # 5
        self.vs_boss_clear_scene = VsBossClearScene(self)       # 6
        self.scene_list = [self.title_scene, self.game_scene, self.how_scene, self.setting_scene, self.over_scene, self.boss_spagetti_scene, self.vs_boss_clear_scene]
        
        self.scene_idx = 0
        self.current_scene = self.scene_list[self.scene_idx]
        self.current_scene.pack()
        
        pygame.init()
        
        while True:
            try:
                self.current_scene.run()
            except TclError:
                return
            
            self.window.after(16)
            self.window.update()
    
    def sceneChange(self, next_scene, **kwargs):
        self.current_scene.unpack()
        
        self.scene_idx = next_scene
        self.current_scene = self.scene_list[self.scene_idx]
        self.current_scene.pack(kwargs) if kwargs else self.current_scene.pack()
    
    def keyPressHandler(self, event):
        self.current_scene.keyPressHandler(event)
    
    def keyReleaseHandler(self, event):
        self.current_scene.keyReleaseHandler(event)
    
    def onClose(self):
        pygame.quit()
        for scene in self.scene_list:
            scene.destroy()
        self.window.destroy()
# ------------------------------------------------------------





if __name__ == "__main__":
    SceneChange()