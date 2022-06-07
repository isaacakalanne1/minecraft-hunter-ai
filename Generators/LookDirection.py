import math
from javascript import require, On
Vec3 = require('vec3')

def getLookDirectionsAround(yaw, pitch, fieldOfView, resolution):
    csYaw = math.cos(yaw)
    snYaw = math.sin(yaw)
    csPitch = math.cos(pitch)
    snPitch = math.sin(pitch)
    x = -snYaw * csPitch
    y = snPitch
    z = -csYaw * csPitch
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