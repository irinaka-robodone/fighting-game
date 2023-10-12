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
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(self.TITLE)
        
        self.current_events = []
        self.prev_events = []
        
        self.player_1 = Player(100, 1)
        self.player_2 = Player(100, 2)
        
        self.bg_color = (230,230,230)
        self.font_color = (20,20,20)
        
        self.img1 = pygame.image.load(f"{base_dir}/asset/img/sleepy_boy.png")
        self.img2 = pygame.image.load(f"{base_dir}/asset/img/salary_person_male.png")
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
                    damage = waza["damage"].split("-")
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
                waza = waza_loader(player.id)[player.waza]
                threshold = waza["kakuritu"]/100.0
                player.waza_desc = waza["desc"]
                if random.random() < threshold:
                    if "-" in waza["damage"]:
                        damage = waza["damage"].split("-")
                        damage = int(random.randrange(int(damage[0]), int(damage[1]), 1))
                        player.damage_give = damage
                    else:
                        player.damage_give = int(waza["damage"])
                    player.waza_seikou = "成功"
                else:
                    player.damage_give = 0
                    player.waza_seikou = "失敗"
                    
        self.player_1.damage_get = self.player_2.damage_give
        self.player_2.damage_get = self.player_1.damage_give
    
    def _render_status(self, scene_name: str, ai_mode: bool = False):
        render_text_middle(f"{self.player_1.name}", [200,30], 20, self.screen)
        render_text_middle(f"HP: {self.player_1.hp}", [200,60], 20, self.screen)
        render_text_middle(f"{self.player_2.name}", [740,30], 20, self.screen)
        render_text_middle(f"HP: {self.player_2.hp}", [740,60], 20, self.screen)
        
    def do_something(self):
        pass
    