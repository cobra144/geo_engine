from osgeo import gdal
import numpy
import struct
import sys
import math

src_ds = gdal.Open( "karkonosze.tif" )
if src_ds is None:
    print ('Unable to open INPUT.tif')
    sys.exit(1)

print ("[ RASTER BAND COUNT ]: ", src_ds.RasterCount)
for band in range( src_ds.RasterCount ):
    band += 1
    print ("[ GETTING BAND ]: ", band)
    srcband = src_ds.GetRasterBand(band)
    if srcband is None:
        continue

    stats = srcband.GetStatistics( True, True )
    if stats is None:
        continue

    print ("[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % ( \
                stats[0], stats[1], stats[2], stats[3] ))

    print ("[ MIN ] = ", srcband.GetMinimum())
    print ("[ MAX ] = ", srcband.GetMaximum())
    geoTransform = src_ds.GetGeoTransform()
    minX = geoTransform[0]
    maxY = geoTransform[3]
    maxX = minX + geoTransform[1] * src_ds.RasterXSize
    minY = maxY + geoTransform[5] * src_ds.RasterYSize
    print("minX:",minX)
    print("maxY",maxY)
    print("minY",minY)
    print("maxX",maxX)
    arcx=15.989166666666668-15.384166666666667
    arcy=50.98541666666666-50.467638888888885
    alfa=math.pi*(maxX-minX/2)/180.0
    r=6378*math.cos(alfa)

    delta_arc_x=1000*(2.0*math.pi)*r/360.0
    delta_arc_y=1000*(2.0*math.pi)*6378/360
    minx=minX*delta_arc_x
    maxx=maxX*delta_arc_x
    miny=minY*delta_arc_y
    maxy=maxY*delta_arc_y
    wymiar_terenu=delta_arc_x*arcx
    print(delta_arc_x)
    print(r)
    print(arcx)
    print(arcy)
    print(wymiar_terenu)
    width = src_ds.RasterXSize
    height = src_ds.RasterYSize
    print(width)
    print(height)

    print(minx)
    print(maxx)
    print(miny)
    print(maxy)

    roznicay=maxy-miny
    roznicax=maxx-minx
    print(roznicax)
    print(roznicay)
horizontalScale = 1000
verticalScale = 1.0



import struct

srtm = gdal.Open( "nepal.tif", gdal.GA_ReadOnly )

band = srtm.GetRasterBand(1)
heights = []
step = 1
for i in range (0,band.YSize):
    if i%step==0:
        scanline = band.ReadRaster(xoff=0, yoff=0,xsize=band.XSize, ysize=i,buf_xsize=band.XSize, buf_ysize=1,buf_type=gdal.GDT_Float32)
        tuple_of_floats = struct.unpack('f' * srtm.RasterXSize, scanline)
        #m1 = min(tuple_of_floats)
        #m2 = max(tuple_of_floats)

        dane = []
        for j in range(band.XSize//step):
            h = verticalScale*tuple_of_floats[j*step]
            dane.append(h)
        heights.append(dane)
        #print (tuple_of_floats)






nX = 800
nY = 800
tX = 1
tY = 1
subData = []
for i in range(tX,tX+nX):
    row = []
    for j in range(tY,tY+nY):
        row.append(1.0*heights[i][j])
    subData.append(row)

hX = (maxx-minx)/(band.XSize)
hY = (maxy-miny)/(band.YSize)

subDataMinX = tX*hX
subDataMaxX = (tX+nX)*hX
subDataMinY = tY*hY
subDataMaxY = (tY+nY)*hY

