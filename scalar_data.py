# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 22:48:37 2017

@author: fraktal
"""

import numpy as np
import copy
import conf
import render_1
#POCZĄTEK ZMIAN
import tempData


terrainMinX = conf.minX
terrainMinY = conf.minY
terrainMaxX = conf.maxX
terrainMaxY = conf.maxY



#heights = tempData.temperatury[0]



#sizeX = tempData.temperatury[1]
#sizeY = tempData.temperatury[2]



#ilosci probek w poziomie i pionie, łacznie z brzegowymi




#borders = {'dim1': [minX, maxX], 'dim2': [minY, maxY]}

#sampleDensity = [sizeX, sizeY]

# Reszta bedzie obliczana

colors =  [[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]

demColors = [[i/255, i/255, i/255] for i in range(256)]
"""demColors = []
type(heights)
heights = np.asarray(heights)
for i in range(heights):
    for j in range(heights[i]):
        if 5>heights[i][j]:
            demColors.append([30, 92, 179])
        else :
            demColors.append([255, 255, 255])"""

#texCoord = [0.0,0.0, 0.5,0.0, 1.0,0.0, 0.0,0.5, 0.5,0.5, 1.0,0.5,  0.0,1.0, 0.5,1.0, 1.0,1.0]
#texCoord = []
#texHX = (1.0-0.0)/(sizeX-1)
#texHY = (1.0-0.0)/(sizeY-1)

#KONIEC ZMIAN

#for i in range(sizeY):
#    for j in range(sizeX):
#        texCoord.append(j*texHX)# współrzędna x
#        texCoord.append(i * texHY) # współrzędna y




HeightRange = [-40,9000]#minmaxT(tempData.temperatury)

colorTab = [[30./255, 92./255, 179./255],
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
            [164./255, 38./255, 44./255]]

TempRange = [-40.0,40.0]#minmaxT(tempData.temperatury)

#colorTab = tempData.colorTab_1

def calculateDemColor(height, colorTab, heightRange):
    """
    zwraca błąd gdy height jest poza zakresem heightRange
    """
    if height < heightRange[0]:
        height = heightRange[0]
    else:
        if height > heightRange[1]:
            height = heightRange[1]
    scale = (height - heightRange[0]) / (heightRange[1] - heightRange[0])
    colorIndex = int(scale * (len(colorTab)-1)) # od 0 do 17
    return colorTab[colorIndex]

def calculateNormal(p1,p2,p3):
    """
    p1,p2,p3 tworzą układ prawoskrętny
    """
    P1 = np.array(p1)
    P2 = np.array(p2)
    P3 = np.array(p3)
    n1 = np.add(P2,-P1)
    n2 = np.add(P3,-P1)
    n = np.cross(n1,n2)
    return n/np.linalg.norm(n)
    
    
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


def createVertexDataOpenGL(Borders, SampleDensity, Heights, Colors=None, ColorPattern=None, HeightRange=None, Normals = None, TexCoord = None):
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
    for i in range(SampleDensity[1]):
        temp = [Borders['dim2'][0] + i * hY for k in range(SampleDensity[0])]
        yData += temp
    print(len(yData))


    print(len(Heights))
    print(len(Heights[0]))
    zData = []
    for i in range(len(Heights)):
        for j in range(len(Heights[0])):
            zData.append(Heights[i][j])

    oglData = []
    print(len(xData))
    for i in range(len(xData)):
        oglData.append(xData[i])
        oglData.append(yData[i])
        oglData.append(zData[i])
        oglData.append(1.0)
        if Colors:
            oglData.append(Colors[i][0])
            oglData.append(Colors[i][1])
            oglData.append(Colors[i][2])
            oglData.append(1.0)
        else:
            if ColorPattern and HeightRange:
                c = calculateDemColor(zData[i], ColorPattern, HeightRange)
                oglData.append(c[0])
                oglData.append(c[1])
                oglData.append(c[2])
                oglData.append(1.0)

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

#if __name__ == '__main__':
 #   vertexDataTabular = createVertexDataTabular(borders, sampleDensity, heights)
