import math
from javascript import require, On
Vec3 = require('vec3')

maxYaw = 6.28
maxPitch = math.pi/2

def getLookDirectionOf(yaw, pitch):
    csYaw = math.cos(yaw)
    snYaw = math.sin(yaw)
    csPitch = math.cos(pitch)
    snPitch = math.sin(pitch)
    x = -snYaw * csPitch
    y = snPitch
    z = -csYaw * csPitch
    return [x,y,z]

def getLookDirectionsAround(yaw, pitch, fieldOfView, resolution):
    lookDirection = getLookDirectionOf(yaw, pitch)
    x = lookDirection[0]
    y = lookDirection[1]
    z = lookDirection[2]
    directions = getLookDirectionsAroundDirection(x, y, z, fieldOfView, resolution)
    return directions

def getLookDirectionsAroundDirection(lookX, lookY, lookZ, fieldOfView, resolution):
    lowerX = getLowerBoundOf(lookX, fieldOfView)
    lowerY = getLowerBoundOf(lookY, fieldOfView)
    lowerZ = getLowerBoundOf(lookZ, fieldOfView)
    lookDirections = getLookDirections(lowerX, lowerY, lowerZ, fieldOfView, resolution)
    return lookDirections

def getLowerBoundOf(val, fieldOfView):
    lower = val - fieldOfView/2
    if lower < -1:
        diff = 1 + lower
        lower = -1 - diff
    return lower

def getUpperBoundOf(val, fieldOfView):
    upper = val + fieldOfView
    if upper > 1:
        diff = upper - 1
        upper = 1 - diff
    return upper

def getLookDirections(lowerX, lowerY, lowerZ, fieldOfView, resolution):
    points = []

    xValues = getRangeOfPointValues(lowerX, fieldOfView, resolution)
    yValues = getRangeOfPointValues(lowerY, fieldOfView, resolution)
    zValues = getRangeOfPointValues(lowerZ, fieldOfView, resolution)

    for x in xValues:
        for y in yValues:
            for z in zValues:
                points.append(Vec3(x, y, z))
    return points

def getRangeOfPointValues(lowerPoint, fieldOfView, resolution):
    pointValues = []
    for number in range(1,resolution + 1):
        point = lowerPoint + number*(fieldOfView/resolution)
        if point > 1:
            diff = point - 1
            point = 1 - diff
        if point < -1:
            diff = point + 1
            point = -1 - diff
        pointValues.append(point)
    return pointValues

def getEyePositionOfBot(currentBot):
    vecPosition = currentBot.entity.position
    height = currentBot.entity.height
    eyePosition = Vec3(vecPosition.x, vecPosition.y + height, vecPosition.z)
    return eyePosition

def getBlockAt(currentBot, lookDirection):
    eyePosition = getEyePositionOfBot(currentBot)
    block = currentBot.world.raycast(eyePosition, lookDirection, 160, None)
    return block

def getBlocksInFieldOfView(currentBot, yaw, pitch, fieldOfView, resolution):
    directions = getLookDirectionsAround(yaw, pitch, fieldOfView, resolution)
    blocksInMemory = []
    for direction in directions:
        block = getBlockAt(currentBot, direction)
        if block is not None:
            # blockData = [round(block.position.x, 2), round(block.position.y, 2), round(block.position.z, 2), block.type]
            try:
                distance = currentBot.entity.position.distanceTo(block.position)
                blockData = [distance, block.type]
            except:
                blockData = [0, 0]
        else:
            blockData = [0, 0]
            # blockData = [0.00, 0.00, 0.00, 0.00]
        blocksInMemory += blockData
    return blocksInMemory

def getYaw(multiplier):
    return maxYaw * multiplier

def getYawChange():
    return maxYaw/8

def getPitch(multiplier):
    pitch = (maxPitch*2) * multiplier
    return pitch - (maxPitch)

def getPitchChange():
    return maxPitch/8