import glfw
from OpenGL.GL import *
import ShaderLoader
import numpy
import pyrr
from PIL import Image
from sys import getsizeof
import struct
import scalar_data
import data1
import data
import math
import dem
import House_Data
# -global data-------------------------------------------------------------------------------------------------

# window
w_width, w_height = 800, 600

# bufory


#globalne przełączniki

LIGHT_SOURCE = False
SUN = True
TEMPERATURE = False
WIND = False

drawSun = False
drawSphere = False
drawTemperature = False
drawHouse = False
terrainHypso = False

genTemperature = True
if genTemperature: import tempData

genSphere = True
if genSphere:
    import sphere1
    from ObjLoader import *

genHouse = True
if genHouse:
    import House_Data



vaoTerrain = 0
vaoTemperature = 1
vaoSphere = 2
vaoHouse = 3
vaoSun = 4


#DANE TERENU
vboTerrain = data1.vertexData
iboTerrain = data1.indexData
minmax = data1.minmaxT(data1.heights)
terrainCenter = [data1.minX + 0.5 * (data1.maxX - data1.minX), data1.minY + 0.5 * (data1.maxY - data1.minY),
                 minmax[0] + 0.5 * (minmax[1] - minmax[0])]


#DANE ŹRÓDŁA PUNKTOWEGO
lightPos = pyrr.Vector4([terrainCenter[0], terrainCenter[1], minmax[1] + terrainCenter[2], 1.0])
spotLightDir = pyrr.Vector4([0.0, 0.0, 1.0, 1.0])
spotLightAngle = 60.0
lightForce = 1.0



#DANE ŚWIATŁA SŁONECZNEGO
LightDir = pyrr.Vector3([0.0, 0.0, 1.0])#potem podmienić na funkcję
InvWavelength = pyrr.Vector3([(1/0.650)**4, (1/0.570)**4, (1/0.475)**4])
CameraHeight = 0.5
CameraHeight2=0.25
OuterRadius=10.25
OuterRadius2=OuterRadius**2
InnerRadius=10.0
InnerRadius2=100.0
KrESun=0.0025*20.0
KmESun=0.0010*20.0
Kr4PI=KrESun*4.0*math.pi
Km4PI=KmESun*4.0*math.pi
Scale=1.0/(OuterRadius-InnerRadius)
ScaleOverScaleDepth=0.25
FrontColor = pyrr.Vector3([1.0,1.0,1.0])
#FrontColorUnif = [0.0,0.0,0.0]
#ColorToSphere = pyrr.Vector4([0.0, 0.0, 0.0, 0.0])


#DANE KAMERY
g_fzFar = 500000.0
g_fzNear = 0.1
g_fYAngle = 0.0
g_fXAngle = 0.0
g_camTarget = pyrr.Vector3([terrainCenter[0], terrainCenter[1], terrainCenter[2]])
g_sphereCamRelPos = pyrr.Vector3([45, 55, 550])  # In spherical coordinates

#GLOBALNE ADRESY UNIFORM
lightPosUnif = 0
spotLightDirUnif = 0
spotLightAngleUnif = 0
lightForceUnif = 0
lightUnif = 0
terrainHypsoUnif = 0


#PROGRAMY
programTerrain = 0
programTemperature = 0
programSphere = 0


def DegToRad(alpha):
    return alpha * math.pi / 180.0


def ResolveCamPosition():
    phi = DegToRad(g_sphereCamRelPos[0])
    theta = DegToRad(g_sphereCamRelPos[1] + 0.0)

    fSinTheta = math.sin(theta)
    fCosTheta = math.cos(theta)
    fCosPhi = math.cos(phi)
    fSinPhi = math.sin(phi)

    dirToCamera = pyrr.Vector3([fSinTheta * fCosPhi, fSinTheta * fSinPhi, fCosTheta])

    return dirToCamera * g_sphereCamRelPos[2] + g_camTarget


def CalcLookAtMatrix(cameraPt, lookPt, upPt):
    lookDir = pyrr.vector.normalize(lookPt - cameraPt)
    upDir = pyrr.vector.normalize(upPt)

    rightDir = pyrr.vector.normalize(pyrr.vector3.cross(lookDir, upDir))
    perpUpDir = pyrr.vector3.cross(rightDir, lookDir)

    rotMat = pyrr.Matrix44.identity()

    rotMat[0] = pyrr.Vector4([rightDir[0], rightDir[1], rightDir[2], 0.0])
    rotMat[1] = pyrr.Vector4([perpUpDir[0], perpUpDir[1], perpUpDir[2], 0.0])

    rotMat[2] = pyrr.Vector4([-lookDir[0], -lookDir[1], -lookDir[2], 0.0])

    rotMat = pyrr.Matrix44.transpose(rotMat)

    transMat = pyrr.Matrix44.identity()

    transMat[3] = pyrr.Vector4([-cameraPt[0], -cameraPt[1], -cameraPt[2], 1.0])

    return rotMat * transMat


def setPerspectiveProj(w, h):
    print("element: \n", pyrr.Matrix44.perspective_projection(45.0, w / h, g_fzNear, g_fzFar))
    global macierz
    macierz = pyrr.Matrix44.perspective_projection(45.0, w / h, g_fzNear, g_fzFar)

    t1 = macierz[2][2]
    t2 = macierz[2][3]
    print(t1)
    print(t2)

    return macierz


def setOrthoProj(w, h):
    return pyrr.Matrix44.orthogonal_projection(-2.0 * (w / h), 2.0 * (w / h), -2.0, 2.0, -1.0, 1.0)


def setPointView():
    return CalcLookAtMatrix(ResolveCamPosition(), g_camTarget, [0.0, 0.0, 1.0])


def setParallelView():
    return pyrr.Matrix44.identity()

def setscaledmodelmatrix():
    scale = pyrr.Vector3([100.0, 80.0, 100.0])
    return pyrr.Matrix44.from_scale(scale)

def setModelMatrix():
    return pyrr.Matrix44.identity()


def window_resize(window, width, height):
    glViewport(0, 0, width, height)

def setHouseModelMatrix():
    translation= pyrr.Vector3([4715.0,5055.0,3760.0])
    return pyrr.Matrix44.from_translation(translation)



def MouseEnter(window, entered):
    if entered:
        print("weszło")
    else:
        print("wyszło")


def IfClicked(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            global pos
            pos = glfw.get_cursor_pos(glfw.get_current_context())
            p1 = pos[0]
            p2 = pos[1]
            p1_f = float(p1)
            p2_f = float(p2)
            print("pos1", pos[0])
            print("pos2", pos[1])

            modelMat = setModelMatrix()
            viewMat = setPointView()
            projMat = setPerspectiveProj(w_width, w_height)
            punkt = [0, 0, 1, 1]
            # viewpos = pyrr.matrix44.apply_to_vector(modelMat,punkt)

            worldpos = pyrr.matrix44.apply_to_vector(modelMat, punkt)  # przestrzeń świata
            worldpos1 = []
            for j in range(4):
                temp = 0
                for i in range(4):
                    temp += modelMat[i][j] * punkt[i]
                worldpos1.append(temp)

            viewpos = pyrr.matrix44.apply_to_vector(viewMat, worldpos)
            viewpos1 = []
            for j in range(4):
                temp = 0
                for i in range(4):
                    temp += viewMat[i][j] * worldpos1[i]
                viewpos1.append(temp)

            projpos = pyrr.matrix44.apply_to_vector(projMat, viewpos)
            projpos1 = []
            for j in range(4):
                temp = 0
                for i in range(4):
                    temp += projMat[i][j] * viewpos1[i]
                projpos1.append(temp)

            ndcpos = projpos
            for i in range(4):
                ndcpos[i] /= ndcpos[3]

            windowpos = ndcpos
            for i in range(3):
                windowpos[i] = (windowpos[i] + 1.0) / 2.0

            screenpos = windowpos
            screenpos[0] = screenpos[0] * float(w_width)
            screenpos[1] = screenpos[1] * float(w_height)

            # (p1/w_width)*2 -1

            modelviewMat = pyrr.matrix44.multiply(modelMat, viewMat)
            modelviewprojMat = pyrr.matrix44.multiply(modelviewMat, projMat)
            invmodelviewprojMat = pyrr.matrix44.inverse(modelviewprojMat)
            posmat = pyrr.matrix44.multiply(modelviewprojMat, invmodelviewprojMat)

            ndc = [0.0, 0.0, 0.0, 0.0]

            # from SS to NDC
            ndc[0] = (2.0 * p1_f / w_width) - 1.0

            print('pos0', pos[0])
            print(p1)
            ndc[1] = (2.0 * p2_f / w_height) - 1.0
            ndc[2] = 2.0 * 1.0 - 1.0
            ndc[3] = 1.0

            # clip_w = projMat[3][2] / (-projMat[2][2] / projMat[2][3] + ndc[2])
            clip_w = projMat[2][3] / (-projMat[2][2] / projMat[3][2] + ndc[2])

            clip = [0.0, 0.0, 0.0, 0.0]

            clip[0] = float(ndc[0]) * clip_w
            clip[1] = float(ndc[1]) * clip_w
            clip[2] = float(ndc[1]) * clip_w
            clip[3] = float(ndc[2]) * clip_w

            pos1 = []

            for j in range(4):
                temp = 0
                for i in range(4):
                    temp += invmodelviewprojMat[i][j] * clip[i]
                pos1.append(temp)

            pos1[3] = 1.0 / pos1[3]

            pos1[0] *= pos1[3]
            pos1[1] *= pos1[3]
            pos1[2] *= pos1[3]

            print(pos1[0], pos1[1], pos1[2])

            print("lewy_wcisniety")
        else:
            if action == glfw.RELEASE:
                print("lewy puszczony")

    else:
        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                pos1 = glfw.get_cursor_pos(glfw.get_current_context())
                print(pos1)
                print("prawy_wcisniety")
            else:
                if action == glfw.RELEASE:
                    print("prawy puszczony")




def keyCallback(window, key, scancode, action, mods):
    global lightForce
    global FrontColor
    global KrESun

    if action == glfw.PRESS:
        if key == glfw.KEY_T:
            global drawTemperature
            drawTemperature = not drawTemperature

        if key == glfw.KEY_S:
            global drawSphere
            drawSphere = not drawSphere

        if key == glfw.KEY_L:
            global LIGHT_SOURCE
            LIGHT_SOURCE = not LIGHT_SOURCE

        if key == glfw.KEY_H:
            global drawHouse
            drawHouse = not drawHouse

        if key == glfw.KEY_1:
            global terrainHypso
            terrainHypso = not terrainHypso

        if key == glfw.KEY_M:
            KrESun -= 0.1

        if key == glfw.KEY_N:
            KrESun += 0.1

    if action == glfw.REPEAT:

        if LIGHT_SOURCE:
            if key == glfw.KEY_A:
                lightPos[0] -= 10

            if key == glfw.KEY_D:
                lightPos[0] += 10

            if key == glfw.KEY_W:
                lightPos[1] += 10

            if key == glfw.KEY_Z:
                lightPos[1] -= 10

            if key == glfw.KEY_X:
                lightPos[2] -= 100

            if key == glfw.KEY_E:
                lightPos[2] += 100

            if key == glfw.KEY_RIGHT_BRACKET:
                lightForce += 0.1

            if key == glfw.KEY_LEFT_BRACKET:
                lightForce -= 0.1





        if key == glfw.KEY_UP:
            g_sphereCamRelPos[2] -= 100

        if key == glfw.KEY_DOWN:
            g_sphereCamRelPos[2] += 100

        if key == glfw.KEY_LEFT:
            g_sphereCamRelPos[0] -= 10

        if key == glfw.KEY_RIGHT:
            g_sphereCamRelPos[0] += 10

        if key == glfw.KEY_U:
            g_sphereCamRelPos[1] += 2

        if key == glfw.KEY_I:
            g_sphereCamRelPos[1] -= 2

        if key == glfw.KEY_F4:
            FrontColor[0] += 0.1
        if key == glfw.KEY_F5:
            FrontColor[1] += 0.1
        if key == glfw.KEY_F6:
            FrontColor[2] += 0.1
        if key == glfw.KEY_F1:
            FrontColor[0] -= 0.1
        if key == glfw.KEY_F2:
            FrontColor[1] -= 0.1
        if key == glfw.KEY_F3:
            FrontColor[2] -= 0.1




def initWindow():
    if not glfw.init():
        return

    w_width, w_height = 800, 600

    # glfw.window_hint(glfw.RESIZABLE, GL_FALSE)

    window = glfw.create_window(w_width, w_height, "My OpenGL window", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # callbacks
    glfw.set_window_size_callback(window, window_resize)
    glfw.set_key_callback(window, keyCallback)
    #    glfw.set_cursor_pos_callback(window, GetMousePosition)
    glfw.set_cursor_enter_callback(window, MouseEnter)
    glfw.set_mouse_button_callback(window, IfClicked)

    return window


def initTerrain():
    # VBO
    # vboDataGL = (GLfloat * len(vboData))(*vboData)
    global vaoTerrain
    vaoTerrain = glGenVertexArrays(1)
    glBindVertexArray(vaoTerrain)

    vboDataGL = numpy.array(vboTerrain, dtype=numpy.float32)

    print(vboDataGL)
    vbo = glGenBuffers(1)

    # print(sizeof(vboDataGL))
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, getsizeof(vboDataGL), vboDataGL, GL_STATIC_DRAW)

    # IBO
    # iboDataGL = (GLuint * len(iboData))(*iboData)

    iboDataGL = numpy.array(iboTerrain, dtype=numpy.uint32)
    ibo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, getsizeof(iboDataGL), iboDataGL, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(16))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(32))

    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(48))

    glBindVertexArray(0)


def initTemperature():
    global vaoTemperature
    global iboTemperature
    a = round(dem.maxX)
    dataIndex = 0
    temperatury = tempData.sampleData(tempData.loadData('temperatura.png'), a, 10)
    borders = {'dim1': [data.minX, data.maxX], 'dim2': [data.minY, data.maxY]}
    iboTemperature = scalar_data.createIndexData(borders, [temperatury[1], temperatury[2]])
    sampleDensity = [temperatury[1], temperatury[2]]
    vboTemperature = scalar_data.createVertexDataOpenGL(borders, sampleDensity, temperatury[0],
                                                        ColorPattern=scalar_data.colorTab,
                                                        HeightRange=tempData.minandmax)

    vaoTemperature = glGenVertexArrays(1)
    glBindVertexArray(vaoTemperature)

    vboDataGL1 = numpy.array(vboTemperature, dtype=numpy.float32)

    print(vboDataGL1)
    vbo1 = glGenBuffers(1)

    # print(sizeof(vboDataGL))
    glBindBuffer(GL_ARRAY_BUFFER, vbo1)
    glBufferData(GL_ARRAY_BUFFER, getsizeof(vboDataGL1), vboDataGL1, GL_STATIC_DRAW)

    # IBO
    # iboDataGL = (GLuint * len(iboData))(*iboData)

    iboDataGL1 = numpy.array(iboTemperature, dtype=numpy.uint32)
    ibo1 = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo1)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, getsizeof(iboDataGL1), iboDataGL1, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(16))

    glBindVertexArray(0)

def initSphere():
    global vaoSphere
    global iboSphere
    # VBO
    vboSphere = sphere1.sphereVBO(50002,50, 50,inwards = False)
    iboSphere = sphere1.sphereIBO(50002,50, 50,inwards = False)
    #vboDataGL = (GLfloat * len(vboData))(*vboData)
    vaoSphere = glGenVertexArrays(1)
    glBindVertexArray(vaoSphere)

    vboDataGL2 = numpy.array(vboSphere, dtype=numpy.float32)
    print(vboDataGL2)
    vbo2 = glGenBuffers(1)

    #print(sizeof(vboDataGL))
    glBindBuffer(GL_ARRAY_BUFFER, vbo2)
    glBufferData(GL_ARRAY_BUFFER, getsizeof(vboDataGL2), vboDataGL2, GL_STATIC_DRAW)

    # IBO
    #iboDataGL = (GLuint * len(iboData))(*iboData)
    iboDataGL2 = numpy.array(iboSphere, dtype=numpy.uint32)
    ibo2 = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo2)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, getsizeof(iboDataGL2), iboDataGL2, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(16))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(32))



def initHouse():
    global vaoHouse
    global iboHouse
    vboHouse = House_Data.vbo_add()[0]
    iboHouse = House_Data.ibo_add()[0]

    vaoHouse = glGenVertexArrays(1)
    glBindVertexArray(vaoHouse)

    vboDataGL3 = numpy.array(vboHouse, dtype=numpy.float32)

    print(vboDataGL3)
    vbo3 = glGenBuffers(1)

    # print(sizeof(vboDataGL))

    glBindBuffer(GL_ARRAY_BUFFER, vbo3)

    glBufferData(GL_ARRAY_BUFFER, getsizeof(vboDataGL3), vboDataGL3, GL_STATIC_DRAW)

    # IBO
    # iboDataGL = (GLuint * len(iboData))(*iboData)

    iboDataGL3 = numpy.array(iboHouse, dtype=numpy.uint32)
    ibo3 = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo3)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, getsizeof(iboDataGL3), iboDataGL3, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(16))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(32))
    glBindVertexArray(0)

def initSun():
    global vaoHouse
    global iboHouse
    vboHouse = House_Data.vbo_add()[0]
    iboHouse = House_Data.ibo_add()[0]

    vaoHouse = glGenVertexArrays(1)
    glBindVertexArray(vaoHouse)

    vboDataGL3 = numpy.array(vboHouse, dtype=numpy.float32)

    print(vboDataGL3)
    vbo3 = glGenBuffers(1)

    # print(sizeof(vboDataGL))

    glBindBuffer(GL_ARRAY_BUFFER, vbo3)

    glBufferData(GL_ARRAY_BUFFER, getsizeof(vboDataGL3), vboDataGL3, GL_STATIC_DRAW)

    # IBO
    # iboDataGL = (GLuint * len(iboData))(*iboData)

    iboDataGL3 = numpy.array(iboHouse, dtype=numpy.uint32)
    ibo3 = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo3)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, getsizeof(iboDataGL3), iboDataGL3, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(16))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 40, ctypes.c_void_p(32))
    glBindVertexArray(0)



def initTexture(shader0,shader1,shader2, name0=None, name1=None, name2=None):
    texture = glGenTextures(3)

    tex0 = glGetUniformLocation(shader0, "tex0")
    glUseProgram(shader0)
    glUniform1i(tex0, 0)

    tex1 = glGetUniformLocation(shader1, "tex1")
    glUseProgram(shader1)
    glUniform1i(tex1, 1)

    tex2 = glGetUniformLocation(shader2, "tex2")
    glUseProgram(shader2)
    glUniform1i(tex2, 2)





    if name0:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture[0])

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # load image
        image = Image.open(name0)
        flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = numpy.array(list(flipped_image.getdata()), numpy.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

    if name1:
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, texture[1])

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # load image
        image = Image.open(name1)
        flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = numpy.array(list(flipped_image.getdata()), numpy.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

    if name2:
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, texture[2])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # load image
        image = Image.open(name2)
        flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = numpy.array(list(flipped_image.getdata()), numpy.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)


def initGL():
    glClearColor(0.9, 0.5, 0.5, 1.0)
    glEnable(GL_DEPTH_TEST)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


def initUniformsTerrain(shader):
    # uniforms getlocation

    # macierze
    modelToWorldMatrix = glGetUniformLocation(shader, "modelToWorldMatrix")
    worldToCameraMatrix = glGetUniformLocation(shader, "worldToCameraMatrix")
    cameraToClipMatrix = glGetUniformLocation(shader, "cameraToClipMatrix")

    # światło
    lightPosUnif = glGetUniformLocation(shader, "worldLightPos")
    spotLightDirUnif = glGetUniformLocation(shader, "spotLightDir")
    spotLightAngleUnif = glGetUniformLocation(shader, "spotLightAngle")
    lightForceUnif = glGetUniformLocation(shader, "lightForce")
    lightUnif = glGetUniformLocation(shader, "light")

    # camera
    worldCamPos = glGetUniformLocation(shader, "worldCamPos")

    #teren
    terrainHypsoUnif = glGetUniformLocation(shader, "terrainHypso")

    # uniforms wysyłka
    # macierze
    glUniformMatrix4fv(modelToWorldMatrix, 1, GL_FALSE, setModelMatrix())
    glUniformMatrix4fv(worldToCameraMatrix, 1, GL_FALSE, setPointView())
    glUniformMatrix4fv(cameraToClipMatrix, 1, GL_FALSE, setPerspectiveProj(w_width, w_height))

    glUniform4fv(spotLightDirUnif, 1, spotLightDir)
    glUniform1f(spotLightAngleUnif, 1.57 * spotLightAngle / 180.0)
    glUniform4fv(lightPosUnif, 1, lightPos)

    # światło
    glUniform4fv(spotLightDirUnif, 1, spotLightDir)
    glUniform1f(spotLightAngleUnif, 1.57 * spotLightAngle / 180.0)
    glUniform4fv(lightPosUnif, 1, lightPos)
    glUniform1f(lightForceUnif, lightForce)
    if LIGHT_SOURCE: glUniform1ui(lightUnif,1)
    else: glUniform1ui(lightUnif,0)
    if terrainHypso: glUniform1ui(terrainHypsoUnif,1)
    else: glUniform1ui(terrainHypsoUnif,0)



    # camera
    camPos = ResolveCamPosition()
    glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]))


def initUniformsTemperature(shader):
    # uniforms getlocation

    # macierze
    modelToWorldMatrix1 = glGetUniformLocation(shader, "modelToWorldMatrix")
    worldToCameraMatrix1 = glGetUniformLocation(shader, "worldToCameraMatrix")
    cameraToClipMatrix1 = glGetUniformLocation(shader, "cameraToClipMatrix")

    # światło
    lightPosUnif = glGetUniformLocation(shader, "worldLightPos")
    spotLightDirUnif = glGetUniformLocation(shader, "spotLightDir")
    spotLightAngleUnif = glGetUniformLocation(shader, "spotLightAngle")
    lightForceUnif = glGetUniformLocation(shader, "lightForce")

    # camera
    worldCamPos = glGetUniformLocation(shader, "worldCamPos")

    # uniforms wysyłka
    # macierze
    glUniformMatrix4fv(modelToWorldMatrix1, 1, GL_FALSE, setModelMatrix())
    glUniformMatrix4fv(worldToCameraMatrix1, 1, GL_FALSE, setPointView())
    glUniformMatrix4fv(cameraToClipMatrix1, 1, GL_FALSE, setPerspectiveProj(w_width, w_height))

    glUniform4fv(spotLightDirUnif, 1, spotLightDir)
    glUniform1f(spotLightAngleUnif, 1.57 * spotLightAngle / 180.0)
    glUniform4fv(lightPosUnif, 1, lightPos)

    # światło
    glUniform4fv(spotLightDirUnif, 1, spotLightDir)
    glUniform1f(spotLightAngleUnif, 1.57 * spotLightAngle / 180.0)
    glUniform4fv(lightPosUnif, 1, lightPos)
    glUniform1f(lightForceUnif, lightForce)

    # camera
    camPos = ResolveCamPosition()
    glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]))

def initUniformsSphere(shader):
    # uniforms getlocation

    # macierze
    modelToWorldMatrix1 = glGetUniformLocation(shader, "modelToWorldMatrix")
    worldToCameraMatrix1 = glGetUniformLocation(shader, "worldToCameraMatrix")
    cameraToClipMatrix1 = glGetUniformLocation(shader, "cameraToClipMatrix")

    # światło
    lightPosUnif = glGetUniformLocation(shader, "worldLightPos")
    spotLightDirUnif = glGetUniformLocation(shader, "spotLightDir")
    spotLightAngleUnif = glGetUniformLocation(shader, "spotLightAngle")
    lightForceUnif = glGetUniformLocation(shader, "lightForce")

    sunDirUnif = glGetUniformLocation(shader, "LightDir")
    InvWavelengthUnif = glGetUniformLocation(shader, "InvWavelength")
    CameraHeightUnif = glGetUniformLocation(shader, "CameraHeight")
    CameraHeight2Unif = glGetUniformLocation(shader, "CameraHeight2")
    OuterRadiusUnif = glGetUniformLocation(shader, "OuterRadius")
    OuterRadius2Unif = glGetUniformLocation(shader, "OuterRadius2")
    InnerRadiusUnif = glGetUniformLocation(shader, "InnerRadius")
    InnerRadius2Unif = glGetUniformLocation(shader, "InnerRadius2")
    KrESunUnif = glGetUniformLocation(shader, "KrESun")
    KmESunUnif = glGetUniformLocation(shader, "KmESun")
    Kr4PIUnif = glGetUniformLocation(shader, "Kr4PI")
    ScaleUnif = glGetUniformLocation(shader, "Scale")
    ScaleOverScaleDepthUnif = glGetUniformLocation(shader, "ScaleOverScaleDepth")
    FrontColorUnif = glGetUniformLocation(shader, "FrontColor")
    # camera
    worldCamPos = glGetUniformLocation(shader, "worldCamPos")

    # uniforms wysyłka
    # macierze
    glUniformMatrix4fv(modelToWorldMatrix1, 1, GL_FALSE, setModelMatrix())
    glUniformMatrix4fv(worldToCameraMatrix1, 1, GL_FALSE, setPointView())
    glUniformMatrix4fv(cameraToClipMatrix1, 1, GL_FALSE, setPerspectiveProj(w_width, w_height))

    glUniform4fv(spotLightDirUnif, 1, spotLightDir)
    glUniform1f(spotLightAngleUnif, 1.57 * spotLightAngle / 180.0)
    glUniform4fv(lightPosUnif, 1, lightPos)

    glUniform3fv(sunDirUnif, 1, LightDir)
    glUniform3fv(InvWavelengthUnif, 1, InvWavelength)
    glUniform1f(CameraHeightUnif, CameraHeight)
    glUniform1f(CameraHeight2Unif, CameraHeight2)
    glUniform1f(OuterRadiusUnif, OuterRadius)
    glUniform1f(OuterRadius2Unif, OuterRadius2)
    glUniform1f(InnerRadiusUnif, InnerRadius)
    glUniform1f(InnerRadius2Unif, InnerRadius2)
    glUniform1f(KrESunUnif, KrESun)
    glUniform1f(KmESunUnif, KmESun)
    glUniform1f(Kr4PIUnif, Kr4PI)
    glUniform1f(ScaleUnif, Scale)
    glUniform1f(ScaleOverScaleDepthUnif, ScaleOverScaleDepth)
    # światło
    glUniform4fv(spotLightDirUnif, 1, spotLightDir)
    glUniform1f(spotLightAngleUnif, 1.57 * spotLightAngle / 180.0)
    glUniform4fv(lightPosUnif, 1, lightPos)
    glUniform1f(lightForceUnif, lightForce)
    glUniform3fv(FrontColorUnif,1, FrontColor)

    # camera
    camPos = ResolveCamPosition()
    glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]))



def initUniformsHouse(shader):
    # uniforms getlocation

        # macierze
    modelToWorldMatrix1 = glGetUniformLocation(shader, "modelToWorldMatrix")
    worldToCameraMatrix1 = glGetUniformLocation(shader, "worldToCameraMatrix")
    cameraToClipMatrix1 = glGetUniformLocation(shader, "cameraToClipMatrix")

        # światło
    lightPosUnif = glGetUniformLocation(shader, "worldLightPos")
    spotLightDirUnif = glGetUniformLocation(shader, "spotLightDir")
    spotLightAngleUnif = glGetUniformLocation(shader, "spotLightAngle")
    lightForceUnif = glGetUniformLocation(shader, "lightForce")

    #camera
    worldCamPos = glGetUniformLocation(shader, "worldCamPos")

    # uniforms wysyłka
        # macierze
    glUniformMatrix4fv(modelToWorldMatrix1, 1, GL_FALSE, setHouseModelMatrix()*setscaledmodelmatrix())
    #glUniformMatrix4fv(modelToWorldMatrix2, 1, GL_FALSE, )
    glUniformMatrix4fv(worldToCameraMatrix1, 1, GL_FALSE, setPointView())
    glUniformMatrix4fv(cameraToClipMatrix1, 1, GL_FALSE, setPerspectiveProj(w_width, w_height))

    glUniform4fv(spotLightDirUnif, 1, spotLightDir)
    glUniform1f(spotLightAngleUnif, 1.57 * spotLightAngle / 180.0)
    glUniform4fv(lightPosUnif, 1, lightPos)

         # światło
    glUniform4fv(spotLightDirUnif, 1, spotLightDir)
    glUniform1f(spotLightAngleUnif, 1.57 * spotLightAngle / 180.0)
    glUniform4fv(lightPosUnif, 1, lightPos)
    glUniform1f(lightForceUnif, lightForce)

        #camera
    camPos = ResolveCamPosition()
    glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]) )



def main():
    window = initWindow()

    programTerrain = ShaderLoader.compile_shader("terrain.vert", "terrain.frag")
    programTemperature = ShaderLoader.compile_shader("temperature.vert", "temperature.frag")
    programSphere = ShaderLoader.compile_shader("sphere.vert", "sphere.frag")
    programHouse = ShaderLoader.compile_shader("house.vert", "house.frag")
    programSun = ShaderLoader.compile_shader("sun.vert", "sun.frag")

    initTerrain()
    if genTemperature:
        initTemperature()
    if genSphere:
        initSphere()

    if genHouse:

        initHouse()

    initGL()

    glBindVertexArray(vaoTerrain)
    glUseProgram(programTerrain)



    """
    bindedTextures = glGetIntegerv( GL_TEXTURE_BINDING_2D )
    activeTextures = glGetIntegerv(GL_ACTIVE_TEXTURE)

    powyzsze wartosci razem  pozwalają sprawdzić, które teksturt są aktywne i podłączone:
    można to wykorzystać do przekazania do sahdera dodatkowej daneje uniform i jej testowania w kodzie shadera
    pozwala to napisać kod wariantowy, używający adekwatnej ilości tekstur 
    """

    initUniformsTerrain(programTerrain)
    #initTexture(programTerrain, "textura_terenu.jpg")
    glUseProgram(programHouse)
    initUniformsHouse(programHouse)
   # initTexture(programHouse, "textury_domu.jpg")
    glUseProgram(programTemperature)
    initUniformsTemperature(programTemperature)
    glUseProgram(programSphere)
   # initTexture(programSphere, "sky.jpg", "textury_domu.jpg")
    initUniformsSphere(programSphere)

    initTexture(programTerrain,programHouse,programSphere, "ter.jpg","textury_domu.jpg","sky2.jpg")


  #  glUseProgram(programTerrain)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glBindVertexArray(vaoTerrain)
        glUseProgram(programTerrain)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glEnable(GL_DEPTH_TEST)

        # glDisable(GL_CULL_FACE)
        # glFrontFace(GL_CCW)
        # glCullFace(GL_BACK)

        if LIGHT_SOURCE:
            lightPosUnif = glGetUniformLocation(programTerrain, "worldLightPos")
            lightUnif = glGetUniformLocation(programTerrain, "light")
            lightForceUnif = glGetUniformLocation(programTerrain, "lightForce")
            glUniform1ui(lightUnif, 1)
            glUniform4fv(lightPosUnif, 1, lightPos)
            glUniform1f(lightForceUnif, lightForce)

        else:
            lightUnif = glGetUniformLocation(programTerrain, "light")
            glUniform1ui(lightUnif, 0)

        if terrainHypso:
            terrainHypsoUnif = glGetUniformLocation(programTerrain, "terrainHypso")
            glUniform1ui(terrainHypsoUnif, 1)
        else:
            terrainHypsoUnif = glGetUniformLocation(programTerrain, "terrainHypso")
            glUniform1ui(terrainHypsoUnif, 0)

        worldCamPos = glGetUniformLocation(programTerrain, "worldCamPos")

        worldToCameraMatrix = glGetUniformLocation(programTerrain, "worldToCameraMatrix")

        camPos = ResolveCamPosition()
        glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]))
        glUniformMatrix4fv(worldToCameraMatrix, 1, GL_FALSE, setPointView())

        glDrawElements(GL_TRIANGLES, len(iboTerrain), GL_UNSIGNED_INT, None)

        if drawSun:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glBindVertexArray(vaoSun)
            glUseProgram(programSun)

            worldCamPos = glGetUniformLocation(programSun, "worldCamPos")

            worldToCameraMatrix = glGetUniformLocation(programSun, "worldToCameraMatrix")

            camPos = ResolveCamPosition()
            glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]))
            glUniformMatrix4fv(worldToCameraMatrix, 1, GL_FALSE, setPointView())

            glDrawElements(GL_TRIANGLES, len(iboSphere), GL_UNSIGNED_INT, None)


        if drawSphere:

            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glBindVertexArray(vaoSphere)
            glUseProgram(programSphere)
            lightForceUnif = glGetUniformLocation(programSphere, "lightForce")
            glUniform1f(lightForceUnif, lightForce)

            FrontColorUnif = glGetUniformLocation(programSphere, "FrontColor")
            glUniform3fv(FrontColorUnif,1, FrontColor)


            worldCamPos = glGetUniformLocation(programSphere, "worldCamPos")

            worldToCameraMatrix = glGetUniformLocation(programSphere, "worldToCameraMatrix")

            camPos = ResolveCamPosition()
            glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]))
            glUniformMatrix4fv(worldToCameraMatrix, 1, GL_FALSE, setPointView())

            glDrawElements(GL_TRIANGLES, len(iboSphere), GL_UNSIGNED_INT, None)



        if drawTemperature:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glBindVertexArray(vaoTemperature)
            glUseProgram(programTemperature)

            worldCamPos = glGetUniformLocation(programTemperature, "worldCamPos")

            worldToCameraMatrix = glGetUniformLocation(programTemperature, "worldToCameraMatrix")

            camPos = ResolveCamPosition()
            glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]))
            glUniformMatrix4fv(worldToCameraMatrix, 1, GL_FALSE, setPointView())

            glDrawElements(GL_TRIANGLES, len(iboTemperature), GL_UNSIGNED_INT, None)


        if drawHouse:

            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            glBindVertexArray(vaoHouse)

            glUseProgram(programHouse)

            worldCamPos = glGetUniformLocation(programHouse, "worldCamPos")

            worldToCameraMatrix = glGetUniformLocation(programHouse, "worldToCameraMatrix")

            camPos = ResolveCamPosition()
            glUniform4fv(worldCamPos, 1, pyrr.Vector4([camPos[0], camPos[1], camPos[2], 1.0]))
            glUniformMatrix4fv(worldToCameraMatrix, 1, GL_FALSE, setPointView())

            glDrawElements(GL_TRIANGLES, len(iboHouse), GL_UNSIGNED_INT, None)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()