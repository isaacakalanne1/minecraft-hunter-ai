import torch
import random
import numpy as np
from collections import deque
from Hunter import Hunter

MAX_MEMORY = 10_000
BATCH_SIZE = 100
LR = 0.001

class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0 # Controls randomness
        self.gamma = 0 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        # model, trainer

    def get_state(self, hunter):
        pass

    def remember(self, state, action, reward, next_state, done):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self):
        pass

    def get_action(self, state):
        pass

def train():
    pass

if __name__ == '__main__':
    train()