import pygame
import random
import player_smooth
import rays
import score
import enemy
import collectables
import screens
import numpy as np
import dfs
import prim
from sys import exit
import time
from walls import Wallsclass
from pathway import Pathwayclass
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

font = "fonts/AldotheApache.ttf"
class Maze:
    def __init__(self, use_prim = True, time_limit = 20, no_of_enemies : int = 10, enemy_speed = 2.5, keys_req : int = 4, no_bombs : int = 5, no_bombs_player : int = 0, grid_dim : int = 32, grid_size : int = 50, screen_size_in_grids : int = 10, branchpaths : int = 10, sol_points : int = 5, filler_density = 0.3):
        self.game_running = True
        self.size = grid_size*grid_dim
        self.use_prim = use_prim
        self.no_enemies = no_of_enemies
        self.no_bombs = no_bombs
        self.no_bombs_player = no_bombs_player
        self.keys_req = keys_req
        self.enemy_speed = enemy_speed
        self.time_limit = time_limit
        self.player_killed = False
        self.grid_dim = grid_dim
        self.filler_density = filler_density
        self.start_time = time.time()
        self.time_left = self.time_limit
        self.branch_paths = branchpaths
        self.is_reported = False
        self.points_in_sol = sol_points
        self.np_sprite_in_screen = np.vectorize(lambda x : self.in_screen(x.rect), otypes=[np.bool_])
        self.np_render_sprite = np.vectorize(self.render_sprite, otypes=[None])
        # self.np_update_acc_vel = np.vectorize(self.update_acc_vel)
        self.fps = clock.get_fps()
        self.grid_size = grid_size
        self.screen_size = self.grid_size*screen_size_in_grids
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        pygame.display.set_caption('Maze Game by Mehul Borad')

        self.time_for_red = 5
        self.non_spawn_rad = 7*self.grid_dim
        # self.fps_updates_delta = 10

        # self.last_fps = 60

        self.step_grid = np.arange(0, self.size, self.grid_size)
        self.grid_points = np.stack((np.meshgrid(self.step_grid, self.step_grid)), axis = 2).reshape((self.grid_dim**2, 2))
        self.included_points = [i for i in self.grid_points if self.included_condition(i)]
        self.start_point = np.array([0, 0])
        self.make_sol_and_walkables()

        self.middle = np.array([int(self.screen_size/2), int(self.screen_size/2)])
        self.background = pygame.Surface((self.size, self.size))
        self.end_box = pygame.Surface((self.grid_size, self.grid_size))
        self.end_box.fill("Red")
        self.end_box_rect = self.end_box.get_rect()
        self.end_box_rect.topleft = self.end_point
        self.background.fill('White')
        self.bomb_sur = pygame.image.load("Sprites/collectables/bomb.png").convert_alpha()
        self.key_sur = pygame.image.load("Sprites/collectables/key.png").convert_alpha()
        self.scaling_factor = self.grid_size/16
        self.bomb_sur = pygame.transform.scale_by(self.bomb_sur, self.scaling_factor)
        self.key_sur = pygame.transform.scale_by(self.key_sur, self.scaling_factor)

        self.walls = pygame.sprite.Group()
        self.pathways = pygame.sprite.Group()
        for i in self.where_walls:
            wall = Wallsclass(self.grid_size, i)
            self.walls.add(wall)
        for i in self.grid_points:
            path = Pathwayclass(self.grid_size, i)
            self.pathways.add(path)
        
        # Initializing the player sprite
        player_smooth.Player.load_images()
        self.player = player_smooth.Player(grid_size=self.grid_size, wallsSprites=self.walls, bombs=self.no_bombs_player, maze = self)
        self.player.rect.topleft = self.start_point
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.player_pos = np.array(self.player.rect.topleft) - self.player.image_rect_offset
        self.offset = self.player_pos - self.middle

        # Initializing the walls
        Wallsclass.set_sprites(where_walls=self.where_walls, spritesgroup = self.walls)
        self.wallsSprites = np.array(self.walls.sprites())
        self.walls_in_screen = self.wallsSprites[self.np_sprite_in_screen(self.wallsSprites)]

        # Initializing the pathways
        self.pathwaysSprites = np.array(self.pathways.sprites())
        self.pathways_in_screen = self.pathwaysSprites[self.np_sprite_in_screen(self.pathwaysSprites)]

        # Initializing the bombs
        self.collectables = pygame.sprite.Group()
        for _ in range(self.no_bombs):
            self.collectables.add(collectables.collectable(self.grid_size, random.choice(self.walkables) + [self.grid_size/2, self.grid_size/2], "bomb"))
        self.collectablesSprites = np.array(self.collectables.sprites())

        # Initializing the enemies
        enemy.Enemy.load_images()
        self.enemies = pygame.sprite.Group()
        self.spawn_tiles = [p for p in self.walkables if not (self.dist(p, self.start_point) <= self.non_spawn_rad)]
        for _ in range(self.no_enemies):
            self.enemies.add(enemy.Enemy(self.grid_size, random.choice(self.spawn_tiles), self, speed=self.enemy_speed))
        self.enemiesSprites = np.array(self.enemies.sprites())

        # Initializing the Ray class
        rays.Ray.walls = self.walls_in_screen
        
    def coord_from_path(self, p, path):
        l = [p]
        def nextp(q, code): # form the code of movement get the next coordinates of the grid cell. There is a code for the movement, 0 is up, 1 is right, 2 is down, 3 is left
            if code%2 == 0:
                return np.array([q[0], q[1] - self.grid_size*(-1)**int(code/2)])
            else:
                return np.array([q[0] + self.grid_size*(-1)**int(code/2), q[1]])
        for i in path:
            l.append(nextp(l[len(l) - 1], i))
        return np.array(l)

    def randompath(self, p1 : np.ndarray, p2 : np.ndarray): # this creates a random path from p1 to p2 but the path is of the smallest length only
        n = int(abs((p1[0] - p2[0])/self.grid_size)) # The diff in x axis
        m = int(abs((p1[1] - p2[1])/self.grid_size)) # The diff in y axis
        px = 1 if p1[0] - p2[0] < 0 else 3 # Based on the arrangments of p1 and p2 we only go right or only go left
        py = 2 if p1[1] - p2[1] < 0 else 0 # Same but for y axis
        path = np.concatenate((np.ones(n)*px, np.ones(m)*py))
        random.shuffle(path) # shuffle the movements codes
        return (path)

    def included_condition(self, p):
        return not (p[0] > self.size*0.2 and p[0] < self.size*0.8)
    
    def get_neighbours(self, p : np.ndarray):
        l = []
        if p[1] + self.grid_size < self.size:
            l.append([p[0], p[1] + self.grid_size])
        if p[1] - self.grid_size >= 0:
            l.append([p[0], p[1] - self.grid_size])
        if p[0] + self.grid_size < self.size:
            l.append([p[0]  + self.grid_size, p[1]])
        if p[0] - self.grid_size >= 0:
            l.append([p[0] - self.grid_size, p[1]])
        return np.array(l)
    def get_border_points(self, points : np.ndarray):
        l = []
        for p in points:
            for m in [n for n in self.get_neighbours(p) if not self.pointin(n, points)]:
                l.append(m)
        return np.array(l)

    def pointin(self, p : np.ndarray, points : np.ndarray):
        return (points == p).all(1).any(0)

    def make_solution(self, no_points):
        rand_points = np.array(random.sample(list(self.included_points), no_points))

        # print("rand_points = ", rand_points)
        path = np.array(self.randompath(self.start_point, rand_points[0]))
        for i in range(no_points - 1):
            path = np.append(path, self.randompath(rand_points[i], rand_points[i + 1]))
        path = np.append(path, self.randompath(rand_points[no_points - 1], self.end_point))
        
        return self.coord_from_path(self.start_point, path)
    # solution = randompath((0, 0), (grid_dim - 1, grid_dim - 1))

    # print("solution = ", solution)
    def make_filler_random(self, density):
        l = []
        for i in self.grid_points:
            if (random.random() < density):
                l.append(i)
        return np.array(l)
    
    def dist(self, p1 : np.ndarray, p2 : np.ndarray):
        return np.linalg.norm(p1 - p2, ord=1)
    
    def make_filler_paths(self, no_lines, solution_path):
        l = []
        rand_path_ends = random.sample(list(self.grid_points), no_lines)
        rand_path_start = random.sample(list(solution_path), no_lines)
        for i in range(no_lines):
            for p in self.coord_from_path(rand_path_start[i],self.randompath(rand_path_start[i], rand_path_ends[i])):
                l.append(p)
        return np.array(l)

    def make_sol_and_walkables(self):
        if self.use_prim:
            grid, self.start_point, self.end_point = (prim.prim(self.grid_dim, self.grid_dim))
            dfs.dfs_solve(self.start_point, self.end_point, grid=='c', [self.start_point], [])
            self.start_point *= self.grid_size
            self.end_point *= self.grid_size
            self.walkables = self.grid_points[(grid=='c').flatten()]
            self.where_walls = self.grid_points[(grid=='w').flatten()]
        else:
            self.start_point = np.array([random.choice(np.arange(0, self.size, self.grid_size)), 0])
            self.end_point = np.array([random.choice(np.arange(0, self.size, self.grid_size)), self.size - self.grid_size])
            self.solution = self.make_solution(self.points_in_sol)
            self.solution_border = self.get_border_points(self.solution)
            self.filler = self.make_filler_paths(self.branch_paths, self.solution)
            self.filler2 = self.make_filler_random(self.filler_density)
            self.walkables = np.concatenate((self.filler, self.filler2, self.solution), axis = 0)
            self.where_walls = np.array([p for p in self.grid_points if not self.pointin(p, self.walkables)])

    def in_screen(self, rect):
        pos = rect.topleft - self.offset
        if (pos >= -self.grid_size).all() and (pos <= self.screen_size).all():
            return True
        else:
            return False
        
    def render_sprite(self, sprite):
        pos = sprite.rect.topleft - self.offset
        if hasattr(sprite, "image_rect_offset"):
            pos -= sprite.image_rect_offset
        self.screen.blit(sprite.image, pos)

    
    def update_acc_vel(self, sprite, f):
        if hasattr(sprite, "accleration"):
            sprite.accleration *= f
        sprite.max_speed *= f

    def update(self):
        # Event loop
        
        rays.Ray.walls = self.walls_in_screen
        self.time = time.time() - self.start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            self.player.player_movement(event)

        self.render_not_enough_keys = False
        if self.player.rect.colliderect(self.end_box_rect): # End the maze game if the player has reached the end
            if self.player.keys >= self.keys_req:
                self.game_running = False
                return 1
            else:
                self.render_not_enough_keys = True
        
        if self.time_left <= 0 :
            self.game_running = True
            return -1
        self.fps = clock.get_fps()

        if self.is_reported:
            self.game_running = False
            return -2
        
        if self.player_killed:
            self.game_running = False
            return -3

        self.player.update()
        for enemy in self.enemies.sprites():
            enemy.update()
        self.enemiesSprites = np.array(self.enemies.sprites())
        self.collectablesSprites = np.array(self.collectables.sprites())

        self.player_pos = np.array(self.player.rect.topleft) - self.player.image_rect_offset
        self.offset = self.player_pos - self.middle

        self.walls_in_screen = self.wallsSprites[self.np_sprite_in_screen(self.wallsSprites)]
        self.pathways_in_screen = self.pathwaysSprites[self.np_sprite_in_screen(self.pathwaysSprites)]
        self.enemies_in_screen = self.enemiesSprites[self.np_sprite_in_screen(self.enemiesSprites)]
        self.collectables_in_screen = self.collectablesSprites[self.np_sprite_in_screen(self.collectablesSprites)]
    
        self.render()

        # print("% time taken by render():",(time_render)*self.fps, "by player.update():",(time_update)*self.fps, "fps =", round(self.fps))
        # print(clock.get_fps())
        clock.tick(40)
        return 0

    # Rendering with blits
    def render(self):
        self.screen.blit(self.background, (0, 0))
        # the Rect of the player is not aligned to the top left of the image of the player, thats why we have many terms to get the actual player_pos
        self.player_image_rect_offset = np.array([(self.player.image.get_width() - self.player.rect.width)/2 + self.player.widthoffset, (self.player.image.get_height() - self.player.rect.height)/2 + self.player.heightoffset])
        player_pos = np.array(self.player.rect.topleft) - self.player_image_rect_offset
        offset = player_pos - self.middle # offset for the images in the screen to make the player in the middle of the screen
        
        # self.enemy_image_rect_offset = np.array([(self.enemy.image.get_width() - self.enemy.rect.width)/2 + self.enemy.widthoffset, (self.enemy.image.get_height() - self.enemy.rect.height)/2 + self.enemy.heightoffset])
        # enemy_pos = np.array(self.enemy.rect.topleft) - self.enemy_image_rect_offset
        # rendering walls and pathways
        self.np_render_sprite(self.pathways_in_screen)
        self.np_render_sprite(self.walls_in_screen)
        self.np_render_sprite(self.player.bombs.sprites())
        self.np_render_sprite(self.collectables_in_screen)
        self.np_render_sprite(self.enemies_in_screen)

        self.screen.blit(self.end_box, self.end_point - offset)
        self.screen.blit(self.player.image, self.middle)
        # Calculation and rendering of the time_left
        self.time_left = self.time_limit - time.time() + self.start_time
        
        if self.time_left > self.time_for_red :
            self.screen.blit(pygame.font.Font(font, 50).render(f"Time left : {round(self.time_left)}", True, "Yellow"), (20, 20))
        else :
            self.screen.blit(pygame.font.Font(font, 50).render(f"Time left : {round(self.time_left)}", True, "Red"), (20, 20))
        
        # render keys and bombs left:
        self.screen.blit(self.bomb_sur, (self.screen_size - 100, 20))
        self.screen.blit(pygame.font.Font(font, 40).render(f"{self.player.bombs_remaining}", True, "chartreuse3"), (self.screen_size - 50, 23))
        self.screen.blit(self.key_sur, (self.screen_size - 240, 25))
        self.screen.blit(pygame.font.Font(font, 40).render(f"{self.player.keys}/{self.keys_req}", True, "gold1"), (self.screen_size - 180, 23))
        self.screen.blit(pygame.font.Font(font, 40).render(f"Floor {current_floor}", True, "blue"), (self.screen_size//2 - 50, self.screen_size-50))

        if self.render_not_enough_keys:
            text = pygame.font.Font(font, 70).render(f"Get {self.keys_req- self.player.keys} more keys", True, "Red")
            text_rect = text.get_rect()
            text_rect.center = self.middle
            self.screen.blit(text, text_rect)
        pygame.display.update()

def makemaze40(bombs):
    return Maze(grid_size = 100, grid_dim = 40, time_limit=200, use_prim=True, screen_size_in_grids=7, no_of_enemies=30, enemy_speed=4, no_bombs_player=bombs, no_bombs=30, keys_req=10)
def makemaze30(bombs):
    return Maze(grid_size = 100, grid_dim = 30, time_limit=200, use_prim=True, screen_size_in_grids=7, no_of_enemies=15, enemy_speed=2.5, no_bombs_player=bombs, no_bombs=10,keys_req=4)
def makemaze15(bombs):
    return Maze(grid_size = 100, grid_dim = 15, time_limit=100, use_prim=True, screen_size_in_grids=7, no_of_enemies=2, enemy_speed=1.5, no_bombs_player=bombs, no_bombs=5,keys_req=1)

pygame.mixer.music.load("music/background.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

initial_bombs = 10

floors = {1:makemaze15, 2:makemaze30, 3:makemaze40}
current_floor = 1
current_maze = floors[current_floor](initial_bombs)
name = screens.inputname(current_maze)
score_till_now = 0

enemy_kill_points = 15
def win_screen(maze : Maze):
    screens.loading(maze)
    global score_till_now
    global current_floor
    global current_maze
    global floors
    print("You won!!")
    is_counting = True
    score_time = 0
    score_enemies = 0
    total_score = 0
    score_enemies_target = (maze.no_enemies - len(maze.enemiesSprites))*enemy_kill_points
    score_time_target = int(maze.time_left)
    total_score_target = score_enemies_target + score_time_target
    
    score_till_now += total_score_target
    ishighscore = score.updatescore(name, total_score_target, f"floor{current_floor}")

    while is_counting:
        maze.screen.blit(maze.background, (0, 0))
        floor_cleared = pygame.font.Font(font, 70).render(f"--Floor {current_floor} Cleared--", True, "Blue")
        time_score_text = pygame.font.Font(font, 50).render(f"Time score : {score_time}", True, "orchid1")
        enemy_score_text = pygame.font.Font(font, 50).render(f"Enemies killed ({maze.no_enemies - len(maze.enemiesSprites)} x {enemy_kill_points}) : {score_enemies}", True, "orchid1")
        total_score_text = pygame.font.Font(font, 50).render(f"Total score : {total_score}", True, "purple")
        maze.screen.blit(floor_cleared, (maze.screen_size//2 - floor_cleared.get_width()//2, 100))
        maze.screen.blit(time_score_text, (maze.screen_size//2 - time_score_text.get_width()//2, 200))
        maze.screen.blit(enemy_score_text, (maze.screen_size//2- enemy_score_text.get_width()//2, 300))
        maze.screen.blit(total_score_text, (maze.screen_size//2- total_score_text.get_width()//2, 400))
        pygame.display.update()
        if score_time != score_time_target:
            score_time+=1
        elif score_enemies != score_enemies_target:
            score_enemies += 1
        elif total_score != total_score_target:
            total_score += 1
        else:
            is_counting = False
    if ishighscore:
        highscore = pygame.font.Font(font, 100).render(f"HighScore!!", True, "deeppink")
        maze.screen.blit(highscore, (maze.screen_size//2- highscore.get_width()//2, 460))

    if current_floor == floors.__len__():
        next_floor_button = pygame.font.Font(font, 50).render(f"finish", True, "blue")
    else:
        next_floor_button = pygame.font.Font(font, 50).render(f"Next floor", True, "blue")
    next_floor_button_rect = next_floor_button.get_rect()
    next_floor_button_rect.topleft = (maze.screen_size//2 - next_floor_button.get_width()//2 + 100, 550)
    repeat_button = pygame.font.Font(font, 50).render(f"Repeat", True, "red")
    repeat_button_rect = repeat_button.get_rect()
    repeat_button_rect.topleft = (maze.screen_size//2- repeat_button.get_width()//2 - 150, 550)
    mainmenu_button = pygame.font.Font(font, 50).render("main menu", True, "Blue")
    mainmenu_button_rect = mainmenu_button.get_rect()
    mainmenu_button_rect.center = (maze.screen_size//2, 630)

    maze.screen.blit(next_floor_button, next_floor_button_rect)
    maze.screen.blit(repeat_button, repeat_button_rect)
    maze.screen.blit(mainmenu_button, mainmenu_button_rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if next_floor_button_rect.collidepoint(pygame.mouse.get_pos()):
                    if current_floor == floors.__len__():
                        current_maze = floors[1](initial_bombs)
                        current_floor = 1
                        score_till_now = 0
                        screens.mainmenu(current_maze)
                        return
                    current_maze = floors[current_floor + 1](current_maze.player.bombs_remaining)
                    current_floor += 1
                    print("next floor!!")
                    return
                elif repeat_button_rect.collidepoint(pygame.mouse.get_pos()):
                    current_maze = floors[current_floor](current_maze.player.bombs_remaining)
                    return
                elif mainmenu_button_rect.collidepoint(pygame.mouse.get_pos()):
                    if current_floor == floors.__len__():
                        current_maze = floors[1](initial_bombs)
                        current_floor = 1
                        score_till_now = 0
                    else:
                        current_maze = floors[current_floor + 1](current_maze.player.bombs_remaining)
                        current_floor += 1
                    screens.mainmenu(current_maze)
                    return
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def lose_screen(maze : Maze, message):
    global current_floor
    global current_maze
    global floors
    global score_till_now
    print(message)
    text = pygame.font.Font(font, 70).render(message, True, "Red")
    text_rect = text.get_rect()
    text_rect.center = (maze.screen_size//2, 200)
    maze.screen.blit(text, text_rect)
    repeat_button = pygame.font.Font(font, 50).render(f"Restart", True, "red")
    repeat_button_rect = repeat_button.get_rect()
    repeat_button_rect.topleft = (maze.screen_size//2- repeat_button.get_width()//2, 300)
    mainmenu_button = pygame.font.Font(font, 50).render("main menu", True, "Blue")
    mainmenu_button_rect = mainmenu_button.get_rect()
    mainmenu_button_rect.center = (maze.screen_size//2, 400)
    # maze.screen.blit(next_floor_button, next_floor_button_rect)
    maze.screen.blit(repeat_button, repeat_button_rect)
    maze.screen.blit(mainmenu_button, mainmenu_button_rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if repeat_button_rect.collidepoint(pygame.mouse.get_pos()):
                    current_maze = floors[1](initial_bombs)
                    current_floor = 1
                    score_till_now = 0
                    return
                elif mainmenu_button_rect.collidepoint(pygame.mouse.get_pos()):
                    current_maze = floors[1](initial_bombs)
                    current_floor = 1
                    score_till_now = 0
                    screens.mainmenu(current_maze)
                    return
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

screens.mainmenu(current_maze)

while True:
    response = current_maze.update()
    if response == 1:
        win_screen(current_maze)
    elif response == -1:
        lose_screen(current_maze, "Time out")
    elif response == -2:
        lose_screen(current_maze, "You have been reported!!")
    elif response == -3:
        lose_screen(current_maze, "You commited suicide!!")

