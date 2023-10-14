import argparse

from world import World
from utils import WazaLoader

argparser = argparse.ArgumentParser()
argparser.add_argument("--ai", required=False, default=0)
argparser.add_argument("--cpu", required=False, default=1)

args = argparser.parse_args()
ai_mode = str(args.ai)
cpu_mode = str(args.cpu)
if ai_mode == "1":
    ai_mode = True
else:
    ai_mode = False
if cpu_mode == "1":
    cpu_mode = True
else:
    cpu_mode = False

waza_loader = WazaLoader("asset/test/waza_test_boss_fire.csv")
world = World(ai_mode, cpu_mode)
world.waza_loader = waza_loader

while world.running:
    world.process()