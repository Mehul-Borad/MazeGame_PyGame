import pygame
import random
import math
import numpy as np
from PIL import Image
from sys import exit

class Player(pygame.sprite.Sprite):
    def __init__(self, grid_size, walkables, maze):
        super().__init__()
        self.maze = maze
        self.grid_size = grid_size
        def processplayerimages(s):
            for i in range(1,5):
                dest = f"{s}{i}.png"
                src = "Sprites/" + dest
                Image.open(src).resize((self.grid_size, self.grid_size)).save(dest)
        
        processplayerimages("front")
        processplayerimages("back")
        processplayerimages("right")
        processplayerimages("left")
        self.image = pygame.image.load("front1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.stridetime = 10
        self.animation_state = 1
        self.animation_frame_time = 23
        self.facing = "front"
        self.time_till_last_movement = 0
        # self.movement_reset_time = 30
        self.thresh_for_movement_when_released = 5
        self.keymaps = {"w" : [False, 0], "a" : [False, 0], "s" : [False, 0], "d" : [False, 0]}
        self.walkables = walkables

    def pointin(self, p : np.ndarray, points : np.ndarray):
        return (points == p).all(1).any(0)
    
    def setplayerimg(self, s):
        self.facing = s
        self.image = pygame.image.load(f"{s}{self.animation_state}.png").convert_alpha()    
    
    def move_with_animation(self, key, newpos):
        delta = np.array(newpos) - np.array(self.rect.topleft)
        for i in range(4):
            self.animation_state = (self.animation_state + 1) % 4
            if self.animation_state == 0: 
                self.animation_state = 4
            self.setplayerimg(key)
            self.rect.topleft += delta*1.0/4.0
            self.maze.render()
            pygame.time.delay(self.animation_frame_time)
        self.rect.topleft = (round(self.rect.topleft[0]/self.grid_size)*self.grid_size, round(self.rect.topleft[1]/self.grid_size)*self.grid_size)
        print(self.rect.topleft)
        pass
    def move(self, key):
            self.time_till_last_movement = 0
            self.animation_state = (self.animation_state + 1) % 4
            if self.animation_state == 0: 
                self.animation_state = 4
            keyn = {"w" : "back", "a" : "left", "s" : "front", "d" : "right"}
            newpos = list(self.rect.topleft)
            if key == "w":
                newpos[1] = self.rect.y - self.grid_size
                self.setplayerimg("back")
            elif key == "s":
                newpos[1] = self.rect.y + self.grid_size
                self.setplayerimg("front")
            elif key == "d":
                newpos[0] = self.rect.x + self.grid_size
                self.setplayerimg("right")
            elif key == "a":
                newpos[0] = self.rect.x - self.grid_size
                self.setplayerimg("left")

            if self.pointin(np.array(newpos), self.walkables):
                self.move_with_animation(keyn[key], newpos)
                print("move_with_animation called!!")
    
    def player_movement(self, event):
        if event.type == pygame.KEYDOWN: # wasd control of the player
            if event.key == pygame.K_w:
                self.keymaps["w"][0] = True
                self.setplayerimg("back")
            if event.key == pygame.K_s:
                self.keymaps["s"][0] = True
                self.setplayerimg("front")
            if event.key == pygame.K_d:
                self.keymaps["d"][0] = True
                self.setplayerimg("right")
            if event.key == pygame.K_a:
                self.keymaps["a"][0] = True
                self.setplayerimg("left")

        if event.type == pygame.KEYUP: # wasd control of the player
            def keyup(key):
                if(self.keymaps[key][0] and self.keymaps[key][1]>self.thresh_for_movement_when_released):
                    self.move(key)
                self.keymaps[key] = [False,0]
            if event.key == pygame.K_w:
                keyup("w")
            if event.key == pygame.K_s:
                keyup("s")
            if event.key == pygame.K_d:
                keyup("d")
            if event.key == pygame.K_a:
                keyup("a")
        pass
    
    def update(self):
        self.time_till_last_movement += 1 # Increase the time from last movement
        # if(self.time_till_last_movement > self.movement_reset_time):
        #     self.animation_state = 1      # reset the animation state to idle when the time limit has passed
        #     self.setplayerimg(self.facing)     # update the image
        mkey = -1
        keyval = ""
        doesmove = False
        for key, value in self.keymaps.items():
            if value[0]:
                value[1]+=1
                if self.keymaps[key][1] > self.stridetime:
                    # self.keymaps[key][1] = 0
                    self.move(key)
                    print("move from update!")
        if mkey > 0:
            self.move(keyval)
