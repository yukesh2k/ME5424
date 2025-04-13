import pygame
import math
from runner import Runner
from chaser import Chaser, create_triangular_formation, draw_chaser_lines
from utils.colors import WHITE, GRAY, GREEN

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1920, 1080
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
    
    # Calculate formation forward vector (we'll use runner's direction)
    formation_angle = math.degrees(math.atan2(runner.direction.y, runner.direction.x))
    
    # for chaser in chasers:
    #     chaser.update(runner.pos, formation_angle)
    
    # Draw
    screen.fill(WHITE)
    
    # Draw grid
    for x in range(0, WIDTH, 100):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 100):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)    
    
    # Draw drones
    for chaser in chasers:
        chaser.draw(screen)
    runner.draw(screen)
    
    draw_chaser_lines(screen, chasers)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()