from enum import Enum

class Direction(Enum):
  forwards = 0
  forwardLeft = 1
  forwardRight = 2
  backwards = 3
  left = 4
  right = 5
  backwardLeft = 6
  backwardRight = 7
  none = 8

def move(currentBot, movement):
  currentBot.setControlState('forward', movement is Direction.forwards or movement is Direction.forwardLeft or movement is Direction.forwardRight)
  currentBot.setControlState('back', movement is Direction.backwards or movement is Direction.backwardLeft or movement is Direction.backwardRight)
  currentBot.setControlState('left', movement is Direction.left or movement is Direction.forwardLeft or movement is Direction.backwardLeft)
  currentBot.setControlState('right', movement is Direction.right or movement is Direction.forwardRight or movement is Direction.backwardRight)