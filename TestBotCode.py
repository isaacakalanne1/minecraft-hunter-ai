from javascript import require, On
import secrets
from enum import Enum
import math
import random
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

class Jump(Enum):
  none = 0
  jump = 1

def move(currentBot, movement):
  currentBot.setControlState('forward', movement is Movement.forwards)
  currentBot.setControlState('back', movement is Movement.backwards)
  currentBot.setControlState('left', movement is Movement.left)
  currentBot.setControlState('right', movement is Movement.right)

def movementModifier(currentBot, movementModifier):
  currentBot.setControlState('sprint', movementModifier is MovementModifier.sprint)
  currentBot.setControlState('sneak', movementModifier is MovementModifier.sneak)

def jump(currentBot, jump):
  currentBot.setControlState('jump', jump is Jump.jump)

def look(currentBot, yaw, pitch):

  currentBot.look(yaw, pitch, True)

def randomYaw():
  return random.uniform(0,6.28)

def randomPitch():
  return random.uniform(-math.pi/2,math.pi/2)

@On(bot, 'chat')
def handleMsg(this, sender, message, *args):
  print("Got message", sender, message)
  if sender and (sender != BOT_USERNAME):
    bot.chat('Hi, you said ' + message)
    match message:
      case "go":
        look(bot, randomYaw(), randomPitch())
        move(bot, Movement.left)
        movementModifier(bot, MovementModifier.sprint)
        jump(bot, Jump.jump)
      case "halt":
        look(bot, randomYaw(), randomPitch())
        move(bot, Movement.none)
        movementModifier(bot, MovementModifier.none)
        jump(bot, Jump.none)
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