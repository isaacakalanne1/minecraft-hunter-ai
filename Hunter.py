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

  def __init__(self, host, port, username):
    self.createBot(host, port, username)
    self.action = HunterAction.HunterAction()


  def createBot(self, host, port, username):
    self.bot = mineflayer.createBot({
                  'host': host,
                  'port': port,
                  'username': username
                })
  
hunter = Hunter('localHost', 50661, 'HelloThere')

@On(hunter.bot, 'spawn')
def handle(self, *args):
  global inventoryItems
  print("I spawned 👋")
  inventoryItems = hunter.action.updateInventory(hunter.bot)

@On(hunter.bot, 'chat')
def handleMsg(self, sender, message, *args):
  print("Got message", sender, message)
  global inventoryItems, blocksInMemory, entitiesInMemory, positionOfEnemyInMemory, currentTimeOfDay
  
  if sender and (sender != 'HelloThere'):
    hunter.bot.chat('Hi, you said ' + message)
    match message:
      case "go":
        hunter.action.look(hunter.bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())
        Movement.move(hunter.bot, Movement.Direction.forwards)
        MovementModifier.modify(hunter.bot, MovementModifier.Type.sprint)
        Jump.jump(hunter.bot, Jump.Jump.jump)
        inventoryItems = hunter.action.updateInventory(hunter.bot)
        if RandomGenerator.randomIndexOf(inventoryItems) is not None:
          index = RandomGenerator.randomIndexOf(inventoryItems)
          item = inventoryItems[index]
          hunter.action.holdItem(hunter.bot, item)
        
      case "halt":
        hunter.action.look(hunter.bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())
        Movement.move(hunter.bot, Movement.Direction.none)
        MovementModifier.modify(hunter.bot, MovementModifier.Type.none)
        Jump.jump(hunter.bot, Jump.Jump.none)
        inventoryItems = hunter.action.updateInventory(hunter.bot)
        if RandomGenerator.randomIndexOf(inventoryItems) is not None:
          index = RandomGenerator.randomIndexOf(inventoryItems)
          item = inventoryItems[index]
          hunter.action.holdItem(hunter.bot, item)

      case 'look':
        hunter.action.look(hunter.bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())

      case "inventory":
        inventoryItems = hunter.action.updateInventory(hunter.bot)
        print("Inventory is", inventoryItems)
      case "dig":
        blocksInMemory.append(hunter.bot.blockAtCursor())
        index = RandomGenerator.randomIndexOf(blocksInMemory)
        if index is not None:
          print('yeee!')
          blockIndex = len(blocksInMemory) - 1
          block = blocksInMemory[blockIndex]
          hunter.action.dig(hunter.bot, block, True, 'rayCast')
      case 'place':
        block = hunter.action.getCurrentlyLookedAtBlock(hunter.bot)
        blocksInMemory.append(block)
        face = {'x' : 0, 'y' : 1, 'z' : 0}
        try:
          hunter.action.place(hunter.bot, block, face)
        except:
          try:
            hunter.bot.chat('I couldn\'t place a block next to ' + block.displayName)
          except:
            hunter.bot.chat('I couldn\'t place a block, there\'s no block in memory to place it next to')

      case 'activate':
        block = hunter.action.getCurrentlyLookedAtBlock(hunter.bot, blocksInMemory)
        blocksInMemory.append(block)
        hunter.bot.activateBlock(block)
        
      case "current block":
        block = hunter.action.getCurrentlyLookedAtBlock(hunter.bot, blocksInMemory)
        blocksInMemory.append(block)
        print('Block is', block)

      case 'attack':
        entity = hunter.action.getEntityFromMemory(entitiesInMemory)
        if entity is not None:
          hunter.action.attack(hunter.bot, entity)
        else:
          hunter.bot.chat('There\'s no entity in memory for me to attack!')

      case 'nearest':
        entity = hunter.action.getNearestEntity(hunter.bot)
        entitiesInMemory.append(entity)

      case 'position':
        entity = hunter.action.getNearestEntity(hunter.bot)
        entitiesInMemory.append(entity)
        positionOfEnemyInMemory = hunter.action.getPositionOfEnemyPlayer(entity, positionOfEnemyInMemory)

      case 'held':
        entity = hunter.action.getNearestEntity(hunter.bot)
        entitiesInMemory.append(entity)
        item = hunter.action.getHeldItemOfEnemyPlayer(entity)

      case 'time':
        currentTimeOfDay = hunter.action.getTimeOfDay(hunter.bot)
        print('Time of day is' + str(currentTimeOfDay))
      
      case 'use':
        hunter.action.activateHeldItem(hunter.bot, False)

      case 'hold':
        if RandomGenerator.randomIndexOf(inventoryItems) is not None:
          index = RandomGenerator.randomIndexOf(inventoryItems)
          item = inventoryItems[index]
          hunter.action.holdItem(hunter.bot, item)

@On(hunter.bot, 'playerCollect')
def handlePlayerCollect(this, collector, collected):
  global inventoryItems
  if collector.username == hunter.bot.username:
    hunter.bot.chat("I collected an item!")
    inventoryItems = hunter.action.updateInventory(hunter.bot)


@On(hunter.bot, 'health')
def handle(*args):
  global currentHealth, currentHunger
  currentHealth = hunter.bot.health
  currentHunger = hunter.bot.food
  hunter.bot.chat('My health is' + str(currentHealth))
  hunter.bot.chat('My hunger is' + str(currentHunger))