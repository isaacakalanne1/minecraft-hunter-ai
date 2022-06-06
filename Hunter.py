from javascript import require, On
import Action.Movement as Movement
import Action.MovementModifier as MovementModifier
import Action.Jump as Jump
import Action.HunterAction as HunterAction
import Generators.RandomGenerator as RandomGenerator
import Generators.LookDirection as LookDirection

mineflayer = require('/Users/iakalann/node_modules/mineflayer')
Vec3 = require('vec3')

class Hunter:
  # Will need to update inventoryItems to dictionary, like {32 : Item} so AI can access items based on their ID, rather than a raw index

  # Will need to update blocksInMemory to dictionary, like { Vec3{x,y,z} : Block} so AI can access blocks based on their position, rather than a raw index

  def __init__(self, host, port, username):
    self.createBot(host, port, username)
    self.action = HunterAction.HunterAction()
    self.inventoryItems = {}
    self.blocksInMemory = {}
    self.entitiesInMemory = []
    self.positionOfEnemyInMemory = {'x' : 0, 'y' : 0, 'z' : 0}
    self.heldItemOfEnemyInMemory = None
    self.currentHealth = None
    self.currentHunger = None
    self.currentTimeOfDay = None
    self.bot.on('spawn', self.handle)
    self.bot.on('chat', self.handleMsg)
    self.bot.on('playerCollect', self.handlePlayerCollect)
    self.bot.on('health', self.healthUpdated)

  def healthUpdated(self, *args):
    self.currentHealth = self.bot.health
    self.currentHunger = self.bot.food
    self.bot.chat('My health is' + str(self.currentHealth))
    self.bot.chat('My hunger is' + str(self.currentHunger))

  def createBot(self, host, port, username):
    self.bot = mineflayer.createBot({
                  'host': host,
                  'port': port,
                  'username': username
                })
                
  def handle(self, *args):
    print("I spawned 👋")
    self.inventoryItems = self.action.updateInventory(self.bot)

  def handleMsg(self, this, sender, message, *args):
    print("Got message", sender, message)
  
    if sender and (sender != 'HelloThere'):
      self.bot.chat('Hi, you said ' + message)
      match message:
        case "go":
          self.action.look(self.bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())
          Movement.move(self.bot, Movement.Direction.forwards)
          MovementModifier.modify(self.bot, MovementModifier.Type.sprint)
          Jump.jump(self.bot, Jump.Jump.jump)
          self.inventoryItems = self.action.updateInventory(self.bot)
          if RandomGenerator.randomIndexOf(self.inventoryItems) is not None:
            index = RandomGenerator.randomIndexOf(self.inventoryItems)
            item = self.inventoryItems[index]
            self.action.holdItem(self.bot, item)
          
        case "halt":
          self.action.look(self.bot, RandomGenerator.randomYaw(), RandomGenerator.randomPitch())
          Movement.move(self.bot, Movement.Direction.none)
          MovementModifier.modify(self.bot, MovementModifier.Type.none)
          Jump.jump(self.bot, Jump.Jump.none)
          self.inventoryItems = self.action.updateInventory(self.bot)
          if RandomGenerator.randomIndexOf(self.inventoryItems) is not None:
            index = RandomGenerator.randomIndexOf(self.inventoryItems)
            item = self.inventoryItems[index]
            self.action.holdItem(self.bot, item)

        case 'look':
          yaw = RandomGenerator.randomYaw()
          pitch = RandomGenerator.randomPitch()
          self.action.look(self.bot, yaw, pitch)

          directions = LookDirection.getLookDirectionsAround(yaw, pitch, 0.7, 2)
          for direction in directions:
            block = self.getBlockAt(direction)
            if block is not None:
              pos = (block.position.x, block.position.y, block.position.z)
              self.blocksInMemory[pos] = block.type
          print('Blocks are', self.blocksInMemory)

        case "inventory":
          self.inventoryItems = {}
          items = self.action.updateInventory(self.bot)
          for item in items:
            self.inventoryItems[(item.type, item.slot)] = item.count
          print("Inventory is", self.inventoryItems)
        case "dig":
          self.blocksInMemory.append(self.bot.blockAtCursor())
          index = RandomGenerator.randomIndexOf(self.blocksInMemory)
          if index is not None:
            blockIndex = len(self.blocksInMemory) - 1
            block = self.blocksInMemory[blockIndex]
            try:
              self.action.dig(self.bot, block, True, 'rayCast')
            except:
              self.bot.chat('Couldn\'t dig block, there\'s no block to dig')
        case 'place':
          block = self.action.getCurrentlyLookedAtBlock(self.bot)
          self.blocksInMemory.append(block)
          face = {'x' : 0, 'y' : 1, 'z' : 0}
          try:
            self.action.place(self.bot, block, face)
          except:
            try:
              self.bot.chat('I couldn\'t place a block next to ' + block.displayName)
            except:
              self.bot.chat('I couldn\'t place a block, there\'s no block in memory to place it next to')

        case 'activate':
          block = self.action.getCurrentlyLookedAtBlock(self.bot, self.blocksInMemory)
          self.blocksInMemory.append(block)
          self.bot.activateBlock(block)
          
        case "current block":
          block = self.action.getCurrentlyLookedAtBlock(self.bot, self.blocksInMemory)
          self.blocksInMemory.append(block)
          print('Block is', block)

        case 'attack':
          entity = self.action.getEntityFromMemory(self.entitiesInMemory)
          if entity is not None:
            self.action.attack(self.bot, entity)
          else:
            self.bot.chat('There\'s no entity in memory for me to attack!')

        case 'nearest':
          entity = self.action.getNearestEntity(self.bot)
          print('Entity is', entity)
          self.entitiesInMemory.append(entity)

        case 'position':
          entity = self.action.getNearestEntity(self.bot)
          self.entitiesInMemory.append(entity)
          self.positionOfEnemyInMemory = self.action.getPositionOfEnemyPlayer(entity, self.positionOfEnemyInMemory)

        case 'held':
          entity = self.action.getNearestEntity(self.bot)
          self.entitiesInMemory.append(entity)
          item = self.action.getHeldItemOfEnemyPlayer(entity)

        case 'time':
          self.currentTimeOfDay = self.action.getTimeOfDay(self.bot)
          print('Time of day is' + str(self.currentTimeOfDay))
        
        case 'use':
          self.action.activateHeldItem(self.bot, False)

        case 'hold':
          if RandomGenerator.randomIndexOf(self.inventoryItems) is not None:
            index = RandomGenerator.randomIndexOf(self.inventoryItems)
            item = self.inventoryItems[index]
            self.action.holdItem(self.bot, item)

  def handlePlayerCollect(self, this, collector, collected, *args):
    if collector.username == self.bot.username:
      self.bot.chat("I collected an item!")
      self.inventoryItems = self.action.updateInventory(self.bot)

  def handleHealth(self):
    self.currentHealth = self.bot.health
    self.currentHunger = self.bot.food
    self.bot.chat('My health is' + str(self.currentHealth))
    self.bot.chat('My hunger is' + str(self.currentHunger))

  def getEyePositionOfBot(self):
    vecPosition = self.bot.entity.position
    height = self.bot.entity.height
    eyePosition = Vec3(vecPosition.x, vecPosition.y + height, vecPosition.z)
    return eyePosition

  def getBlockAt(self, lookDirection):
    eyePosition = self.getEyePositionOfBot()
    block = self.bot.world.raycast(eyePosition, lookDirection, 160, None)
    return block

hunter = Hunter('localHost', 62217, 'HelloThere')

# It seems like if this listener isn't placed here, the Python file assumes it only needs to run briefly, and stops itself running
@On(hunter.bot, 'eventNeverUsed')
def h(*args):
  pass