from javascript import require, On
from mcpi_e.minecraft import Minecraft

flyingSquid = require('/Users/iakalann/node_modules/flying-squid')
mc = Minecraft.create('localHost', 25652, 'RoyalCentaur')
pos = mc.player.getPos()

print("pos: x:{},y:{},z:{}".format(pos.x,pos.y,pos.z))