from enum import Enum

class Type(Enum):
  none = 0
  sprint = 1
  sneak = 2

def modify(currentBot, movementModifier):
  currentBot.setControlState('sprint', movementModifier is Type.sprint)
  currentBot.setControlState('sneak', movementModifier is Type.sneak)