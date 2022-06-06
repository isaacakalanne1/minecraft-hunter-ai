from javascript import require, On
from mcpi_e.minecraft import Minecraft

flyingSquid = require('/Users/iakalann/node_modules/flying-squid')
mc = Minecraft.create('localHost', 25652, 'RoyalCentaur')
pos = mc.player.getPos()

print("pos: x:{},y:{},z:{}".format(pos.x,pos.y,pos.z))
# test = "test"

# flyingSquid.createMCServer({
#   'motd': 'A Minecraft Server \nRunning flying-squid',
#   'port': 25565,
#   'max-players': 10,
#   'online-mode': False,
#   'logging': True,
#   'gameMode': 0,
#   'difficulty': 1,
#   'worldFolder': 'world',
#   'generation': {
#     'name': 'empty',
#     'options': {
#       'worldHeight': 80
#     }
#   },
#   'kickTimeout': 10000,
#   'plugins': {

#   },
#   'modpe': False,
#   'view-distance': 10,
#   'player-list-text': {
#     'header': 'Flying squid',
#     'footer': 'Test server'
#   },
#   'everybody-op': False,
#   'max-entities': 100,
#   'version': '1.18'
# })

# while True:
#     pass