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
SERVER_PORT = 60468

SELECT_QUICKBAR_SLOT = 'selectQuickBarSlot'
MOVE_ITEM_SLOT = 'moveItemSlot'

class HunterData:
  # Will need to update inventoryItems to dictionary, like {32 : Item} so AI can access items based on their ID, rather than a raw index
  inventoryItems = []

  # Will need to update blocksInMemory to dictionary, like { Vec3{x,y,z} : Block} so AI can access blocks based on their position, rather than a raw index
  blocksInMemory = []

  entitiesInMemory = []

  bot = mineflayer.createBot({
    'host': SERVER_HOST,
    'port': SERVER_PORT,
    'username': BOT_USERNAME
  })

hunterData = HunterData()
bot = hunterData.bot

@On(bot, 'spawn')
def handle(*args):
  print("I spawned 👋")
  updateInventory(bot)
  
class ItemSlot(Enum):
  none = 0
  moveItemSlot = 1
  selectSlot = 2

class BlockFace(Enum):
  front = [0,0,0]
  back = [1,0,0]
  left = [0,0,0]
  right = [0,0,1]
  bottom = [0,0,0]
  top = [0,1,0]

def look(currentBot, yaw, pitch):
  currentBot.look(yaw, pitch, True)

def randomYaw():
  return random.uniform(0,6.28)

def randomPitch():
  return random.uniform(-math.pi/2,math.pi/2)

def holdItem(currentBot, item):
  currentBot.equip(item)

def randomIndexOf(list):
  if not list:
    return None
  return int(round(random.uniform(0,len(list) - 1), 0))

def randomInventoryIndex():
  updateInventory(bot)
  return randomIndexOf(hunterData.inventoryItems)

@On(bot, 'chat')
def handleMsg(this, sender, message, *args):
  print("Got message", sender, message)
  if sender and (sender != BOT_USERNAME):
    bot.chat('Hi, you said ' + message)
    match message:
      case "go":
        look(bot, randomYaw(), randomPitch())
        Movement.move(bot, Movement.Direction.forwards)
        MovementModifier.modify(bot, MovementModifier.Type.sprint)
        Jump.jump(bot, Jump.Jump.jump)
        if randomInventoryIndex() is not None:
          holdItem(bot, hunterData.inventoryItems[randomInventoryIndex()])
        
      case "halt":
        look(bot, randomYaw(), randomPitch())
        Movement.move(bot, Movement.Direction.none)
        MovementModifier.modify(bot, MovementModifier.Type.none)
        Jump.jump(bot, Jump.Jump.none)
        if randomInventoryIndex() is not None:
          holdItem(bot, hunterData.inventoryItems[randomInventoryIndex()])
      case "inventory":
        print("Inventory is", hunterData.inventoryItems)
      case "find blocks":
        scanArea(bot)
      case "dig":
        hunterData.blocksInMemory.append(bot.blockAtCursor())
        index = randomIndexOf(hunterData.blocksInMemory)
        if index is not None:
          print('yeee!')
          blockIndex = len(hunterData.blocksInMemory) - 1
          block = hunterData.blocksInMemory[blockIndex]
          dig(bot, block, True, 'rayCast')
      case 'place':
        block = getCurrentlyLookedAtBlock(bot)
        face = {'x' : 0, 'y' : 1, 'z' : 0}
        try:
          place(bot, block, face)
        except:
          bot.chat('I couldn\'t place a block next to ' + block.displayName)

      case 'activate':
        block = getCurrentlyLookedAtBlock(bot)
        bot.activateBlock(block)
        
      case "current block":
        block = getCurrentlyLookedAtBlock(bot)
        print("Block is", block)

      case 'attack':
        entity = getEntityFromMemory()
        if entity is not None:
          attack(bot, entity)
        else:
          bot.chat('There\'s no entity in memory for me to attack!')

      case 'nearest':
        getNearestEntity(bot)

def dig(currentBot, block, forceLook, digFace):
  currentBot.dig(block, forceLook, digFace)

def place(currentBot, block, face):
  currentBot.placeBlock(block, face)

def attack(currentBot, entityToAttack):
  currentBot.attack(entityToAttack)

match = lambda entity: entity.name == 'player'

def getNearestEntity(currentBot):
  entity = currentBot.nearestEntity(match)
  hunterData.entitiesInMemory.append(entity)

def nameIsCow(entity):
  return entity.name == 'cow'

def getCurrentlyLookedAtBlock(currentBot):
  hunterData.blocksInMemory.append(currentBot.blockAtCursor())
  blockIndex = len(hunterData.blocksInMemory) - 1
  block = hunterData.blocksInMemory[blockIndex]
  return block

def getEntityFromMemory():
  if len(hunterData.entitiesInMemory) is not 0:
    index = len(hunterData.entitiesInMemory) -1
    entity = hunterData.entitiesInMemory[index]
    return entity
  return None

@On(bot, 'playerCollect')
def handlePlayerCollect(this, collector, collected):
  if collector.username == bot.username:
    bot.chat("I collected an item!")
    updateInventory(bot)

def updateInventory(currentBot):
  hunterData.inventoryItems = []
  for item in currentBot.inventory.items():
    hunterData.inventoryItems.append(item)

def canSeeTheBlock(block):
  if block.position is None:
    return False
  if block.boundingBox == 'block' and bot.canSeeBlock(block) is True:
    return True
  else:
    return False

def scanArea(currentBot):
  blocks = currentBot.findBlocks({
    "matching": lambda block:
      canSeeTheBlock(block),
    "maxDistance": 16,
    "count": 20
  })
  print("The blocks are", blocks)
  print('Da type is', type(blocks[0]))

def generalAction(currentBot):
  currentBot.craft()