from javascript import require, On
from enum import Enum
Vec3 = require('vec3')

class BlockFace(Enum):
  front = Vec3(-1, 0, 0)
  back = Vec3(1, 0, 0)
  left = Vec3(0, 0, -1)
  right = Vec3(0, 0, 1)
  bottom = Vec3(0, -1, 0)
  top = Vec3(0, 1, 0)