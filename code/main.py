from random import randint
from typing import Any
import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class Player(pygame.sprite.Sprite):
    
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.direction = pygame.math.Vector2()
        self.speed = 300

        self.can_shoot = True
        self.shoot_timer = 0
        self.cooldown_duration = 400

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        tmp = self.direction
        self.direction = self.direction.normalize() if self.direction else self.direction
        #print(f"Before normalization: {tmp}, after normalization: {self.direction},Speed: {self.speed}, dt: {dt}")
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            Laser(laser_surf, self.rect.midtop, all_sprites)

        self.laser_timer()
   
    def laser_timer(self):  
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True
            
class Star(pygame.sprite.Sprite):

    def __init__(self, groups, surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(center=(randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt

        if self.rect.bottom <= 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
    
    def update(self, dt):
        self.rect.centery += 400 * dt
        if self.rect.top >= SCREEN_HEIGHT:
            self.kill()

pygame.init()
pygame.display.set_caption("Jon's Game")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

all_sprites = pygame.sprite.Group()

star_surface = pygame.image.load("images/star.png").convert_alpha()
for i in range(20):
    Star(all_sprites, star_surface)

player = Player(all_sprites)

meteor_surf = pygame.image.load("images/meteor.png").convert_alpha()
meteor_rect = meteor_surf.get_frect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

laser_surf = pygame.image.load("images/laser.png").convert_alpha()
laser_rect = laser_surf.get_frect(bottomleft=(20, SCREEN_HEIGHT -20))

meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            Meteor(meteor_surf, (randint(0, SCREEN_WIDTH), randint(-200, -100)), all_sprites)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
    # update
    all_sprites.update(dt)

    # draw
    screen.fill("darkgray")
    all_sprites.draw(screen)
    
    pygame.display.update()

pygame.quit()