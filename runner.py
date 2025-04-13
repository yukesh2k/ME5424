import pygame
import random
from utils.colors import RED

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
