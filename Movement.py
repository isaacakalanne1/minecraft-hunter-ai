from enum import Enum

class Direction(Enum):
  none = 0
  forwards = 1
  backwards = 2
  left = 3
  right = 4

def move(currentBot, movement):
  currentBot.setControlState('forward', movement is Direction.forwards)
  currentBot.setControlState('back', movement is Direction.backwards)
  currentBot.setControlState('left', movement is Direction.left)
  currentBot.setControlState('right', movement is Direction.right)