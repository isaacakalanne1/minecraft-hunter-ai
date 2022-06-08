import torch
import random
import numpy as np
from collections import deque
from Hunter import Hunter
from model import Linear_QNet, QTrainer

MAX_MEMORY = 10_000
BATCH_SIZE = 100
LR = 0.001

class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0 # Controls randomness
        self.gamma = 0.9 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, hunter):
        # state = {
        #     0: list(hunter.inventoryItems.items()), # May be worth using text instead of numbers
        #     1: list(hunter.blocksInMemory.items()),
        #     2: list(hunter.entitiesInMemory.items()),
        #     3: hunter.currentHeldItem,
        #     4: hunter.currentHealth,
        #     5: hunter.currentHunger,
        #     6: hunter.currentTimeOfDay,
        #     7: hunter.currentPosition
        # }

        state = {
            1: list(hunter.blocksInMemory.items()),
            7: hunter.currentPosition # Same numbers in case simple AI can be used to train other AIs
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
        # Random moves: tradeoff betwen exploration & exploitation
        self.epsilon = 80 - self.number_of_games
        final_move = [0,0,0] # Change to format of Hunter moves
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2) # 2 is included
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

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