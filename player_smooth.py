import pygame
import time
import numpy as np
import bomb
from sys import exit

class Player(pygame.sprite.Sprite):
    facings = ["right", "left", "front", "back"]
    images = {"right":[0, 0, 0, 0], "left":[0, 0, 0, 0],"back":[0, 0, 0, 0],"front":[0, 0, 0, 0],}
    spritefolder = "Sprites/assassin/"
    def __init__(self, grid_size, wallsSprites, maze, bombs, spritefolder = "Sprites/assassin/"):
        super().__init__()
        self.maze = maze
        self.walls = wallsSprites
        self.spritefolder = spritefolder
        self.grid_size = grid_size
        # print(self.rect.width)
        
        # print(self.rect.width)
        
        self.max_speed = 6*(grid_size/50)
        self.accleration = 0.75*(grid_size/50)
        self.sizeWRTgridsize = 0.7
        self.collisionfac = 0.1
        self.animation_rate = 0.06*(50.0/grid_size)

        self.heightfactor = 0.8
        self.widthfactor = 0.6
        self.heightoffset = 5*(self.grid_size*self.sizeWRTgridsize/35)
        self.widthoffset = 0
        self.bombs_remaining = bombs
        self.keys = 0

        self.ismoving = False
        self.facing = "front"
        self.animation_state = 0
        self.time_till_last_movement = 0
        self.speed = 0
        self.bombs = pygame.sprite.Group()
        self.size = self.grid_size*self.sizeWRTgridsize
        self.image = pygame.image.load(self.spritefolder + "front1.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, round(self.size/16))
        self.walking = pygame.mixer.Sound("music/running.mp3")
        self.walking.set_volume(0.5)
        self.walking_is_playing = False
        self.rect = self.image.get_rect()
        self.np_get_state = np.vectorize(self.get_state, otypes=[np.ndarray])
        # self.collision_rect = pygame.rect.Rect()
        self.rect.width *= self.widthfactor
        self.rect.height *= self.heightfactor
        self.keymaps = {"w" : [False, [0, -1]], "a" : [False, [-1, 0]], "s" : [False, [0, 1]], "d" : [False, [1, 0]]}
        # self.walkables = walkables
        self.image_rect_offset = np.array([(self.image.get_width() - self.rect.width)/2 + self.widthoffset, (self.image.get_height() - self.rect.height)/2 + self.heightoffset])

    def pointin(self, p : np.ndarray, points : np.ndarray):
        return (points == p).all(1).any(0)
    @classmethod
    def load_images(cls):
        for fac in cls.facings:
            for i in range(4):
                cls.images[fac][i] = pygame.image.load(cls.spritefolder + f"{fac}{i + 1}.png").convert_alpha()

    def setplayerimg(self, s):
        self.facing = s
        self.image = Player.images[s][int(self.animation_state)]
        self.image = pygame.transform.scale_by(self.image,round(self.size/16))

    def onkill(self):
        # on kill?
        self.maze.player_killed = True
        pass

    def get_state(self, sprite, state):
        return sprite.__getattribute__(state)
    
    def setbomb(self):
        states = self.np_get_state(self.bombs.sprites(), "state")
        in_hand = np.array(self.bombs.sprites())[states == "in_hand"]
        for i in in_hand:
            i.throw_time(time.time()-self.bomb_time)
        if not in_hand.any():
            if self.bombs_remaining > 0:
                self.bombs.add(bomb.Bomb(self.grid_size, self.maze))
                self.bombs_remaining -= 1

    def player_movement(self, event):
        if event.type == pygame.KEYDOWN: # wasd control of the player
            if event.key == pygame.K_w:
                self.keymaps["w"][0] = True
                # self.setplayerimg("back")
            if event.key == pygame.K_s:
                self.keymaps["s"][0] = True
                # self.setplayerimg("front")
            if event.key == pygame.K_d:
                self.keymaps["d"][0] = True
                # self.setplayerimg("right")
            if event.key == pygame.K_a:
                self.keymaps["a"][0] = True
                # self.setplayerimg("left")
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bomb_time = time.time()
            self.setbomb()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.setbomb()

        if event.type == pygame.KEYUP: # wasd control of the player
            def keyup(key):
                self.keymaps[key][0] = False
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
        # Update the facing direction
        for sprite in self.bombs.sprites():
            sprite.update()
        if self.keymaps["w"][0] == True:
            self.setplayerimg("back")
        elif self.keymaps["s"][0] == True:
            self.setplayerimg("front")
        elif self.keymaps["d"][0] == True:
            self.setplayerimg("right")
        elif self.keymaps["a"][0] == True:
            self.setplayerimg("left")

        direction = np.array([0, 0])
        for key, val in self.keymaps.items():
            if val[0]:
                direction += val[1]

        if not (direction == 0).all():
            direction = direction*1.0/np.linalg.norm(direction)

            self.speed += self.accleration

            if(self.speed > self.max_speed):
                self.speed = self.max_speed
            
            # Collision detection
            temprect = pygame.Rect(self.rect) # We make the temprect to check for collision, if the moved rect is colliding then we dont move our player rect
            self.rect.topleft += direction*self.speed
            if any(pygame.sprite.spritecollide(self, self.maze.walls_in_screen, dokill=False)):
                self.rect.topleft = temprect.topleft
                self.walking.stop()
                self.walking_is_playing = False
            for sprite in pygame.sprite.spritecollide(self, self.maze.collectables, dokill=True):
                if sprite.type == "bomb":
                    self.bombs_remaining += 1
                else:
                    self.keys += 1
        else:
            self.speed = 0
            self.walking.stop()
            self.walking_is_playing = False

        if self.speed > 0:
            self.animation_state += self.speed*self.animation_rate
            while self.animation_state >= 4.0:
                self.animation_state -= 4.0
            self.setplayerimg(self.facing)
            if not self.walking_is_playing:
                self.walking.play()
                self.walking_is_playing = True
        else:
            self.animation_state = 0
            self.setplayerimg(self.facing)
        