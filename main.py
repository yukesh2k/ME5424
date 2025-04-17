import pygame
import math
from runner import Runner
from chaser import Chaser, create_triangular_formation, draw_chaser_lines
from utils.colors import WHITE, GRAY, GREEN
from utils.params import WIDTH, HEIGHT, SENSE_RADIUS
import random

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smooth Drone Movement")

def is_far_from_chasers(candidate, chasers, radius):
    return all(candidate.distance_to(ch.pos) >= radius for ch in chasers)

chasers = create_triangular_formation(pygame.Vector2(WIDTH//2, HEIGHT//2), 500)

while True:
    rand_pos = pygame.Vector2(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
    if is_far_from_chasers(rand_pos, chasers, SENSE_RADIUS):
        break

# Create runner
runner = Runner(rand_pos.x, rand_pos.y)

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update
    runner.update_random()
    # runner.update_with_avoidance(chasers)
    runner_pos = runner.get_position()
    for chaser in chasers:
        dist = chaser.pos.distance_to(runner_pos)
        # chaser.update_simple(runner_pos, dist <= SENSE_RADIUS, chasers)
        chaser.update_hybrid_1(runner_pos, dist <= SENSE_RADIUS, chasers)
    
    # Draw
    screen.fill(WHITE)
    
    # Draw grid
    for x in range(0, WIDTH, 100):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 100):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)    
    
    captured = False
    # Draw drones
    for chaser in chasers:
        chaser.draw(screen)
        if (chaser.has_captured(runner.get_position())):
            print("RUNNER CAPTURED")
            captured = True
            break

    if (captured):
        break     

    runner.draw(screen)
    
    draw_chaser_lines(screen, chasers)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()