import pygame
from pygame import mixer
import os
import random
import csv
import button
from settings import *
import settings #some functions create local variables rather than accessing these ones
import threading
import time
import math

pygame.mixer.pre_init(44100, 16, 2, 4096) #sound optimisation
mixer.init()
pygame.init()


#load music and sounds
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)


#load images
#button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
achieve_img = pygame.image.load('img/achievement_button.png').convert_alpha()
controls_img = pygame.image.load('img/controls.png').convert_alpha()
back_img = pygame.image.load('img/back.png').convert_alpha()

#background
pine1_img = None
pine2_img = None
mountain_img = None
sky_img = None

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    try:
        img = pygame.image.load(f'img/Tile/{x}.png')
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)
    except:
        print("no tile")
#bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
#pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health'	: health_box_img,
    'Ammo'		: ammo_box_img,
    'Grenade'	: grenade_box_img
}
logo = pygame.image.load('img/icons/logo.png').convert_alpha()

endimg = pygame.image.load('img/endScreen.png').convert_alpha()


#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

#define font
font = pygame.font.SysFont('Futura', 30)
font2 = pygame.font.SysFont('Futura', 17)
font3 = pygame.font.SysFont('Futura', 12)
font4 = pygame.font.SysFont('Futura', 50)

def draw_text(text, font, text_col, x, y):
    global screen
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def loadBackgrounds():
    global pine1_img, pine2_img, mountain_img, sky_img
    #background
    pine1_img = pygame.image.load(f'img/Background/{settings.level}/pine1.png').convert_alpha()
    pine2_img = pygame.image.load(f'img/Background/{settings.level}/pine2.png').convert_alpha()
    mountain_img = pygame.image.load(f'img/Background/{settings.level}/mountain.png').convert_alpha()
    sky_img = pygame.image.load(f'img/Background/{settings.level}/sky_cloud.png').convert_alpha()

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

#function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = settings.playerPreviousHealth
        self.max_health = settings.maxHealth
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        
        #load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        
        #reset movement variables
        screen_scroll = 0
        self.dx = 0
        self.dy = 0

        #assign movement variables if moving left or right
        if moving_left:
            self.dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            self.dx = self.speed
            self.flip = False
            self.direction = 1

        threading.Thread(target = self.gravUpdate, daemon = True).start()

        #check for collision
        for tile in world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + self.dx, self.rect.y, self.width, self.height):
                self.dx = 0
                #if the ai has hit a wall then make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + self.dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    self.dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    self.dy = tile[1].top - self.rect.bottom


        #check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        #check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0


        #check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + self.dx < 0 or self.rect.right + self.dx > SCREEN_WIDTH:
                self.dx = 0

        #update rectangle position
        self.rect.x += self.dx
        self.rect.y += self.dy

        #update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(self.dx)):
                self.rect.x -= self.dx
                screen_scroll = -self.dx

        return screen_scroll, level_complete
    
    def gravUpdate(self):
        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        self.dy += self.vel_y

    def shoot(self, firingMode):
        if firingMode == "Semi":
            if self.shoot_cooldown == 0 and self.ammo > 0:
                self.shoot_cooldown = 20
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                bullet_group.add(bullet)
                #reduce ammo
                self.ammo -= 1
                settings.ammo = player.ammo
                shot_fx.play()
        elif firingMode == "3 Round Burst":
            t = threading.Thread(target = player.burst)
            t.start()
        elif firingMode == "Automatic":
            automat = threading.Thread(target = player.auto)
            
            if settings.automaticMode == False:
                settings.automaticMode = True
                automat.start()
            elif settings.automaticMode == True:
                settings.automaticMode = False              
            
    def burst(self):
        counter = 0
        if self.shoot_cooldown == 0 and self.ammo > 0: 
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1
            settings.ammo = player.ammo
            shot_fx.play()

            pygame.time.wait(100)
            if self.ammo > 0:
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                bullet_group.add(bullet)
                #reduce ammo
                self.ammo -= 1
                settings.ammo = player.ammo
                shot_fx.play()

            pygame.time.wait(100)
            if self.ammo > 0:
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
                bullet_group.add(bullet)
                #reduce ammo
                self.ammo -= 1
                settings.ammo = player.ammo
                shot_fx.play()

    def auto(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:  
            self.shoot_cooldown = 3
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1
            settings.ammo = player.ammo
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: idle
                self.idling = True
                self.idling_counter = 50
            #check if the ai in near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0)#0: idle
                #shoot
                self.shoot("Semi")
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])

        #iterate through each value in settings.leveldata file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:#create player
                        player = Player('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, settings.ammo, settings.grenades)
                        health_bar = HealthBar(10, 10, settings.playerPreviousHealth, player.max_health)
                    elif tile == 16:#create enemies
                        enemy = Player('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:#create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:#create grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:#create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:#create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar


    def draw(self):
        
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                settings.playerPreviousHealth += 25
                if player.health > player.max_health:
                    player.health = player.max_health
                    settings.playerPreviousHealth = player.max_health
                    settings.itemBoxesGained += 1
            elif self.item_type == 'Ammo':
                player.ammo += 15
                settings.ammo += 15
                settings.itemBoxesGained += 1
            elif self.item_type == 'Grenade':
                player.grenades += 3
                settings.grenades += 3
                settings.itemBoxesGained += 1
            #delete the item box
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        
        #move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                settings.playerPreviousHealth -= 5
                settings.damageTaken -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    settings.score += 10
                    settings.shotsHit += 1
                    settings.enemiesDamagedByGrenades = 999999
                    if enemy.health == 0:
                        settings.enemyCounter -= 1
                        settings.enemiesKilled += 1
                        settings.score += 100
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        
        self.vel_y += GRAVITY
        self.dx = self.direction * self.speed
        self.dy = self.vel_y

        #check for collision with level
        for tile in world.obstacle_list:
            #check collision with walls
            if tile[1].colliderect(self.rect.x + self.dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                self.dx = self.direction * self.speed
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + self.dy, self.width, self.height):
                self.speed = 0
                #check if below the ground, i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    self.dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.dy = tile[1].top - self.rect.bottom	


        #update grenade position
        self.rect.x += self.dx + screen_scroll
        self.rect.y += self.dy

        #countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
                settings.playerPreviousHealth -= 50
                settings.damageTaken -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
                    settings.score += 40
                    settings.enemiesDamagedByGrenades += 1
                    if enemy.health == 0:
                        settings.enemyCounter -= 1
                        settings.enemiesKilled += 1
                        settings.score += 100

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        
        #scroll
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4
        #update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, colour, speed):
        
        self.direction = direction
        self.colour = colour
        self.speed = speed * 2
        self.fade_counter = 0


    def fade(self):
        
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:#whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:#vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete

class Achievements(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.achievements = []
        self.achievements_list = []
        self.achievementStatus = []
        self.hitbox_list = []
        self.uncompletedAchievements = 0
        self.completedAchievements = 0
        oldachievements = open("achievements.txt", "r").readlines()
        ##Achievement array layout
        # AchievementName:AchievementDescription:Completed/NotCompleted

        achievementsArray = []
        achievements = []
        for achievement in oldachievements:
            achievementsArray = []
            achievement = achievement.strip("\n")
            achievement = achievement.split(":")
            self.achievements.append(achievement)
            self.achievements_list.append(achievement[0])
            self.achievementStatus.append(achievement[2])
        
        
        for item in self.achievementStatus:
            if item == "True":
                self.completedAchievements += 1
    
    def draw(self):
        global font, screen
        mainX = 20
        mainY = 10
        descX = 20
        descY = 30
        splitDistance = 52
        for achievement in self.achievements:
            if str(achievement[2]) == "True":
                img = font2.render(str(achievement[0] + " - Completed"), True, WHITE)
                desc = font3.render(achievement[1], True, WHITE)
            else:
                img = font2.render(str(achievement[0] + " - Not Completed"), True, BLACK)
                desc = font3.render(achievement[1], True, BLACK)
            #hitbox = img.get_rect()
            #self.hitbox_list.append(hitbox)
            screen.blit(img, (mainX, mainY))
            screen.blit(desc, (descX, descY))
            mainY += splitDistance
            descY += splitDistance
        settings.counter = 1

    def optionsAchievementCheck(self):
        achievementRatio = (self.completedAchievements / len(self.achievementStatus)) * 100
        if achievementRatio >= 50:
            a.achievementGained(optionsoptionsoptions)
            settings.firingModesOn = True

    def achievementGained(self, achievement):
        self.indexValue = self.achievements_list.index(achievement)
        if self.achievementStatus[self.indexValue] == "False":
            self.achievementStatus[self.indexValue] = True
            self.achievements[self.indexValue][2] = self.achievementStatus[self.indexValue]
        a.achievementsWrite()
    
    def achievementsWrite(self):
        achievementsFile = open("achievements.txt", "w+")
        counter = 0
        for line in self.achievements_list:
            if counter == 0: ##removes unnecessary newline at end of text file that may cause some unexpected errors
                stringToWrite = f"{self.achievements[counter][0]}:{self.achievements[counter][1]}:{self.achievements[counter][2]}"
            else:
                stringToWrite = f"\n{self.achievements[counter][0]}:{self.achievements[counter][1]}:{self.achievements[counter][2]}"
            achievementsFile.write(stringToWrite)
            counter += 1

    def endLevelAchievementCheck(self):
        if(player.ammo == 0) and (player.grenades == 0) and (player.health <= 25): ##last legs achievement
            a.achievementGained(lastlegs)
        if enemyCounter == 0 and settings.damageTaken == 0: ##Assassin achievement
            a.achievementGained(assassin)
        if player.ammo == 0:
            settings.roundsFinishedWithEmptyMagazine += 1
    
    def endGameAchievementCheck(self):
        a.achievementGained(armyspecialist)
        if settings.grenadesThrown == 0 and settings.shotsFired == 0: #Pacifist achievement
            a.achievementGained(pacifist)
        if settings.damageTaken == 0: ##Imortal Achievement
            a.achievementGained(immortal)
        if settings.totalEnemyCounter == settings.enemiesKilled: #Path of Destruction achievement
            a.achievementGained(pathofdestruction)
        if settings.itemBoxesGained == 0: #Resourceful Achievement
            a.achievementGained(resourceful)
        if settings.shotsFired == settings.shotsHit: #Sniper achievement
            a.achievementGained(sniper)
        if (settings.enemiesDamagedByGrenades == settings.grenadesThrown) and player.grenades == 0: #Explosives Expert achievement
            a.achievementGained(explosivesexpert)
        if settings.roundsFinishedWithEmptyMagazine == settings.level: #Trigger Finger achievement
            a.achievementGained(triggerfinger)

class changeFiringModes():
    def getCurrentFiringMode():
        currentFiringMode = settings.activeFiringMode
        changeFiringModes.iterateFiringMode(currentFiringMode)

    def iterateFiringMode(firingmode):
        if settings.firingModeCounter + 1 == len(settings.firingModes):
            settings.firingModeCounter = 0
        else:
            settings.firingModeCounter += 1

        
        changeFiringModes.changeFiringMode()
    
    def changeFiringMode():
        settings.activeFiringMode = settings.firingModes[settings.firingModeCounter]

class testingFramework():
    def debugger(debuggerInfo, *args):
        os.system("cls")
        print(debuggerInfo)
        for i in args:
            print(i)


#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)


#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
start_button2 = button.Button(SCREEN_WIDTH // 2 + 110, SCREEN_HEIGHT // 2 + 70, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
back_button2 = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 150, back_img, 1)
back_button = button.Button(SCREEN_WIDTH // 2 + 110, SCREEN_HEIGHT // 2 + 190, back_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
achievements_button = button.Button(SCREEN_WIDTH // 2 - 215, SCREEN_HEIGHT // 2 + 250, achieve_img, 2)
restart_button_endscreen = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 200, exit_img, 2)
controls_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 40, controls_img, 2)



#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
    
#load in settings.leveldata and create world
with open(f'levels/level{settings.level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

a = Achievements()

run = True
setup = False
controlsMenu = False
while run:

    clock.tick(FPS)

    if start_game == False:
        #draw menu
        screen.fill(BG)
        #add buttons
        a.optionsAchievementCheck()
        if achievementMenu == False and controlsMenu == False:
            screen.blit(logo, (100, 15))
            settings.level = 1
            if start_button.draw(screen):
                start_game = True
                start_intro = True  
            if exit_button.draw(screen):
                run = False
            if achievements_button.draw(screen):
                achievementMenu = True
            if controls_button.draw(screen):
                controlsMenu = True
        elif controlsMenu == True:
            screen.blit(logo, (100, 15))
            ##Windows Settings
            draw_text("Movement Controls", font4, WHITE, 220, 150)
            draw_text("Move Left: A or Left Arrow", font, WHITE, 250, 190)
            draw_text("Move Right: D or Right Arrow", font, WHITE, 250, 220)
            draw_text("Jump: Spacebar or Up Arrow", font, WHITE, 250, 250)

            draw_text("Interaction Controls", font4, WHITE, 220, 300)
            draw_text("Fire Gun: K", font, WHITE, 330, 340)
            draw_text("Grenade: P", font, WHITE, 330, 370)
            draw_text("Change Firing Mode: V - [Achievement Unlock]", font, WHITE, 170, 400)

            ##Mac Settings
            #draw_text("Movement Controls", font, WHITE, 250, 150)
            #draw_text("Move Left: A or Left Arrow", font2, WHITE, 250, 190)
            #draw_text("Move Right: D or Right Arrow", font2, WHITE, 250, 220)
            #draw_text("Jump: Spacebar or Up Arrow", font2, WHITE, 250, 250)

            #draw_text("Interaction Controls", font, WHITE, 250, 300)
            #draw_text("Fire Gun: K", font2, WHITE, 330, 340)
            #draw_text("Grenade: P", font2, WHITE, 330, 370)
            #draw_text("Change Firing Mode: V - [Achievement Unlock]", font2, WHITE, 200, 400)
            if back_button2.draw(screen):
                controlsMenu = False
        
        elif achievementMenu == True:
            a.draw()
            for event in pygame.event.get():
                #quit game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            if start_button2.draw(screen):
                start_game = True
                start_intro = True
            if back_button.draw(screen):
                achievementMenu = False

    else:
        if not settings.timerStarted and settings.startTime == 0:
            settings.startTime = time.time()
            settings.timerStarted = True
            settings.ammo = player.ammo
            settings.grenades = player.grenades
            settings.level = 1
            loadBackgrounds()
        #update background
        draw_bg()
        #draw world map
        world.draw()
        #show player health
        health_bar.draw(player.health)
        #show ammo
        draw_text(f'AMMO: {player.ammo}', font2, WHITE, 10, 35)
        for x in range(player.ammo):
            break
            #screen.blit(bullet_img, (90 + (x * 10), 40))
        #show grenades
        draw_text(f'GRENADES: {player.grenades}', font2, WHITE, 10, 60)
        for x in range(player.grenades):
            break
            #screen.blit(grenade_img, (135 + (x * 15), 60))


        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            if (enemy.rect.x <= -64) or (enemy.rect.x >= 864): ##If enemy is outside of screen
                pass ##Enemy is off screen
            else:
                enemy.update()
            enemy.draw()   
            if (enemy.alive == False) and (enemy.rect.x <= -64): ##Removes the enemies from the list, so when dead enemies leave the screen, they are no longer rendered
                enemy_group.remove(enemy)
               
            

        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        threading.Thread(target = testingFramework.debugger("Player Stats:", player.health, settings.playerPreviousHealth, player.grenades, settings.grenades, player.ammo, settings.ammo)).start()

        threading.Thread(target = bullet_group.draw(screen), daemon = True).start()
        threading.Thread(target = grenade_group.draw(screen), daemon = True).start()
        threading.Thread(target = explosion_group.draw(screen), daemon = True).start()
        threading.Thread(target = item_box_group.draw(screen), daemon = True).start()
        threading.Thread(target = decoration_group.draw(screen), daemon = True).start()
        threading.Thread(target = water_group.draw(screen), daemon = True).start()
        threading.Thread(target = exit_group.draw(screen), daemon = True).start()

        if settings.firingModesOn:
            draw_text(settings.activeFiringMode, font2, WHITE, 625, 10)

        if not setup: ##level-specific one-time events
            settings.enemyCounter = len(enemy_group)
            settings.totalEnemyCounter += len(enemy_group)
            setup = True
        #show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0


        #update player actions
        if player.alive:
            #shoot bullets
            if shoot:
                threading.Thread(target = player.shoot(settings.activeFiringMode)).start()
            #throw grenade
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                             player.rect.top, player.direction)
                settings.grenadesThrown += 1
                settings.grenades -= 1
                grenade_group.add(grenade)
                #reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)#2: jump
            elif moving_left or moving_right:
                player.update_action(1)#1: run
            else:
                player.update_action(0)#0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll


            #check if player has completed the level
            if level_complete:
                if MAX_LEVELS == settings.level:
                    settings.gameCompleted = True
                if not settings.gameCompleted:
                    a.endLevelAchievementCheck()
                    start_intro = True
                    
                    #empty groups
                    enemy_group.empty()
                    bullet_group.empty()
                    grenade_group.empty()
                    explosion_group.empty()
                    item_box_group.empty()
                    decoration_group.empty()
                    water_group.empty()
                    exit_group.empty()

                    setup = False
                    settings.level += 1
                    loadBackgrounds()
                    bg_scroll = 0
                    world_data = reset_level()
                    if settings.level <= settings.MAX_LEVELS:
                        #load in settings.leveldata and create world
                        with open(f'levels/level{settings.level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
                else:
                    a.endGameAchievementCheck()
                    a.endLevelAchievementCheck()
                    player.speed = 0

                    screen.blit(endimg, (0,0))
                    draw_text("Congratulations!", font4, WHITE, 235, 50)

                    if settings.timerStarted and settings.endTime == 0:
                        settings.timerStarted = False
                        settings.endTime = time.time()
                        unalteredScore = settings.score
                        settings.score += player.health * 5
                        settings.score += player.ammo * 2
                        settings.score += player.grenades * 30
                    
                    settings.timeCompleted = settings.endTime - settings.startTime
                    draw_text("You completed the game in", font, WHITE, 240, 120)
                    draw_text(str(round(settings.timeCompleted, 2)) + " seconds", font4, WHITE, 275, 160)
                    draw_text("with a total score of", font, WHITE, 290, 250)
                    draw_text(str(settings.score + 500) + " points", font4, WHITE, 300, 290)
                    score_text = f"+{unalteredScore + 500} normal points scored"
                    score_text1 = f"+{player.health * 5}pts bonus from your leftover health"
                    score_text2 = f"+{player.ammo * 2}pts bonus from your leftover ammo"
                    score_text3 = f"+{player.grenades * 30}pts bonus from your leftover grenades"
                    draw_text(score_text, font2, WHITE, 280, 360)
                    draw_text(score_text1, font2, WHITE, 280, 380)
                    draw_text(score_text2, font2, WHITE, 280, 400)
                    draw_text(score_text3, font2, WHITE, 280, 420)
                    if restart_button_endscreen.draw(screen):
                        run = False
        
        
        
        else:
            screen_scroll = 0
            if death_fade.fade():

                if restart_button.draw(screen):
                    ##Reset game
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    settings.level = 1
                    world_data = reset_level()
                    loadBackgrounds()
                    #load in settings.leveldata and create world
                    with open(f'levels/level1_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    settings.ammo = 20
                    settings.grenades = 9
                    settings.startTime = time.time()
                    settings.playerPreviousHealth = 100
                    player, health_bar = world.process_data(world_data)


    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        if not settings.gameCompleted:
            #keyboard presses
            if event.type == pygame.KEYDOWN:
                if player.alive:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        moving_left = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        moving_right = True
                    if event.key == pygame.K_k:
                        if start_game == True: #done to make sure that no keys pressed before game starts account towards firing shots, as well as preventing shots fired from enemies counting towards this variable
                            settings.shotsFired += 1
                            if settings.activeFiringMode == "Automatic":
                                settings.automaticMode = True
                        shoot = True
                    if event.key == pygame.K_p:
                        if start_game == True:
                            grenade = True
                    if event.key == pygame.K_w and player.alive or event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        player.jump = True
                        jump_fx.play()
                    if event.key == pygame.K_v:
                        if settings.firingModesOn:
                            changeFiringModes.getCurrentFiringMode()


            #keyboard button released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    moving_left = False
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    moving_right = False
                if event.key == pygame.K_k:
                    shoot = False
                    settings.automaticMode = False
                if event.key == pygame.K_p:
                    grenade = False
                    grenade_thrown = False


    pygame.display.update()

pygame.quit()
exit()
