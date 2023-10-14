import pygame

"""

スタート画面で「スペースキーでスタート」と表示し、
透明度をなめらかに上げ下げを繰り返す。
スペースキーを押した後に3,2,1,GOがでて、それが出終わったらスタート

1PはDキーでパンチ(ダメージ40)
　　Aキーでガード(ダメージ60%軽減)
　　Sキーでキック(ダメージ50)
　　Zキーでしゃがむ(パンチ攻撃を避けられる)
　　Eキーで強力パンチ(20%の確率で出せ、ダメージは80)
　　TABキーで何をするか決定する
　　
2Pは＋キーでパンチ(ダメージ40)
　　」キーでガード(ダメージ60%軽減)
　　「キーでキック(ダメージ50)
　　＿キーでしゃがむ(パンチ攻撃を避けられる)
　　Pキーで強力パンチ(20%の確率で出せ、ダメージは80)
　　Enter↩キーで何をするか決定する

これらを2つまで組み合わせてそれぞれ攻撃ができる。
2つ目の動作は1Pは1キー、2Pは｜(BackSpceの隣)を押してからか、何も押さずにいてから決定すれば何もしないという動作をすることができる。
両者のHPは750に最初にセットする。
HPを表示する。
HPがダメージによって減った時に表示されている文字を3回揺らす。
1Pと2Pは1つ目の攻撃と2つ目の攻撃を順番に決められる。
自分と相手が選び終わったら(選び終わったかどうかを表示する)
同時にそのターンに決めた行動をする。(この時に決めた技名を表示する)
戦っている時にBGMを流す。
HPが先に0以下になったプレイヤーが負けになり、どっちが勝ちか文字で表示する。(1Pなら「1Pの勝利！」と表示する)
スタート画面に戻る


"""

def render_text(text, pos, screen, size=24, bold=True):
    font = pygame.font.SysFont("MS UI Gothic", size, bold)
    title = font.render(text, True, (255,255,255))
    screen.blit(title, pos)

class World():
    def __init__(self) -> None:
        self.SCREEN_SIZE = [960,480]
        self.TITLE = "2P格闘ゲーム"
        self.scene = "start"
        self.running = True
        pygame.init()
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE,)
        pygame.display.set_caption(self.TITLE)
        
        
    def process(self):
        if self.scene == "sentaku":
            self.sentaku()
        if self.scene == "kekka":
            self.kekka()
        if self.scene == "start":
            self.start()
        if self.scene == "katimake":
            self.katimake()
            
    def katimake(self):
        pass
            
            
    def start(self):
        
        render_text("2P格闘ゲーム", [400,100], self.screen)
        render_text("スペースを押してゲームスタート", [250,200], self.screen)
        
        
        pygame.display.flip()
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.scence = "sentaku"
            
            
    def sentaku(self):
        pass
        
    def kekka(self):
        pass
        
    def show_start_screen(self):
        pygame.display.set_caption("2P格闘ゲーム")
        
    def do_something(self):
        pass
    
    