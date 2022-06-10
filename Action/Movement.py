from enum import Enum

class Direction(Enum):
  none = 0
  forwards = 1
  backwards = 2
  left = 3
  right = 4
  forwardLeft = 5
  forwardRight = 6
  backwardLeft = 7
  backwardRight = 8

def move(currentBot, movement):
  currentBot.setControlState('forward', movement is Direction.forwards or movement is Direction.forwardLeft or movement is Direction.forwardRight)
  currentBot.setControlState('back', movement is Direction.backwards or movement is Direction.backwardLeft or movement is Direction.backwardRight)
  currentBot.setControlState('left', movement is Direction.left or movement is Direction.forwardLeft or movement is Direction.backwardLeft)
  currentBot.setControlState('right', movement is Direction.right or movement is Direction.forwardRight or movement is Direction.backwardRight)