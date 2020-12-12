# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 22:48:37 2017

@author: fraktal
"""

import numpy as np
import copy

# POCZĄTEK ZMIAN
import dem

subData = True

minX = -(dem.maxx - dem.minx) / 2
maxX = (dem.maxx - dem.minx) / 2
minY = -(dem.maxy - dem.miny) / 2
maxY = (dem.maxy - dem.miny) / 2

sizeX = dem.band.XSize
sizeY = dem.band.YSize

heights = dem.heights

if subData:
    minX = -(dem.subDataMaxX - dem.subDataMinX) / 2
    maxX = (dem.subDataMaxX - dem.subDataMinX) / 2
    minY = -(dem.subDataMaxY - dem.subDataMinY) / 2
    maxY = (dem.subDataMaxY - dem.subDataMinY) / 2
    sizeX = dem.nX
    sizeY = dem.nY
    heights = dem.subData

# ilosci probek w poziomie i pionie, łacznie z brzegowymi




borders = {'dim1': [minX, maxX], 'dim2': [minY, maxY]}

sampleDensity = [sizeX, sizeY]

# Reszta bedzie obliczana

colors = [[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]

demColors = [[i / 255, i / 255, i / 255] for i in range(256)]

# texCoord = [0.0,0.0, 0.5,0.0, 1.0,0.0, 0.0,0.5, 0.5,0.5, 1.0,0.5,  0.0,1.0, 0.5,1.0, 1.0,1.0]
texCoord = []
texHX = (1.0 - 0.0) / (sizeX - 1)
texHY = (1.0 - 0.0) / (sizeY - 1)

# KONIEC ZMIAN

for i in range(sizeY):
    for j in range(sizeX):
        texCoord.append(j * texHX)  # współrzędna x
        texCoord.append(i * texHY)  # współrzędna y


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


HeightRange = minmaxT(heights)

HypsoColors = [
    [50, 136, 189],
    [102, 194, 165],
    [171, 221, 164],
    [230, 245, 152],
    [255, 255, 191],
    [253, 174, 97],
    [244, 109, 67],
    [213, 62, 79]
]


def calculateDemColor(height, colorTab, heightRange):
    """
    zwraca błąd gdy height jest poza zakresem heightRange
    """
    if height < heightRange[0] or height > heightRange[1]:
        return 0
    else:
        scale = (height - heightRange[0]) / (heightRange[1] - heightRange[0])
        colorIndex = int(scale * (len(colorTab) - 1))
        return colorTab[colorIndex]


def calculateNormal(p1, p2, p3):
    """
    p1,p2,p3 tworzą układ prawoskrętny
    """
    P1 = np.array(p1)
    P2 = np.array(p2)
    P3 = np.array(p3)
    n1 = np.add(P2, -P1)
    n2 = np.add(P3, -P1)
    n = np.cross(n1, n2)
    return n / np.linalg.norm(n)


def createVertexDataTabular(Borders, SampleDensity, Heights):
    """
    Decydujemy się na przechowanie próbek (x,y,z) w trzech niezależnych
    strukturach jednowymiarowych, czyli w przypadku języka R strukturach
    wektorowych ( konstruktor c()  ). Przyjmujemy ich nazwy jako:
    xData, yData, zData
    """

    # Dla prostoty  obliczamy odległości pomiędzy dwoma kolejnymi
    # próbkami w kierunkach X oraz Y i oznaczamy je przez hX oraz hY

    hX = (Borders['dim1'][1] - Borders['dim1'][0]) / (SampleDensity[0] - 1)
    hY = (Borders['dim2'][1] - Borders['dim2'][0]) / (SampleDensity[1] - 1)

    temp = [Borders['dim1'][0] + i * hX for i in range(SampleDensity[0])]
    xData = copy.copy(temp)
    for i in range(SampleDensity[1] - 1): xData += temp

    yData = []
    for i in range(sizeY):
        temp = [Borders['dim2'][0] + i * hY for k in range(SampleDensity[0])]
        yData += temp

    zData = []
    for i in range(len(Heights)):
        for j in range(len(Heights[0])):
            zData.append(Heights[i][j])

    return {'X': xData, 'Y': yData, 'Z': zData}


def createVertexDataOpenGL(Borders, SampleDensity, Heights, Colors=None, ColorPattern=None, HeightRange=None,
                           Normals=None, TexCoord=None):
    """
    Decydujemy się na przechowanie próbek (x,y,z) w
    jednej strukturze liniowej, dodając czwartą wspołrzędną
    Zakładamy, że Colors jest listą trojek: (r,g,b) zapisanych w postaci list 3-elementowych
    Podobnie dla TexCoords - w tym przypadku dopuszczamy rzutowanie perspektywiczne tekstury
    """

    # Dla prostoty  obliczamy odległości pomiędzy dwoma kolejnymi
    # próbkami w kierunkach X oraz Y i oznaczamy je przez hX oraz hY

    hX = (Borders['dim1'][1] - Borders['dim1'][0]) / (SampleDensity[0] - 1)
    hY = (Borders['dim2'][1] - Borders['dim2'][0]) / (SampleDensity[1] - 1)

    temp = [Borders['dim1'][0] + i * hX for i in range(SampleDensity[0])]
    xData = copy.copy(temp)
    for i in range(SampleDensity[1] - 1): xData += temp

    yData = []
    for i in range(sizeY):
        temp = [Borders['dim2'][0] + i * hY for k in range(SampleDensity[1])]
        yData += temp

    zData = []
    for i in range(len(Heights)):
        for j in range(len(Heights[0])):
            zData.append(Heights[i][j])

    oglData = []

    for i in range(len(xData)):
        oglData.append(xData[i])
        oglData.append(yData[i])
        oglData.append(zData[i])
        oglData.append(1.0)
        if Colors:
            oglData.append(Colors[i][0] / 255.0)
            oglData.append(Colors[i][1] / 255.0)
            oglData.append(Colors[i][2] / 255.0)
            oglData.append(1.0)
        else:
            if ColorPattern and HeightRange:
                c = calculateDemColor(zData[i], ColorPattern, HeightRange)
                oglData.append(c[0] / 255.0)
                oglData.append(c[1] / 255.0)
                oglData.append(c[2] / 255.0)
                oglData.append(1.0)
        if Normals:
            if i == 0:
                w1 = [xData[i], yData[i], zData[i]]
                w2 = [xData[i + SampleDensity[0] + 1], yData[i + SampleDensity[0] + 1], zData[i + SampleDensity[0] + 1]]
                w3 = [xData[i + SampleDensity[0]], yData[i + SampleDensity[0]], zData[i + SampleDensity[0]]]
            else:
                if i % sampleDensity[0] != sampleDensity[0] - 1 and i < (sampleDensity[1] - 1) * sampleDensity[0]:
                    w1 = [xData[i], yData[i], zData[i]]
                    w2 = [xData[i + SampleDensity[0] + 1], yData[i + SampleDensity[0] + 1],
                          zData[i + SampleDensity[0] + 1]]
                    w3 = [xData[i + SampleDensity[0]], yData[i + SampleDensity[0]], zData[i + SampleDensity[0]]]
                else:
                    if i % sampleDensity[0] == sampleDensity[0] - 1 and i < (sampleDensity[1] - 1) * sampleDensity[
                        0]:  # prawa kolumna
                        w1 = [xData[i - 1], yData[i - 1], zData[i - 1]]
                        w2 = [xData[i], yData[i], zData[i]]
                        w3 = [xData[i + SampleDensity[0]], yData[i + SampleDensity[0]], zData[i + SampleDensity[0]]]
                    else:  # górny wiersz
                        if i != (SampleDensity[0] - 1) * SampleDensity[1] + SampleDensity[0] - 1:
                            w1 = [xData[i - SampleDensity[0]], yData[i - SampleDensity[0]], zData[i - SampleDensity[0]]]
                            w2 = [xData[i + 1], yData[i + 1], zData[i + 1]]
                            w3 = [xData[i], yData[i], zData[i]]
                        else:  # prawy górny
                            w1 = [xData[i - SampleDensity[0] - 1], yData[i - SampleDensity[0] - 1],
                                  zData[i - SampleDensity[0] - 1]]
                            w2 = [xData[i], yData[i], zData[i]]
                            w3 = [xData[i - 1], yData[i - 1], zData[i - 1]]
            n = calculateNormal(w1, w2, w3)
            oglData.append(n[0])
            oglData.append(n[1])
            oglData.append(n[2])
            oglData.append(1.0)
        if TexCoord:
            oglData.append(TexCoord[2 * i])
            oglData.append(TexCoord[2 * i + 1])
            # oglData.append(TexCoord[i][2])
            # oglData.append(TexCoord[i][3])
    return oglData


# Budujemy strukturę trójkątów

# Każdy trójkąt zapisujemy w postaci 3 indeksów
# tablic xData, yData, zData, czyli numerów
# wierzchołków zapisanych w tych tablicach

# Przyjmując prawoskrętny układ współrzędnych XYZ oraz prawoskrętną
# orientację każdego trójkąta otrzymujemy następujące konkluzje

# j=0...sizeX-1 - kolumna = X
# i=0...sizeY-1 - wiersz = Y

# dwa trójkąty w oczku siatki o numerze (i,j) - lewy dolny narożnik
# trójkąt1_i_j = [(i,j), (i+1,j+1), (i+1,j)]
# trójkąt2_i_j = [(i,j), (i,j+1), (i+1,j+1)]

# lista trójkątów: lista par (trojkat1_i_j,trojkat2_i_j), i=0...sizeX-2, j=0...sizeY-2
# ilość trójkątów w jednym wierszu siatki: 2*(sizeX-1)
# sumaryczna ilość trójkątów: (sizeY-1)*2*(sizeX-1)

# Pierwsza wersja struktury trójkątów - wektor trójek indeksów wierzchołków
# Ozn. ten wektor przez indexData


def createIndexDataTabular(Borders, SampleDensity):
    indexFirst = []
    for i in range(SampleDensity[1]):
        for j in range(SampleDensity[0]):
            indexFirst.append((i) * SampleDensity[0] + j + 1)
            indexFirst.append((i) * SampleDensity[0] + j + 1)

    indexSecond = []
    for i in range(SampleDensity[1]):
        for j in range(SampleDensity[0]):
            indexSecond.append((i + 1) * SampleDensity[0] + j + 2)
            indexSecond.append((i) * SampleDensity[0] + j + 2)

    indexThird = []
    for i in range(SampleDensity[1]):
        for j in range(SampleDensity[0]):
            indexThird.append((i + 1) * SampleDensity[0] + j + 1)
            indexThird.append((i + 1) * SampleDensity[0] + j + 2)

    # Utworzone  wektory pakujemy do listy o nazwie indexData1 z polami: first, second, third

    return {'first': indexFirst, 'second': indexSecond, 'third': indexThird}


def createIndexData(Borders, SampleDensity):
    indices = []
    for i in range(SampleDensity[1] - 1):  # wiersze
        for j in range(SampleDensity[0] - 1):  # kolumny
            indices.append(i * SampleDensity[0] + j)
            indices.append((i + 1) * SampleDensity[0] + (j + 1))
            indices.append((i + 1) * SampleDensity[0] + (j))
            indices.append((i) * SampleDensity[0] + (j))
            indices.append((i) * SampleDensity[0] + (j + 1))
            indices.append((i + 1) * SampleDensity[0] + (j + 1))

    # Utworzone  wektory pakujemy do tablicy

    return indices


# if __name__ == '__main__':
#   vertexDataTabular = createVertexDataTabular(borders, sampleDensity, heights)
indexData = createIndexData(borders, sampleDensity)
vertexData = createVertexDataOpenGL(borders, sampleDensity, heights, ColorPattern=HypsoColors,
                                    HeightRange=minmaxT(heights), Normals=True, TexCoord=texCoord)
for i in range(9):
    print(vertexData[i * 14:(i + 1) * 14])
print(" ")
for i in range(8):
    print(indexData[i * 3:(i + 1) * 3])
# normalData = createNormalData(borders, sampleDensity)


