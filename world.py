import pygame
from pygame.locals import *
import pandas as pd

class World():
    def __init__(self) -> None:
        self.SCREEN_SIZE = [960, 480]
        self.TITLE = "格闘ゲーム"
        self.scene = "start"
        self.running = True
        self.FPS = 60
        self.clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, )
        pygame.display.set_caption(self.TITLE)
        
    
    def process(self): # ゲームの状態に応じて実行する関数を分ける
        if self.scene == "sentaku":
            self.sentaku()
        if self.scene == "kekka":
            self.kekka()
        if self.scene == "start":
            self.show_start_screen()
            
        self.update_screen()
            
    def update_screen(self):
        pygame.display.flip()
        pygame.display.update()
        
    def sentaku(self):
        pass
    
    def kekka(self):
        pass
    
    def render_text(self, text, pos: tuple[int, int], size, color: tuple[int, int, int], font_name: str = "MS UI Gothic", bold = True, italic = False):
        font = pygame.font.SysFont(font_name, size, bold, italic)
        text = font.render(text, True, color)
        rect = text.get_rect()
        self.screen.blit(text, (pos[0]-rect.w//2, pos[1]-rect.h//2))
        
    def show_start_screen(self):
        self.screen.fill((255,255,255))
        
        self.render_text("シューティングゲーム", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2-40), 32, (0,0,0), bold=True)
        self.render_text("エンターキーを押してゲームスタート", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2+60), 16, (0,0,0))
        for event in pygame.event.get():
            
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                
                elif event.key == K_RETURN:
                    self.current_scene = "main"
    
def scene_switcher(scene_from: str = "start"):
    import os
    base_dir = os.environ.get("BASE_DIR")
    scene_change_list = pd.read_csv(f"{base_dir}/scene_change_list.csv", sep=",", encoding="utf-8", header=0)
    
    print(scene_change_list)
    
if __name__ == "__main__":
    scene_switcher()