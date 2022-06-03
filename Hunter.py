from javascript import require, On
import Action.Movement as Movement
import Action.MovementModifier as MovementModifier
import Action.Jump as Jump
import Action.HunterAction as HunterAction
import Generators.RandomGenerator as RandomGenerator

mineflayer = require('/Users/iakalann/node_modules/mineflayer')

RandomGenerator = RandomGenerator.RandomGenerator 

class Hunter:
  # Will need to update inventoryItems to dictionary, like {32 : Item} so AI can access items based on their ID, rather than a raw index

  # Will need to update blocksInMemory to dictionary, like { Vec3{x,y,z} : Block} so AI can access blocks based on their position, rather than a raw index

  def __init__(self, host, port, username):
    self.createBot(host, port, username)
    self.action = HunterAction.HunterAction()
    self.inventoryItems = []
    self.blocksInMemory = []
    self.entitiesInMemory = []
    self.positionOfEnemyInMemory = {'x' : 0, 'y' : 0, 'z' : 0}
    self.heldItemOfEnemyInMemory = None
    self.currentHealth = None
    self.currentHunger = None
    self.currentTimeOfDay = None

  def createBot(self, host, port, username):
    self.bot = mineflayer.createBot({
                  'host': host,
                  'port': port,
                  'username': username
                })
  
hunter = Hunter('localHost', 50661, 'HelloThere')

@On(hunter.bot, 'spawn')
def handle(*args):
  print("I spawned 👋")
  hunter.inventoryItems = hunter.action.updateInventory(hunter.bot)

@On(hunter.bot, 'chat')
def handleMsg(self, sender, message, *args):
  print("Got message", sender, message)
  
  if sender and (sender != 'HelloThere'):
    hunter.bot.chat('Hi, you said ' + message)
    match message:
      case "go":
        hunter.action.look(hunter.bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())
        Movement.move(hunter.bot, Movement.Direction.forwards)
        MovementModifier.modify(hunter.bot, MovementModifier.Type.sprint)
        Jump.jump(hunter.bot, Jump.Jump.jump)
        hunter.inventoryItems = hunter.action.updateInventory(hunter.bot)
        if RandomGenerator.randomIndexOf(hunter.inventoryItems) is not None:
          index = RandomGenerator.randomIndexOf(hunter.inventoryItems)
          item = hunter.inventoryItems[index]
          hunter.action.holdItem(hunter.bot, item)
        
      case "halt":
        hunter.action.look(hunter.bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())
        Movement.move(hunter.bot, Movement.Direction.none)
        MovementModifier.modify(hunter.bot, MovementModifier.Type.none)
        Jump.jump(hunter.bot, Jump.Jump.none)
        hunter.inventoryItems = hunter.action.updateInventory(hunter.bot)
        if RandomGenerator.randomIndexOf(hunter.inventoryItems) is not None:
          index = RandomGenerator.randomIndexOf(hunter.inventoryItems)
          item = hunter.inventoryItems[index]
          hunter.action.holdItem(hunter.bot, item)

      case 'look':
        hunter.action.look(hunter.bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())

      case "inventory":
        hunter.inventoryItems = hunter.action.updateInventory(hunter.bot)
        print("Inventory is", hunter.inventoryItems)
      case "dig":
        hunter.blocksInMemory.append(hunter.bot.blockAtCursor())
        index = RandomGenerator.randomIndexOf(hunter.blocksInMemory)
        if index is not None:
          print('yeee!')
          blockIndex = len(hunter.blocksInMemory) - 1
          block = hunter.blocksInMemory[blockIndex]
          hunter.action.dig(hunter.bot, block, True, 'rayCast')
      case 'place':
        block = hunter.action.getCurrentlyLookedAtBlock(hunter.bot)
        hunter.blocksInMemory.append(block)
        face = {'x' : 0, 'y' : 1, 'z' : 0}
        try:
          hunter.action.place(hunter.bot, block, face)
        except:
          try:
            hunter.bot.chat('I couldn\'t place a block next to ' + block.displayName)
          except:
            hunter.bot.chat('I couldn\'t place a block, there\'s no block in memory to place it next to')

      case 'activate':
        block = hunter.action.getCurrentlyLookedAtBlock(hunter.bot, hunter.blocksInMemory)
        hunter.blocksInMemory.append(block)
        hunter.bot.activateBlock(block)
        
      case "current block":
        block = hunter.action.getCurrentlyLookedAtBlock(hunter.bot, hunter.blocksInMemory)
        hunter.blocksInMemory.append(block)
        print('Block is', block)

      case 'attack':
        entity = hunter.action.getEntityFromMemory(hunter.entitiesInMemory)
        if entity is not None:
          hunter.action.attack(hunter.bot, entity)
        else:
          hunter.bot.chat('There\'s no entity in memory for me to attack!')

      case 'nearest':
        entity = hunter.action.getNearestEntity(hunter.bot)
        hunter.entitiesInMemory.append(entity)

      case 'position':
        entity = hunter.action.getNearestEntity(hunter.bot)
        hunter.entitiesInMemory.append(entity)
        hunter.positionOfEnemyInMemory = hunter.action.getPositionOfEnemyPlayer(entity, hunter.positionOfEnemyInMemory)

      case 'held':
        entity = hunter.action.getNearestEntity(hunter.bot)
        hunter.entitiesInMemory.append(entity)
        item = hunter.action.getHeldItemOfEnemyPlayer(entity)

      case 'time':
        hunter.currentTimeOfDay = hunter.action.getTimeOfDay(hunter.bot)
        print('Time of day is' + str(hunter.currentTimeOfDay))
      
      case 'use':
        hunter.action.activateHeldItem(hunter.bot, False)

      case 'hold':
        if RandomGenerator.randomIndexOf(hunter.inventoryItems) is not None:
          index = RandomGenerator.randomIndexOf(hunter.inventoryItems)
          item = hunter.inventoryItems[index]
          hunter.action.holdItem(hunter.bot, item)

@On(hunter.bot, 'playerCollect')
def handlePlayerCollect(this, collector, collected):
  if collector.username == hunter.bot.username:
    hunter.bot.chat("I collected an item!")
    hunter.inventoryItems = hunter.action.updateInventory(hunter.bot)


@On(hunter.bot, 'health')
def handle(*args):
  hunter.currentHealth = hunter.bot.health
  hunter.currentHunger = hunter.bot.food
  hunter.bot.chat('My health is' + str(hunter.currentHealth))
  hunter.bot.chat('My hunger is' + str(hunter.currentHunger))