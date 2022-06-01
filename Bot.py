from javascript import require, On
from enum import Enum
import math
import random
import asyncio
import Action.Movement as Movement

mineflayer = require('/Users/iakalann/node_modules/mineflayer')

BOT_USERNAME = 'HelloThere'
BOT_USERNAME_2 = 'HelloThereMate'
SERVER_HOST = "localHost"
SERVER_PORT = 52589

inventoryItems = {}

bot = mineflayer.createBot({
  'host': SERVER_HOST,
  'port': SERVER_PORT,
  'username': BOT_USERNAME
})

@On(bot, 'spawn')
def handle(*args):
  print("I spawned 👋")

class MovementModifier(Enum):
  none = 0
  sprint = 1
  sneak = 2

class Jump(Enum):
  none = 0
  jump = 1

class ItemSlot(Enum):
  none = 0
  moveItemSlot = 1
  selectSlot = 2

def look(currentBot, yaw, pitch):
  currentBot.look(yaw, pitch, True)

def movementModifier(currentBot, movementModifier):
  currentBot.setControlState('sprint', movementModifier is MovementModifier.sprint)
  currentBot.setControlState('sneak', movementModifier is MovementModifier.sneak)

def jump(currentBot, jump):
  currentBot.setControlState('jump', jump is Jump.jump)

def selectQuickBarSlot(currentBot, slot):
  if slot is not None:
    currentBot.setQuickBarSlot(slot)

def randomYaw():
  return random.uniform(0,6.28)

def randomPitch():
  return random.uniform(-math.pi/2,math.pi/2)

async def moveItem(currentBot, sourceSlot, destSlot):
  await currentBot.moveSlotItem(sourceSlot, destSlot)

def randomQuickBarSlot():
  return random.uniform(0,8)

@On(bot, 'chat')
def handleMsg(this, sender, message, *args):
  print("Got message", sender, message)
  if sender and (sender != BOT_USERNAME):
    bot.chat('Hi, you said ' + message)
    match message:
      case "go":
        look(bot, randomYaw(), randomPitch())
        Movement.move(bot, Movement.Direction.left)
        movementModifier(bot, MovementModifier.sprint)
        jump(bot, Jump.jump)
        moveItem(bot, 37, 36)
        selectQuickBarSlot(bot, randomQuickBarSlot())
      case "halt":
        look(bot, randomYaw(), randomPitch())
        Movement.move(bot, Movement.Direction.none)
        movementModifier(bot, MovementModifier.none)
        jump(bot, Jump.none)
        moveItem(bot, 37, 36)
        selectQuickBarSlot(bot, randomQuickBarSlot())
      case "item slots":
        moveItem(bot, 37, 36)
        selectQuickBarSlot(bot, 0)
        print("Inventory is", bot.inventory.items())
      case "find blocks":
        scanArea(bot)
      case "current block":
        block = bot.blockAtCursor()
        print("Block is", block)

@On(bot, 'playerCollect')
def handlePlayerCollect(this, collector, collected):
  if collector.username == bot.username:
    bot.chat("I collected an item!")
    updateInventory(bot)

def updateInventory(currentBot):
  items = bot.inventory.items()
  for item in items:
    inventoryItems[item.slot] = item

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

def generalAction(currentBot):
  currentBot.craft()