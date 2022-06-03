import math
import random

class RandomGenerator:
    def randomYaw():
        return random.uniform(0,6.28)

    def randomPitch():
        return random.uniform(-math.pi/2,math.pi/2)

    def randomIndexOf(list):
        if not list:
            return None
        return int(round(random.uniform(0,len(list) - 1), 0))