import numpy as np
from ppo_agent import Agent
# from utils import plot_learning_curve
from helper import plot
from Hunter import Hunter
import time

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
    N = 20
    batch_size = 500
    n_epochs = 4
    alpha = 0.0003
    agent = Agent(n_actions=len(env.getEmptyActions()), batch_size=batch_size,
                    alpha=alpha, n_epochs=n_epochs,
                    input_dims=env.getState().shape)

    n_games = 30000
    figure_file = 'plots/cartpole.png'

    best_score = 0
    score_history = []
    plot_scores = []
    plot_mean_scores = []
    
    learn_iters = 0
    avg_score = 0
    n_steps = 0

    for i in range(n_games):
        observation = env.reset()
        done = False
        score = 0
        while not done:
            action, prob, val = agent.choose_action(observation)
            observation_, reward, done = env.play_step(action)

            n_steps += 1
            score += reward
            agent.remember(observation, action, prob, val, reward, done)
            if n_steps % N == 0:
                agent.learn()
                learn_iters += 1
            observation = observation_
        score_history.append(score)
        avg_score = np.mean(score_history[-100:])

        if avg_score > best_score:
            best_score = avg_score
            agent.save_models()

        print('episode', i, 'score %.1f' % score, 'avg score %.1f' % avg_score,
                'time_steps', n_steps, 'learning_steps', learn_iters)
        x = [i+1 for i in range(len(score_history))]
        plot_scores.append(score)
        plot_mean_scores.append(avg_score)
        plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train(1)