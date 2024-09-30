import pygame
import numpy as np

spritesfolder = "Sprites/walls/verydarkwalls/"
class Wallsclass(pygame.sprite.Sprite):
    def __init__(self, grid_size, position):
        super().__init__()
        self.grid_size = grid_size
        Wallsclass.grid_size = grid_size
        self.image = pygame.image.load(spritesfolder+"00.png").convert_alpha()
        self.scaling_factor = self.grid_size/self.image.get_height()
        self.image = pygame.transform.scale_by(self.image, (self.scaling_factor))
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        
        

    def set_image_rect(self, imagefile, rectfile):
        pos = np.array(self.rect.topleft)
        self.image = pygame.image.load(spritesfolder + imagefile).convert_alpha()
        self.rect_image = pygame.image.load(spritesfolder + rectfile).convert_alpha() # self have another image for each wall which has the rect bounding
        scaling_factor = (self.grid_size/self.image.get_height())
        self.image = pygame.transform.scale_by(self.image, scaling_factor)
        self.rect_image = pygame.transform.scale_by(self.rect_image, scaling_factor) # Scale them by the same factor
        
        self.rect = self.rect_image.get_rect() # Make the rect from the new rect image
        self.rect.topleft = pos
    @classmethod
    def set_sprites(cls, where_walls, spritesgroup : pygame.sprite.Group):
        for i in spritesgroup.sprites():
            pos = np.array(i.rect.topleft)
            xaxis = int(cls.pointin(pos + [cls.grid_size, 0], where_walls))
            yaxis = int(cls.pointin(pos + [0, cls.grid_size], where_walls))
            i.image = pygame.image.load(spritesfolder + f"{xaxis}{yaxis}.png").convert_alpha()
            i.rect_image = pygame.image.load(spritesfolder + f"{xaxis}{yaxis}rect.png").convert_alpha() # I have another image for each wall which has the rect bounding
            scaling_factor = (cls.grid_size/i.image.get_height())
            i.image = pygame.transform.scale_by(i.image, scaling_factor)
            i.rect_image = pygame.transform.scale_by(i.rect_image, scaling_factor) # Scale them by the same factor

            i.rect = i.rect_image.get_rect() # Make the rect from the new rect image
            i.rect.topleft = pos

            if xaxis == 1 and yaxis == 1:
                
                if cls.pointin(pos + [cls.grid_size, cls.grid_size], where_walls): # This means that there is a square of walls formed, this isnt rendered nicely as it is so there should be another white square to render it properly
                    filling_box_image = pygame.Surface((cls.grid_size, cls.grid_size))
                    # filling_box_image.fill(pygame.Color(74, 74, 74))
                    filling_box_image.fill("White")
                    i.image = filling_box_image
                else:
                    temp = Wallsclass(cls.grid_size, pos)
                    temp.set_image_rect("11.png", "11rect2.png") # make another bounding box because this wall's bounding box is a combination of two rectangles
                    spritesgroup.add(temp)

    @classmethod
    def pointin(cls, p : np.ndarray, points : np.ndarray):
        return (points == p).all(1).any(0)
