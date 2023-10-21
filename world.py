import os
import random

import pygame
from pygame.locals import *
import pandas as pd
import pygame_gui
from pygame_textinput.textinput import TextInput

from utils import render_text_center, render_text_middle, WazaLoader
from ai import ai_response
from component import Player

base_dir = os.environ.get("BASE_DIR")

class World():
    def __init__(self, ai_mode: bool = False, vs_computer: bool = True) -> None:
        self.SCREEN_SIZE = [960, 640]
        self.TITLE = "言うほどしょぼくない格ゲー"
        self.scene = "start"
        self.scene_prev = "launch"
        self.running = True
        self.FPS = 60
        self.vs_computer = vs_computer
        self.clock = pygame.time.Clock()
        pygame.init()
        self.ai_mode = ai_mode
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(self.TITLE)
        
        self.current_events = []
        self.prev_events = []
        
        self.player_1 = Player(100, 1)
        self.player_2 = Player(100, 2)
        
        self.bg_color = (230,230,230)
        self.font_color = (20,20,20)
        
        self.fade_color = 20
        self.fade_inversion = 230
        
        self.img1 = pygame.image.load(f"{base_dir}/asset/img/images.jpg")
        self.img2 = pygame.image.load(f"{base_dir}/asset/img/download.jpg")
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
        
        self.bgm_fight = pygame.mixer.Sound(f"{base_dir}/asset/sound/bgm.mp3")
        self.sound_title_call = pygame.mixer.Sound(f"{base_dir}/asset/sound/bgm.mp3")
        self.es_attack_normal = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_se_battle14.mp3")
        self.es_attack_heavy = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_se_battle06.mp3")
        self.es_attack_missed = pygame.mixer.Sound(f"{base_dir}/asset/sound/maou_se_8bit26.mp3")
        
        self.channel2.play(self.sound_title_call, loops=0)
        
        self.input_box_player_name = TextInput(pygame.font.SysFont("yumincho", 30), self.font_color)
        
        self.elapsed_time = 0.0
        self.waza_loader: WazaLoader
        self.responses = ["", ""]
        
        self.players = [self.player_1, self.player_2]
    
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
        elif self.scene == "321go":
            self.go321()
        self._update_screen()
        self._control_sound()
        self.scene_timer()
        self.scene_prev = self.scene
        
    def _update_screen(self):
        pygame.display.flip()
        pygame.display.update()
        self.screen.fill(self.bg_color)
        self.manager.update(self.time_delta)
        self.screen.blit(self.background, (0,0))
        self.manager.draw_ui(self.screen)
    
    def show_start_screen(self):
        self.channel1.stop()

        bg_color, text_color = self.fadein_out()
        
        self.screen.fill(bg_color)
        render_text_middle(self.TITLE, (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2-20), 32, self.screen, text_color)
        render_text_middle("スペースキーを押してスタート", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2+20), 16, self.screen, text_color)
        
        self._get_event()
        self._handle_event(self.scene)
    
    def fadein_out(self):
        # self.screen.fill((self.fade_color, self.fade_color, self.fade_color))
        if self.fade_color <= 20:
            self.fade_value = 1
        elif self.fade_color >= 230:
            self.fade_value = -1
        
        self.fade_color += self.fade_value
        self.fade_inversion += self.fade_value *-1
        
        bg_color = (self.fade_color, self.fade_color, self.fade_color)
        text_color = (self.fade_inversion,self.fade_inversion,self.fade_inversion)
        return bg_color, text_color
        
    def input_name(self, player: Player):
        
        render_text_middle(f"プレイヤー{player.id}の名前を入力", [480, 100], 24, self.screen, bold = False)
        self._get_event()
        self._handle_event(self.scene, player)
            
        self.input_box_player_name.update(self.current_events)
        self.screen.blit(self.input_box_player_name.get_surface(), [480, 130])
    
    def go321(self):
        
        if self.elapsed_time < 1:
            render_text_middle("3", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2-20), 300, self.screen, self.font_color)
        elif self.elapsed_time < 2:
            render_text_middle("2", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2-20), 300, self.screen, self.font_color)
        elif self.elapsed_time < 3:
            render_text_middle("1", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2-20), 300, self.screen, self.font_color)
        else:
            render_text_middle("戦え!", (self.SCREEN_SIZE[0]//2, self.SCREEN_SIZE[1]//2-20), 300, self.screen, self.font_color)
        
        self._get_event()
        self._handle_event(self.scene)
    
    def sentaku(self):
        
        self._render_status(self.scene)
        self.screen.blit(self.img1, [60, 320])
        self.screen.blit(self.img2, [600, 320])
        
        self._get_event()
        
        if self.elapsed_time < 3 and self.vs_computer == True:
            render_text_middle("AI思考中", [860, 56], 24, self.screen, self.font_color)
        elif self.elapsed_time >= 3 and self.vs_computer == True:
            render_text_middle("✔", [860, 56], 24, self.screen, self.font_color)
            
        if self.player_1.waza != None:
            render_text_middle("✔", [300, 56], 24, self.screen, self.font_color)
            
        if self.player_2.waza != None:
            render_text_middle("✔", [860, 56], 24, self.screen, self.font_color)
        
        if self.player_1.waza != None and self.vs_computer == True and self.elapsed_time >= 3 and self.player_2.waza == None:
            self.player_2.waza = random.choice([0,1,2,3])
            print(self.player_2.waza)
            
        self._handle_event(self.scene)

    
    def kekka(self, ai_mode: bool = False):
        
        self._render_status("kekka:before")
        
        """
        todo
        1. openai api アクセスを非同期処理にする。(待機時間が長いし正常なResponseが返ってくる確証がないため)
            a. timeout を設定できるようにして、それ以上返ってこなかったら、llmの出力を使わないようにする。
            b. llmの返答待ちの間も、アプリを閉じたり、スタート画面に行ったり、他のセリフを表示したりなど、ユーザーのインプットを受け付けられるようにする。
            
        """
        if self.n < 1:
            self._judge_waza_success([self.player_1, self.player_2])
            
            for player in self.players:
                player.hp -= player.damage_get
                player.hp += player.heal
            
            if ai_mode == True:
                render_text_center("AI思考中", 32, self.screen, self.font_color)
                self._update_screen()
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
                self.responses = ai_response.get_script(df, max_retries=2, temperature=0.8)
                self.elapsed_time = 0.0
            else:
                pass
            
            if self.player_2.waza_seikou == "成功" and self.player_2.waza != 2:
                self.channel2.play(self.es_attack_normal)
            elif self.player_2.waza_seikou == "成功" and self.player_2.waza == 2:
                self.channel2.play(self.es_attack_heavy)
            else:
                self.channel2.play(self.es_attack_missed)
        
        self._render_status("kekka", ai_mode)
        
        if self.elapsed_time >= 2 and self._player_1_attack_was_displayed == False:
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
        self._render_status(self.scene, self.ai_mode)
        
        self._get_event()
        self._handle_event(self.scene)
        
    def _get_event(self):
        if len(self.current_events) > 0:
            self.prev_events = self.current_events
        self.current_events = pygame.event.get()
        
    def _judge_waza_success(self, players: list[Player] | Player):
        if type(players) == Player:
            waza = self.waza_loader.load_waza(players.id, player.waza)
            threshold = waza["kakuritu"]/100.0
            players.waza_desc = waza["desc"]
            if random.random() < threshold:
                
                if "-" in str(waza["damage"]):
                    damage = str(waza["damage"]).split("-")
                    damage = int(random.randrange(int(damage[0]), int(damage[1]), 1))
                    players.damage_give = damage
                else:
                    players.damage_give = int(waza["damage"])
                players.waza_seikou = "成功"
            else:
                players.damage_give = 0                              
                players.waza_seikou = "失敗"
        else:
            for player in players:
                waza = self.waza_loader.load_waza(player.id, player.waza)
                threshold = waza["kakuritu"]/100.0
                player.waza_desc = waza["desc"]
                player.yuuri =  waza["yuuri"]
                player.waza_id = waza["id"]
                player.waza_kind = waza["kind"]
                player.guard = waza["guard"]
                if random.random() < threshold:
                    player.heal = waza["heal"]
                    if "-" in str(waza["damage"]):
                        damage = str(waza["damage"]).split("-")
                        damage = int(random.randrange(int(damage[0]), int(damage[1]), 1))
                        player.damage_give = damage
                    else:
                        
                        player.damage_give = int(waza["damage"])
                    player.waza_seikou = "成功"
                else:
                    player.heal = 0
                    player.damage_give = 0
                    player.waza_seikou = "失敗"
                    
            for i, player in enumerate(players):
                teki = players[i-1]
                if player.yuuri == teki.waza_id:
                    teki.damage_give *= 0.5
                    
        self.player_1.damage_get = self.player_2.damage_give
        self.player_2.damage_get = self.player_1.damage_give
    
        for player in self.players:
            if player.waza_kind == "guard":
                player.damage_get *= player.guard
    def _render_status(self, scene_name: str, ai_mode: bool = False):
        render_text_middle(f"{self.player_1.name}", [200,30], 20, self.screen)
        render_text_middle(f"HP: {self.player_1.hp}", [200,60], 20, self.screen)
        render_text_middle(f"{self.player_2.name}", [740,30], 20, self.screen)
        render_text_middle(f"HP: {self.player_2.hp}", [740,60], 20, self.screen)
        
        if scene_name == "sentaku":
            render_text_middle("VS", [480, 30], 24, self.screen)
            self._render_waza(self.player_1.id, pos=[100, 100])
            self._render_waza(self.player_2.id, pos=[640, 100])
            
        elif scene_name == "kekka:before":
            render_text_middle("VS", [480, 30], 24, self.screen)
            self._render_waza(self.player_1.id, pos=[100, 100])
            self._render_waza(self.player_2.id, pos=[640, 100])
            
        elif scene_name == "kekka":
            render_text_middle("VS", [480, 30], 24, self.screen)
            if self.elapsed_time >= 1:
                render_text_middle(f"{self.player_1.name}は「{self.waza_loader.load_waza(self.player_1.id, self.player_1.waza)['wazamei']}」を繰り出した！ {self.player_1.waza_seikou}", [480, 200], 20, self.screen, self.font_color)
                render_text_middle(f"- {self.player_2.damage_get}", [840, 56], 26, self.screen, [255,0,0], bold=True)
                render_text_middle(f"+ {self.player_2.heal}", [840, 24], 26, self.screen, [0,0,255], bold=True)

                if ai_mode == True:
                    render_text_middle(f"{self.responses[0]}", [480, 230], 16, self.screen, bold=False)
            if self.elapsed_time >= 2:
                render_text_middle(f"{self.player_2.name}は「{self.waza_loader.load_waza(self.player_2.id, self.player_2.waza)['wazamei']}」を繰り出した！ {self.player_2.waza_seikou}", [480, 270], 20, self.screen, self.font_color)
                render_text_middle(f"- {self.player_1.damage_get}", [300, 56], 26, self.screen, [255,0,0], bold=True)
                render_text_middle(f"+ {self.player_1.heal}", [300, 24], 26, self.screen, [0,0,255], bold=True)
                if ai_mode == True:
                    render_text_middle(f"{self.responses[1]}", [480, 300], 16, self.screen, bold=False)
            
        elif scene_name == "katimake":
            self._render_waza(self.player_1.id, pos=[100, 100])
            self._render_waza(self.player_2.id, pos=[640, 100])
            render_text_middle(f"{self.player_1.name}は「{self.waza_loader.load_waza(self.player_1.id, self.player_1.waza)['wazamei']}」を繰り出した！ {self.player_1.waza_seikou}", [480, 200], 20, self.screen, self.font_color)
            render_text_middle(f"- {self.player_2.damage_get}", [840, 56], 26, self.screen, [255,0,0], bold=True)
            render_text_middle(f"{self.player_2.name}は「{self.waza_loader.load_waza(self.player_2.id, self.player_2.waza)['wazamei']}」を繰り出した！ {self.player_2.waza_seikou}", [480, 270], 20, self.screen, self.font_color)
            render_text_middle(f"- {self.player_1.damage_get}", [300, 56], 26, self.screen, [255,0,0], bold=True)
            
            if self.player_1.hp <= 0 and self.player_2.hp <= 0:
                text_result = "引き分け"
                self.screen.blit(self.img_loser_mark, [60, 320])
                self.screen.blit(self.img_loser_mark, [600, 320])
                
            elif self.player_1.hp <= 0:
                text_result = f'{self.player_2.name}の勝ち'
                self.screen.blit(self.img_loser_mark, [60, 320])
                
            elif self.player_2.hp <= 0:
                text_result = f'{self.player_1.name}の勝ち'
                self.screen.blit(self.img_loser_mark, [600, 320])
                
            if self.elapsed_time > 1:
                render_text_middle(text_result, [480, 20], 30, self.screen)
                render_text_middle("Escキーでスタート画面に戻る", [480, 50], 20, self.screen, bold=True)
            
            if ai_mode == True:
                render_text_middle(f"{self.responses[0]}", [480, 230], 16, self.screen, bold=False)
                render_text_middle(f"{self.responses[1]}", [480, 300], 16, self.screen, bold=False)
            else:
                pass
    
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
                        # self.scene = "input_name_1"
                        pass
                elif event.key == K_SPACE:
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
                elif event.key == K_r:
                    if scene_name == "sentaku":
                        self.player_1.waza = 3
                elif event.key == K_t:
                    if scene_name == "sentaku":
                        self.player_1waza =4
                elif event.key == K_i and self.vs_computer == False:
                    if scene_name == "sentaku":
                        self.player_2.waza = 0
                elif event.key == K_o and self.vs_computer == False:
                    if scene_name == "sentaku":
                        self.player_2.waza = 1
                elif event.key == K_p and self.vs_computer == False:
                    if scene_name == "sentaku":
                        self.player_2.waza = 2
                elif event.key == K_u and self.vs_computer == False:
                    if scene_name == "sentaku":
                        self.player_2.waza = 3
                
            elif event.type == pygame.USEREVENT:
                if scene_name.__contains__("input_name"):
                    print(event.Text)
                    if 0 < len(event.Text):
                        player_on_focus.name = event.Text
                        print(player_on_focus)
                        if self.player_1.name != "" and self.player_2.name != "":
                            self.scene = "321go"
                            self.channel1.play(self.bgm_fight, loops = 1)
                            
                        elif self.player_2.name == "":
                            self.scene = "input_name_2"
                        elif self.player_1.name == "":
                            self.scene = "input_name_1"
                        
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                print(event)
                if event.ui_element == self.end_choice_button:
                    if self.player_1.waza != None and self.player_2.waza != None:
                        print("sentaku -> kekka")
                        self.scene = "kekka"
                        self.n = 0
                        self._player_1_attack_was_displayed = False
                        self.end_choice_button.disable()
                        self.next_turn_button.enable()
                        # self.responses = ["", ""]
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
        
        if self.scene == "321go" and self.elapsed_time >= 4.0:
            print("321go -> sentaku")
            self.end_choice_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((420, 80), (120, 40)),
                        text='End Choice',
                        manager=self.manager)
            self.next_turn_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((420, 120), (120, 40)),
                                text='Next Turn',
                                manager=self.manager)
            self.next_turn_button.disable()
            self.end_choice_button.enable()
            self.scene = "sentaku"
            
    
    def _render_waza(self, player_id: int, pos: list):
        waza_list = self.waza_loader.load_player_waza_list(player_id)
        for i,waza in enumerate(waza_list):
            render_text_middle(f'{waza["wazamei"]} [{waza["key"]}]', [pos[0], pos[1]+30*i], 16, self.screen)
            render_text_middle(f'ダメージ: {waza["damage"]}', [pos[0]+100, pos[1]+30*i], 15, self.screen)
            render_text_middle(f'確率: {waza["kakuritu"]}', [pos[0]+200, pos[1]+30*i], 15, self.screen)
    
    def _control_sound(self):
        if self.scene != "start" and self.channel1.get_busy() == False:
            self.channel1.play(self.bgm_fight, loops=1)
            
    def scene_timer(self):
        if self.scene != self.scene_prev:
            self.elapsed_time = 0
        self.elapsed_time += self.time_delta
        print(self.elapsed_time)

if __name__ == "__main__":
    world = World(ai_mode=True, vs_computer=True)
    waza_loader = WazaLoader("asset/test/waza_character.csv")
    world.waza_loader = waza_loader
    while True:
        world.process()