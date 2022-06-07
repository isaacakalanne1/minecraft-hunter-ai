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
        self.model = None # TODO
        self.trainer = None # TODO

    def get_state(self, hunter):
        state = {
            'inventory': list(hunter.inventoryItems.items()),
            'blocks': list(hunter.blocksInMemory.items()),
            'entities': list(hunter.entitiesInMemory.items()),
            'heldItem': hunter.currentHeldItem,
            'currentHealth': hunter.currentHealth,
            'currentHunger': hunter.currentHunger,
            'currentTimeOfDay': hunter.currentTimeOfDay,
            'currentPosition': hunter.currentPosition
        }

        stateArray = np.array(state, dtype=np.object0) # May need to use dtype=object, or one of other dtype=np.obj... values
        return stateArray

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popLeft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        pass

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Hunter('localHost', 62217, 'HelloThere')
    while True:
        # Get old state
        state_old = agent.get_state(game)

        # Get move
        final_move = agent.get_action(state_old)

        # Perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # Train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # Remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # Train long memory
            game.reset()
            agent.number_of_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                # agent.model.save()

            print('Game', agent.number_of_games, 'Score', score, 'Record', record)

            # TODO: Plot

if __name__ == '__main__':
    train()