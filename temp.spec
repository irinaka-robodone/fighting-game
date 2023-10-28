a.datas += [('enemy0.png', './asset/img/enemy0.png', 'DATA'),
            ('enemy1.png', './asset/img/enemy1.png', 'DATA'),
            ('bread_boy.png', './asset/img/bread_boy.png', 'DATA'),
            ('dead.png', './asset/img/dead.png', 'DATA'),
            ('stage0.csv', './asset/stage0.csv', 'DATA'),
            ('stage1.csv', './asset/stage1.csv', 'DATA'),
            ('bgm.mp3', './asset/sound/bgm.mp3', 'DATA'),
            ('se_8bit26.mp3', './asset/sound/se_8bit26.mp3', 'DATA'),
            ('se_battle06.mp3', './asset/sound/se_battle06.mp3', 'DATA'),
            ('se_battle14.mp3', './asset/sound/se_battle14.mp3', 'DATA'),
            ]

pyz = PYZ(a.pure, a.zipped_data)