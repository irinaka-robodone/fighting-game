import os
import sys

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

class WazaLoader():
    def __init__(self, filepath: str) -> None:
        import os
        self.__waza_df = pd.read_csv(resource_path(filepath), sep=",", encoding="utf-8", header=0)
        
    def load_player_waza_list(self, player_id) -> list[dict]:
        return self.__waza_df[self.__waza_df.player==player_id].to_dict('records')
    
    def load_waza(self, player_id, waza_id) -> dict:
        return self.load_player_waza_list(player_id)[waza_id]
    
    @property
    def waza_df(self) -> pd.DataFrame:
        return self.__waza_df 

def resource_path(relative_path):
    print(os.getcwd())
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("asset/"), relative_path)