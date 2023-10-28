import subprocess
subprocess.Popen('PAUSE', shell=True)

# import argparse

from src import world

world = world.World(True, True)
while world.running:
    world.process()