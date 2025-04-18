import pygame
import numpy as np
from chaser_rl import RLAgent

class Chaser:
    def __init__(self, x, y, state_dim, action_dim):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = 12
        self.max_speed = 3.0
        self.steering_strength = 0.08
        self.rl_agent = RLAgent(state_dim, action_dim)
        self.last_state = None
        self.last_action = None
        self.current_target = None
        self.last_target = None

    def update(self, env, runners, other_chasers, captured_flags, training=True):
        # 1. Observe
        state = env.get_state(self, runners, other_chasers)
        # 2. Determine visibility and choose runner to pursue
        visible = [i for i, r in enumerate(runners) if env._can_see(self.pos, r.pos)]
        self.last_target = self.current_target
        if visible:
            # choose nearest visible runner
            dists = [self.pos.distance_to(runners[i].pos) for i in visible]
            self.current_target = visible[int(np.argmin(dists))]
        else:
            self.current_target = None
        # 3. Select action
        action = self.rl_agent.select_action(state, training)
        # 4. Decode action into movement
        angle = action * (2 * np.pi / self.rl_agent.action_dim)
        direction = pygame.Vector2(np.cos(angle), np.sin(angle)).normalize()
        # 5. Move
        self.velocity += (direction * self.max_speed - self.velocity) * self.steering_strength
        self.pos += self.velocity
        # 6. Enforce bounds
        self.pos.x = max(20, min(self.pos.x, env.width - 20))
        self.pos.y = max(20, min(self.pos.y, env.height - 20))
        # 7. Learn
        next_state = env.get_state(self, runners, other_chasers)
        reward = env.get_reward(self, runners, captured_flags)
        done = any(captured_flags)
        self.rl_agent.store_experience(state, action, reward, next_state, done)
        self.rl_agent.train()
        # 8. Save last
        self.last_state = state
        self.last_action = action

    def draw(self, surface):
        color = (0, 0, 139) if self.current_target is not None else (173, 216, 230)
        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def has_captured(self, runner):
        return self.pos.distance_to(runner.pos) < self.radius * 2

