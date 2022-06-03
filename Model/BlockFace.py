from enum import Enum

class BlockFace(Enum):
  front = {'x' : 0, 'y' : 1, 'z' : 0}
  back = {'x' : 0, 'y' : 1, 'z' : 0}
  left = {'x' : 0, 'y' : 1, 'z' : 0}
  right = {'x' : 0, 'y' : 1, 'z' : 0}
  bottom = {'x' : 0, 'y' : 1, 'z' : 0}
  top = {'x' : 0, 'y' : 1, 'z' : 0}