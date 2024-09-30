import pygame
import random
import rays
import collectables
import numpy as np
import time
from sys import exit

class Enemy(pygame.sprite.Sprite):
    facings = ["right", "left", "front", "back"]
    images = {"right":[0, 0, 0, 0], "left":[0, 0, 0, 0],"back":[0, 0, 0, 0],"front":[0, 0, 0, 0],"killed":[0,0]}
    spritefolder = "Sprites/Enemy/"
    def __init__(self, grid_size, position, maze, speed, spritefolder = "Sprites/Enemy/"):
        super().__init__()
        self.maze = maze
        self.spritefolder = spritefolder
        self.grid_size = grid_size

        self.max_speed = speed*(grid_size/50)
        self.inblockcoeff = 0.05
        self.sizeWRTgridsize = 0.7
        self.animation_rate = 0.08*(50.0/grid_size)

        self.heightfactor = 0.8
        self.widthfactor = 0.6
        self.heightoffset = 5*(self.grid_size*self.sizeWRTgridsize/35)
        self.widthoffset = 0
        self.time_bw_move_mu = 0.5
        self.time_bw_move_sigma = 0.2
        self.no_of_rays = 20
        self.time_to_report = 3
        
        self.time_last_move = 0
        self.animation_state = 0
        self.killed_anim_frames = 2
        self.killed_anim_speed = 0.05
        self.ismoving = True
        self.pursuing = False
        self.facing = "front"
        self.time_start_of_report = time.time()
        self.time_bw_move = random.Random().normalvariate(mu = self.time_bw_move_mu, sigma = self.time_bw_move_sigma)
        self.size = self.grid_size*self.sizeWRTgridsize
        self.image = pygame.image.load(self.spritefolder + "front1.png")
        self.image = pygame.transform.scale_by(self.image, round(self.size/16))
        self.pursuing_music = pygame.mixer.Sound(self.spritefolder + "pursuing.mp3")
        self.walking = pygame.mixer.Sound("music/running.mp3")
        self.walking.set_volume(0.5)
        self.walking_is_playing = False
        self.rect = self.image.get_rect()
        self.rect.width *= self.widthfactor
        self.rect.height *= self.heightfactor
        self.rect.topleft = position
        self.target = position
        self.keymap = {0 : "right", 1 : "left", 2 : "front", 3 : "back"}
        self.facing_to_dir = {"right" : [1, 0], "left" : [-1, 0], "back" : [0, -1], "front" : [0, 1]}
        self.image_rect_offset = np.array([(self.image.get_width() - self.rect.width)/2 + self.widthoffset, (self.image.get_height() - self.rect.height)/2 + self.heightoffset])
    @classmethod
    def load_images(cls):
        for fac in cls.facings:
            for i in range(4):
                cls.images[fac][i] = pygame.image.load(cls.spritefolder + f"{fac}{i + 1}.png").convert_alpha()
        for i in range(2):
            cls.images["killed"][i] = pygame.image.load(cls.spritefolder + f"killed{i+1}.png").convert_alpha()
    def onkill(self):
        # killed animations and stuff
        self.animation_state = 0
        self.facing = "killed"
        self.pursuing_music.stop()
        self.walking.stop()
        # print("enemy killed!")
        pass

    def pointin(self, p : np.ndarray, points : np.ndarray):
        return (points == p).all(1).any(0)
    
    def setplayerimg(self, s):
        self.facing = s
        self.image = Enemy.images[s][int(self.animation_state)]
        self.image = pygame.transform.scale_by(self.image,round(self.size/16))

    def get_neighbours(self, p : np.ndarray):
        l = []
        l.append([p[0], p[1] + self.grid_size])
        l.append([p[0], p[1] - self.grid_size])
        l.append([p[0]  + self.grid_size, p[1]])
        l.append([p[0] - self.grid_size, p[1]])
        return np.array(l)
    
    def next_target(self, prevtarget):
        # print(prevtarget, self.get_neighbours(prevtarget), [p for p in self.get_neighbours(prevtarget) if self.pointin(p, self.maze.walkables)])
        return random.choice([p for p in self.get_neighbours(prevtarget) if self.pointin(p, self.maze.walkables)])
    
    # gives the facing direction in "front", "left", "right" and "back"
    def dir_to_facing(self, dir):
        len = np.linalg.norm(dir)
        if len == 0:
            return "front"
        dir = dir/len
        return list(self.facing_to_dir.keys())[np.argmax(np.linalg.multi_dot((np.array(list(self.facing_to_dir.values())), dir)))] # gets the direction with the max dot product with the dir
    
    def sight_to_player(self):
        dir = self.maze.player.rect.center - np.array(self.rect.center)
        if self.dir_to_facing(dir) != self.facing:
            return False
        hit, sprite, key = rays.Ray(5).go(self.rect.center, dir, self.maze.player)
        if key == 0:
            return False
        return True
    
    def roam(self):
        if self.ismoving:
            direction = self.target + np.array([1.0, 1.0])*self.grid_size/2.0 - np.array(self.rect.center) # define target!!
            length = np.linalg.norm(direction)
            if length < self.inblockcoeff*self.grid_size:
                self.ismoving = False
                self.walking_is_playing = False
                self.walking.stop()
                self.time_last_move = time.time()
            else:
                direction = direction/length
                self.rect.topleft += direction*self.max_speed
            arg = np.argmax(np.array([direction[0], -direction[0], direction[1], -direction[1]]))
            self.setplayerimg(self.keymap[arg])
        else:
            if time.time() - self.time_last_move > self.time_bw_move:
                self.target = self.next_target(self.target)
                self.ismoving = True
                self.time_bw_move = random.Random().normalvariate(mu = self.time_bw_move_mu, sigma = self.time_bw_move_sigma)
    
    def pursue(self):
        self.ismoving = True
        # print(time.time() - self.time_start_of_report)
        if time.time() - self.time_start_of_report > self.time_to_report:
            self.maze.is_reported = True
        direction = self.maze.player.rect.center - np.array(self.rect.center)
        length = np.linalg.norm(direction)
        if length > 10:
            direction = direction/length
            self.rect.topleft += direction*self.max_speed
            arg = np.argmax(np.array([direction[0], -direction[0], direction[1], -direction[1]]))
            self.setplayerimg(self.keymap[arg])
            if not self.sight_to_player():
                self.pursuing_music.stop()
                
                self.pursuing = False
                self.target = [int(self.rect.topleft[0]/self.grid_size)*self.grid_size, int(self.rect.topleft[1]/self.grid_size)*self.grid_size]

    def update(self):
        if self.facing == "killed":
            self.animation_state += self.killed_anim_speed
            if self.animation_state >= self.killed_anim_frames:
                on_point = np.array([int(self.rect.center[0]/self.grid_size)*self.grid_size, int(self.rect.center[1]/self.grid_size)*self.grid_size])
                if not self.pointin(on_point, self.maze.walkables):
                    on_point = self.next_target(on_point)
                self.maze.collectables.add(collectables.collectable(self.grid_size, on_point + [self.grid_size/2, self.grid_size/2],"key"))
                self.kill()
            else:
                self.setplayerimg(self.facing)
        else:
            if self.maze.in_screen(self.rect):
                if not self.pursuing:
                    if self.sight_to_player():
                        self.pursuing_music.play()
                        self.pursuing = True
                    else:
                        self.time_start_of_report = time.time()
                        self.roam()
                else:
                    self.pursue()
                    
                if self.ismoving:
                    self.animation_state += self.max_speed*self.animation_rate
                    while self.animation_state >= 4.0:
                        self.animation_state -= 4.0
                    self.setplayerimg(self.facing)
                    if not self.walking_is_playing:
                        self.walking.play()
                        self.walking_is_playing = True
                else:
                    self.animation_state = 0
                    self.setplayerimg(self.facing)
                # print(rays.Ray(5).go(self.rect.center, self.maze.player.rect.center - np.array(self.rect.center), player = self.maze.player))
            else:
                self.pursuing_music.stop()
                self.walking.stop()
                self.walking_is_playing = False
                self.time_start_of_report = time.time()

        