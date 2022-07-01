from turtle import pos
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
import re
import ast

mineflayer = require('/Users/iakalann/node_modules/mineflayer')
pvp = require('/Users/iakalann/node_modules/mineflayer-pvp').plugin
pathfinder = require('/Users/iakalann/node_modules/mineflayer-pathfinder').pathfinder
movements = require('/Users/iakalann/node_modules/mineflayer-pathfinder').Movements
goals = require('/Users/iakalann/node_modules/mineflayer-pathfinder').goals
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
    self.bot.on('path_stop', self.pathStopped)
    self.bot.on('goal_reached', self.goalReached)
    self.bot.on('path_update', self.noPathListener)
    self.bot.on('goal_updated', self.goalChangedListener)
    self.bot.on('playerCollect', self.handlePlayerCollect)

  def handlePlayerCollect(self, *args):
    print('Collected item!')

  def pathStopped(self, *args):
    self.bot.chat('Path stopped!')

  def goalReached(self, *args):
    self.bot.chat('Goal reached!')

  def noPathListener(self, *args):
    pass
    # self.bot.chat('No path!')

  def goalChangedListener(self, *args):
    self.bot.chat('Goal changed!')

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
    move = movements(self.bot, self.mcData)
    move.canDig = True
    move.allowFreeMotion = True
    self.bot.pathfinder.setMovements(move)
    self.bot.loadPlugin(pvp)
    self.bot.loadPlugin(collectBlock)
    self.bot.pathfinder.allowSprinting = True
    self.bot.pvp.viewDistance = 100000000000000000
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

  def find_between(self, s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return None

  def getPositionFrom(self, message):
    try:
      position = self.find_between(message, 'Pos: ', ', Health:')
      position = re.sub('d', '', position)
      positionList = ast.literal_eval(position)
      return positionList
    except:
      return None

  def handleMsg(self, this, sender, message, *args):
    if sender and (sender == self.username or sender == 'data'):
      position = self.getPositionFrom(message)
      if position is not None:
        self.goto(position)

    if sender and (sender != 'Kratos') and (sender != 'data'):
      print('Received message:', message)
      match message:

        case 'collect':
          self.collectLog()

        case 'go':
          self.bot.chat('/data get entity RoyalCentaur')

        case 'fight me':
          self.attackPlayer()

        case 'stop':
          self.bot.pathfinder.stop()

        case 'inventory':
          pass

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
    player = self.bot.players['RoyalCentaur']
    if player.entity is not None:
      self.bot.pvp.attack(player.entity)
      print('Attacking player', player)
    else:
      self.bot.pathfinder.setGoal(None)
      time.sleep(1)
      self.triggerGoToPlayer()

  def triggerGoToPlayer(self):
    self.bot.chat('/data get entity RoyalCentaur')
  
  def goto(self, position):
    playerX = int(position[0])
    playerY = int(position[1])
    playerZ = int(position[2])
    kratosX = self.bot.entity.position.x
    kratosY = self.bot.entity.position.y
    kratosZ = self.bot.entity.position.z
    diffX = abs(playerX - kratosX)
    diffY = abs(playerY - kratosY)
    diffZ = abs(playerZ - kratosZ)
    x, y, z = self.convertDiffToInRange(diffX, diffY, diffZ)
    print('x y z is', x, y, z)
    goal = goals.GoalNear(x, y, z, 0)
    try:
      self.bot.pathfinder.setGoal(goal)
      print('Set goal!')
    except:
      print('Couldn\'t set goal!')
        
  def convertDiffToInRange(self, x, y, z):
    maxDistance = 100
    if x > maxDistance or y > maxDistance or z > maxDistance:
      x /= 2
      y /= 2
      z /= 2
    if x > maxDistance or y > maxDistance or z > maxDistance:
      return self.convertDiffToInRange(x, y, z)
    else:
      return x, y, z
      
  def collectLog(self):
    block = self.bot.findBlock({
      'matching' : self.mcData.blocksByName.oak_log.id,
      'maxDistance' : 64
    })

    if block is not None:
      try:
        self.bot.collectBlock.collect(block)
        self.collectBlock()
      except:
        print('Couldn\'t collect block!')
    else:
      print('Couldn\'t find a block!')

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