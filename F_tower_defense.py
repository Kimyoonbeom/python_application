import pygame
import math
import random
from pygame.math import Vector2

# 게임 초기화
pygame.init()
pygame.mixer.init()

# 화면 크기 설정
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("F 학점 디펜스")

# 색상 설정
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)

# 배경음악 로드
background_music = pygame.mixer.Sound('학점 디펜스.ogg')
background_music.set_volume(0.5)

# 사운드 컨트롤 UI 이미지 로드
sound_on_img = pygame.transform.scale(pygame.image.load("sound_on.png"), (40, 40))
sound_off_img = pygame.transform.scale(pygame.image.load("sound_off.png"), (40, 40))
sound_button_rect = pygame.Rect(SCREEN_WIDTH - 50, 10, 40, 40)
is_sound_on = True

# 강조 표시를 위한 surface 생성
highlight_surface = pygame.Surface((160, 160), pygame.SRCALPHA)
pygame.draw.rect(highlight_surface, (255, 255, 0, 128), highlight_surface.get_rect(), 5)


# 한글 폰트 설정
font_path = "MaruBuri-Bold.ttf"
font = pygame.font.Font(font_path, 50)

def draw_wave_info(screen, wave_system):
        font = pygame.font.Font(font_path, 36)
        wave_text = font.render(f"Wave: {wave_system.current_wave}", True, COLOR_WHITE)
        enemies_left_text = font.render(f"Enemies Left: {wave_system.enemies_in_wave}", True, COLOR_WHITE)
        screen.blit(wave_text, (10, 50))
        screen.blit(enemies_left_text, (10, 90))

class Enemy:
    def __init__(self, path):
        self.pos = Vector2(path[0])
        self.path = path
        self.path_index = 0
        self.speed = 2
        self.health = 100
        self.max_health = 100
        self.radius = 15
        
    def update(self):
        target = Vector2(self.path[self.path_index])
        direction = target - self.pos
        if direction.length() < self.speed:
            self.path_index = (self.path_index + 1) % len(self.path)
        else:
            self.pos += direction.normalize() * self.speed
            
    def draw(self, screen):
        screen.blit(enemy_img, (self.pos.x - self.radius, self.pos.y - self.radius))
        # 체력바
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (self.pos.x - 20, self.pos.y - 25, 40 * health_ratio, 5))

class Bullet:
    def __init__(self, pos, target):
        self.pos = Vector2(pos)
        self.direction = (Vector2(target) - self.pos).normalize()
        self.speed = 7
        self.damage = 25
        
    def update(self):
        self.pos += self.direction * self.speed
        
    def draw(self, screen):
        pygame.draw.circle(screen, COLOR_WHITE, (int(self.pos.x), int(self.pos.y)), 5)

class Tower:
    def __init__(self, pos, tower_type):
        self.pos = Vector2(pos)
        self.tower_type = tower_type
        self.radius = 20
        self.range = 150
        self.damage = 25
        self.attack_speed = 1.0
        self.last_shot = 0
        self.level = 1
        

        if tower_type == "normal":
            self.color = (0, 0, 255)
            self.cost = 100
        elif tower_type == "slow":
            self.color = COLOR_GREEN
            self.cost = 150
            self.slow_factor = 0.5
        elif tower_type == "buff":
            self.color = (255, 165, 0)
            self.cost = 200
            self.buff_factor = 1.5

        self.upgrade_cost = self.cost *0.5
    def upgrade(self):
        if game.score >= self.upgrade_cost:
            game.score -= self.upgrade_cost
            self.level += 1
            self.damage *= 1.2
            self.range *= 1.1
            self.upgrade_cost *= 1.5
            return True
        return False
    
    def draw(self, screen):
        if self.tower_type == "normal":
            screen.blit(tower_normal_img, (self.pos.x - self.radius, self.pos.y - self.radius))
        elif self.tower_type == "slow":
            screen.blit(tower_slow_img, (self.pos.x - self.radius, self.pos.y - self.radius))
        elif self.tower_type == "buff":
            screen.blit(tower_buff_img, (self.pos.x - self.radius, self.pos.y - self.radius))
        
        small_font = pygame.font.Font(font_path, 20)
        level_text = small_font.render(f"Lv.{self.level}", True, COLOR_WHITE)
        screen.blit(level_text, (self.pos.x - 15, self.pos.y - 40))

        # 타워 범위 표시
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.range, 1)

class WaveSystem:
    def __init__(self):
        self.current_wave = 0
        self.enemies_in_wave = 0
        self.time_between_waves = 10
        self.wave_countdown = self.time_between_waves

    def update(self, game):
        if self.enemies_in_wave == 0:
            self.wave_countdown -= 1 / 60  # 60 FPS 기준
            if self.wave_countdown <= 0:
                self.start_next_wave(game)
        
    def start_next_wave(self, game):
        self.current_wave += 1
        self.enemies_in_wave = self.current_wave * 5
        self.wave_countdown = self.time_between_waves
        for _ in range(self.enemies_in_wave):
            game.spawn_enemy()

wave_system = WaveSystem()

class SheepSprite:
    def __init__(self):
        self.frame1 = pygame.image.load("lamp1.png")
        self.frame2 = pygame.image.load("lamp2.png")
        
        self.frame1 = pygame.transform.scale(self.frame1, (100, 100))
        self.frame2 = pygame.transform.scale(self.frame2, (100, 100))
        
        self.frames = [self.frame1, self.frame2]
        
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_delay = 150
        self.rect = self.frames[0].get_rect()
        self.last_pos = pygame.math.Vector2(0, 0)
        
        # 자동 공격 관련 변수 추가
        self.last_shot_time = 0
        self.shot_delay = 200  # 0.2초마다 발사
        
    def update(self, mouse_pos, game):
        current_time = pygame.time.get_ticks()
        current_pos = pygame.math.Vector2(mouse_pos)
        
        distance = (current_pos - self.last_pos).length()
        
        if distance > 1:
            if current_time - self.animation_timer > self.animation_delay:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.animation_timer = current_time
        
        self.rect.center = mouse_pos
        self.last_pos = current_pos
        
        # 자동 공격 로직
        if current_time - self.last_shot_time > self.shot_delay:
            if game.enemies:  # 적이 있다면
                closest_enemy = min(game.enemies, key=lambda e: Vector2(self.rect.center).distance_to(e.pos))
                game.bullets.append(Bullet(self.rect.center, closest_enemy.pos))
                self.last_shot_time = current_time
    
    def draw(self, surface):
        surface.blit(self.frames[self.current_frame], self.rect)



class Game:
    def __init__(self):
        self.enemies = []
        self.bullets = []
        self.towers = []
        self.score = 0
        self.selected_tower = None
        self.path = [
    (450, 150),   # 상단 중앙
    (700, 150),   # 상단 우측
    (700, 550),   # 하단 우측
    (200, 550),   # 하단 좌측
    (200, 150),   # 상단 좌측
    (450, 150)    # 다시 상단 중앙으로
]
    def spawn_enemy(self):
        if len(self.enemies) < 30 and random.random() < 0.02:
            self.enemies.append(Enemy(self.path))
            
    def update(self):
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.score += 10
                
        for bullet in self.bullets[:]:
            bullet.update()
            if not (0 <= bullet.pos.x <= SCREEN_WIDTH and 0 <= bullet.pos.y <= SCREEN_HEIGHT):
                self.bullets.remove(bullet)
                continue
                
            for enemy in self.enemies:
                if (bullet.pos - enemy.pos).length() < enemy.radius+10:
                    enemy.health -= bullet.damage
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
                    
        current_time = pygame.time.get_ticks()
        for tower in self.towers:
            if current_time - tower.last_shot > tower.attack_speed * 1000:
                for enemy in self.enemies:
                    if (tower.pos - enemy.pos).length() <= tower.range:
                        self.bullets.append(Bullet(tower.pos, enemy.pos))
                        tower.last_shot = current_time
                        break
    
    
    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        for tower in self.towers:
            tower.draw(screen)
        
        #점수 표시
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, COLOR_WHITE)
        screen.blit(score_text, (10, 10))

        #웨이브 정보 표시
        draw_wave_info(screen, wave_system)


# 게임 객체 생성
game = Game()

# PNG 파일 불러오기
hero1_image = pygame.image.load("lamp1.png")
hero2_image = pygame.image.load("lamp3.png")

# 배경 이미지 로드
background_image_select = pygame.image.load("kang1.png")
background_image_select = pygame.transform.scale(background_image_select, (SCREEN_WIDTH, SCREEN_HEIGHT))

background_image_game = pygame.image.load("map_1.png")
background_image_game = pygame.transform.scale(background_image_game, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 타워 이미지 로드
tower_normal_img = pygame.image.load("tower_1.png")
tower_slow_img = pygame.image.load("tower_2.png")
tower_buff_img = pygame.image.load("tower_3.png")

# 타워 크기 조정
tower_normal_img = pygame.transform.scale(tower_normal_img, (80, 80))
tower_slow_img = pygame.transform.scale(tower_slow_img, (80, 80))
tower_buff_img = pygame.transform.scale(tower_buff_img, (80, 80))

# 적 몬스터 이미지 로드 및 조정.
enemy_img = pygame.image.load("mon_1.png")
enemy_img = pygame.transform.scale(enemy_img, (90, 90))

# 상태 변수
STATE_INTRO = "intro"
STATE_WAIT = "wait"
STATE_SELECT = "select"
STATE_GAME = "game"
current_state = STATE_INTRO
selected_hero = None

# FPS 설정
frame_clock = pygame.time.Clock()
highlight_color_index = 0

# 양 스프라이트 생성
sheep = SheepSprite()

# 게임 루프
game_active = True
while game_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_active = False

        if current_state == STATE_INTRO:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                current_state = STATE_WAIT

        elif current_state == STATE_WAIT:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                current_state = STATE_SELECT

        elif current_state == STATE_SELECT:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if sound_button_rect.collidepoint(event.pos):
                    is_sound_on = not is_sound_on
                    if is_sound_on:
                        background_music.play(-1)
                    else:
                        background_music.stop()
                
                elif 200 <= mouse_x <= 350 and 400 <= mouse_y <= 550:
                    selected_hero = "hero1"
                    print("영웅 1 선택")
                    current_state = STATE_GAME
                elif 550 <= mouse_x <= 700 and 400 <= mouse_y <= 550:
                    selected_hero = "hero2"
                    print("영웅 2 선택")
                    current_state = STATE_GAME

        elif current_state == STATE_GAME:
            # 타워 설치
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game.selected_tower:
                pos = pygame.mouse.get_pos()
                game.towers.append(Tower(pos, game.selected_tower))
                game.selected_tower = None

            # 타워 업그레이드를 위한 우클릭 이벤트 처리
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 우클릭
                pos = pygame.mouse.get_pos()
                for tower in game.towers:
                    if (tower.pos - Vector2(pos)).length() < tower.radius:
                        if tower.upgrade():
                            print(f"Tower upgraded to level {tower.level}")
                        else:
                            print("Not enough score to upgrade")
    # 화면 업데이트
    if current_state == STATE_INTRO:
        window.fill(COLOR_BLACK)
        intro_text = font.render("이루고 싶은 일이 있나?", True, COLOR_WHITE)
        window.blit(intro_text, (SCREEN_WIDTH // 2 - intro_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2 - intro_text.get_height() // 2))

    elif current_state == STATE_WAIT:
        window.fill(COLOR_BLACK)
        wait_text = font.render("그렇다면 디펜스다!!", True, COLOR_WHITE)
        window.blit(wait_text, (SCREEN_WIDTH // 2 - wait_text.get_width() // 2, 
                               SCREEN_HEIGHT // 2 - wait_text.get_height() // 2))

    elif current_state == STATE_SELECT:
        if is_sound_on and not pygame.mixer.get_busy():
            background_music.play(-1)
            
        window.blit(background_image_select, (0, 0))

        button_width, button_height = 300, 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = 300
        pygame.draw.rect(window, (0, 0, 0, 128), (button_x, button_y, button_width, button_height))
        start_text = font.render("게임 시작!", True, COLOR_WHITE)
        window.blit(start_text, (button_x + button_width // 2 - start_text.get_width() // 2, 
                                button_y + button_height // 2 - start_text.get_height() // 2))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if 200 <= mouse_x <= 350 and 400 <= mouse_y <= 550:
            window.blit(highlight_surface, (200 - 5, 400 - 5))
        window.blit(hero1_image, (200, 400))
        hero1_text = font.render("영웅 1", True, COLOR_WHITE)
        window.blit(hero1_text, (200 + 75 - hero1_text.get_width() // 2, 560))

        if 550 <= mouse_x <= 700 and 400 <= mouse_y <= 550:
            window.blit(highlight_surface, (550 - 5, 400 - 5))
        window.blit(hero2_image, (550, 400))
        hero2_text = font.render("영웅", True, COLOR_WHITE)
        window.blit(hero2_text, (550 + 75 - hero2_text.get_width() // 2, 560))

        sound_img = sound_on_img if is_sound_on else sound_off_img 
        window.blit(sound_img, sound_button_rect)

    elif current_state == STATE_GAME:
        window.blit(background_image_game, (0, 0))
        
        # 게임 로직 업데이트
        game.spawn_enemy()
        game.update()
        game.draw(window)
        wave_system.update(game)
        
        # 키 입력 처리
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            game.selected_tower = "normal"
        elif keys[pygame.K_2]:
            game.selected_tower = "slow"
        elif keys[pygame.K_3]:
            game.selected_tower = "buff"
        
        # 영웅 캐릭터 업데이트 및 표시
        if selected_hero == "hero1":
            sheep.update(pygame.mouse.get_pos(), game)
            sheep.draw(window)
        elif selected_hero == "hero2":
            lamp2_rect = hero2_image.get_rect(center=pygame.mouse.get_pos())
            window.blit(hero2_image, lamp2_rect)

        # 게임 화면에서도 사운드 컨트롤 UI 표시 
        sound_img = sound_on_img if is_sound_on else sound_off_img 
        window.blit(sound_img, sound_button_rect)

        # 게임 오버 조건
        if len(game.enemies) >= 30:
            current_state = STATE_INTRO

    pygame.display.flip()
    frame_clock.tick(60)

pygame.quit()