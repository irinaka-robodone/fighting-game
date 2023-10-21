from dataclasses import dataclass

@dataclass
class Player:
    hp: float
    id: int
    name: str = ""
    waza: int = None
    waza_desc: str = None
    damage_get: int = None
    damage_give: int = None
    waza_seikou: str = ""
    yuuri: str = None
    waza_id = None
    
@dataclass
class Enemy(Player):
    level: int = None