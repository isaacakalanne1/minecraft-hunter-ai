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
BATCH_SIZE = 5
LR = 0.0001

class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0 # Controls randomness
        self.gamma = 0.9 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(33, 300, 50, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, hunter):
        blocks = hunter.getBlocksInMemory() # 27 floats
        lookDirection = hunter.getCurrentYawAndPitch() # 2 floats
        position = hunter.getCurrentPositionData() # 4 floats

        state = blocks + lookDirection + position

        # print('State is', state)
        
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

        final_move = [0,0,0,0]
        if random.randint(0, 200) < self.epsilon:
            action_index = random.randint(0, 3)
            final_move[action_index] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            print('The prediction is', prediction)
            action_index = torch.argmax(prediction).item()
            final_move[action_index] = 1
            print('Predicted final move is', final_move)

        return final_move

def train(i):
    game = Hunter('localHost', 25565, 'HelloThere' + str(i))
    game.bot.on('spawn', checkIfReady(game))

def checkIfReady(game):
    print('Checking!')
    if game.rlIsActive == False and game.botHasDied == False:
        if hasattr(game.bot.entity, 'position') and hasattr(game.bot, 'health'):
            game.rlIsActive = True
            game.resetValues()
            startTraining(game)
        else:
            time.sleep(1)
            checkIfReady(game)

def startTraining(game):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    looped_number_of_games = 0
    loop_number = 0
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
        time.sleep(0.4)
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
            looped_number_of_games += 1
            if looped_number_of_games == 99:
                loop_number += 1
                agent.model.save(file_name='model-ryoshi-run-2.0-game-' + str(loop_number*100) + '.pth')
                looped_number_of_games = 0
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