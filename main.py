import pygame
import math
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smooth Drone Movement")

RUNNER_ANGLE_LIMIT = 30

# Drone settings
class Runner:
    def __init__(self):
        self.pos = pygame.Vector2(600, 300)
        self.speed = 2.5
        self.direction = pygame.Vector2(1, 0).rotate(random.randint(0, 360))
        self.max_turn_angle = 15  # Max degrees per frame
        self.speed = 3.0
        self.max_speed = 4.5
        self.min_speed = 1.5
        self.last_direction = self.direction
        self.border_margin = 50
        self.turn_smoothing = 0.2
    
    def update_random(self):
        # Small random directional adjustments
        prev_direction = self.direction.copy()
        
        # Random directional adjustment (smaller changes more likely)
        turn_magnitude = random.uniform(0, 1) ** 2  # Squared for bias toward small turns
        turn_angle = random.uniform(-30, 30) * turn_magnitude
        self.direction.rotate_ip(turn_angle)
        
        # Calculate direction change amount
        angle_change = math.degrees(self.last_direction.angle_to(self.direction))
        normalized_change = min(abs(angle_change) / 30.0, 1.0)  # 0-1 range
        
        # Adaptive speed control
        target_speed = self.max_speed * (1 - normalized_change)  # Slower when turning sharply
        self.speed += (target_speed - self.speed) * self.turn_smoothing
        self.speed = max(self.min_speed, min(self.max_speed, self.speed))
        
        # Update last direction
        self.last_direction = self.direction.copy()
        
        # Border handling with smooth redirection
        if self.pos.x < self.border_margin or self.pos.x > WIDTH - self.border_margin:
            new_dir = pygame.Vector2(-1 if self.pos.x > WIDTH/2 else 1, 0)
            new_dir.rotate_ip(random.uniform(-30, 30))
            self.direction = new_dir
            self.speed = self.min_speed  # Slow down during border turns
            
        if self.pos.y < self.border_margin or self.pos.y > HEIGHT - self.border_margin:
            new_dir = pygame.Vector2(0, -1 if self.pos.y > HEIGHT/2 else 1)
            new_dir.rotate_ip(random.uniform(-30, 30))
            self.direction = new_dir
            self.speed = self.min_speed
        
        # Normalize and move
        self.direction = self.direction.normalize()
        self.pos += self.direction * self.speed


# Create runner
runner = Runner()

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update
    runner.update_random()
    
    # Draw
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (int(runner.pos.x), int(runner.pos.y)), 15)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()