from javascript import require, On
mineflayer = require('/Users/iakalann/node_modules/mineflayer')

class HunterAction:

  def getNearestEntity(self, currentBot):
    entity = currentBot.nearestEntity(lambda entity: entity.name == 'RoyalCentaur')
    return entity

  def getPositionOfEnemyPlayer(self, entity):
    position = entity.position
    positionAsVec3 = {'x' : position.x, 'y' : position.y, 'z' : position.z}
    print('Position is', positionAsVec3)
    return positionAsVec3

  def holdItem(self, currentBot, item):
    currentBot.equip(item)

  def getHeldItemOfEnemyPlayer(self, entity):
    print('Held item is', entity.heldItem)
    return entity.heldItem

  def attack(self, currentBot, entityToAttack):
    currentBot.attack(entityToAttack)

  def getEntityFromMemory(self, entitiesInMemory):
    if len(entitiesInMemory) is not 0:
      index = len(entitiesInMemory) -1
      entity = entitiesInMemory[index]
      return entity
    return None

  def getCurrentlyLookedAtBlock(self, currentBot):
    return currentBot.blockAtCursor()

  def look(self, currentBot, yaw, pitch):
    currentBot.look(yaw, pitch, True)

  def updateInventory(self, currentBot):
    items = []
    for item in currentBot.inventory.items():
      items.append(item)
    return items

  def activateHeldItem(self, currentBot, offHand):
    currentBot.activateItem(offHand)

  def place(self, currentBot, block, face):
    currentBot.placeBlock(block, face)

  def dig(self, currentBot, block, forceLook, digFace):
    currentBot.dig(block, forceLook, digFace)
  
  def getTimeOfDay(currentBot):
    return currentBot.time.timeOfDay