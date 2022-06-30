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
import asyncio

mineflayer = require('/Users/iakalann/node_modules/mineflayer')
Vec3 = require('vec3')

class Hunter:

  def __init__(self, host, port, username):
    self.bot = mineflayer.createBot({
                  'host': host,
                  'port': port,
                  'username': username
                })
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
    self.seeDistance = 5
    self.currentYaw = 0
    self.currentPitch = 0
    self.spawnX = -58
    self.spawnY = 101
    self.spawnZ = -35
    self.entityListSize = 4
    self.fieldOfView = 0.8
    self.resolution = 3
    self.botHasDied = False
    self.rlIsActive = False
    self.newlyCollectedBlocks = 0
    self.bot.on('spawn', self.handle)
    self.bot.on('death', self.handleDeath)
    self.bot.on('chat', self.handleMsg)
    self.bot.on('playerCollect', self.handlePlayerCollect)
    self.bot.on('health', self.healthUpdated)

  def healthUpdated(self, *args):
    self.currentHealth = self.bot.health
    self.currentHunger = self.bot.food
                
  def handle(self, *args):
    print("I spawned 👋")
    self.resetValues()

  def resetValues(self):
    self.inventoryItems = {}
    self.initialTimeOfDay = self.action.getTimeOfDay(self.bot)
    self.deleteInventory()
    items = self.action.updateInventory(self.bot)
    print('Inventory items are', items)
    self.currentYaw = 0
    self.currentPitch = 0
    self.action.look(self.bot, self.currentYaw, self.currentPitch)
    for item in items:
      self.inventoryItems[(item.type, item.slot)] = item.count

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

        case 'run':
          Movement.move(self.bot, Movement.Direction.forwards)

        case 'stop':
          Movement.move(self.bot, Movement.Direction.none)

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
          try:
            block = self.bot.blockAtCursor()
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
          blockData = self.getLidarDataOfBlock(block)
          print('Block is', blockData)

        case 'current look':
          eyePos = LookDirection.getEyePositionOfBot(self.bot)
          direction = LookDirection.getLookDirectionOf(self.currentYaw, self.currentPitch)
          x = direction[0]
          y = direction[1]
          z = direction[2]
          vecDirection = Vec3(x, y, z)
          seen = self.bot.world.raycast(eyePos, vecDirection, 10, None)
          print('seen is', seen)

        case 'attack':
          entity = self.action.getNearestEntity(self.bot)
          if entity is not None:
            self.action.attack(self.bot, entity)
          else:
            self.bot.chat('There\'s no entity in memory for me to attack!')

        case 'nearest':
          listOfEntities = self.getVisibleEntities()
                
          print('Entities are ', listOfEntities)

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
          blockss = LookDirection.getBlocksInFieldOfView(currentBot=self.bot, yaw=yaw, pitch=pitch, fieldOfView=self.fieldOfView, resolution=self.resolution)
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

        case 'ranges':
          self.isWithinFieldOfView()

  def getLidarDataOfBlock(self, block):
    distance = self.bot.entity.position.distanceTo(block.position)
    distance = round(block.distance, 1) * 10
    return [block.id, int(distance)]

  def canSee(self, entity):
    return self.bot.entity.position.distanceTo(entity.position) <= self.seeDistance and \
            self.bot.canSeeEntity(entity) and \
            entity.username != self.username

  def isDroppedItem(self, entity):
    return hasattr(entity.metadata[8], 'itemId')

  def getVisibleEntityData(self):
    dataPerItem = 2

    try:
      listOfAllEntities = self.bot.entities
    except:
      print('Couldn\'t get bot entities!')
      return [0] * dataPerItem * self.entityListSize

    listOfLiveEntities = []
    listOfDroppedItems = []
    for id in listOfAllEntities:
      entity = listOfAllEntities[id]
      try:
        if self.canSee(entity):
          positionData = self.getRelativePositionDataOf(entity)
          if self.isDroppedItem(entity):
            id = self.getItemIdOf(entity)
            itemData = [id] + positionData
            if len(listOfDroppedItems) < self.entityListSize:
              listOfDroppedItems += itemData
          else:
            pass # Activate below code to save data for live entity, though may have to use a different identifier than id for players, as id changes on each session
            # entityData = [entity.id] + positionData
            # if len(listOfDroppedItems) < 2:
            #   listOfLiveEntities.append(entityData)
      except:
        pass
    remainingEmptyData = len(listOfDroppedItems) % dataPerItem * self.entityListSize
    listOfDroppedItems += [0] * remainingEmptyData
    listOfVisibleEntities = listOfLiveEntities + listOfDroppedItems
    return listOfVisibleEntities

  def getItemIdOf(entity):
    return entity.metadata[8].itemId

  def getRelativePositionDataOf(self, entity):
    position = entity.position
    selfPosition = self.bot.entity.position

    xIsNegative = 0
    yIsNegative = 0
    zIsNegative = 0

    relativeX = round(position.x - selfPosition.x, 1) * 10
    relativeY = round(position.y - selfPosition.y, 1) * 10
    relativeZ = round(position.z - selfPosition.z, 1) * 10

    if relativeX < 0:
      xIsNegative = 1
      relativeX = -relativeX
    if relativeY < 0:
      yIsNegative = 1
      relativeY = -relativeY
    if relativeZ < 0:
      zIsNegative = 1
      relativeZ = -relativeZ

    blockData = [xIsNegative, int(relativeX), yIsNegative, int(relativeY), zIsNegative, int(relativeZ)]
    return blockData
  
  def isWithinFieldOfView(self):
    minX, maxX, minY, maxY, minZ, maxZ = LookDirection.getMinAndMaxValuesForLookDirection(self.currentYaw, self.currentPitch, self.fieldOfView, self.resolution)
    print('values are', minX, maxX, minY, maxY, minZ, maxZ)


  def randomLook(self):
    self.currentYaw = RandomGenerator.randomYaw()
    print('Yaw is', self.currentYaw)
    self.currentPitch = 0
    self.action.look(self.bot, self.currentYaw, self.currentPitch)

  def handlePlayerCollect(self, this, collector, collected, *args):
    if collector.username == self.bot.username and \
        self.isDroppedItem(collected):
      # itemId = self.getItemIdOf(collected)
      # if itemId == 101: # For now, just train bot to collect blocks
      self.newlyCollectedBlocks += 1
      print('Bot collected an item!')
      # self.inventoryItems = self.action.updateInventory(self.bot)

  def getBlocksInMemory(self):
    self.blocksInMemory = LookDirection.getBlocksInFieldOfView(currentBot=self.bot, yaw=self.currentYaw, pitch=self.currentPitch, fieldOfView=self.fieldOfView, resolution=self.resolution)
    return self.blocksInMemory

  def getCurrentPositionData(self):
    position = self.bot.entity.position
    return [round(position.x, 2), round(position.y, 2), round(position.z, 2)]

  def getCurrentYawAndPitch(self):
    yaw = (round(self.currentYaw, 1) * 10)
    pitch = round(self.currentPitch + (math.pi /2), 1) * 10
    return [int(yaw), int(pitch)]

  def getState(self):
    
    entityData = self.getVisibleEntityData()

    try:
      cursorBlock = self.action.getCurrentlyLookedAtBlock(self.bot)
      cursorBlockData = self.getLidarDataOfBlock(cursorBlock)
    except:
      cursorBlockData = [0,0]

    try:
      blocks = self.getBlocksInMemory()
    except:
      blocks = [0, 0] * self.resolution * self.resolution * self.resolution

    lookDirection = self.getCurrentYawAndPitch()

    stateList = entityData + cursorBlockData + blocks + lookDirection
    state = np.array(stateList, dtype=float)
    return state

  def getEmptyActions(self):
    return np.array([0] * 8, dtype=float)

  def play_step(self, action):

    yawChange = LookDirection.getYawChange()
    pitchChange = LookDirection.getPitchChange()
    print('action is', action)

    # print('target dig block is', self.bot.targetDigBlock)

    if action == 5:
      Movement.move(self.bot, Movement.Direction.forwards)
    else:
      Movement.move(self.bot, Movement.Direction.none)
      
    if action == 6:
      Movement.move(self.bot, Movement.Direction.forwards)
      Jump.jump(self.bot, Jump.Jump.jump)
    else:
      Jump.jump(self.bot, Jump.Jump.none)
      

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
      case 3:
        if self.currentPitch - pitchChange < -math.pi/2:
          self.currentPitch = -math.pi/2
        else:
          self.currentPitch -= pitchChange # Look down
      case 4:
        if self.currentPitch + pitchChange > math.pi/2:
          self.currentPitch = math.pi/2
        else:
          self.currentPitch += pitchChange # Look up
      case 7:
        try:
          block = self.bot.blockAtCursor()
          self.action.dig(self.bot, block, True, 'rayCast') # Currently digging blocks other functions from running, which isn't perfect, but is partially what I was going to implement anyway
        except:
          print('No block to dig!')
          # self.bot.chat('Couldn\'t dig block, there\'s no block to dig')

    if action != 7:
      self.action.look(self.bot, self.currentYaw, self.currentPitch)

    

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
    reward = self.newlyCollectedBlocks
    self.newlyCollectedBlocks = 0

    if self.botHasDied == True and self.rlIsActive == True:
      self.botHasDied = False
      return 0, True
    
    return reward, timeDifference > 400

  def reset(self):
    self.rlIsActive = False
    self.deleteInventory()
    self.respawnBot()
    state = self.getState()
    self.rlIsActive = True
    return state

  def respawnBot(self):
    self.bot.chat('/time set 300')
    self.bot.chat('/weather clear')
    self.bot.chat('/kill')

# hunter = Hunter('localHost', 25565, 'HelloThere')

# while True:
#   time.sleep(1)

# if __name__ == '__main__':
#   for i in range(10):
#     p = multiprocessing.Process(target=createHunter(i))
#     p.start()