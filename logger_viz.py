import json
import os
import matplotlib.pyplot as plt

total_reward = []
steps = []
explored = []
average_q_val = []

# Load JSON from file
for filename in os.listdir("./logs"):
    if filename.endswith('.json'):
        file_path = os.path.join("./logs", filename)
        
        # Open and load the JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Extract episode data
        episodes = data["episode_data"]

        # Iterate over each episode and print summary
        for episode_id, stats in episodes.items():
            # print(f"Episode {episode_id}:")
            # print(f"  Total Reward: {stats['total_reward']}")
            # print(f"  Steps: {stats['steps']}")
            # print(f"  Capture Success: {stats['capture_success']}")
            # print(f"  Explored Percentage: {stats['explored_percentage']:.2%}")
            # print(f"  Avg Q-Value: {stats['avg_q_value']:.4f}")
            # print()
            total_reward.append(stats['total_reward'])
            steps.append(stats['steps'])
            explored.append(stats['explored_percentage'])
            average_q_val.append(stats['explored_percentage'])
