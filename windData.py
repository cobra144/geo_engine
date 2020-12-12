import conf
import random

terrainMinX = conf.minX
terrainMinY = conf.minY
terrainMaxX = conf.maxX
terrainMaxY = conf.maxY
minZ = 0
maxZ = 500

colorTab = [[30. / 255, 92. / 255, 179. / 255],
            [23. / 255, 111. / 255, 193. / 255],
            [11. / 255, 142. / 255, 216. / 255],
            [4. / 255, 161. / 255, 230. / 255],
            [25. / 255, 181. / 255, 241. / 255],
            [51. / 255, 188. / 255, 207. / 255],
            [102. / 255, 204. / 255, 206. / 255],
            [153. / 255, 219. / 255, 184. / 255],
            [192. / 255, 229. / 255, 136. / 255],
            [204. / 255, 230. / 255, 75. / 255],
            [243. / 255, 240. / 255, 29. / 255],
            [254. / 255, 222. / 255, 39. / 255],
            [252. / 255, 199. / 255, 7. / 255],
            [248. / 255, 157. / 255, 14. / 255],
            [245. / 255, 114. / 255, 21. / 255],
            [241. / 255, 71. / 255, 28. / 255],
            [219. / 255, 30. / 255, 38. / 255],
            [164. / 255, 38. / 255, 44. / 255]]

size = [10,10,10]

hX=(terrainMaxX-terrainMinX)/(size[0]-1)
hY=(terrainMaxY-terrainMinY)/(size[1]-1)
hZ=(maxZ-minZ)/(size[2]-1)

data = []
for i in range(size[0]):
    slice = []
    for j in range(size[1]):
        row = []
        for k in range(size[2]):
            #row.append([200.0,0.0, 200.0])
            row.append([random.randrange(100, 300),random.randrange(100, 150),random.randrange(0, 20)])
        slice.append(row)
    data.append(slice)

print(data)
