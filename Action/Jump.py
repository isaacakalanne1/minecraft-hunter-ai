from enum import Enum

class Jump(Enum):
  none = 0
  jump = 1

def jump(currentBot, jump):
  currentBot.setControlState('jump', jump is Jump.jump)