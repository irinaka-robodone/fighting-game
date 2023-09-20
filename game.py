from world import World

world = World(ai_mode=False)
while world.running:
    world.process()