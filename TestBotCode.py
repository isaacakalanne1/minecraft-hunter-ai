from javascript import require, On
import secrets
from enum import Enum
mineflayer = require('/Users/iakalann/node_modules/mineflayer')

BOT_USERNAME = 'HelloThere'
BOT_USERNAME_2 = 'HelloThereMate'
SERVER_HOST = "localHost"
SERVER_PORT = 52589

bot = mineflayer.createBot({
  'host': SERVER_HOST,
  'port': SERVER_PORT,
  'username': BOT_USERNAME
})

@On(bot, 'spawn')
def handle(*args):
  print("I spawned 👋")

class Movement(Enum):
  none = 0
  forwards = 1
  backwards = 2
  left = 3
  right = 4

class MovementModifier(Enum):
  none = 0
  sprint = 1
  sneak = 2

def move(movement):
  bot.setControlState('forward', movement is Movement.forwards)
  bot.setControlState('back', movement is Movement.backwards)
  bot.setControlState('left', movement is Movement.left)
  bot.setControlState('right', movement is Movement.right)

def movementModifier(movementModifier):
  bot.setControlState('sprint', movementModifier is MovementModifier.sprint)
  bot.setControlState('sneak', movementModifier is MovementModifier.sneak)

@On(bot, 'chat')
def handleMsg(this, sender, message, *args):
  print("Got message", sender, message)
  if sender and (sender != BOT_USERNAME):
    bot.chat('Hi, you said ' + message)
    match message:
      case "go":
        bot.setControlState('forward', True)
      case "halt":
        bot.setControlState('forward', False)
      case "find blocks":
        blocks = bot.findBlocks({
          "matching": lambda block:
            block.boundingBox is "block",
          "maxDistance": 16,
          "count": 200
        })
        print("The blocks are", blocks)
      case "current block":
        block = bot.blockAtCursor()
        print("Block is", block)

def canSeeTheBlock(block):
  if block.position is None:
    return False
  if block.boundingBox is "block" and bot.canSeeBlock(block) is True:
    return True
  return False