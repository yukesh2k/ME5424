import pygame
import random
from drone_env import DroneEnv
from chaser_intelligent import Chaser
from runner import Runner
from utils.params import WIDTH, HEIGHT, SENSE_RADIUS
import math

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

NUM_EPISODES = 1000
ACTION_DIM = 8  # eight discrete movement directions
STATE_DIM = 3 * 2 + 4 + 2  # 2 runners -> 6, 4 exploration, 2 nearest chaser -> 12

for episode in range(NUM_EPISODES):
    # Initialize environment and agents
    env = DroneEnv(WIDTH, HEIGHT, SENSE_RADIUS)
    chasers = []
    center = pygame.Vector2(WIDTH//2, HEIGHT//2)
    # Spawn chasers in triangular formation
    for i, angle in enumerate([30, 150, 270]):
        offset = pygame.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * 200
        chasers.append(Chaser(center.x + offset.x, center.y + offset.y, STATE_DIM, ACTION_DIM))
    # Spawn two runners far from chasers
    runners = []
    for _ in range(2):
        while True:
            rx = random.randint(50, WIDTH - 50)
            ry = random.randint(50, HEIGHT - 50)
            pos = pygame.Vector2(rx, ry)
            if all(pos.distance_to(c.pos) >= SENSE_RADIUS for c in chasers):
                runners.append(Runner(rx, ry))
                break

    for step in range(1000):
        screen.fill((255, 255, 255))
        # Update and draw runners
        for r in runners:
            r.update_random()
            r.draw(screen)
        # Check captures
        captured_flags = [any(c.has_captured(r) for c in chasers) for r in runners]
        # Update and draw chasers
        for c in chasers:
            c.update(env, runners, [o for o in chasers if o is not c], captured_flags)
            env.mark_visited(c.pos)
            c.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        if any(captured_flags):
            break
pygame.quit()