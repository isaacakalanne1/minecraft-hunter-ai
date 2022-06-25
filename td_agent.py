import numpy as np
import random
from collections import deque
import time

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import copy

from Hunter import Hunter

ENV_NAME = "CartPole-v1"

GAMMA = 0.95
LEARNING_RATE = 3e-4

MEMORY_SIZE = 1000000
BATCH_SIZE = 20

EXPLORATION_MAX = 1.0
EXPLORATION_MIN = 0.01
EXPLORATION_DECAY = 0.995

class DQN(torch.nn.Module):
    def __init__(self, observation_space, action_space):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(observation_space, 20),
            nn.ReLU(inplace = True),
            nn.Linear(20, 20),
            nn.ReLU(inplace = True),
            nn.Linear(20, 10),
            nn.ReLU(inplace = True),
            nn.Linear(10, action_space),
        )

    def forward(self, observation):
        return self.net(observation)


class GameSolver:
    def __init__(self, observation_space, action_space):
        self.exploration_rate = EXPLORATION_MAX

        self.action_space = action_space
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.Q_policy = DQN(observation_space, action_space)
        self.Q_target = copy.deepcopy(self.Q_policy)
        self.optimizer = optim.Adam(self.Q_policy.parameters(), lr = LEARNING_RATE)
        self.lossFuc = torch.nn.MSELoss()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def predict(self, state):
        if np.random.rand() < self.exploration_rate:
            return random.randrange(self.action_space)

        q_values = self.Q_policy(state)[0]

        # best action
        max_q_index =  torch.max(q_values, 0).indices.numpy()
       # print(torch.max(q_values).detach().numpy())
        return max_q_index

    def experince_replay(self):
        if len(self.memory) < BATCH_SIZE:
            return
        batch = random.sample(self.memory, BATCH_SIZE)
        for state, action, reward, state_next, terminal in batch:
            self.optimizer.zero_grad()

            y = reward
            if not terminal:
                y = reward + GAMMA * torch.max( self.Q_target(state_next) )
            state_values = self.Q_policy(state)
            action_values = [0, 0, 0, 0]
            action_values[action] = 1.0
            real_state_action_values = torch.sum(state_values * torch.FloatTensor(action_values))
            print('real_state_action_values is', real_state_action_values)
            loss = self.lossFuc(y, real_state_action_values)
            print('loss is', loss)
            loss.backward()
            self.optimizer.step()
        self.exploration_rate *= EXPLORATION_DECAY
        self.exploration_rate  = max(EXPLORATION_MIN, self.exploration_rate)

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

def startTraining(env):
    stateSpace = env.getState()
    observation_space = np.array(stateSpace).shape[0]
    emptyActions = env.getEmptyActions()
    action_space = np.array(emptyActions).shape[0]
    gameSolver = GameSolver(observation_space, action_space)
    run = 0
    while True:
        run += 1
        state = env.reset()
        state = torch.FloatTensor(np.reshape(state, [1, observation_space]))
        step = 0
        while True:
            step += 1
          #  time.sleep(0.05)
            action = gameSolver.predict(state)
            state_next, reward, terminal = env.play_step(action)
            reward = reward if not terminal else -reward * 10
            reward = torch.tensor(reward)
            state_next = torch.FloatTensor(np.reshape(state_next, [1, observation_space]))
            gameSolver.remember(state, action, reward, state_next, terminal)

            state = state_next

            if terminal:
                print ("Run: " + str(run) + ", exploration: " + str(gameSolver.exploration_rate) + ", score: " + str(step) )
                break
            gameSolver.experince_replay()
            if run % 3 == 0 or step % 100 == 0:
                gameSolver.Q_target = copy.deepcopy(gameSolver.Q_policy)

if __name__ == "__main__":
    train(1)