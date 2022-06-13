import torch
import random
import numpy as np
from collections import deque
from Hunter import Hunter
from model import Linear_QNet, QTrainer
from helper import plot
from javascript import require, On
import time

MAX_MEMORY = 10_000
BATCH_SIZE = 100
LR = 0.001

class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0 # Controls randomness
        self.gamma = 0.9 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(38, 256, 100, 17)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, hunter):
        blocks = hunter.getBlocksInMemory()
        position = hunter.getCurrentPosition()
        lookDirection = hunter.getCurrentLookDirection()
        state = blocks + position + lookDirection
        
        print('The state is', state)
        stateArray = np.array(state, dtype=float)
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

        if random.randint(0, 200) < self.epsilon:
            lookYawValue = random.random()
            lookPitchValue = random.random()
            moveValue = random.randint(0, 8)
            jumpValue = random.randint(0, 1)
            moveModifierValue = random.randint(0, 2)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            print('The prediction is', prediction)
            noLookChangeIndex = torch.tensor([0])
            lookYawIndex = torch.tensor([1])
            lookPitchIndex = torch.tensor([2])
            allLookTensor = torch.index_select(prediction, 0, noLookChangeIndex)
            maxLook = torch.argmax(allLookTensor).item()

            if maxLook == 0:
                lookYawValue = -1
                lookPitchValue = -1
            else:
                lookYawValue = torch.index_select(prediction, 0, lookYawIndex).item()
                lookPitchValue = torch.index_select(prediction, 0, lookPitchIndex).item()

            moveIndexesAll = torch.tensor([3, 4, 5, 6, 7, 8, 9, 10, 11])
            moveTensor = torch.index_select(prediction, 0, moveIndexesAll)
            moveValue = torch.argmax(moveTensor).item()

            jumpIndexesAll = torch.tensor([12, 13])
            jumpTensor = torch.index_select(prediction, 0, jumpIndexesAll)
            jumpValue = torch.argmax(jumpTensor).item()

            moveModifierIndexesAll = torch.tensor([14, 15, 16])
            moveModifierTensor = torch.index_select(prediction, 0, moveModifierIndexesAll)
            moveModifierValue = torch.argmax(moveModifierTensor).item()

        final_move = [lookYawValue, lookPitchValue, moveValue, jumpValue, moveModifierValue]
        return final_move

def train():
    print('Trainingg!')
    game = Hunter('localHost', 25565, 'HelloThere')
    game.bot.on('spawn', startTraining(game))

def startTraining(game):
    time.sleep(1.5)
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    print('Starting training!')
    while True:
        # Get old state
        state_old = agent.get_state(game)

        # Get move
        final_move = agent.get_action(state_old)

        # Perform move and get new state
        print('Final move is', final_move)
        game.play_step(final_move)
        time.sleep(0.2)
        reward, done, score = game.getRewardDoneScore()
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

            plot_scores.append(score)
            total_score += score
            mean_score = total_score/agent.number_of_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()