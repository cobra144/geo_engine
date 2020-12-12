from osgeo import gdal
import numpy
import struct
import sys
import math
import dem
from PIL import Image

import data1

dataSources = [

    ['source_1', [[30./255, 92./255, 179./255],
            [23./255,111./255, 193./255],
            [11./255, 142./255,216./255],
            [4./255,161./255,  230./255],
            [25./255,181./255, 241./255],
            [51./255,188./255, 207./255],
            [102./255,204./255,206./255],
            [153./255,219./255,184./255],
            [192./255,229./255,136./255],
            [204./255,230./255, 75./255],
            [243./255,240./255, 29./255],
            [254./255,222./255, 39./255],
            [252./255,199./255,  7./255],
            [248./255,157./255, 14./255],
            [245./255,114./255, 21./255],
            [241./255, 71./255, 28./255],
            [219./255, 30./255, 38./255],
            [164./255, 38./255, 44./255]],[0.0,30.0]]

]



def loadData(name):
    im=Image.open(name)
    rgb_im = im.convert('RGB')
    ld = im.load()
    return [rgb_im,im.size]
    #print(width)
    #print(height)



def sampleData(image,scale,step):
    XSize = 0
    YSize = 0

    temperatury = []
    step = 10
    vScale = 20
    hOffset = data1.HeightRange[1]


    min = 0

    for y in range(image[1][1]):
        if (y) % step == 0 or y == 0 or y == (image[1][0] - 1):
            row = []
            YSize += 1
            for x in range(image[1][0]):
                if (x) % step == 0 or x == 0 or x == (image[1][0] - 1):
                    # r, g, b = rgb_im.getpixel((x, y))
                    img = image[0].getpixel((x, y))
                    # r,g,b = ld[x,y]
                    if img[0] < min: min = img[0]
                    # mean_px = (r + g + b) / 3
                    # lista=list(img)
                    row.append(img[0])
                    # print(img[0])
                    if y == 0: XSize += 1

            temperatury.append(row)


    for y in range(len(temperatury)):
        for x in range(len(temperatury[0])):
            temperatury[y][x] = (temperatury[y][x]-min)*vScale+hOffset

    return [temperatury,XSize,YSize]

tempy=sampleData(loadData('temperatura.png'), round(dem.maxX), 10)[0]




def minmaxT(heights):
    min = heights[0][0]
    max = heights[0][0]
    for i in range(len(heights)):
        for j in range(len(heights[0])):
            if (heights[i][j] < min):
                min = heights[i][j]
            else:
                if (heights[i][j] > max): max = heights[i][j]

    return [min, max]

minandmax=minmaxT(tempy)

