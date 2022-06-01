from ast import Num
from javascript import require, On
from enum import Enum
from fastnumbers import fast_real
import math
import random
import asyncio
import Action.Movement as Movement
import Action.MovementModifier as MovementModifier
import Action.Jump as Jump

mineflayer = require('/Users/iakalann/node_modules/mineflayer')

BOT_USERNAME = 'HelloThere'
BOT_USERNAME_2 = 'HelloThereMate'
SERVER_HOST = "localHost"
SERVER_PORT = 59878

SELECT_QUICKBAR_SLOT = 'selectQuickBarSlot'
MOVE_ITEM_SLOT = 'moveItemSlot'

inventoryItems = {}

bot = mineflayer.createBot({
  'host': SERVER_HOST,
  'port': SERVER_PORT,
  'username': BOT_USERNAME
})

loop = asyncio.get_event_loop()

@On(bot, 'spawn')
def handle(*args):
  print("I spawned 👋")

class ItemSlot(Enum):
  none = 0
  moveItemSlot = 1
  selectSlot = 2

def look(currentBot, yaw, pitch):
  currentBot.look(yaw, pitch, True)

def selectQuickBarSlot(currentBot, slot):
  if slot is not None:
    currentBot.setQuickBarSlot(slot)

def randomYaw():
  return random.uniform(0,6.28)

def randomPitch():
  return random.uniform(-math.pi/2,math.pi/2)

async def updateSlots(currentBot, type, slotValue):
  if type == MOVE_ITEM_SLOT:
    sourceSlot = int(slotValue[0])
    destSlot = int(slotValue[1])
    x = await moveItem(currentBot, 37, 40)
  if type == SELECT_QUICKBAR_SLOT:
    selectQuickBarSlot(currentBot, 1)

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
        MovementModifier.modify(bot, MovementModifier.Type.sprint)
        Jump.jump(bot, Jump.Jump.jump)
        updateSlots(bot, MOVE_ITEM_SLOT, (36, 40))
      case "halt":
        look(bot, randomYaw(), randomPitch())
        Movement.move(bot, Movement.Direction.none)
        MovementModifier.modify(bot, MovementModifier.Type.none)
        Jump.jump(bot, Jump.Jump.none)
        updateSlots(bot, SELECT_QUICKBAR_SLOT, 1)
      case "item slots":
        moveItem(bot, 37, 36)
        selectQuickBarSlot(bot, 0)
        print("Inventory is", bot.inventory.items())
      case "find blocks":
        scanArea(bot)
      case "current block":
        block = bot.blockAtCursor()
        print("Block is", block)
      case "slot test":
        updateSlots(bot, MOVE_ITEM_SLOT, (36, 38))

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