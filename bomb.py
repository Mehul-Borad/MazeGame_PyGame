import pygame
import numpy as np
import time

class Bomb(pygame.sprite.Sprite):
    def __init__(self, grid_size, maze):
        super().__init__()
        self.maze = maze

        self.explosion_anim_speed = 0.5
        self.explosion_anim_frames = 4

        self.throw_speed_fac_time = 30
        self.throw_speed_fac = 0.19
        self.dist_to_player = 50
        self.thresh_dist = 500

        self.grid_size = grid_size
        self.dir = np.array([1, 0])
        self.animation_state = 0
        self.velocity = np.array([0.0, 0.0])
        self.deceleration = 0.05*(grid_size/50)
        self.state = "in_hand"
        self.scaling_factor = self.grid_size/16
        self.explosion_radius = self.grid_size*1
        self.image_path = "Sprites/bomb/bomb/"
        self.image = pygame.image.load(self.image_path + "1.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, self.scaling_factor)
        self.rect = self.image.get_rect()

    def setplayerimg(self):
        self.image = pygame.image.load(self.image_path + f"{1 + int(self.animation_state)}.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, self.scaling_factor)
    
    def explode(self):
        self.image_path = "Sprites/bomb/explosion/"
        self.animation_state = 0
        pos = self.rect.center
        self.scaling_factor *= 1.5
        self.setplayerimg()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        for i in pygame.sprite.spritecollide(self, self.maze.enemies.sprites(), dokill=False):
            i.onkill()
        if self.rect.colliderect(self.maze.player.rect):
            self.maze.player.onkill()
        self.state = "exploded"
        explosion = pygame.mixer.Sound("Sprites/bomb/explosion/sound.mp3")
        explosion.set_volume(0.5)
        explosion.play()

    def exploded(self):
        self.animation_state += self.explosion_anim_speed
        if(self.animation_state >= self.explosion_anim_frames):
            self.kill()
        else:
            self.setplayerimg()

    def throw(self):
        self.state = "threw"
        to_mouse = -self.maze.middle + np.array(pygame.mouse.get_pos()) - self.maze.player.image_rect_offset
        to_mouse = np.linalg.norm(to_mouse)
        if to_mouse > self.thresh_dist:
            to_mouse = self.thresh_dist
        self.throw_speed = to_mouse*self.throw_speed_fac
        self.velocity = self.throw_speed*self.dir/np.linalg.norm(self.dir)
        self.animation_state = 0
        self.count_down = pygame.mixer.Sound("Sprites/bomb/bomb/countdown.mp3")
        self.count_down.play()
        self.time_to_explode = self.count_down.get_length()
        self.time_start_explode = time.time()

    def throw_time(self, Time_pressed):
        self.state = "threw"
        self.throw_speed = Time_pressed*self.throw_speed_fac_time
        self.velocity = self.throw_speed*self.dir/np.linalg.norm(self.dir)
        self.animation_state = 0
        self.count_down = pygame.mixer.Sound("Sprites/bomb/bomb/countdown.mp3")
        self.count_down.play()
        self.time_to_explode = self.count_down.get_length()
        self.time_start_explode = time.time()

    def threw(self): # when state == "threw"
        speed = np.linalg.norm(self.velocity)
        if time.time() - self.time_start_explode > self.time_to_explode:
            self.explode()
        else:
            self.velocity -= self.velocity*self.deceleration
            self.rect.topleft += self.velocity

    def update(self):
        if self.state == "in_hand":
            # In hand things
            self.dir = -self.maze.middle - self.maze.player.image_rect_offset + np.array(pygame.mouse.get_pos())
            len = np.linalg.norm(self.dir)
            if len == 0:
                self.dir = [1, 0]
                len = 1
            self.dir = (self.dir/len)*self.dist_to_player
            self.rect.center = self.maze.player.rect.center + self.dir
            pass
        elif self.state == "threw":
            # projectile motion and shit

            self.threw()
            pass
        elif self.state == "exploded":
            # explosion animation
            self.exploded()

