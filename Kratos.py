from turtle import pos
from javascript import require, On, AsyncTask
import Action.Movement as Movement
import Action.MovementModifier as MovementModifier
import Action.Jump as Jump
import Action.HunterAction as HunterAction
import Generators.RandomGenerator as RandomGenerator
import Generators.LookDirection as LookDirection
import random
import time
import asyncio
import numpy as np
from threading import Barrier
import re
import ast
from enum import Enum

mineflayer = require('/Users/iakalann/node_modules/mineflayer')
pvp = require('/Users/iakalann/node_modules/mineflayer-pvp').plugin
pathfinder = require('/Users/iakalann/node_modules/mineflayer-pathfinder').pathfinder
movements = require('/Users/iakalann/node_modules/mineflayer-pathfinder').Movements
goals = require('/Users/iakalann/node_modules/mineflayer-pathfinder').goals
collectBlock = require('/Users/iakalann/node_modules/mineflayer-collectblock').plugin
Vec3 = require('vec3')

class Block(Enum):
  oakLog = 'oak_log'

class CustomGoal(Enum):
  noGoal = 'no_goal'
  attackPlayer = 'attack_player'
  collectLog = 'collect_log'
  craftPlanks = 'craft_planks'
  craftCraftingTable = 'craft_crafting_table'
  collectScaffolding = 'collect_scaffolding'

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
    self.inventory = {}
    self.botHasDied = False
    self.rlIsActive = False
    self.mcData = ""
    self.currentGoal = CustomGoal.noGoal
    self.barrier = Barrier(1, timeout=5)
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
    print('Goal reached!')
    # time.sleep(0.2)
    if self.bot.targetDigBlock == None:
      match self.currentGoal:
        case CustomGoal.collectLog:
          self.collectLog()

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
    self.bot.pathfinder.setMovements(move)
    self.bot.loadPlugin(pvp)
    self.bot.loadPlugin(collectBlock)
    self.bot.pathfinder.allowSprinting = True
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

        case 'items':
          print('items are', self.mcData.itemsByName.wooden_axe.id)

        case 'go':
          self.bot.chat('/data get entity RoyalCentaur')

        case 'fight me':
          self.attackPlayer()

        case 'reset':
          self.bot.resetPath()

        case 'stop':
          self.stop()

        case 'inventory':
          print('Inventory is', self.bot.inventory)
          print('Oak log is', Block.oakLog.value)

        case 'player':
          player = self.bot.players['RoyalCentaur']
          print('player is', player)

        case 'self':
          print('Bot is', self.bot.entity)

        case 'entities':
          print('Entities are', self.bot.entities)

        case 'physics':
          # self.bot.physics.playerSpeed = 0.2
          entity = self.action.getNearestEntity(self.bot)
          print('Player physics is', entity)
          print('bot.physics is', self.bot.physics)
    
  def stop(self):
    try:
      self.currentGoal = CustomGoal.noGoal
      self.bot.pathfinder.stop()
    except:
      print('Couldn\'t stop pathfinder!')

  def hasOakLogsInInventory(self):
    items = self.bot.inventory.slots
    self.inventory = {}
    for item in items:
      if hasattr(item, 'name') and item.name == Block.oakLog.value:
        if Block.oakLog.value in self.inventory:
          self.inventory[Block.oakLog.value] += item.count
        else:
          self.inventory[Block.oakLog.value] = item.count
    if self.inventory[Block.oakLog.value] >= 1:
      return True
    else:
      return False

  def attemptToCraftOakPlanks(self):
    recipe = self.getOakPlanksRecipe()
    if len(list(recipe)) == 0:
      print('Collecting log!')
      self.collectLog()
    else:
      recipe = recipe[0]
      self.craft(recipe)
      print('Crafted planks!')

  def attackPlayer(self):
    player = self.bot.players['RoyalCentaur']
    if player.entity is not None:
      print('Attacking player', player)
      self.bot.pvp.attack(player.entity)
    else:
      print('I can\'t find you!')
      pass
      # if self.bot.pathfinder.isMoving() == False:
      #   print('Going to player!')
      #   self.bot.pathfinder.setGoal(None)
      self.triggerGoToPlayer()

  def triggerGoToPlayer(self):
    self.bot.chat('/data get entity RoyalCentaur')
  
  def getDistanceTo(self, playerX, playerZ):
    kratosX = self.bot.entity.position.x
    kratosZ = self.bot.entity.position.z
    diffX = playerX - kratosX
    diffZ = playerZ - kratosZ
    return diffX, diffZ

  def goto(self, position):
    playerX = int(position[0])
    playerZ = int(position[2])
    x, z = self.getDistanceTo(playerX, playerZ)
    print('total distance x z is', x, z)
    x, z = self.convertToGhostWalkDistance(x, z)
    print('ghost distance x z is', x, z)
    kratosX = self.bot.entity.position.x
    kratosZ = self.bot.entity.position.z
    ghostWalkX = kratosX + x
    ghostWalkZ = kratosZ + z
    self.ghostWalkTo(ghostWalkX, ghostWalkZ)

  def ghostWalkTo(self, x, z):
    time.sleep(3)
    self.bot.chat('/spreadplayers ' + str(x) + ' ' + str(z) + ' 0 10 false Kratos')
    time.sleep(1)
    self.attackPlayer()
        
  def convertToGhostWalkDistance(self, x, z):
    ghostWalkDistance = 40
    if x > ghostWalkDistance or x < -ghostWalkDistance:
      mult = abs(ghostWalkDistance / x)
      x *= mult
      z *= mult
    if z > ghostWalkDistance or z < -ghostWalkDistance:
      mult = abs(ghostWalkDistance / z)
      x *= mult
      z *= mult
    return x, z
      
  def collectLog(self):
    self.stop()
    self.currentGoal = CustomGoal.collectLog
    block = self.bot.findBlock({
      'matching' : self.mcData.blocksByName.oak_log.id,
      'maxDistance' : 64
    })

    if block is not None:

      try:
        @AsyncTask(start=True)
        def getLog(task):
          self.bot.collectBlock.collect(block, {
            'ignoreNoPath' : True
          }, timeout=99)
          if self.currentGoal == CustomGoal.collectLog:
            self.collectLog()
              
        print('Done!')
      except:
        print('Couldn\'t collect block!')
    else:
      print('Couldn\'t find a block!')
    

  def getOakPlanksRecipe(self):
    return self.bot.recipesFor(self.mcData.itemsByName.oak_planks.id, None, 1, None)

  def attemptToPlaceCraftingTable(self):
    print('Placing crafting table!')
    self.bot.equip(246)
    print('A!')
    blockToPlace = Vec3(2, 1, 0)
    print('B!')
    # self.bot.placeBlock(blockToPlace, Vec3(0, 1, 0))
    self.bot.pathfinder.goto(goals.GoalPlaceBlock(blockToPlace.offset(0, 1, 0), self.bot.world, {
      range: 4
    }))
    print('C!')

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

kratos = Kratos('localHost', 63109, 'Kratos')

while True:
  time.sleep(1)

# if __name__ == '__main__':
#   for i in range(10):
#     p = multiprocessing.Process(target=createHunter(i))
#     p.start()