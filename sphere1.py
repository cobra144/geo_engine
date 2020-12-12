from math import sin, cos, pi




def sphereVBO(radius,latSectors, longSectors,inwards = False):
    """
        longSectors jest parzyste
        x = radius * cos(phi) * cos(theta)
        y = radius * sin(phi)* cos(theta)
        z = radius * sin(theta)
        phi in [0,2*pi]
        theta in [-pi/2, pi/2]
        DeltaPhi = 2*pi /latSectors
        phi_j = j * DeltaPhi, j=0,1,..., latSectors
        DeltaTheta = pi /longSectors
        theta_i = -pi/2 + i * DeltaTheta, i=0,1,..., longSectors
    """
    
    DeltaPhi = 2*pi /latSectors
    DeltaTheta = pi /longSectors
    
    vbo = []
    
    s = 1.0
    if inwards: s = -1.0
    
    #biegun S
    #position
    vbo.append(0.0)
    vbo.append(0.0)
    vbo.append(-radius)
    vbo.append(1.0)
    #normal
    vbo.append(0.0)
    vbo.append(0.0)
    vbo.append(-1.0*s)
    vbo.append(1.0)
    #texCoord
    vbo.append(0.5)
    vbo.append(0.0)
    

    #pomiędzy
    for i in  range(1,longSectors):
        theta = -pi/2 + i * DeltaTheta 
        for j  in  range(latSectors):
            phi = j * DeltaPhi
            x = cos(phi) * cos(theta)
            y = sin(phi) * cos(theta)
            z = sin(theta)
            
            #positions
            vbo.append(radius*x)
            vbo.append(radius*y)
            vbo.append(radius*z)
            vbo.append(1.0)
            
            #normals
            vbo.append(s*x)
            vbo.append(s*y)
            vbo.append(s*z)
            vbo.append(1.0)
            
            #texCoordsS
            u = phi / (2*pi)
            v = theta/pi + 0.5 
            vbo.append(u)
            vbo.append(v)
    
    #biegun N
    #position
    vbo.append(0.0)
    vbo.append(0.0)
    vbo.append(radius)
    vbo.append(1.0)
    #normal
    vbo.append(0.0)
    vbo.append(0.0)
    vbo.append(1.0*s)
    vbo.append(1.0)
    #texCoord
    vbo.append(0.5)
    vbo.append(1.0)
    
    return vbo


def sphereIBO(radius,latSectors, longSectors,inwards = False):
    """
        longSectors jest parzyste
        x = radius * cos(phi) * cos(theta)
        y = radius * sin(phi)* cos(theta)
        z = radius * sin(theta)
        phi in [0,2*pi]
        theta in [-pi/2, pi/2]
        DeltaPhi = 2*pi /latSectors
        phi_j = j * DeltaPhi, j=0,1,..., latSectors
        DeltaTheta = pi /longSectors
        theta_i = -pi/2 + i * DeltaTheta, i=0,1,..., longSectors
        PRAWOSKRĘTNIE
    """
    
    ibo = []
    #czapa S
    for j in range(1,latSectors):
        ibo.append(0)
        ibo.append(j+1)
        ibo.append(j)
    ibo.append(0)
    ibo.append(1)
    ibo.append(latSectors)
    
    #pomiędzy na S
    for i in range(longSectors//2-1):
        for j in range(1,latSectors):
            ibo.append(i*(latSectors)+j)
            ibo.append(i*(latSectors)+j+1)
            ibo.append((i+1)*(latSectors)+j)
              
            ibo.append(i*(latSectors)+j+1)
            ibo.append((i+1)*(latSectors)+j+1)
            ibo.append((i+1)*(latSectors)+j)
        ibo.append((i+1)*latSectors)
        ibo.append((i+1)*(latSectors)+1)
        ibo.append((i+2)*(latSectors))
        
        ibo.append((i+1)*latSectors)
        ibo.append(i*(latSectors)+1)
        ibo.append((i+1)*(latSectors)+1)
     #pomiędzy na N
    for i in range(longSectors//2-1,longSectors-2):
        for j in range(1,latSectors):
            ibo.append(i*(latSectors)+j)
            ibo.append(i*(latSectors)+j+1)
            ibo.append((i+1)*(latSectors)+j)
              
            ibo.append(i*(latSectors)+j+1)
            ibo.append((i+1)*(latSectors)+j+1)
            ibo.append((i+1)*(latSectors)+j)
            
        ibo.append((i+1)*latSectors)
        ibo.append((i+1)*(latSectors)+1)
        ibo.append((i+2)*(latSectors))
        
        ibo.append((i+1)*latSectors)
        ibo.append(i*(latSectors)+1)
        ibo.append((i+1)*(latSectors)+1)
    
    
    #czapa N
    nVert = latSectors*(longSectors-1)+2
    for j in range(2,latSectors+1):
        ibo.append(nVert-1)
        ibo.append(nVert-j-1)
        ibo.append(nVert-j)
    ibo.append(nVert-1)
    ibo.append(nVert-2)
    ibo.append(nVert-latSectors-1)
              
        
    return ibo   
        
vbo = sphereVBO(2.0,4,4)
VBO = [round(x,2) for x in vbo]
print(VBO[0:10])
for i  in range(13):
    print(VBO[10+i*10:10+(i+1)*10])
print(VBO[len(vbo)-10:])

ibo = sphereIBO(2.0,4,4)
    