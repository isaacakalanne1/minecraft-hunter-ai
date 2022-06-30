from javascript import require, On
import Action.Movement as Movement
import Action.MovementModifier as MovementModifier
import Action.Jump as Jump
import Action.HunterAction as HunterAction
import Generators.RandomGenerator as RandomGenerator
import Generators.LookDirection as LookDirection
import random
import time
import math
import numpy as np
from threading import Thread

mineflayer = require('/Users/iakalann/node_modules/mineflayer')
pvp = require('/Users/iakalann/node_modules/mineflayer-pvp').plugin
pathfinder = require('/Users/iakalann/node_modules/mineflayer-pathfinder').pathfinder
collectBlock = require('/Users/iakalann/node_modules/mineflayer-collectblock').plugin
Vec3 = require('vec3')

class Kratos:

  def __init__(self, host, port, username):
    self.bot = mineflayer.createBot({
                  'host': host,
                  'port': port,
                  'username': username
                })
    self.username = username
    self.action = HunterAction.HunterAction()
    self.currentHealth = 0
    self.currentHunger = 0
    self.initialTimeOfDay = 0
    self.currentTimeOfDay = 0
    self.botHasDied = False
    self.rlIsActive = False
    self.mcData = ""
    self.bot.on('spawn', self.handle)
    self.bot.on('death', self.handleDeath)
    self.bot.on('chat', self.handleMsg)
    self.bot.on('health', self.healthUpdated)

  def healthUpdated(self, *args):
    self.currentHealth = self.bot.health
    self.currentHunger = self.bot.food
                
  def handle(self, *args):
    print("I spawned 👋")
    self.resetValues()

  def resetValues(self):
    self.initialTimeOfDay = self.bot.time.timeOfDay
    self.mcData = require('/Users/iakalann/node_modules/minecraft-data')(self.bot.version)
    self.bot.loadPlugin(pathfinder)
    self.bot.loadPlugin(pvp)
    self.bot.loadPlugin(collectBlock)
    self.bot.pathfinder.allowSprinting = True
    self.bot.pvp.viewDistance = 1_000_000_000
    self.bot.pvp.attackRange = 3
    self.bot.pvp.followRange = 0

  def deleteInventory(self):
    self.bot.chat('/gamemode creative')
    self.bot.creative.clearInventory()
    self.bot.chat('/gamemode survival')


  def handleDeath(self, *args):
    if self.rlIsActive == True:
      self.botHasDied = True
    print('I died!')

  def handleMsg(self, this, sender, message, *args):
    print('Received message:', message)
    if sender and (sender != 'HelloThere'):
      match message:

        case 'find':

          block = self.bot.findBlock({
            'matching' : self.mcData.blocksByName.grass_block.id,
            'maxDistance' : 64
          })

          if block is not None:
            try:
              self.bot.collectBlock.collect(block)
            except:
              print('Couldn\'t collect block!')
          else:
            print('Couldn\'t find a block!')

        case 'fight me':
          self.attackPlayer()

        case 'self':
          print('Bot is', self.bot.entity)

        case 'entities':
          print('Entities are', self.bot.entities)

        case 'physics':
          # self.bot.physics.playerSpeed = 0.2
          entity = self.action.getNearestEntity(self.bot)
          print('Player physics is', entity)
          print('bot.physics is', self.bot.physics)

  def attackPlayer(self):
    try:
      player = self.bot.players['RoyalCentaur']
      self.bot.pvp.attack(player.entity)
    except:
      if player is None:
        self.bot.chat('I can\'t see you!')
      else:
        self.bot.chat('I can\'t attack you!')
      

  def getState(self):
    
    stateList = [0]
    state = np.array(stateList, dtype=float)
    return state

  def getEmptyActions(self):
    return np.array([0] * 8, dtype=float)

  def play_step(self, action):

    print('action is', action)

    match action:
      case 0:
        print('Action here!')

    time.sleep(0.3)

    state = self.getState()
    reward, terminal = self.getRewardTerminal()
    return state, reward, terminal

  def getRewardTerminal(self):

    self.currentTimeOfDay = self.bot.time.timeOfDay
    timeDifference = self.currentTimeOfDay - self.initialTimeOfDay
    reward = 1

    if self.botHasDied == True and self.rlIsActive == True:
      self.botHasDied = False
      return 0, True
    
    return reward, timeDifference > 400

  def reset(self):
    self.rlIsActive = False
    self.respawnBot()
    state = self.getState()
    self.rlIsActive = True
    return state

  def respawnBot(self):
    self.bot.chat('/time set 300')
    self.bot.chat('/weather clear')
    self.bot.chat('/kill')

kratos = Kratos('localHost', 25565, 'Kratos')

while True:
  time.sleep(1)

# if __name__ == '__main__':
#   for i in range(10):
#     p = multiprocessing.Process(target=createHunter(i))
#     p.start()