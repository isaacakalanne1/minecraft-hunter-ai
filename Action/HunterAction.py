from javascript import require, On
mineflayer = require('/Users/iakalann/node_modules/mineflayer')

class HunterAction:

  def getHeldItemOfEnemyPlayer(self, entity):
    print('Held item is', entity.heldItem)
    return entity.heldItem

  def updateInventory(self, currentBot):
    items = []
    for item in currentBot.inventory.items():
      items.append(item)
    return items