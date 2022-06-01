from javascript import require, On
import secrets
mineflayer = require('/Users/iakalann/node_modules/mineflayer')

BOT_USERNAME = 'HelloThere'
BOT_USERNAME_2 = 'HelloThereMate'

bot = mineflayer.createBot({
  'host': 'localHost',
  'port': 54281,
  'username': BOT_USERNAME
})

bot2 = mineflayer.createBot({
  'host': 'localHost',
  'port': 54281,
  'username': BOT_USERNAME_2
})

@On(bot, 'spawn')
def handle(*args):
  print("I spawned 👋")

@On(bot2, 'spawn')
def handle(*args):
  print("I spawned 👋")

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
          "maxDistance": 100,
          "count": 30
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