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

  def getNearestEntity(self, currentBot, entitiesInMemory):
    entity = currentBot.nearestEntity(lambda entity: entity.name == 'RoyalCentaur')
    entitiesInMemory.append(entity)
    print('Entity is', entity)
    return entity

  def getPositionOfEnemyPlayer(self, entity, positionInMemory):
    position = entity.position
    positionInMemory = {'x' : position.x, 'y' : position.y, 'z' : position.z}
    print('Position is', positionInMemory)
    return position

  def holdItem(self, currentBot, item):
    currentBot.equip(item)

  def getHeldItemOfEnemyPlayer(self, entity, heldItemInMemory):
    heldItemInMemory = entity.heldItem
    print('Held item is', heldItemInMemory)
    return heldItemInMemory

  def attack(self, currentBot, entityToAttack):
    currentBot.attack(entityToAttack)

  def getEntityFromMemory(entitiesInMemory):
    if len(entitiesInMemory) is not 0:
      index = len(entitiesInMemory) -1
      entity = entitiesInMemory[index]
      return entity
    return None

  def getCurrentlyLookedAtBlock(self, currentBot, blocksInMemory):
    block = currentBot.blockAtCursor()
    blocksInMemory.append(currentBot.blockAtCursor())
    return block

  def look(self, currentBot, yaw, pitch):
    currentBot.look(yaw, pitch, True)

class Hunter:
  # Will need to update inventoryItems to dictionary, like {32 : Item} so AI can access items based on their ID, rather than a raw index
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

  currentHealth = None
  currentHunger = None

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
    updateInventory(bot)

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
          if randomInventoryIndex() is not None:
            action.holdItem(bot, hunter.inventoryItems[randomInventoryIndex()])
          
        case "halt":
          action.look(bot, randomYaw(), randomPitch())
          Movement.move(bot, Movement.Direction.none)
          MovementModifier.modify(bot, MovementModifier.Type.none)
          Jump.jump(bot, Jump.Jump.none)
          if randomInventoryIndex() is not None:
            action.holdItem(bot, hunter.inventoryItems[randomInventoryIndex()])

        case 'look':
          action.look(bot, randomYaw(), randomPitch())

        case "inventory":
          print("Inventory is", hunter.inventoryItems)
        case "dig":
          hunter.blocksInMemory.append(bot.blockAtCursor())
          index = randomIndexOf(hunter.blocksInMemory)
          if index is not None:
            print('yeee!')
            blockIndex = len(hunter.blocksInMemory) - 1
            block = hunter.blocksInMemory[blockIndex]
            dig(bot, block, True, 'rayCast')
        case 'place':
          block = action.getCurrentlyLookedAtBlock(bot, blocksInMemory)
          face = {'x' : 0, 'y' : 1, 'z' : 0}
          try:
            place(bot, block, face)
          except:
            try:
              bot.chat('I couldn\'t place a block next to ' + block.displayName)
            except:
              bot.chat('I couldn\'t place a block, there\'s no block in memory to place it next to')

        case 'activate':
          block = action.getCurrentlyLookedAtBlock(bot, blocksInMemory)
          bot.activateBlock(block)
          
        case "current block":
          block = action.getCurrentlyLookedAtBlock(bot, blocksInMemory)
          print('Block is', block)

        case 'attack':
          entity = action.getEntityFromMemory(entitiesInMemory)
          if entity is not None:
            action.attack(bot, entity)
          else:
            bot.chat('There\'s no entity in memory for me to attack!')

        case 'nearest':
          action.getNearestEntity(bot, entitiesInMemory)

        case 'position':
          entity = action.getNearestEntity(bot, entitiesInMemory)
          action.getPositionOfEnemyPlayer(entity, positionOfEnemyInMemory)

        case 'held':
          entity = action.getNearestEntity(bot, entitiesInMemory)
          action.getHeldItemOfEnemyPlayer(entity, heldItemOfEnemyInMemory)

        case 'time':
          hunter.currentTimeOfDay = bot.time.timeOfDay
          print('Time of day is' + str(bot.time.timeOfDay))
        
        case 'use':
          activateHeldItem(bot, False)

        case 'hold':
          if randomInventoryIndex() is not None:
            action.holdItem(bot, hunter.inventoryItems[randomInventoryIndex()])

  @On(bot, 'playerCollect')
  def handlePlayerCollect(this, collector, collected):
    if collector.username == bot.username:
      bot.chat("I collected an item!")
      updateInventory(bot)

  @On(bot, 'health')
  def handle(*args):
    hunter.currentHealth = bot.health
    hunter.currentHunger = bot.food
    bot.chat('My health is' + str(hunter.currentHealth))
    bot.chat('My hunger is' + str(hunter.currentHunger))
  
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

def randomInventoryIndex():
  updateInventory(bot)
  return randomIndexOf(hunter.inventoryItems)

def dig(currentBot, block, forceLook, digFace):
  currentBot.dig(block, forceLook, digFace)

def place(currentBot, block, face):
  currentBot.placeBlock(block, face)

def activateHeldItem(currentBot, offHand):
  currentBot.activateItem(offHand)

def updateInventory(currentBot):
  hunter.inventoryItems = []
  for item in currentBot.inventory.items():
    hunter.inventoryItems.append(item)