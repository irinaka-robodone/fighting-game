import pygame
import pandas as pd

def render_text_middle(text: str, pos: tuple[int, int], size: int, screen: pygame.Surface, color: tuple[int, int, int] = [0,0,0], font_name: str = "MS UI Gothic", bold = False, italic = False):
        font = pygame.font.SysFont(font_name, size, bold, italic)
        text = font.render(text, True, color)
        rect = text.get_rect()
        screen.blit(text, (pos[0]-rect.w//2, pos[1]-rect.h//2))
        
def render_text_center(text: str, size, screen: pygame.Surface, color: tuple[int, int, int] = (0,0,0), font_name: str = "MS UI Gothic", bold = False, italic = False):
    screen_size = screen.get_size()
    font = pygame.font.SysFont(font_name, size, bold, italic)
    text = font.render(text, True, color)
    rect = text.get_rect()
    screen.blit(text, ((screen_size[0] - rect.w)//2, (screen_size[1] - rect.h)//2))

def waza_loader(player_id: str):
    import os
    base_dir = os.environ.get("BASE_DIR")
    waza = pd.read_csv(f"{base_dir}/waza.csv", sep=",", encoding="utf-8", header=0)
    return waza[waza.player==player_id].to_dict('records')

def scene_switcher(scene_from: str = "start"):
    import os
    base_dir = os.environ.get("BASE_DIR")
    scene_change_list = pd.read_csv(f"{base_dir}/scene_change_list.csv", sep=",", encoding="utf-8", header=0)
    
    print(scene_change_list)