import pygame
import numpy as np
from drone_env_2 import DroneEnv
from runner import Runner
from chaser_intelligent_2 import create_triangular_formation
from chaser_rl import RLAgent
import random
from metrics_logger import MetricsLogger
import torch
from itertools import product

# Constants
WIDTH, HEIGHT = 1920, 1080
SENSE_RADIUS = 400
NUM_EPISODES = 1000
MAX_STEPS = 1000

def is_far_from_chasers(candidate, chasers, radius):
    return all(candidate.distance_to(ch.pos) >= radius for ch in chasers)

def initialize_simulation(rl_agent):
    """Initialize Pygame and create new entities"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Drone Pursuit RL")
    clock = pygame.time.Clock()
    
    env = DroneEnv(WIDTH, HEIGHT, SENSE_RADIUS)
    
    chasers = create_triangular_formation(pygame.Vector2(WIDTH//2, HEIGHT//2), 500, rl_agent)

    runners = []
    for i in range(2):
        while True:
            rand_pos = pygame.Vector2(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
            if is_far_from_chasers(rand_pos, chasers, SENSE_RADIUS):
                break

        runner = Runner(rand_pos.x, rand_pos.y)
        runners.append(runner)

    return screen, clock, env, runners, chasers

def main():
    logger = MetricsLogger()
    rl_agent = RLAgent(state_dim=9, action_dim=8)
    
    for episode in range(NUM_EPISODES):
        episode_metrics = {
            'total_reward': 0,
            'steps': 0,
            'capture_success': 0,
            'explored_cells': 0,
            'mode_switches': 0
        }
        q_values = []
        # Initialize new simulation
        screen, clock, env, runners, chasers = initialize_simulation(rl_agent)
        episode_reward = 0
        done = False
        
        for step in range(MAX_STEPS):
            step_metrics = {
                'q_values': [],
                'actions': [],
                'exploration_map': env.exploration_map.copy()
            }
            # Handle Pygame events (quit signal)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Update entities
            [runner.update_random() for runner in runners]
            
            for chaser in chasers:
                chaser.update(env, runners, [c for c in chasers if c != chaser])
                if chaser.mode_switch:
                    episode_metrics['mode_switches'] += 1
                env.mark_visited(chaser.pos)
            
            any_pursuit = any(chaser.mode == "pursuit" for chaser in chasers)
            if any_pursuit:
                for chaser in chasers:
                    if chaser.mode != "pursuit":
                        chaser.mode = "pursuit"
                        chaser.switch_cooldown = 15

            # Check for capture
            captured = False
            capturing_chaser = None

            for _idx, (chaser, runner) in enumerate(product(chasers, runners)):
                if chaser.pos.distance_to(runner.pos) < chaser.radius + runner.radius:
                    captured = True
                    capturing_chaser = chaser
                    episode_metrics['capture_success'] += 1
                    break
            
            # Store experiences and calculate rewards
            
            for chaser in chasers:
                if chaser.last_state is not None and chaser.last_action is not None:
                    next_state = env.get_state(chaser, runners, 
                                             [c for c in chasers if c != chaser])
                    reward = env.get_reward(chaser, runner, 
                                          [c for c in chasers if c != chaser])
                    
                    if captured and chaser == capturing_chaser:
                        reward += 100.0  # Significant capture bonus
                    
                    # Small shared reward for other chasers
                    elif captured and chaser.mode == "pursuit":
                        reward += 20.0  # Cooperative bonus
                    
                    rl_agent.store_experience(
                        chaser.last_state,
                        chaser.last_action,
                        reward,
                        next_state,
                        captured
                    )
                    episode_reward += reward
            
                    with torch.no_grad():
                            q_values.append(torch.max(rl_agent.q_net(torch.FloatTensor(next_state))).item())
                
                    episode_metrics['total_reward'] += reward

            # Train RL agent
            rl_agent.train()
            episode_metrics['steps'] = step + 1
            
            # Render
            screen.fill((255, 255, 255))
            [pygame.draw.circle(screen, (255, 0, 0), (int(runner.pos.x), int(runner.pos.y)), runner.radius) for runner in runners]
            
            for chaser in chasers:
                if chaser.mode == "pursuit":
                    color = (255, 165, 0)  # Light red
                    pygame.draw.line(screen, (255, 0, 0, 100), 
                                   (int(chaser.pos.x), int(chaser.pos.y)),
                                   (int(runner.pos.x), int(runner.pos.y)), 2)
                else:
                    color = (100, 100, 255)  # Light blue
                
                pygame.draw.circle(screen, color, (int(chaser.pos.x), int(chaser.pos.y)), chaser.radius)
            
            pygame.display.flip()
            clock.tick(60)
            
            # End episode if captured
            if captured:
                break
        
        episode_metrics['explored_percentage'] = len(env.exploration_map) / ((WIDTH//env.cell_size) * (HEIGHT//env.cell_size))
        episode_metrics['avg_q_value'] = np.mean(q_values) if q_values else 0

        logger.log_episode(episode, **episode_metrics)

        # Clean up and prepare for next episode
        print(f"Episode {episode + 1}, Reward: {episode_reward:.2f}, Epsilon: {rl_agent.epsilon:.2f}")
        if episode % 50 == 0 or episode == NUM_EPISODES - 1:
            logger.save(f"logs/metrics_ep{episode}.json")
            rl_agent.save(f"model/rl_agent_ep{episode}.pth")
        pygame.quit()  # Close current window
        
    # Save final model
    rl_agent.save("model/chaser_rl_final.pth")

if __name__ == "__main__":
    main()