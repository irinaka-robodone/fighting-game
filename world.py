import os
import random

import pygame
from pygame.locals import *
import pandas as pd
import pygame_gui
from pygame_textinput.textinput import TextInput

from utils import render_text_center, render_text_middle, waza_loader
from ai import ai_response
from component import Player

base_dir = os.environ.get("BASE_DIR")

class World():
    def __init__(self, ai_mode: bool = False) -> None:
        self.SCREEN_SIZE = [960, 640]
        self.TITLE = "格闘ゲーム"
        self.scene = "start"
        self.running = True
        self.FPS = 60
        self.clock = pygame.time.Clock()
        pygame.init()
        self.ai_mode = ai_mode
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.display.set_caption(self.TITLE)
        
        self.current_events = []
        self.prev_events = []
        
        self.player_1 = Player(100, 1)
        self.player_2 = Player(100, 2)
        
        self.bg_color = (230,230,230)
        self.font_color = (20,20,20)
        
        self.img1 = pygame.image.load(f"{base_dir}/asset/img/player1.png")
        self.img2 = pygame.image.load(f"{base_dir}/asset/img/player2.jpg")
        self.img1 = pygame.transform.scale(self.img1, (300, 300))
        self.img2 = pygame.transform.scale(self.img2, (300, 300))
        
        self.img_loser_mark = pygame.image.load(f"{base_dir}/asset/img/dead.png").convert()
        self.img_loser_mark = pygame.transform.scale(self.img_loser_mark, (300, 300))
        self.img_loser_mark.set_colorkey((255,255,255))
        
        self.manager = pygame_gui.UIManager((self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]))
        
        self.background = pygame.Surface(self.SCREEN_SIZE)
        self.background.fill(self.bg_color)
        
        pygame.mixer.init(frequency = 44100, size = -16, channels = 1, buffer = 2**12)
        self.channel1 = pygame.mixer.Channel(0)
        self.channel2 = pygame.mixer.Channel(1)
        self.channel1.set_volume(0.2)
        self.channel2.set_volume(0.5)
        
        self.bgm_fight = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_game_boss06.mp3")
        self.sound_title_call = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_game_boss06.mp3")
        self.es_attack_normal = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_se_battle14.mp3")
        self.es_attack_heavy = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_se_battle06.mp3")
        self.es_attack_missed = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_se_8bit26.mp3")
        
        self.channel2.play(self.sound_title_call, loops=0)
        
        self.input_box_player_name = TextInput(pygame.font.SysFont("yumincho", 30), self.font_color)
        
    
    def process(self): # ゲームの状態に応じて実行する関数を分ける
        self.time_delta = self.clock.tick(self.FPS)/1000.0
        
        if self.scene == "sentaku":
            self.sentaku()
        elif self.scene == "kekka":
            self.kekka(self.ai_mode)
        elif self.scene == "start":
            self.show_start_screen()
        elif self.scene == "katimake":
            self.katimake()
        elif self.scene == "input_name_1":
            self.input_name(self.player_1)
        elif self.scene == "input_name_2":
            self.input_name(self.player_2)
        self._update_screen()
        self._control_sound()
            
    def _update_screen(self):
        pygame.display.flip()
        pygame.display.update()
        self.screen.fill(self.bg_color)
        self.manager.update(self.time_delta)
        self.screen.blit(self.background, (0,0))
        self.manager.draw_ui(self.screen)
    
    def show_start_screen(self):
        self.channel1.stop()
        self.screen.fill(self.bg_color)
        
        render_text_middle("しょぼい格ゲー", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2-20), 32, self.screen, self.font_color)
        render_text_middle("エンターキーを押してスタート", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2+20), 16, self.screen, self.font_color)
        
        self._get_event()
        self._handle_event(self.scene)
    
    def input_name(self, player: Player):
        
        render_text_middle(f"プレイヤー{player.id}の名前を入力", [480, 100], 24, self.screen, bold = False)
        self._get_event()
        self._handle_event(self.scene, player)
            
        self.input_box_player_name.update(self.current_events)
        self.screen.blit(self.input_box_player_name.get_surface(), [480, 130])
    
    def sentaku(self):
        
        self._render_status(self.scene)
        self.screen.blit(self.img1, [60, 320])
        self.screen.blit(self.img2, [600, 320])
        
        self._get_event()
        self._handle_event(self.scene)
    
    def kekka(self, ai_mode: bool = False):
        
        self.elapsed_time += self.time_delta
        self._render_status("kekka:before")
        
        """
        todo
        1. openai api アクセスを非同期処理にする。(待機時間が長いし正常なResponseが返ってくる確証がないため)
            a. timeout を設定できるようにして、それ以上返ってこなかったら、llmの出力を使わないようにする。
            b. llmの返答待ちの間も、アプリを閉じたり、スタート画面に行ったり、他のセリフを表示したりなど、ユーザーのインプットを受け付けられるようにする。
            
        """
        if self.n < 1:
            self._judge_waza_success([self.player_1, self.player_2])
            self.player_1.hp -= self.player_1.damage_get
            self.player_2.hp -= self.player_2.damage_get
            
            if ai_mode == True:
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
            else:
                pass
            
            if self.player_2.waza_seikou == "成功" and self.player_2.waza != 2:
                self.channel2.play(self.es_attack_normal)
            elif self.player_2.waza_seikou == "成功" and self.player_2.waza == 2:
                self.channel2.play(self.es_attack_heavy)
            else:
                self.channel2.play(self.es_attack_missed)
        
        self._render_status("kekka", ai_mode)
        
        if self.elapsed_time >= 1 and self._player_1_attack_was_displayed == False:
            if self.player_1.waza_seikou == "成功" and self.player_1.waza != 2:
                self.channel2.play(self.es_attack_normal)
            elif self.player_1.waza_seikou == "成功" and self.player_1.waza == 2:
                self.channel2.play(self.es_attack_heavy)
            else:
                self.channel2.play(self.es_attack_missed)
            self._player_1_attack_was_displayed = True

        self.screen.blit(self.img1, [60, 320])
        self.screen.blit(self.img2, [600, 320])
        
        if self.player_1.hp <= 0 or self.player_2.hp <= 0:
            self.scene = "katimake"
        
        self._get_event()
        self._handle_event(self.scene)
            
        self.n += 1
    
    def katimake(self):
        
        self.screen.blit(self.img1, [60, 320])
        self.screen.blit(self.img2, [600, 320])
        self._render_status(self.scene)
        
        self._get_event()
        self._handle_event(self.scene)
        
    def _get_event(self):
        if len(self.current_events) > 0:
            self.prev_events = self.current_events
        self.current_events = pygame.event.get()
        
    def _judge_waza_success(self, players: list[Player] | Player):
        if type(players) == Player:
            waza = (players.id)[players.waza]
            threshold = waza["kakuritu"]/100.0
            players.waza_desc = waza["desc"]
            if random.random() < threshold:
                if "-" in waza["damage"]:
                    damage = waza["damage"]
                    damage = random.randrange("-")
                    players.damage_give = damage
                players.damage_give = waza["damage"]
                players.waza_seikou = "成功"
            else:
                players.damage_give = 0
                players.waza_seikou = "失敗"
        else:
            for player in players:
                waza = waza_loader(player.id)[player.waza]
                player.yuuri = waza["yuuri"]
                threshold = waza["kakuritu"]/100.0
                player.waza_desc = waza["desc"]
                player.waza_id = waza["id"]
                if random.random() < threshold:
                    player.damage_give = waza["damage"]
                    player.waza_seikou = "成功"
                else:
                    player.damage_give = 0
                    player.waza_seikou = "失敗"
                    
            for i, player in enumerate(players):
                teki = players[i-1]
                
                    
        self.player_1.damage_get = self.player_2.damage_give
        self.player_2.damage_get = self.player_1.damage_give
    
    def _render_status(self, scene_name: str, ai_mode: bool = False):
        render_text_middle(f"{self.player_1.name}", [200,30], 20, self.screen)
        render_text_middle(f"HP: {self.player_1.hp}", [200,60], 20, self.screen)
        render_text_middle(f"{self.player_2.name}", [740,30], 20, self.screen)
        render_text_middle(f"HP: {self.player_2.hp}", [740,60], 20, self.screen)
        
        if scene_name == "sentaku":
            self._render_waza(self.player_1.id, pos=[100, 100])
            self._render_waza(self.player_2.id, pos=[640, 100])
            
        elif scene_name == "kekka:before":
            render_text_middle("VS", [480, 30], 24, self.screen)
            self._render_waza(self.player_1.id, pos=[100, 100])
            self._render_waza(self.player_2.id, pos=[640, 100])
            
        elif scene_name == "kekka":
            if self.elapsed_time >= 0:
                render_text_middle(f"{self.player_1.name}は{self.player_1.damage_get}のダメージをうけた！", [480, 270], 16, self.screen)
            if self.elapsed_time >= 1:
                render_text_middle(f"{self.player_2.name}は{self.player_2.damage_get}のダメージをうけた！", [480, 300], 16, self.screen)
            
            if ai_mode == True:
                render_text_middle(f"{self.player_1.name}: {self.responses[0]}", [480, 200], 16, self.screen, bold=False)
                render_text_middle(f"{self.player_2.name}: {self.responses[1]}", [480, 224], 16, self.screen, bold=False)
            else:
                pass
            
        elif scene_name == "katimake":
            self._render_waza(self.player_1.id, pos=[100, 100])
            self._render_waza(self.player_2.id, pos=[640, 100])
            render_text_middle(f"{self.player_1.name}は{self.player_1.damage_get}のダメージをうけた！", [480, 200], 18, self.screen)
            render_text_middle(f"{self.player_2.name}は{self.player_2.damage_get}のダメージをうけた！", [480, 230], 18, self.screen)
            
            if self.player_1.hp <= 0 and self.player_2.hp <= 0:
                render_text_middle(f"引き分け", [480, 300], 32, self.screen)
                self.screen.blit(self.img_loser_mark, [60, 320])
                self.screen.blit(self.img_loser_mark, [600, 320])
                
            elif self.player_1.hp <= 0:
                render_text_middle(f'{self.player_2.name}の勝ち', [480, 300], 32, self.screen)
                self.screen.blit(self.img_loser_mark, [60, 320])
                
            elif self.player_2.hp <= 0:
                render_text_middle(f'{self.player_1.name}の勝ち', [480, 300], 32, self.screen)
                self.screen.blit(self.img_loser_mark, [600, 320])
            
            render_text_middle("Escキーでスタート画面に戻る", [480, 360], 20, self.screen, bold=True)
    
    def _handle_event(self, scene_name: str = None, player_on_focus: Player = None):
        """### 各フレームで１回だけ呼ばれイベントを処理する。
        
        Args:
            scene_name (str, optional): イベントを処理する現在のシーンを指定します。シーンごとに使用するキーや想定されたイベントが異なっているため正しいシーン名を与えてください。None の場合は、self.scene に置換されます。 Defaults to None.
            player_on_focus (Player, optional): イベントを処理させる対象を特定のプレイヤーのみに限定したいときに与えてください。例: プレイヤー1の名前を入力するシーンなど。 Defaults to None.
        """
        
        for event in self.current_events:
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    self.__init__()
                    self.next_turn_button.disable()
                    self.end_choice_button.disable()
                    if scene_name == "start":
                        self.running = False
                        pygame.quit()
                    elif scene_name == "katimake":
                        self.__init__()
                        self.scene = "start"
                    else:
                        self.scene = "start"
                        
                elif event.key == K_RETURN:
                    if scene_name == "start":
                        self.scene = "input_name_1"
                        
                elif event.key == K_q:
                    if scene_name == "sentaku":
                        self.player_1.waza = 0
                elif event.key == K_w:
                    if scene_name == "sentaku":
                        self.player_1.waza = 1
                elif event.key == K_e:
                    if scene_name == "sentaku":
                        self.player_1.waza = 2
                elif event.key == K_i:
                    if scene_name == "sentaku":
                        self.player_2.waza = 0
                elif event.key == K_o:
                    if scene_name == "sentaku":
                        self.player_2.waza = 1
                elif event.key == K_p:
                    if scene_name == "sentaku":
                        self.player_2.waza = 2
                
            elif event.type == pygame.USEREVENT:
                if scene_name.__contains__("input_name"):
                    print(event.Text)
                    if 0 < len(event.Text):
                        player_on_focus.name = event.Text
                        print(player_on_focus)
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
                            self.scene = "input_name_2"
                        elif self.player_1.name == "":
                            self.scene = "input_name_1"
                        
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.end_choice_button:
                    if self.player_1.waza != None and self.player_2.waza != None:
                        self.scene = "kekka"
                        self.n = 0
                        self._player_1_attack_was_displayed = False
                        self.elapsed_time = 0.0
                        self.end_choice_button.disable()
                        self.next_turn_button.enable()
                        self.responses = ["", ""]
                        print(self.scene)
                
                if event.ui_element == self.next_turn_button:
                    self.scene = "sentaku"
                    self.elapsed_time = 0.0
                    self.player_2.waza = None
                    self.player_1.waza = None
                    
                    self.end_choice_button.enable()
                    self.next_turn_button.disable()
                    print(self.scene)
            
            self.manager.process_events(event)
    
    def _render_waza(self, player_id: int, pos: list):
        waza_list = waza_loader(player_id)
        for i,waza in enumerate(waza_list):
            render_text_middle(f'{waza["wazamei"]} [{waza["key"]}]', [pos[0], pos[1]+30*i], 16, self.screen)
            render_text_middle(f'ダメージ: {waza["damage"]}', [pos[0]+100, pos[1]+30*i], 15, self.screen)
            render_text_middle(f'確率: {waza["kakuritu"]}', [pos[0]+200, pos[1]+30*i], 15, self.screen)
    
    def _control_sound(self):
        if self.scene != "start" and self.channel1.get_busy() == False:
            self.channel1.play(self.bgm_fight, loops=1)

if __name__ == "__main__":
    # scene_switcher()
    waza_list = waza_loader(0)
    print(waza_list)