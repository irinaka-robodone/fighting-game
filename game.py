from world import World
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--ai", required=True)

args = argparser.parse_args()
ai_mode = str(args.ai)
if ai_mode == "1":
    ai_mode = True
else:
    ai_mode = False

world = World(ai_mode)
while world.running:
    world.process()