import subprocess
subprocess.Popen('PAUSE', shell=True)

# import argparse

import world

world = world.World(True, False)
while world.running:
    world.process()