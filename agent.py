import torch
import random
import numpy as np
from collections import deque
from Hunter import Hunter
from model import Linear_QNet, QTrainer
from helper import plot
from javascript import require, On
import time
import multiprocessing

MAX_MEMORY = 10_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0 # Controls randomness
        self.gamma = 0.9 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(37, 500, 500, 500, 500, 6)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, hunter):
        blocks = hunter.getBlocksInMemory() # 32 floats
        position = hunter.getCurrentPosition() # 3 floats
        lookDirection = hunter.getCurrentYawAndPitch() # 2 floats
        state = blocks + position + lookDirection
        
        stateArray = np.array(state, dtype=float)
        # print('The stateArray is', stateArray)
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
        final_move = [0,0,0,0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 5)
            final_move[move] = 1
            # print('Random final move is', final_move)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()

            final_move[move] = 1
            print('Prediction final move is', prediction)
            print('Predicted final move is', final_move)
        return final_move

def train(i):
    game = Hunter('localHost', 25565, 'HelloThere' + str(i))
    game.bot.on('spawn', checkIfReady(game))

def checkIfReady(game):
    print('Checking!')
    if game.rlIsActive == False:
        if hasattr(game.bot.entity, 'position') and hasattr(game.bot, 'health'):
            print('Killing!')
            game.bot.chat('/kill')
            # game.bot.chat('/spreadplayers -9 -25 0 1 false @a')
            time.sleep(1)
            game.rlIsActive = True
            startTraining(game)
        else:
            time.sleep(1)
            checkIfReady(game)

def startTraining(game):
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
        # print('Final move is', final_move)
        game.play_step(final_move)
        # time.sleep(0.2)
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
                agent.model.save()

            print('Game', agent.number_of_games, 'Score', score, 'Record', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score/agent.number_of_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train(1)
    # for i in range(10):
    #     p = multiprocessing.Process(target=train, args=[i])
    #     p.start()