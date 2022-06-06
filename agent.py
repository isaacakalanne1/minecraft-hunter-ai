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
        state = [
            hunter.inventoryItemsArray,
            hunter.blocksInMemoryArray,
            hunter.entitiesInMemoryArray,
            hunter.currentHeldItem,
            hunter.currentHealth,
            hunter.currentHunger,
            hunter.currentTimeOfDay,
            hunter.currentPosition
        ]
        inventoryNames = ['itemId','slot', 'count']
        inventoryFormats = ['i4','i4', 'i4']
        inventoryDType = dict(names = inventoryNames, formats=inventoryFormats)

        blockPositionNames = ['blockX','blockX', 'blockX']
        blockPositionFormats = ['i4','i4', 'i4']

        blockNames = [blockPositionNames,'blockType']
        blockFormats = [blockPositionFormats,'i4']
        blockDType = dict(names = blockNames, names = blockFormats)

        dtype = dict(inventory = inventoryDType, blocks = blockDType)
        np.array(list(state.items()), dtype=dtype)
        return np.array(state, dtype=np.single)

    def remember(self, state, action, reward, next_state, done):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self, state, action, reward, next_state, done):
        pass

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