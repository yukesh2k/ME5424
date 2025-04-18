import json
import time
import numpy as np
from collections import defaultdict

class MetricsLogger:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = time.time()
        self.episode_data = {}
        
    def log_episode(self, episode, **kwargs):
        """Record all episode-level metrics"""
        self.episode_data[episode] = kwargs
        for k, v in kwargs.items():
            self.metrics[k].append(v)
        
    def log_step(self, step_data):
        """Record step-level details"""
        if 'step_data' not in self.metrics:
            self.metrics['step_data'] = []
        self.metrics['step_data'].append(step_data)
    
    def get_stats(self, metric_name, window=100):
        """Get moving averages"""
        vals = self.metrics.get(metric_name, [])
        if len(vals) >= window:
            return np.mean(vals[-window:])
        return np.mean(vals) if vals else 0
    
    def save(self, path):
        """Save all metrics to JSON"""
        with open(path, 'w') as f:
            json.dump({
                'episode_data': self.episode_data,
                'aggregated_metrics': dict(self.metrics),
                'training_duration': time.time() - self.start_time
            }, f, indent=2)