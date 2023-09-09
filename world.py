import pygame

class World():
    def __init__(self) -> None:
        pygame.init()
        self.scene = "start"
        pass
    
    def process(self):
        if self.scene == "choise":
            self.do_something()
        elif self.scene == "start":
            self.show_start_screen()
        
    def show_start_screen(self):
        pygame.display.set_caption("2P格闘ゲーム")
        
    def do_something(self):
        pass
    