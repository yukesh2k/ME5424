import pygame
import math
from runner import Runner
from chaser import Chaser, create_triangular_formation, draw_chaser_lines
from utils.colors import WHITE, GRAY, GREEN
from utils.params import WIDTH, HEIGHT

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smooth Drone Movement")

# Create runner
runner = Runner(WIDTH//2, HEIGHT//2)
chasers = create_triangular_formation(runner.pos, 500)

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update
    runner.update_random()
    [chaser.update_simple(runner.get_position()) for chaser in chasers]
    
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