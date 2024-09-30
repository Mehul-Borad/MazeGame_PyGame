import pygame

image_path = "Sprites/collectables/"
class collectable(pygame.sprite.Sprite):
    def __init__(self, grid_size, position, type):
        self.grid_size = grid_size
        self.type = type
        super().__init__()
        if type == "bomb":
            self.image_path = image_path + "bomb.png"
        else:
            self.image_path = image_path + "key.png"
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.scaling_fac = (self.grid_size/16)
        self.image = pygame.transform.scale_by(self.image, self.scaling_fac)
        self.rect = self.image.get_rect()
        self.rect.center = position # Note : the middle is taken as the position