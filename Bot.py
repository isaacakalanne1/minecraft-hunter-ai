from operator import inv
from javascript import require, On
from enum import Enum
import math
import random
import Action.Movement as Movement
import Action.MovementModifier as MovementModifier
import Action.Jump as Jump

mineflayer = require('/Users/iakalann/node_modules/mineflayer')

BOT_USERNAME = 'HelloThere'
BOT_USERNAME_2 = 'HelloThereMate'
SERVER_HOST = "localHost"
SERVER_PORT = 62022

class HunterAction:

  def getNearestEntity(self, currentBot):
    entity = currentBot.nearestEntity(lambda entity: entity.name == 'RoyalCentaur')
    return entity

  def getPositionOfEnemyPlayer(self, entity):
    position = entity.position
    positionAsVec3 = {'x' : position.x, 'y' : position.y, 'z' : position.z}
    print('Position is', positionAsVec3)
    return positionAsVec3

  def holdItem(self, currentBot, item):
    currentBot.equip(item)

  def getHeldItemOfEnemyPlayer(self, entity):
    print('Held item is', entity.heldItem)
    return entity.heldItem

  def attack(self, currentBot, entityToAttack):
    currentBot.attack(entityToAttack)

  def getEntityFromMemory(self, entitiesInMemory):
    if len(entitiesInMemory) is not 0:
      index = len(entitiesInMemory) -1
      entity = entitiesInMemory[index]
      return entity
    return None

  def getCurrentlyLookedAtBlock(self, currentBot):
    return currentBot.blockAtCursor()

  def look(self, currentBot, yaw, pitch):
    currentBot.look(yaw, pitch, True)

  def updateInventory(self, currentBot):
    items = []
    for item in currentBot.inventory.items():
      items.append(item)
    return items

  def activateHeldItem(self, currentBot, offHand):
    currentBot.activateItem(offHand)

  def place(self, currentBot, block, face):
    currentBot.placeBlock(block, face)

  def dig(self, currentBot, block, forceLook, digFace):
    currentBot.dig(block, forceLook, digFace)
  
  def getTimeOfDay(currentBot):
    return currentBot.time.timeOfDay

class Hunter:
  # Will need to update inventoryItems to dictionary, like {32 : Item} so AI can access items based on their ID, rather than a raw index
  global inventoryItems
  inventoryItems = []

  # Will need to update blocksInMemory to dictionary, like { Vec3{x,y,z} : Block} so AI can access blocks based on their position, rather than a raw index
  global blocksInMemory
  blocksInMemory = []

  global entitiesInMemory
  entitiesInMemory = []

  global positionOfEnemyInMemory
  positionOfEnemyInMemory = {'x' : 0, 'y' : 0, 'z' : 0}

  global heldItemOfEnemyInMemory
  heldItemOfEnemyInMemory = None

  global currentHealth
  currentHealth = None
  global currentHunger
  currentHunger = None

  global currentTimeOfDay
  currentTimeOfDay = None

  global action
  action = HunterAction()

  global bot
  bot = mineflayer.createBot({
    'host': SERVER_HOST,
    'port': SERVER_PORT,
    'username': BOT_USERNAME
  })

  @On(bot, 'spawn')
  def handle(*args):
    print("I spawned 👋")
    inventoryItems = action.updateInventory(bot, inventoryItems)

  @On(bot, 'chat')
  def handleMsg(this, sender, message, *args):
    print("Got message", sender, message)
    if sender and (sender != BOT_USERNAME):
      bot.chat('Hi, you said ' + message)
      match message:
        case "go":
          action.look(bot, randomYaw(), randomPitch())
          Movement.move(bot, Movement.Direction.forwards)
          MovementModifier.modify(bot, MovementModifier.Type.sprint)
          Jump.jump(bot, Jump.Jump.jump)
          inventoryItems = action.updateInventory(bot, inventoryItems)
          if randomIndexOf(inventoryItems) is not None:
            index = randomIndexOf(inventoryItems)
            item = hunter.inventoryItems[index]
            action.holdItem(bot, item)
          
        case "halt":
          action.look(bot, randomYaw(), randomPitch())
          Movement.move(bot, Movement.Direction.none)
          MovementModifier.modify(bot, MovementModifier.Type.none)
          Jump.jump(bot, Jump.Jump.none)
          inventoryItems = action.updateInventory(bot, inventoryItems)
          if randomIndexOf(inventoryItems) is not None:
            index = randomIndexOf(inventoryItems)
            item = hunter.inventoryItems[index]
            action.holdItem(bot, item)

        case 'look':
          action.look(bot, randomYaw(), randomPitch())

        case "inventory":
          inventoryItems = action.updateInventory(bot, inventoryItems)
          print("Inventory is", inventoryItems)
        case "dig":
          hunter.blocksInMemory.append(bot.blockAtCursor())
          index = randomIndexOf(hunter.blocksInMemory)
          if index is not None:
            print('yeee!')
            blockIndex = len(hunter.blocksInMemory) - 1
            block = hunter.blocksInMemory[blockIndex]
            action.dig(bot, block, True, 'rayCast')
        case 'place':
          block = action.getCurrentlyLookedAtBlock(bot)
          blocksInMemory.append(block)
          face = {'x' : 0, 'y' : 1, 'z' : 0}
          try:
            action.place(bot, block, face)
          except:
            try:
              bot.chat('I couldn\'t place a block next to ' + block.displayName)
            except:
              bot.chat('I couldn\'t place a block, there\'s no block in memory to place it next to')

        case 'activate':
          block = action.getCurrentlyLookedAtBlock(bot, blocksInMemory)
          blocksInMemory.append(block)
          bot.activateBlock(block)
          
        case "current block":
          block = action.getCurrentlyLookedAtBlock(bot, blocksInMemory)
          blocksInMemory.append(block)
          print('Block is', block)

        case 'attack':
          entity = action.getEntityFromMemory(entitiesInMemory)
          if entity is not None:
            action.attack(bot, entity)
          else:
            bot.chat('There\'s no entity in memory for me to attack!')

        case 'nearest':
          entity = action.getNearestEntity(bot)
          entitiesInMemory.append(entity)

        case 'position':
          entity = action.getNearestEntity(bot)
          entitiesInMemory.append(entity)
          positionOfEnemyInMemory = action.getPositionOfEnemyPlayer(entity, positionOfEnemyInMemory)

        case 'held':
          entity = action.getNearestEntity(bot)
          entitiesInMemory.append(entity)
          item = action.getHeldItemOfEnemyPlayer(entity)

        case 'time':
          currentTimeOfDay = action.getTimeOfDay(bot)
          print('Time of day is' + str(currentTimeOfDay))
        
        case 'use':
          action.activateHeldItem(bot, False)

        case 'hold':
          if randomIndexOf(inventoryItems) is not None:
            index = randomIndexOf(inventoryItems)
            item = inventoryItems[index]
            action.holdItem(bot, item)

  @On(bot, 'playerCollect')
  def handlePlayerCollect(this, collector, collected):
    if collector.username == bot.username:
      bot.chat("I collected an item!")
      inventoryItems = action.updateInventory(bot, inventoryItems)

  @On(bot, 'health')
  def handle(*args):
    currentHealth = bot.health
    currentHunger = bot.food
    bot.chat('My health is' + str(currentHealth))
    bot.chat('My hunger is' + str(currentHunger))
  
hunter = Hunter()

class BlockFace(Enum):
  front = {'x' : 0, 'y' : 1, 'z' : 0}
  back = {'x' : 0, 'y' : 1, 'z' : 0}
  left = {'x' : 0, 'y' : 1, 'z' : 0}
  right = {'x' : 0, 'y' : 1, 'z' : 0}
  bottom = {'x' : 0, 'y' : 1, 'z' : 0}
  top = {'x' : 0, 'y' : 1, 'z' : 0}

def randomYaw():
  return random.uniform(0,6.28)

def randomPitch():
  return random.uniform(-math.pi/2,math.pi/2)

def randomIndexOf(list):
  if not list:
    return None
  return int(round(random.uniform(0,len(list) - 1), 0))