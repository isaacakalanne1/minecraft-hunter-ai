import math
from javascript import require, On
Vec3 = require('vec3')

def getLookDirectionOf(yaw, pitch):
    csYaw = math.cos(yaw)
    snYaw = math.sin(yaw)
    csPitch = math.cos(pitch)
    snPitch = math.sin(pitch)
    x = -snYaw * csPitch
    y = snPitch
    z = -csYaw * csPitch
    return [x,y,z]

def getYawChange():
    return 6.28 / 8

def getPitchChange():
    return math.pi / 8

def getLookDirectionsAround(yaw, pitch, fieldOfView, resolution):
    lookDirection = getLookDirectionOf(yaw, pitch)
    x = lookDirection[0]
    y = lookDirection[1]
    z = lookDirection[2]
    directions = getLookDirectionsAroundDirection(x, y, z, fieldOfView, resolution)
    return directions

def getMinAndMaxValuesForLookDirection(yaw, pitch, fieldOfView, resolution):

    lookDirection = getLookDirectionOf(yaw, pitch)

    x = lookDirection[0]
    y = lookDirection[1]
    z = lookDirection[2]

    lowerX = getLowerBoundOf(x, fieldOfView)
    lowerY = getLowerBoundOf(y, fieldOfView)
    lowerZ = getLowerBoundOf(z, fieldOfView)

    xValues, yValues, zValues = getRangeOfDirectionValues(lowerX, lowerY, lowerZ, fieldOfView, resolution)
    minX = min(xValues)
    maxX = max(xValues)
    minY = min(yValues)
    maxY = max(yValues)
    minZ = min(zValues)
    maxZ = max(zValues)
    return minX, maxX, minY, maxY, minZ, maxZ

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

def getRangeOfDirectionValues(lowerX, lowerY, lowerZ, fieldOfView, resolution):
    xValues = getRangeOfPointValues(lowerX, fieldOfView, resolution)
    yValues = getRangeOfPointValues(lowerY, fieldOfView, resolution)
    zValues = getRangeOfPointValues(lowerZ, fieldOfView, resolution)
    return xValues, yValues, zValues

def getLookDirections(lowerX, lowerY, lowerZ, fieldOfView, resolution):
    points = []

    xValues, yValues, zValues = getRangeOfDirectionValues(lowerX, lowerY, lowerZ, fieldOfView, resolution)

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
    block = currentBot.world.raycast(eyePosition, lookDirection, 10, None)
    return block


def getBlocksInFieldOfView(currentBot, yaw, pitch, fieldOfView, resolution):
    directions = getLookDirectionsAround(yaw, pitch, fieldOfView, resolution)
    blocksInMemory = []
    for direction in directions:
        blockData = convertDirectionIntoBlockData(currentBot, direction)
        blocksInMemory += blockData
    return blocksInMemory

def convertDirectionIntoBlockData(currentBot, direction):
    block = getBlockAt(currentBot, direction)
    if block is not None:
        try:
            distance = round(currentBot.entity.position.distanceTo(block.position), 1) * 10
            distanceInt = int(distance)
            return [distanceInt, block.type]
        except:
            return [0, 0]
    else:
        return [0, 0]

def getYaw(multiplier):
    return 6.28 * multiplier

def getPitch(multiplier):
    pitch = math.pi * multiplier
    return pitch - (math.pi/2)