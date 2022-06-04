from javascript import require, On
import Hunter

hunter = Hunter.Hunter('localHost', 54352, 'HelloThere')

# It seems like if this listener isn't placed here, the Python file assumes it only needs to run briefly, and stops itself running
@On(hunter.bot, 'eventNeverUsed')
def h(*args):
  pass