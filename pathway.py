import pygame
import random

image_path = "Sprites/tiles/cleantile.png"
randomized_path = "Sprites/tiles/randomizedcleantile/"
class Pathwayclass(pygame.sprite.Sprite):
    randomized = True
    no_of_rand_tiles = 4
    def __init__(self, grid_size, position):
        self.grid_size = grid_size
        super().__init__()

        # Randomize the tiles
        if Pathwayclass.randomized: 
            n = random.randint(0, Pathwayclass.no_of_rand_tiles - 1)
            self.image = pygame.image.load(randomized_path + f"{n}.png").convert_alpha()
        else:
            self.image = pygame.image.load(image_path).convert_alpha()
        
        self.scaling_fac = (self.grid_size/self.image.get_height())
        self.image = pygame.transform.scale_by(self.image, self.scaling_fac)
        self.rect = self.image.get_rect()
        self.m = 0
        self.offset = [self.scaling_fac*self.m, self.scaling_fac*self.m]
        self.rect.topleft = position + self.offset