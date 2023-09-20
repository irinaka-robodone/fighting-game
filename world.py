import os
import random
from dataclasses import dataclass

import pygame
from pygame.locals import *
import pandas as pd
import pygame_gui
from pygame_textinput.textinput import TextInput

from ai import ai_response, template

base_dir = os.environ.get("BASE_DIR")

def render_text(text: str, pos: tuple[int, int], size: int, screen: pygame.Surface, color: tuple[int, int, int] = [0,0,0], font_name: str = "MS UI Gothic", bold = True, italic = False):
        font = pygame.font.SysFont(font_name, size, bold, italic)
        text = font.render(text, True, color)
        rect = text.get_rect()
        screen.blit(text, (pos[0]-rect.w//2, pos[1]-rect.h//2))

@dataclass
class Player:
    hp: float
    id: int
    name: str = ""
    waza: int = None
    waza_desc: str = None
    damage_get: int = None
    waza_seikou: str = ""

class World():
    def __init__(self) -> None:
        self.SCREEN_SIZE = [960, 640]
        self.TITLE = "格闘ゲーム"
        self.scene = "start"
        self.running = True
        self.FPS = 60
        self.clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, )
        pygame.display.set_caption(self.TITLE)
        
        self.current_events = []
        self.prev_events = []
        
        self.player_1 = Player(100, 1, name="")
        self.player_2 = Player(100, 2, name="")
        
        self.bg_color = (230,230,230)
        self.font_color = (20,20,20)
        
        self.img1 = pygame.image.load(f"{base_dir}/asset/img/pencil_head.png")
        self.img2 = pygame.image.load(f"{base_dir}/asset/img/fire_robo.png")
        self.img1 = pygame.transform.scale(self.img1, (300, 300))
        self.img2 = pygame.transform.scale(self.img2, (300, 300))
        
        self.img_make_mark = pygame.image.load(f"{base_dir}/asset/img/dead.png").convert()
        self.img_make_mark = pygame.transform.scale(self.img_make_mark, (300, 300))
        self.img_make_mark.set_colorkey((255,255,255))
        
        self.manager = pygame_gui.UIManager((self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]))
        
        self.background = pygame.Surface(self.SCREEN_SIZE)
        self.background.fill(self.bg_color)
        
        pygame.mixer.init(frequency = 44100, size = -16, channels = 1, buffer = 2**12)
        self.channel1 = pygame.mixer.Channel(0)
        self.channel2 = pygame.mixer.Channel(1)
        self.channel1.set_volume(0.2)
        self.channel2.set_volume(0.5)
        
        self.bgm_fight = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_game_boss06.mp3")
        self.sound_title_call = pygame.mixer.Sound(f"{base_dir}/asset/sound/title_call.mp3")
        
        self.channel2.play(self.sound_title_call, loops=0)
        
        self.text_box_player_1 = TextInput(pygame.font.SysFont("yumincho", 30), self.font_color)
        self.text_box_player_2 = TextInput(pygame.font.SysFont("yumincho", 30), self.font_color)
        
    
    def process(self): # ゲームの状態に応じて実行する関数を分ける
        self.time_delta = self.clock.tick(self.FPS)/1000.0
        
        if self.scene == "sentaku":
            self.sentaku()
        elif self.scene == "kekka":
            self.kekka()
        elif self.scene == "start":
            self.show_start_screen()
        elif self.scene == "katimake":
            self.katimake()
        elif self.scene == "namae_gime_1":
            self.namae_gime(self.player_1)
        elif self.scene == "namae_gime_2":
            self.namae_gime(self.player_2)
        self.update_screen()
            
    def update_screen(self):
        pygame.display.flip()
        pygame.display.update()
        self.screen.fill(self.bg_color)
        self.manager.update(self.time_delta)

        self.screen.blit(self.background, (0,0))
        self.manager.draw_ui(self.screen)
        
    def sentaku(self):
        if self.channel1.get_busy() == False:
            self.channel1.play(self.bgm_fight, loops = 1)
            
        render_text(f"{self.player_1.name}", [200,30], 20, self.screen)
        render_text(f"HP: {self.player_1.hp}", [200,60], 20, self.screen)
        
        render_text(f"{self.player_2.name}", [740,30], 20, self.screen)
        render_text(f"HP: {self.player_2.hp}", [740,60], 20, self.screen)
        
        render_text("VS", [480, 30], 24, self.screen)

        self._render_waza(self.player_1.id, pos=[100, 100])
        self._render_waza(self.player_2.id, pos=[640, 100])
        
        self.screen.blit(self.img1, [60, 300])
        self.screen.blit(self.img2, [600, 300])
        
        self._get_event()
        for event in self.current_events:
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.scene = "start"
                
                elif event.key == K_RETURN:
                    self.scene = "sentaku"
                    print(self.scene)
                    
                elif event.key == K_q:
                    self.player_1.waza = 0
                elif event.key == K_w:
                    self.player_1.waza = 1
                elif event.key == K_e:
                    self.player_1.waza = 2
                elif event.key == K_i:
                    self.player_2.waza = 0
                elif event.key == K_o:
                    self.player_2.waza = 1
                elif event.key == K_p:
                    self.player_2.waza = 2
                    
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.end_choice_button:
                    if self.player_1.waza != None and self.player_2.waza != None:
                        self.scene = "kekka"
                        self.n = 0
                        self.end_choice_button.disable()
                        self.next_turn_button.enable()
                        self.responses = ["", ""]
                        print(self.scene)
                    
            self.manager.process_events(event)
    
    def kekka(self):
        
        render_text(f"{self.player_1.name}", [200,30], 20, self.screen)
        render_text(f"HP: {self.player_1.hp}", [200,60], 20, self.screen)
        
        render_text(f"{self.player_2.name}", [740,30], 20, self.screen)
        render_text(f"HP: {self.player_2.hp}", [740,60], 20, self.screen)
        
        render_text("VS", [480, 30], 24, self.screen)
        
        if self.n < 1:
            if random.random() <= waza_loader(self.player_1.id)[self.player_1.waza]["kakuritu"]/100.0:
                self.player_2.damage_get = waza_loader(self.player_1.id)[self.player_1.waza]["damage"]
                self.player_1.waza_desc = waza_loader(self.player_1.id)[self.player_1.waza]["desc"]
                self.player_1.waza_seikou = "成功"
            else:
                self.player_2.damage_get = 0
                self.player_1.waza_desc = waza_loader(self.player_1.id)[self.player_1.waza]["desc"]
                self.player_1.waza_seikou = "失敗"

            if random.random() <= waza_loader(self.player_2.id)[self.player_2.waza]["kakuritu"]/100.0:
                self.player_1.damage_get = waza_loader(self.player_2.id)[self.player_2.waza]["damage"]
                self.player_2.waza_desc = waza_loader(self.player_2.id)[self.player_2.waza]["desc"]
                self.player_2.waza_seikou = "成功"
            else:
                self.player_1.damage_get = 0
                self.player_2.waza_desc = waza_loader(self.player_2.id)[self.player_2.waza]["desc"]
                self.player_2.waza_seikou = "失敗"
                
            data = [["Status Name", "Description"], 
                    ["player_1_id", f"{self.player_1.id}"], 
                    ["player_2_id", f"{self.player_2.id}"], 
                    ["プレイヤー1_名前", f"{self.player_1.name}"], 
                    ["プレイヤー2_名前", f"{self.player_2.name}"], 
                    ["技を受ける前のプレイヤー1のHP", f"{self.player_1.hp}"], 
                    ["技を受ける前のプレイヤー2のHP", f"{self.player_2.hp}"], 
                    ["プレイヤー1の出した技", f"{self.player_1.waza_desc}"], 
                    ["プレイヤー2の出した技", f"{self.player_2.waza_desc}"], 
                    ["プレイヤー1の出した技の結果", self.player_1.waza_seikou], 
                    ["プレイヤー2の出した技の結果", self.player_2.waza_seikou]]
            
            df = pd.DataFrame(data[1:], index=None, columns=data[0])
            self.responses = ai_response.get_script(df, max_retries=5)
            
            
            self.player_1.hp -= self.player_1.damage_get
            self.player_2.hp -= self.player_2.damage_get
            
        render_text(f"{self.player_1.name}: {self.responses[0]}", [480, 200], 16, self.screen, bold=False)
        render_text(f"{self.player_2.name}: {self.responses[1]}", [480, 224], 16, self.screen, bold=False)
        
        render_text(f"{self.player_1.name}は{self.player_1.damage_get}のダメージをうけた！", [480, 270], 16, self.screen)
        render_text(f"{self.player_2.name}は{self.player_2.damage_get}のダメージをうけた！", [480, 300], 16, self.screen)

        self._render_waza(self.player_1.id, pos=[100, 100])
        self._render_waza(self.player_2.id, pos=[640, 100])
        
        self.screen.blit(self.img1, [60, 320])
        self.screen.blit(self.img2, [600, 320])
        
        # self.end_choice_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((430, 100), (100, 40)),
        #                                     text='Next Turn',
        #                                     manager=self.manager)
        
        if self.player_1.hp <= 0 or self.player_2.hp <= 0:
            self.scene = "katimake"
        
        self._get_event()
        for event in self.current_events:
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.scene = "start"
                
                elif event.key == K_RETURN:
                    # self.scene = "sentaku"
                    print(self.scene)
                    
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.next_turn_button:
                    self.scene = "sentaku"
                    self.player_2.waza = None
                    self.player_1.waza = None
                    
                    self.end_choice_button.enable()
                    self.next_turn_button.disable()
                    print(self.scene)
                    
            self.manager.process_events(event)
            
        self.n += 1

    
    def katimake(self):
        render_text(f"{self.player_1.name}", [200,30], 20, self.screen)
        render_text(f"HP: {self.player_1.hp}", [200,60], 20, self.screen)
        
        render_text(f"{self.player_2.name}", [740,30], 20, self.screen)
        render_text(f"HP: {self.player_2.hp}", [740,60], 20, self.screen)
        
        # render_text("VS", [480, 30], 24, self.screen)

        render_text(f"{self.player_1.name}は{self.player_1.damage_get}のダメージをうけた！", [480, 200], 18, self.screen)
        render_text(f"{self.player_2.name}は{self.player_2.damage_get}のダメージをうけた！", [480, 230], 18, self.screen)

        self._render_waza(self.player_1.id, pos=[100, 100])
        self._render_waza(self.player_2.id, pos=[640, 100])
        
        self.screen.blit(self.img1, [60, 300])
        self.screen.blit(self.img2, [600, 300])
        
        self.next_turn_button.disable()
        self.end_choice_button.disable()
        
        render_text("Escキーでスタート画面に戻る", [480, 360], 20, self.screen)
        if self.player_1.hp <= 0 and self.player_2.hp <= 0:
            render_text(f"引き分け", [480, 300], 32, self.screen)
            self.screen.blit(self.img_make_mark, [60, 240])
            self.screen.blit(self.img_make_mark, [600, 240])
            
        elif self.player_1.hp <= 0:
            render_text(f'{self.player_2.name}の勝ち', [480, 300], 32, self.screen)
            self.screen.blit(self.img_make_mark, [60, 240])

        elif self.player_2.hp <= 0:
            render_text(f'{self.player_1.name}の勝ち', [480, 300], 32, self.screen)
            self.screen.blit(self.img_make_mark, [600, 240])
        
        self._get_event()
        for event in self.current_events:
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.scene = "start"
                    self.__init__()
                
                elif event.key == K_RETURN:
                    # self.scene = "sentaku"
                    print(self.scene)
                    
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.next_turn_button:
                    self.scene = "sentaku"
                    self.player_2.waza = None
                    self.player_1.waza = None
                    
                    self.end_choice_button.enable()
                    self.next_turn_button.disable()
                    print(self.scene)
                    
            self.manager.process_events(event)
        
    def show_start_screen(self):
        self.channel1.stop()
        self.screen.fill(self.bg_color)
        
        render_text("しょぼい格ゲー", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2-20), 32, self.screen, self.font_color)
        render_text("エンターキーを押してスタート", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2+20), 16, self.screen, self.font_color)
        
        self._get_event()
        for event in self.current_events:
            
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                
                elif event.key == K_RETURN:
                    self.scene = "namae_gime_1"
                    # self.next_turn_button.enable()
                    print(self.scene)
                    
            elif event.type == pygame.USEREVENT:
                print(event.Text)
                    
        # self.text_box_player_2.update(self.current_events)
        # self.screen.blit(self.text_box_player_2.get_surface(), [600, 100])
        
    def namae_gime(self, player: Player):
        
        render_text(f"プレイヤー{player.id}の名前を入力", [480, 100], 24, self.screen, bold = False)
        self._get_event()
        for event in self.current_events:
            
            if event.type == QUIT:
                self.running = False
            elif event.type == pygame.USEREVENT:
                print(event.Text)
                if 0 < len(event.Text):
                    player.name = event.Text
                    print(player)
                    if self.player_1.name != "" and self.player_2.name != "":
                        self.scene = "sentaku"
                        self.end_choice_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((420, 80), (120, 40)),
                                            text='End Choice',
                                            manager=self.manager)
                        self.next_turn_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((420, 120), (120, 40)),
                                            text='Next Turn',
                                            manager=self.manager)
                        self.next_turn_button.disable()
                        self.channel1.play(self.bgm_fight, loops = 1)
                        
                        
                    elif self.player_2.name == "":
                        self.scene = "namae_gime_2"
                    elif self.player_1.name == "":
                        self.scene = "namae_gime_1"
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                
                # elif event.key == K_RETURN:
                #     self.scene = "namae_gime_2"
                #     self.channel1.play(self.bgm_fight, loops = 1)
                #     # self.next_turn_button.enable()
                #     self.end_choice_button.enable()
                #     print(self.scene)
                    
            self.manager.process_events(event)
            
        self.text_box_player_1.update(self.current_events)
        self.screen.blit(self.text_box_player_1.get_surface(), [480, 130])
        
        
                    
    def _get_event(self):
        if len(self.current_events) > 0:
            self.prev_events = self.current_events
        self.current_events = pygame.event.get()
        
    def _render_waza(self, player_id: int, pos: list):
        waza_list = waza_loader(player_id)
        for i,waza in enumerate(waza_list):
            render_text(f'{waza["wazamei"]} [{waza["key"]}]', [pos[0], pos[1]+30*i], 16, self.screen)
            render_text(f'ダメージ: {waza["damage"]}', [pos[0]+100, pos[1]+30*i], 15, self.screen)
            render_text(f'確率: {waza["kakuritu"]}', [pos[0]+200, pos[1]+30*i], 15, self.screen)
    
def scene_switcher(scene_from: str = "start"):
    import os
    base_dir = os.environ.get("BASE_DIR")
    scene_change_list = pd.read_csv(f"{base_dir}/scene_change_list.csv", sep=",", encoding="utf-8", header=0)
    
    print(scene_change_list)
    
def waza_loader(player_id: str):
    import os
    base_dir = os.environ.get("BASE_DIR")
    waza = pd.read_csv(f"{base_dir}/waza.csv", sep=",", encoding="utf-8", header=0)
    return waza[waza.player==player_id].to_dict('records')
    
if __name__ == "__main__":
    # scene_switcher()
    waza_list = waza_loader(0)
    print(waza_list)