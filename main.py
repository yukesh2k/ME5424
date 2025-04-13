import pygame
import math
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smooth Drone Movement")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0, 50)

RUNNER_ANGLE_LIMIT = 30

# Drone settings
class Runner:
    def __init__(self, x = 600, y = 300):
        self.pos = pygame.Vector2(x, y)
        self.speed = 2.5
        self.color = RED
        self.radius = 15
        self.direction = pygame.Vector2(1, 0).rotate(random.randint(0, 360))
        self.max_turn_angle = 30  # Max degrees per frame
        self.speed = 3.0
        self.max_speed = 4.5
        self.min_speed = 1.5
        self.last_direction = self.direction
        self.border_margin = 50
        self.turn_std_dev = 12
        self.turn_smoothing = 0.2

    def get_turn_angle(self):
        angle = random.gauss(0, self.turn_std_dev)
        return max(-self.max_turn_angle, min(self.max_turn_angle, angle))
    
    def update_random(self):
        # Small random directional adjustments
        prev_direction = self.direction.copy()
        
        # Random directional adjustment (smaller changes more likely)
        turn_angle = self.get_turn_angle()
        self.direction.rotate_ip(turn_angle)
        
        # Calculate direction change amount
        # angle_change = math.degrees(self.last_direction.angle_to(self.direction))
        normalized_change = min(abs(turn_angle) / 30.0, 1.0)  # 0-1 range
        
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
        print(turn_angle, normalized_change, target_speed, self.speed)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


class Chaser:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.color = BLUE
        self.radius = 12
        self.speed = 0  # Will be set in formation update
        self.direction = pygame.Vector2(0, 0)  # Will be calculated
        self.formation_offset = pygame.Vector2(0, 0)  # Position relative to formation center

    def update(self, formation_center, formation_angle):
        # Maintain formation position (no chasing logic yet)
        target_pos = formation_center + self.formation_offset.rotate(formation_angle)
        self.direction = (target_pos - self.pos).normalize()
        self.pos += self.direction * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

def create_triangular_formation(center, radius):
    """Creates 3 chasers in equilateral triangle formation"""
    chasers = []
    for angle in [30, 150, 270]:  # 120° separation
        chaser = Chaser(
            center.x + radius * math.cos(math.radians(angle)),
            center.y + radius * math.sin(math.radians(angle))
        )
        chaser.formation_offset = pygame.Vector2(
            radius * math.cos(math.radians(angle)),
            radius * math.sin(math.radians(angle))
        )
        chaser.speed = 4.0
        chasers.append(chaser)
    return chasers

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
    
    # Draw formation lines
    if len(chasers) >= 3:
        pygame.draw.polygon(screen, GREEN, 
                          [(c.pos.x, c.pos.y) for c in chasers[:3]], 2)
    
    # Draw drones
    for chaser in chasers:
        chaser.draw(screen)
    runner.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()