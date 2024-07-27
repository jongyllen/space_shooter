from posixpath import join
from random import randint, uniform
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

        self.mask = pygame.mask.from_surface(self.image)

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
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            laser_sound.play()

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
        self.mask = pygame.mask.from_surface(self.image)

class Laser(pygame.sprite.Sprite):
    
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.centery -= 400 * dt

        if self.rect.bottom <= 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 500)
        self.mask = pygame.mask.from_surface(self.image)
        self.rotation_speed = randint(20,50)
        self.rotation = 0
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top >= SCREEN_HEIGHT:
            self.kill()
        
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):

    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        self.frame_index += 20 * dt

        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()    

def collisions():
    global running
    global score

    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        damage_sound.play()
        score = 0
        text_game_over_surf = font_game_over.render("GAME OVER!", True, (240,240,240))
        text_game_over_rect = text_game_over_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT/2))
        screen.blit(text_game_over_surf, text_game_over_rect)
        running = False

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            explosion_sound.play()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            score += 1

def display_score(score):
    text_surf = font.render(f"Score: {score}", True, (240,240,240))
    text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, (240,240,240), text_rect.inflate(20, 20).move(0,-8), 5, 10)


pygame.init()
pygame.display.set_caption("Jon's Game")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
score = 0

# import
star_surface = pygame.image.load("images/star.png").convert_alpha()
meteor_surf = pygame.image.load("images/meteor.png").convert_alpha()
laser_surf = pygame.image.load("images/laser.png").convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 20)
font_game_over = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 50)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.5)
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
damage_sound.set_volume(0.5)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops=-1)

# Sprite
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    Star(all_sprites, star_surface)

player = Player(all_sprites)


# Events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            Meteor(meteor_surf, (randint(0, SCREEN_WIDTH), randint(-200, -100)), (all_sprites, meteor_sprites))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
    # update
    all_sprites.update(dt)

    collisions()

    # draw
    screen.fill('#3a2e3f')
    display_score(score)
    all_sprites.draw(screen)
    
    pygame.display.update()

pygame.quit()