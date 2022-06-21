from email.policy import default
from typing_extensions import Self
from javascript import require, On
import Action.Movement as Movement
import Action.MovementModifier as MovementModifier
import Action.Jump as Jump
import Action.HunterAction as HunterAction
import Generators.RandomGenerator as RandomGenerator
import Generators.LookDirection as LookDirection
import numpy as np
import random
import torch
import time

mineflayer = require('/Users/iakalann/node_modules/mineflayer')
Vec3 = require('vec3')

class Hunter:

  def __init__(self, host, port, username):
    self.bot = ""
    self.createBot(host, port, username)
    self.action = HunterAction.HunterAction()
    self.inventoryItems = {}
    self.blocksInMemory = [0] * 16
    self.entitiesInMemory = {}
    self.currentHeldItem = [0, 0] # [Id, count]
    self.currentHealth = 0
    self.currentHunger = 0
    self.initialTimeOfDay = 0
    self.currentTimeOfDay = 0
    self.currentPosition = [0,0,0]
    self.currentYaw = 0
    self.currentPitch = 0
    self.initialX = 0
    self.currentScore = 0
    self.botHasDied = False
    self.rlIsActive = False
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
    self.rlIsActive = True
    self.inventoryItems = {}
    self.initialX = self.bot.entity.position.x
    self.currentYaw = self.bot.entity.yaw
    self.currentPitch = self.bot.entity.pitch
    self.initialTimeOfDay = self.action.getTimeOfDay(self.bot)
    self.currentScore = 0
    items = self.action.updateInventory(self.bot)
    for item in items:
      self.inventoryItems[(item.type, item.slot)] = item.count

  def handleDeath(self, *args):
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
          print('Entities in memory are:', self.entitiesInMemory)

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
    yaw = RandomGenerator.randomYaw()
    pitch = RandomGenerator.randomPitch()
    self.action.look(self.bot, yaw, pitch)

  def handlePlayerCollect(self, this, collector, collected, *args):
    if collector.username == self.bot.username:
      self.bot.chat("I collected an item!")
      self.inventoryItems = self.action.updateInventory(self.bot)

  def getBlocksInMemory(self):
    return self.blocksInMemory

  def getCurrentPosition(self):
    position = self.bot.entity.position
    self.currentPosition = [position.x, position.y, position.z]
    return self.currentPosition

  def getCurrentYawAndPitch(self):
    return [self.currentYaw, self.currentPitch]
  
  def getCurrentHealth(self):
    return [float(self.bot.health)]

  def play_step(self, action):

    lookYawMultiplier, lookPitchMultiplier, move, jumpVal, moveMod = action

    if lookYawMultiplier != -1:
      yaw = LookDirection.getYaw(lookYawMultiplier)
      pitch = LookDirection.getPitch(lookPitchMultiplier)
      self.currentYaw = yaw
      self.currentPitch = pitch

    self.action.look(self.bot, self.currentYaw, self.currentPitch)
    self.blocksInMemory = LookDirection.getBlocksInFieldOfView(currentBot=self.bot, yaw=self.currentYaw, pitch=self.currentPitch, fieldOfView=0.9, resolution=2)

    movement = Movement.Direction(move)
    movementMod = MovementModifier.Type(moveMod)
    jump = Jump.Jump(jumpVal)
      
    Movement.move(self.bot, movement)
    MovementModifier.modify(self.bot, movementMod)
    Jump.jump(self.bot, jump)

  def getRewardDoneScore(self):

    if self.botHasDied == True and self.rlIsActive == True:
      self.botHasDied = False
      print('Game ended from bot death!')
      return 0, 1, self.currentScore
    else:
      reward = self.bot.entity.position.x - self.initialX

    self.initialX = self.bot.entity.position.x

    currentTime = self.action.getTimeOfDay(self.bot)
    if self.initialTimeOfDay + 400 < currentTime:
      print('Game ended naturally!')
      done = 1
    else:
      done = 0
      
    self.currentScore += reward
    return reward, done, self.currentScore

  def reset(self):
    self.rlIsActive = False
    self.respawnBot()
    time.sleep(0.5)
    self.moveBot()
    time.sleep(2)
    self.randomLook()
    time.sleep(0.5)
    self.rlIsActive = True

  def randomPositionChange(self, initial):
    return int(round(random.uniform(initial, initial - 100), 0))

  def respawnBot(self):
    currentPosition = self.bot.entity.position
    self.bot.chat('/time set 300')
    self.bot.chat('/weather clear')
    self.bot.chat('/gamerule spawnradius 0')
    self.bot.chat('/spawnpoint @a ' + str(currentPosition.x) + ' ' + str(currentPosition.y) + ' ' + str(currentPosition.z))
    self.bot.chat('/kill')

  def moveBot(self):
    currentPosition = self.bot.entity.position
    currentX = currentPosition.x
    currentZ = currentPosition.z
    randomX = self.randomPositionChange(currentX)
    randomZ = self.randomPositionChange(currentZ)
    self.bot.chat('/spreadplayers ' + str(randomX) + ' ' + str(randomZ) + ' 0 5 false @a')

hunter = Hunter('localHost', 25565, 'HelloThere')

while True:
  time.sleep(1)

# if __name__ == '__main__':
#   for i in range(10):
#     p = multiprocessing.Process(target=createHunter(i))
#     p.start()