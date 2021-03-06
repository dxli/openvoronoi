import openvoronoi as ovd
import ovdvtk
import time
import vtk
import datetime
import math
import random
import os




def drawLine(myscreen, p1, p2):
    myscreen.addActor( ovdvtk.Line( p1 = (p1.x,p1.y,0), p2=(p2.x,p2.y,0), color = ovdvtk.yellow ) )

def writeFrame( w2if, lwr, nframe ):
    w2if.Modified() 
    current_dir = os.getcwd()
    filename = current_dir + "/frames/frame"+ ('%05d' % nframe)+".png"
    lwr.SetFileName( filename )
    lwr.Write()

def regularGridGenerators(far, Nmax):
    # REGULAR GRID
    rows = int(math.sqrt(Nmax))
    print "rows= ",rows
    gpos=[-0.7*far ,  1.4*far/float(rows-1) ]  # start, stride
    plist = []
    for n in range(rows):
        for m in range(rows):
            x=gpos[0]+gpos[1]*n
            y=gpos[0]+gpos[1]*m
            # rotation
            #alfa = 0
            #xt=x
            #yt=y
            #x = xt*math.cos(alfa)-yt*math.sin(alfa)
            #y = xt*math.sin(alfa)+yt*math.cos(alfa)
            plist.append( ovd.Point(x,y) )
    random.shuffle(plist)
    return plist

def randomGenerators(far, Nmax):
    pradius = (1.0/math.sqrt(2))*far
    plist=[]
    for n in range(Nmax):
        x=-pradius+2*pradius*random.random()
        y=-pradius+2*pradius*random.random()
        plist.append( ovd.Point(x,y) )
    return plist
    
def circleGenerators(far, Nmax):
    # POINTS ON A CIRCLE
    #"""
    #cpos=[50,50]
    #npts = 100
    dalfa= float(2*math.pi)/float(Nmax-1)
    #dgamma= 10*2*math.pi/npts
    #alfa=0
    #ofs=10
    plist=[]
    radius=0.81234*float(far)
    for n in range(Nmax):
        x=float(radius)*math.cos(float(n)*float(dalfa))
        y=float(radius)*math.sin(float(n)*float(dalfa))
        plist.append( ovd.Point(x,y) )
    #random.shuffle(plist)
    return plist

def drawFrame(N=2,nframe=1):   
    myscreen = ovdvtk.VTKScreen(width=1920, height=1080)
    ovdvtk.drawOCLtext(myscreen)    
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(myscreen.renWin)
    lwr = vtk.vtkPNGWriter()
    lwr.SetInput( w2if.GetOutput() )
    #lwr.SetFileName(filename)

    random.seed(42)
    scale=1
    far = 1
    camPos = far
    zmult = 4
    myscreen.camera.SetPosition(0, -camPos/float(1000), zmult*camPos) 
    myscreen.camera.SetClippingRange(-(zmult+1)*camPos,(zmult+1)*camPos)
    myscreen.camera.SetFocalPoint(0.0, 0, 0)
    
    vd = ovd.VoronoiDiagram(far,120)
    print vd.version()
    # for vtk visualization
    vod = ovdvtk.VD(myscreen,vd,float(scale), textscale=0.01, vertexradius=0.003)
    vod.drawFarCircle()
    Nmax = N
    # random points
    plist = randomGenerators(far, Nmax)

    t_before = time.time() 
    n=0
    id_list=[]
    for p in plist: 
        print n," adding ",p
        id_list.append( vd.addVertexSite( p ) )
        n=n+1
    id1 = id_list[0]
    id2 = id_list[1]
    print "add segment ",id1, " to ", id2
    vd.addLineSite( id1, id2 )
    t_after = time.time()
    calctime = t_after-t_before
    print " VD done in ", calctime," s, ", calctime/Nmax," s per generator"
    
    vod.setAll()
    myscreen.render()
    #writeFrame( w2if, lwr, nframe )
    
    print "PYTHON All DONE."

if __name__ == "__main__":  
    Nmax = 300
    for n in range(Nmax):
        drawFrame(N=(2+n),nframe=n)        
    


