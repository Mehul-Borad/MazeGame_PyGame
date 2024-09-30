import pygame
import sys
import cloud
import numpy as np

font = "fonts/AldotheApache.ttf"
# folder = "scores/"
def loading(maze):
    maze.screen.fill("white")
    loading_text = pygame.font.Font(font, 80).render(f"Loading...", True, "green")
    loading_text_rect = loading_text.get_rect()
    loading_text_rect.center = (maze.screen_size//2, maze.screen_size//2)
    maze.screen.blit(loading_text, loading_text_rect)
    pygame.display.update()

def mainmenu(maze):
    loading(maze) # display the loading screen till we fetch info from dropbox

    top_players = 5
    leader_board_text = pygame.font.Font(font, 70).render("Leaderboard", 1, "maroon1")
    texts = ["floor1", "floor2", "floor3", "total"]
    floors_text = [pygame.font.Font(font, 30).render(i, 1, "maroon1") for i in texts]
    npfloors = [cloud.get_as_list(i) for i in texts]
    online_text = pygame.font.Font(font, 30).render("(global)" if cloud.isonline else "(local)", 1, "maroon1")
    top_texts = [ [ "" for i in range(top_players)] for fl in range(4)]
    for fl in range(4):
        for i in range(top_players):
            top_texts[fl][i] = f"{i + 1}. " + npfloors[fl][i][0] + "-" + npfloors[fl][i][1]
    top_texts = [[pygame.font.Font(font, 30).render(i, 1, "red") for i in fl] for fl in top_texts]

    start_button = pygame.font.Font(font, 80).render(f"Start", True, "blue")
    start_button_rect = start_button.get_rect()
    start_button_rect.center = (maze.screen_size//2, 500)
        
    maze.screen.fill((255, 255, 255))
    maze.screen.blit(leader_board_text, (maze.screen_size//2 - 150, 20))
    maze.screen.blit(online_text, (maze.screen_size//2 - 50, 90))
    maze.screen.blit(start_button, start_button_rect)
    for fl in range(len(texts)):
        maze.screen.blit(floors_text[fl], (50 + 160*fl, 130))
        for i in range(top_players):
            maze.screen.blit(top_texts[fl][i], (50 + 160*fl, 180 + 50*i))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if start_button_rect.collidepoint(pygame.mouse.get_pos()):
                    return

def inputname(maze):
    base_font = pygame.font.Font(font, 100)
    user_text = ''
    input_rect = pygame.Rect(maze.screen_size//2 - 50, maze.screen_size//2, 500, 110)
    # input_rect.center = (maze.screen_size//2, maze.screen_size//2)
    color_active = pygame.Color('lightskyblue3')  # Color of the input box
    color_passive = pygame.Color('dimgray')
    active = False

    enter_name = pygame.font.Font(font, 70).render("Enter your name:", 1, "deepskyblue")
    enter_name_rect = enter_name.get_rect()
    enter_name_rect.center = (maze.screen_size//2, 200)
    while True:
        user_text = user_text.upper()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return user_text
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        maze.screen.fill((255, 255, 255))
        color = color_active if active else color_passive

        text_surface = base_font.render(user_text, True, (255, 255, 255))

        input_rect.w = max(100, text_surface.get_width() + 10)
        input_rect.centerx = maze.screen_size//2
        pygame.draw.rect(maze.screen, color, input_rect)

        maze.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        maze.screen.blit(enter_name, enter_name_rect)
        pygame.display.update()
