# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 22:48:37 2017

@author: fraktal
"""

import numpy as np
import copy
import conf
import math

#import windData

# POCZĄTEK ZMIAN
import tempData


import data1

# heights = tempData.temperatury[0]



# sizeX = tempData.temperatury[1]
# sizeY = tempData.temperatury[2]




# ilosci probek w poziomie i pionie, łacznie z brzegowymi




# borders = {'dim1': [minX, maxX], 'dim2': [minY, maxY]}

# sampleDensity = [sizeX, sizeY]

# Reszta bedzie obliczana

colors = [[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]

demColors = [[i / 255, i / 255, i / 255] for i in range(256)]
"""demColors = []
type(heights)
heights = np.asarray(heights)
for i in range(heights):
    for j in range(heights[i]):
        if 5>heights[i][j]:
            demColors.append([30, 92, 179])
        else :
            demColors.append([255, 255, 255])"""


# texCoord = [0.0,0.0, 0.5,0.0, 1.0,0.0, 0.0,0.5, 0.5,0.5, 1.0,0.5,  0.0,1.0, 0.5,1.0, 1.0,1.0]
# texCoord = []
# texHX = (1.0-0.0)/(sizeX-1)
# texHY = (1.0-0.0)/(sizeY-1)

# KONIEC ZMIAN

# for i in range(sizeY):
#    for j in range(sizeX):
#        texCoord.append(j*texHX)# współrzędna x
#        texCoord.append(i * texHY) # współrzędna y

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



import windData
size = windData.size
colorTab = windData.colorTab

minR = math.sqrt(windData.data[0][0][0][0] ** 2 + windData.data[0][0][0][0] ** 2 + windData.data[0][0][0][2] ** 2)
maxR= minR

for i in range(size[0]):
        for j in range(size[1]):
            for k in range(size[2]):
                scale = math.sqrt(windData.data[i][j][k][0]**2+windData.data[i][j][k][1]**2+windData.data[i][j][k][2]**2)
                if scale > maxR: maxR = scale
                if scale < minR : minR = scale

lengthRange = [minR, maxR]  # minmaxT(tempData.temperatury)




# colorTab = tempData.colorTab_1

def calculateVectorColor(length, colorTab, lengthRange):
    """
    zwraca błąd gdy height jest poza zakresem heightRange
    """
    if length < lengthRange[0]:
        length = lengthRange[0]
    else:
        if length > lengthRange[1]:
            length = lengthRange[1]
    scale = (length - lengthRange[0]) / (lengthRange[1] - lengthRange[0])
    colorIndex = int(scale * (len(colorTab) - 1))  # od 0 do 17
    return colorTab[colorIndex]




def fieldVectorVBO(posRange,fieldVectors,sampleDensity, Colors,ColorPattern,LengthRange):
    '''

    :param posRange: fielsBorders [xmin,xmax,ymin,ymax,zmin,zmax]
    :param fieldVectors: 3D tab
    :param sampleDensity: number of points, X, Y, Z
    :param Colors: 3D tab
    :param ColorPattern:
    :param LengthRange:
    :return:
    '''

    hX = (posRange[1]-posRange[0])/(sampleDensity[0]-1)
    hY = (posRange[3]-posRange[2])/ (sampleDensity[1] - 1)
    hZ = (posRange[5] - posRange[4]) / (sampleDensity[2] - 1)

    vec = []
    for i in range(sampleDensity[0]):
        for j in range(sampleDensity[1]):
            for k in range(sampleDensity[2]):
                scale = math.sqrt(fieldVectors[i][j][k][0]**2+fieldVectors[i][j][k][1]**2+fieldVectors[i][j][k][2]**2)
                p0 = [posRange[0]+i*hX,posRange[2]+j*hY,posRange[4]+k*hZ]
                p1 = [p0[0]+fieldVectors[i][j][k][0],p0[1]+fieldVectors[i][j][k][1],p0[2]+fieldVectors[i][j][k][2]]
                ps = [p0[0]+0.5*(p1[0]-p0[0]),p0[1]+0.5*(p1[1]-p0[1]) , p0[2]+0.5*(p1[2]-p0[2])]
                q = [ 0.001*(p1[1]-ps[1])+ps[0], 0.001*(p1[0]-ps[0])+ps[1], 0.0 ]
                t = [q[0]-ps[0], q[1]-ps[1],q[2]-ps[2] ]
                r = [ps[0]-t[0],ps[1]-t[1],ps[2]-t[2]]

                vec.append(p0[0])
                vec.append(p0[1])
                vec.append(p0[2]+ data1.HeightRange[1])
                vec.append(1.0)
                if Colors:
                    vec.append(Colors[i][j][k][0])
                    vec.append(Colors[i][j][k][1])
                    vec.append(Colors[i][j][k][2])
                    vec.append(1.0)
                else:
                    if ColorPattern and LengthRange:
                        c = calculateVectorColor(scale, ColorPattern, LengthRange)
                        vec.append(c[0])
                        vec.append(c[1])
                        vec.append(c[2])
                        vec.append(1.0)

                vec.append(p1[0])
                vec.append(p1[1])
                vec.append(p1[2]+ data1.HeightRange[1])
                vec.append(1.0)
                if Colors:
                    vec.append(Colors[i][j][k][0])
                    vec.append(Colors[i][j][k][1])
                    vec.append(Colors[i][j][k][2])
                    vec.append(1.0)
                else:
                        vec.append(c[0])
                        vec.append(c[1])
                        vec.append(c[2])
                        vec.append(1.0)

                '''
                vec.append(p1[0])
                vec.append(p1[1])
                vec.append(p1[2] + data1.HeightRange[1])
                vec.append(1.0)
                if Colors:
                    vec.append(Colors[i][j][k][0])
                    vec.append(Colors[i][j][k][1])
                    vec.append(Colors[i][j][k][2])
                    vec.append(1.0)
                else:
                    vec.append(c[0])
                    vec.append(c[1])
                    vec.append(c[2])
                    vec.append(1.0)

                vec.append(q[0])
                vec.append(q[1])
                vec.append(q[2] + data1.HeightRange[1])
                vec.append(1.0)
                if Colors:
                    vec.append(Colors[i][j][k][0])
                    vec.append(Colors[i][j][k][1])
                    vec.append(Colors[i][j][k][2])
                    vec.append(1.0)
                else:
                    vec.append(c[0])
                    vec.append(c[1])
                    vec.append(c[2])
                    vec.append(1.0)


                vec.append(p1[0])
                vec.append(p1[1])
                vec.append(p1[2] + data1.HeightRange[1])
                vec.append(1.0)
                if Colors:
                    vec.append(Colors[i][j][k][0])
                    vec.append(Colors[i][j][k][1])
                    vec.append(Colors[i][j][k][2])
                    vec.append(1.0)
                else:
                    vec.append(c[0])
                    vec.append(c[1])
                    vec.append(c[2])
                    vec.append(1.0)

                vec.append(r[0])
                vec.append(r[1])
                vec.append(r[2] + data1.HeightRange[1])
                vec.append(1.0)
                if Colors:
                    vec.append(Colors[i][j][k][0])
                    vec.append(Colors[i][j][k][1])
                    vec.append(Colors[i][j][k][2])
                    vec.append(1.0)
                else:
                    vec.append(c[0])
                    vec.append(c[1])
                    vec.append(c[2])
                    vec.append(1.0)

                '''

    return vec



def createIndexData(Borders, sampleDensity):
    indices = []
    for i in range(sampleDensity[0]):
        for j in range(sampleDensity[1]):
            for k in range(sampleDensity[2]):
                indices.append(i*sampleDensity[1]*sampleDensity[2]+j*sampleDensity[1]+k)
                indices.append((i + 1) * sampleDensity[0] + (j + 1))


    # Utworzone  wektory pakujemy do tablicy

    return indices

#if __name__ == '__main__':
#vertexData = fieldVectorVBO([windData.terrainMinX,windData.terrainMaxX,windData.terrainMinY,windData.terrainMaxY,windData.minZ,windData.maxZ] ,windData.data,size, None,colorTab,lengthRange)
#print(vertexData)