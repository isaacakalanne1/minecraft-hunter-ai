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
import torch
import numpy as np
import multiprocessing

mineflayer = require('/Users/iakalann/node_modules/mineflayer')
Vec3 = require('vec3')

class Hunter:

  def __init__(self, host, port, username):
    self.bot = ""
    self.createBot(host, port, username)
    self.username = username
    self.action = HunterAction.HunterAction()
    self.inventoryItems = {}
    self.blocksInMemory = [0.00] * 8
    self.entitiesInMemory = {}
    self.currentHeldItem = [0, 0] # [Id, count]
    self.currentHealth = 0
    self.currentHunger = 0
    self.initialTimeOfDay = 0
    self.currentTimeOfDay = 0
    self.currentPosition = [0.00] * 3
    self.currentYaw = 0
    self.currentPitch = 0
    self.initialX = 0
    self.spawnX = -58
    self.spawnY = 101
    self.spawnZ = -35
    self.zoneRadius = 4
    self.botHasDied = False
    self.rlIsActive = False
    self.respawnResetDelay = 0.5
    self.bot.on('spawn', self.handle)
    self.bot.on('death', self.handleDeath)
    self.bot.on('chat', self.handleMsg)
    self.bot.on('playerCollect', self.handlePlayerCollect)
    self.bot.on('health', self.healthUpdated)

  def healthUpdated(self, *args):
    self.currentHealth = self.bot.health
    self.currentHunger = self.bot.food

  def createBot(self, host, port, username):
    self.bot = mineflayer.createBot({
                  'host': host,
                  'port': port,
                  'username': username
                })
                
  def handle(self, *args):
    print("I spawned 👋")
    self.resetValues()

  def resetValues(self):
    self.inventoryItems = {}
    self.initialTimeOfDay = self.action.getTimeOfDay(self.bot)
    items = self.action.updateInventory(self.bot)
    self.initialX = self.bot.entity.position.x
    self.randomLook()
    Movement.move(self.bot, Movement.Direction.forwards)
    MovementModifier.modify(self.bot, MovementModifier.Type.sprint)
    for item in items:
      self.inventoryItems[(item.type, item.slot)] = item.count

  def handleDeath(self, *args):
    if self.rlIsActive == True:
      self.botHasDied = True
    print('I died!')

  def handleMsg(self, this, sender, message, *args):
    print('Received message:', message)
    if sender and (sender != 'HelloThere'):
      match message:

        case "inventory":
          self.inventoryItems = {}
          items = self.action.updateInventory(self.bot)
          for item in items:
            self.inventoryItems[(item.type, item.slot)] = item.count
          print("Inventory is", self.inventoryItems)

        case 'self':
          print('Bot is', self.bot.entity)

        case 'spin':
          Movement.move(self.bot, Movement.Direction.forwards)
          for i in range(50):
            self.randomLook()
            time.sleep(0.3)

        case "dig":
          block = self.bot.blockAtCursor()
          try:
            self.action.dig(self.bot, block, True, 'rayCast')
          except:
            self.bot.chat('Couldn\'t dig block, there\'s no block to dig')

        case 'place':
          block = self.action.getCurrentlyLookedAtBlock(self.bot)
          face = Vec3(0,1,0)
          try:
            self.action.place(self.bot, block, face)
          except:
            try:
              self.bot.chat('I couldn\'t place a block next to ' + block.displayName)
            except:
              self.bot.chat('I couldn\'t place a block, there\'s no block in memory to place it next to')

        case 'activate':
          block = self.action.getCurrentlyLookedAtBlock(self.bot)
          self.bot.activateBlock(block)
          
        case "current block":
          block = self.action.getCurrentlyLookedAtBlock(self.bot)
          print('Block is', block)

        case 'attack':
          entity = self.action.getNearestEntity(self.bot)
          if entity is not None:
            self.action.attack(self.bot, entity)
          else:
            self.bot.chat('There\'s no entity in memory for me to attack!')

        case 'nearest':
          entity = self.action.getNearestEntity(self.bot)
          # print('Entity is', entity)
          position = (entity.position.x, entity.position.y, entity.position.z)
          if entity.heldItem is None:
            heldItem = None
          else:
            heldItem = entity.heldItem.type
          self.entitiesInMemory[entity.id] = [position, heldItem]
          # print('Entities in memory are:', self.entitiesInMemory)
          print('Entity is', entity)

        case 'held':
          entity = self.action.getNearestEntity(self.bot)
          position = (entity.position.x, entity.position.y, entity.position.z)
          self.entitiesInMemory[entity.id] = [position, entity.heldItem.type]
          item = self.action.getHeldItemOfEnemyPlayer(entity)

        case 'own held':
          heldItem = self.bot.entity.heldItem
          self.currentHeldItem = [heldItem.type, heldItem.count]
          print('Current held is', self.currentHeldItem)

        case 'time':
          self.currentTimeOfDay = self.action.getTimeOfDay(self.bot)
          print('Time of day is' + str(self.currentTimeOfDay))
        
        case 'use':
          self.action.activateHeldItem(self.bot, False)

        case 'look':
          self.randomLook()

        case 'blocks':
          yaw = RandomGenerator.randomYaw()
          pitch = RandomGenerator.randomPitch()
          self.action.look(self.bot, yaw, pitch)
          blockss = LookDirection.getBlocksInFieldOfView(currentBot=self.bot, yaw=yaw, pitch=pitch, fieldOfView=0.9, resolution=3)
          print('Blocks are:', blockss)

        case 'hold':
          if RandomGenerator.randomIndexOf(self.inventoryItems) is not None:
            index = RandomGenerator.randomIndexOf(self.inventoryItems)
            item = self.inventoryItems[(index)]
            self.action.holdItem(self.bot, item)

        case 'physics':
          # self.bot.physics.playerSpeed = 0.2
          entity = self.action.getNearestEntity(self.bot)
          print('Player physics is', entity)
          print('bot.physics is', self.bot.physics)

  def randomLook(self):
    self.currentYaw = RandomGenerator.randomYaw()
    print('Yaw is', self.currentYaw)
    self.currentPitch = 0
    self.action.look(self.bot, self.currentYaw, self.currentPitch)

  def handlePlayerCollect(self, this, collector, collected, *args):
    if collector.username == self.bot.username:
      self.bot.chat("I collected an item!")
      self.inventoryItems = self.action.updateInventory(self.bot)

  def getBlocksInMemory(self):
    self.blocksInMemory = LookDirection.getBlocksInFieldOfView(currentBot=self.bot, yaw=self.currentYaw, pitch=self.currentPitch, fieldOfView=1.0, resolution=3)
    return self.blocksInMemory

  def getCurrentPositionData(self):
    position = self.bot.entity.position
    return [round(position.x, 2), round(position.y, 2), round(position.z, 2)]

  def getCurrentYawAndPitch(self):
    yaw = (round(self.currentYaw, 1) * 10)
    pitch = round(self.currentPitch + (math.pi /2), 1) * 10
    return [int(yaw), int(pitch)]

  def getState(self):
    blocks = self.getBlocksInMemory() # 27 floats
    lookDirection = self.getCurrentYawAndPitch() # 2 floats
    position = self.getCurrentPositionData() # 3 floats
    stateList = blocks + lookDirection + position
    state = np.array(stateList, dtype=float)
    return state

  def getEmptyActions(self):
    return np.array([0,0,0,0], dtype=float)

  def play_step(self, action):

    yawChange = LookDirection.getYawChange()
    print('action is', action)
    match action:
      case 1:
        if self.currentYaw - yawChange < 0:
          change = self.currentYaw - yawChange
          self.currentYaw = 6.28 - change
        else:
          self.currentYaw -= yawChange # Turn left
      case 2:
        if self.currentYaw + yawChange > 6.28:
          change = self.currentYaw + yawChange
          self.currentYaw = change - 6.28
        else:
          self.currentYaw += yawChange # Turn right

    self.action.look(self.bot, self.currentYaw, self.currentPitch)
      
    if action == 3:
      Jump.jump(self.bot, Jump.Jump.jump)
    else:
      Jump.jump(self.bot, Jump.Jump.none)

    time.sleep(0.3)

    state = self.getState()
    reward, terminal = self.getRewardTerminal()
    return state, reward, terminal

  def random_of_ranges(*ranges):
    all_ranges = sum(ranges, [])
    return random.choice(all_ranges)

  def getRewardTerminal(self):

    self.currentTimeOfDay = self.action.getTimeOfDay(self.bot)
    timeDifference = self.currentTimeOfDay - self.initialTimeOfDay
    currentX = self.bot.entity.position.x
    reward = currentX - self.initialX
    self.initialX = currentX

    if (self.botHasDied == True and self.rlIsActive == True) or timeDifference > 200:
      self.botHasDied = False
      return 0, True
    
    if timeDifference > 200:
      return reward, True
    print('Reward is', reward)
    return reward, False

  def reset(self):
    self.rlIsActive = False
    self.respawnBot()
    state = self.getState()
    self.rlIsActive = True
    return state

  def respawnBot(self):
    self.bot.chat('/time set 300')
    self.bot.chat('/weather clear')
    self.bot.chat('/gamerule spawnRadius 0') # Spawnradius seems to default to 5 or so, even when set to 0
    self.bot.chat('/spawnpoint ' + self.username + ' ' + str(self.spawnX) + ' ' + str(self.spawnY) + ' ' + str(self.spawnZ))
    self.bot.chat('/kill')

# hunter = Hunter('localHost', 25565, 'HelloThere')

# while True:
#   time.sleep(1)

# if __name__ == '__main__':
#   for i in range(10):
#     p = multiprocessing.Process(target=createHunter(i))
#     p.start()