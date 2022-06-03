from javascript import require, On
import Action.Movement as Movement
import Action.MovementModifier as MovementModifier
import Action.Jump as Jump
import Action.HunterAction as HunterAction
import Generators.RandomGenerator as RandomGenerator

mineflayer = require('/Users/iakalann/node_modules/mineflayer')

RandomGenerator = RandomGenerator.RandomGenerator 

BOT_USERNAME = 'HelloThere'
BOT_USERNAME_2 = 'HelloThereMate'
SERVER_HOST = "localHost"
SERVER_PORT = 62022

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
  action = HunterAction.HunterAction()

  global bot
  bot = mineflayer.createBot({
    'host': SERVER_HOST,
    'port': SERVER_PORT,
    'username': BOT_USERNAME
  })

  @On(bot, 'spawn')
  def handle(*args):
    global inventoryItems
    print("I spawned 👋")
    inventoryItems = action.updateInventory(bot)

  @On(bot, 'chat')
  def handleMsg(this, sender, message, *args):
    print("Got message", sender, message)
    global inventoryItems, blocksInMemory, entitiesInMemory, positionOfEnemyInMemory, currentTimeOfDay
    
    if sender and (sender != BOT_USERNAME):
      bot.chat('Hi, you said ' + message)
      match message:
        case "go":
          action.look(bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())
          Movement.move(bot, Movement.Direction.forwards)
          MovementModifier.modify(bot, MovementModifier.Type.sprint)
          Jump.jump(bot, Jump.Jump.jump)
          inventoryItems = action.updateInventory(bot)
          if RandomGenerator.randomIndexOf(inventoryItems) is not None:
            index = RandomGenerator.randomIndexOf(inventoryItems)
            item = inventoryItems[index]
            action.holdItem(bot, item)
          
        case "halt":
          action.look(bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())
          Movement.move(bot, Movement.Direction.none)
          MovementModifier.modify(bot, MovementModifier.Type.none)
          Jump.jump(bot, Jump.Jump.none)
          inventoryItems = action.updateInventory(bot)
          if RandomGenerator.randomIndexOf(inventoryItems) is not None:
            index = RandomGenerator.randomIndexOf(inventoryItems)
            item = inventoryItems[index]
            action.holdItem(bot, item)

        case 'look':
          action.look(bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())

        case "inventory":
          inventoryItems = action.updateInventory(bot)
          print("Inventory is", inventoryItems)
        case "dig":
          blocksInMemory.append(bot.blockAtCursor())
          index = RandomGenerator.randomIndexOf(blocksInMemory)
          if index is not None:
            print('yeee!')
            blockIndex = len(blocksInMemory) - 1
            block = blocksInMemory[blockIndex]
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
          if RandomGenerator.randomIndexOf(inventoryItems) is not None:
            index = RandomGenerator.randomIndexOf(inventoryItems)
            item = inventoryItems[index]
            action.holdItem(bot, item)

  @On(bot, 'playerCollect')
  def handlePlayerCollect(this, collector, collected):
    if collector.username == bot.username:
      bot.chat("I collected an item!")
      inventoryItems = action.updateInventory(bot)


  @On(bot, 'health')
  def handle(*args):
    currentHealth = bot.health
    currentHunger = bot.food
    bot.chat('My health is' + str(currentHealth))
    bot.chat('My hunger is' + str(currentHunger))
  
hunter = Hunter()