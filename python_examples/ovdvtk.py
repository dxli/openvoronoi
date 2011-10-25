"""@camvtk docstring
This module provides classes for visualizing CAD/CAM algorithms using VTK.
This module is part of OpenCAMLib (ocl), a toolpath-generation library.

Copyright 2010-2011 Anders Wallin (anders.e.e.wallin "at" gmail.com)
Published under the GNU General Public License, see http://www.gnu.org/licenses/
"""

import vtk
import time
import datetime
# import ocl
# import pyocl
import openvoronoi as ovd
import math

white = (1,1,1)
black = (0,0,0)
grey = ( float(127)/255,float(127)/255,float(127)/255)

red= (1,0,0)
pink = ( float(255)/255,float(192)/255,float(203)/255)
orange = ( float(255)/255,float(165)/255,float(0)/255)
yellow= (1,1,0)

green= (0,1,0)
lgreen = ( float(150)/255,float(255)/255,float(150)/255)
grass = ( float(182)/255,float(248)/255,float(71)/255)

blue= (0,0,1)
lblue= ( float(125)/255,float(191)/255,float(255)/255 )
cyan=  (0,1,1)
mag = ( float(153)/255 , float(42)/255 , float(165)/255  )


class VD:
    def __init__(self, myscreen, vd, scale=1):
        self.myscreen = myscreen
        self.gen_pts=[ovd.Point(0,0)]
        self.generators = PointCloud(pointlist=self.gen_pts)
        self.verts=[]
        self.far=[]
        self.edges =[]
        self.gens =[]
        self.generatorColor = green
        self.vertexColor = red
        self.edgeColor = cyan
        self.vdtext  = Text()
        self.vertexRadius = scale/50
        self.vdtext.SetPos( (50, myscreen.height-150) )
        self.Ngen = 0
        self.vdtext_text = ""
        self.setVDText(vd)
        self.scale=scale
        
        myscreen.addActor(self.vdtext)
    def setVertexRadius(self, r):
        self.vertexRadius=r
        
    def setVDText(self, vd):
        self.Ngen = len( vd.getGenerators() )-3
        self.vdtext_text = "VD with " + str(self.Ngen) + " generators.\n"
        #self.vdtext_text += "YELLOW = New point-generator/site\n"
        #self.vdtext_text += "PINK = Seed vertex\n"
        #self.vdtext_text += "RED = Delete vertices/edges\n"
        #self.vdtext_text += "GREEN = Modified VD edges\n"
        self.vdtext.SetText( self.vdtext_text )
        
        
    def setGenerators(self, vd):
        for p in self.gens:
            self.myscreen.removeActor(p)
        self.gens = []
        for pt in vd.getGenerators():
            p = self.scale*pt
            actor = Sphere( center=(p.x,p.y, 0), radius=self.vertexRadius, color=self.generatorColor )
            self.gens.append(actor)
            self.myscreen.addActor( actor )
        """
        if len(self.gen_pts)>0:
            myscreen.removeActor( self.generators ) 
        #self.generators=[]
        self.gen_pts = []
        for p in vd.getGenerators():
            self.gen_pts.append(self.scale*p)
        self.generators= ovdvtk.PointCloud(pointlist=self.gen_pts) 
        self.generators.SetPoints()
        myscreen.addActor(self.generators)
        self.setVDText(vd)
        """
        self.myscreen.render() 
    
    def setFar(self, vd):
        for pt in vd.getFarVoronoiVertices():
            p=self.scale*pt[0]
            self.myscreen.addActor( Sphere( center=(p.x,p.y, 0), radius=self.vertexRadius, color=pink ) )
            cir_actor = Circle( center=(p.x,p.y,0), radius=(pt[1])*self.scale, color=self.vertexColor )
            #self.verts.append(cir_actor)
            self.myscreen.addActor(cir_actor)
            
        self.myscreen.render() 
    
    def setVertices(self, vd, clearance_disk=0):
        for p in self.verts:
            self.myscreen.removeActor(p)
        self.verts = []
        for pt in vd.getVoronoiVertices():
            p = self.scale*pt[0]
            actor = Sphere( center=(p.x,p.y, 0), radius=self.vertexRadius, color=self.vertexColor )
            self.verts.append(actor)
            self.myscreen.addActor( actor )
            if clearance_disk:
                #draw clearance-disk
                cir_actor = Circle( center=(p.x,p.y,0), radius=pt[1]*self.scale, color=self.vertexColor )
                self.verts.append(cir_actor)
                self.myscreen.addActor(cir_actor)
            
        self.myscreen.render() 
        
    def setEdgesPolydata(self, vd):
        self.edges = []
        self.edges = vd.getEdgesGenerators()
        self.epts = vtk.vtkPoints()
        nid = 0
        lines=vtk.vtkCellArray()
        for e in self.edges:
            p1 = self.scale*e[0]
            p2 = self.scale*e[1] 
            self.epts.InsertNextPoint( p1.x, p1.y, 0)
            self.epts.InsertNextPoint( p2.x, p2.y, 0)
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0,nid)
            line.GetPointIds().SetId(1,nid+1)
            nid = nid+2
            lines.InsertNextCell(line)
        
        linePolyData = vtk.vtkPolyData()
        linePolyData.SetPoints(self.epts)
        linePolyData.SetLines(lines)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(linePolyData)
        
        self.edge_actor = vtk.vtkActor()
        self.edge_actor.SetMapper(mapper)
        self.edge_actor.GetProperty().SetColor( cyan )
        self.myscreen.addActor( self.edge_actor )
        self.myscreen.render() 

    def setEdges(self, vd):
        for e in self.edges:
            self.myscreen.removeActor(e)
        self.edges = []
        for e in vd.getEdgesGenerators():
            p1 = self.scale*e[0]  
            p2 = self.scale*e[1] 
            actor = Line( p1=( p1.x,p1.y, 0), p2=(p2.x,p2.y, 0), color=self.edgeColor )
            self.myscreen.addActor(actor)
            self.edges.append(actor)
        self.myscreen.render() 
        
    def setAll(self, vd):
        self.setGenerators(vd)
        self.setFar(vd)
        #self.setVertices(vd)
        #self.setEdgesPolydata(vd)
        self.setEdges(vd)
        

def drawOCLtext(myscreen):
    t = Text()
    t.SetPos( (myscreen.width-200, myscreen.height-50) )
    date_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t.SetText( "OpenCAMLib\n" + date_text )
    myscreen.addActor(t)

def drawBB( myscreen, vol ):
    """ draw a bounding-box """
    lines = []
    lines.append( Line(p1=(vol.bb.minx, vol.bb.miny, vol.bb.minz) , p2=(vol.bb.maxx, vol.bb.miny, vol.bb.minz))  )
    lines.append( Line(p1=(vol.bb.minx, vol.bb.maxy, vol.bb.minz) , p2=(vol.bb.maxx, vol.bb.maxy, vol.bb.minz))  )
    lines.append( Line(p1=(vol.bb.minx, vol.bb.maxy, vol.bb.maxz) , p2=(vol.bb.maxx, vol.bb.maxy, vol.bb.maxz))  )
    lines.append( Line(p1=(vol.bb.minx, vol.bb.miny, vol.bb.maxz) , p2=(vol.bb.maxx, vol.bb.miny, vol.bb.maxz))  )
    
    lines.append( Line(p1=(vol.bb.minx, vol.bb.miny, vol.bb.minz) , p2=(vol.bb.minx, vol.bb.miny, vol.bb.maxz))  )
    lines.append( Line(p1=(vol.bb.maxx, vol.bb.miny, vol.bb.minz) , p2=(vol.bb.maxx, vol.bb.miny, vol.bb.maxz))  )
    
    lines.append( Line(p1=(vol.bb.minx, vol.bb.maxy, vol.bb.minz) , p2=(vol.bb.minx, vol.bb.maxy, vol.bb.maxz))  )
    lines.append( Line(p1=(vol.bb.maxx, vol.bb.maxy, vol.bb.minz) , p2=(vol.bb.maxx, vol.bb.maxy, vol.bb.maxz))  )
    
    lines.append( Line(p1=(vol.bb.minx, vol.bb.miny, vol.bb.minz) , p2=(vol.bb.minx, vol.bb.maxy, vol.bb.minz))  )
    lines.append( Line(p1=(vol.bb.maxx, vol.bb.miny, vol.bb.minz) , p2=(vol.bb.maxx, vol.bb.maxy, vol.bb.minz))  )
    
    lines.append( Line(p1=(vol.bb.minx, vol.bb.miny, vol.bb.maxz) , p2=(vol.bb.minx, vol.bb.maxy, vol.bb.maxz))  )
    lines.append( Line(p1=(vol.bb.maxx, vol.bb.miny, vol.bb.maxz) , p2=(vol.bb.maxx, vol.bb.maxy, vol.bb.maxz))  )    
    
    for l in lines:
        myscreen.addActor(l)

def drawTree(myscreen,t,color=red,opacity=0.2, offset=(0,0,0)):
    """ draw an octree """
    nodes = t.get_nodes()
    #nmax=len(nodes)
    #i=0
    for n in nodes:
        cen = n.point() # center of cube
        scale = n.get_scale() # scale of cube
        cube = camvtk.Cube(center=(cen.x+offset[0], cen.y+offset[1], cen.z+offset[2]), length= scale, color=color)
        cube.SetOpacity(opacity)
        #cube.SetPhong()
        cube.SetGouraud()
        #cube.SetWireframe()
        myscreen.addActor( cube )
        #if (nmax>100):
        #    print "i=", i
        #    print "div=", (float(nmax)/10)
        #    if ( (i % (float(nmax)/10))==0):
        #        print ".",
        #i=i+1
    #print "done."



def drawTree2(myscreen,t,color=red,opacity=0.2):
    """ draw an octree as an STLSurface """
    tlist = pyocl.octree2trilist(t)
    surf = STLSurf(triangleList=tlist)
    surf.SetColor(color)
    surf.SetOpacity(opacity)
    myscreen.addActor(surf)
    
def drawArrows(myscreen,center=(0,0,0)):
    # X Y Z arrows
    arrowcenter=center
    xar = Arrow(color=red,   center=arrowcenter, rotXYZ=(0,0,0))
    yar = Arrow(color=green, center=arrowcenter, rotXYZ=(0,0,90))
    zar = Arrow(color=blue,  center=arrowcenter, rotXYZ=(0,-90,0))
    myscreen.addActor(xar)
    myscreen.addActor(yar)
    myscreen.addActor(zar)

def drawCylCutter(myscreen, c, p):
    cyl = Cylinder(center=(p.x,p.y,p.z), radius=c.radius,
                            height=c.length,
                            rotXYZ=(90,0,0), color=grey)
    cyl.SetWireframe()
    myscreen.addActor(cyl) 

def drawBallCutter(myscreen, c, p):
    cyl = Cylinder(center=(p.x,p.y,p.z+c.getRadius() ), radius=c.getRadius(),
                            height=c.getLength(),
                            rotXYZ=(90,0,0), color=red)
    #cyl.SetWireframe()
    sph = Sphere(center=(p.x,p.y,p.z+c.getRadius()), radius=c.getRadius(), color=red)
    myscreen.addActor(cyl) 
    myscreen.addActor(sph)
    acts=[]
    acts.append(cyl)
    acts.append(sph)
    return acts 


class VTKScreen():
    """
    a vtk render window for displaying geometry
    """
    def __init__(self, width=1280, height=720):
        """ create a screen """
        self.width=width
        self.height=height

        self.ren = vtk.vtkRenderer()
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.renWin.SetSize(self.width,self.height)
        
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)
        interactorstyle = self.iren.GetInteractorStyle()
        interactorstyle.SetCurrentStyleToTrackballCamera()     
           
        self.camera = vtk.vtkCamera()
        self.camera.SetClippingRange(0.01, 1000)
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetPosition(0, 35, 5)
        self.camera.SetViewAngle(30)
        self.camera.SetViewUp(0, 0, 1)
        self.ren.SetActiveCamera(self.camera)
        self.iren.Initialize()
        
        
    def setAmbient(self, r, g, b):
        """ set ambient color """
        self.ren.SetAmbient(r, g, b)
                    
    def addActor(self, actor):
        """ add an actor """
        self.ren.AddActor(actor)
    
    def removeActor(self, actor):
        """ remove an actor"""
        #actor.Delete()
        self.ren.RemoveActor(actor)
        

    def render(self):
        """ render scene"""
        self.renWin.Render()
        
    def GetLights(self):
        return self.ren.GetLights()
    def CreateLight(self):
        self.ren.CreateLight()
    def MakeLight(self):
        return self.ren.MakeLight()
    def AddLight(self,l):
        self.ren.AddLight(l)
    def RemoveAllLights(self):
        self.ren.RemoveAllLights()
    def SetLightCollection(self,lights):
        self.ren.SetLightCollection(lights)
    def Close(self):
        self.iren.TerminateApp()
        

class CamvtkActor(vtk.vtkActor):
    """ base class for actors"""
    def __init__(self):
        """ do nothing"""
        pass
    
    def Delete(self):
        self.Delete()
    
    def SetColor(self, color):
        """ set color of actor"""
        self.GetProperty().SetColor(color)
    
    def SetOpacity(self, op=0.5):
        """ set opacity of actor, 0 is see-thru (invisible)"""
        self.GetProperty().SetOpacity(op)   
    
    def SetWireframe(self):
        """ set surface to wireframe"""
        self.GetProperty().SetRepresentationToWireframe()
        
    def SetSurface(self):
        """ set surface rendering on"""
        self.GetProperty().SetRepresentationToSurface() 
        
    def SetPoints(self):
        """ render only points"""
        self.GetProperty().SetRepresentationToPoints()
        
    def SetFlat(self):     
        """ set flat shading"""
        self.GetProperty().SetInterpolationToFlat()
    
    def SetGouraud(self):
        """ set gouraud shading"""
        self.GetProperty().SetInterpolationToGouraud()
    
    def SetPhong(self):
        """ set phong shading"""
        self.GetProperty().SetInterpolationToPhong()
    
    # possible TODOs
    # specular
    # diffuse
    # ambient
    

class Cone(CamvtkActor):
    """ a cone"""
    def __init__(self,  center=(-2,0,0), radius = 1, angle=45, height=0.4, color=(1,1,0) , resolution=60):
        """ cone"""
        self.src = vtk.vtkConeSource()
        self.src.SetResolution(resolution)
        self.src.SetRadius( radius ) 
        #self.src.SetAngle( angle )
        self.src.SetHeight( height )
        #self.src.SetCenter(center)
        
        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2] - self.src.GetHeight()/2)
        #transform.RotateX(rotXYZ[0])
        transform.RotateY( -90 )
        #transform.RotateZ(rotXYZ[2])
        transformFilter=vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(self.src.GetOutputPort())
        transformFilter.Update()
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(transformFilter.GetOutput())
        
        
        #self.mapper = vtk.vtkPolyDataMapper()
        #self.mapper.SetInput(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)

class Sphere(CamvtkActor):
    """ a sphere"""
    def __init__(self, radius=1, resolution=20, center=(0,2,0),
                color=(1,0,0)):
        """ create sphere"""
        self.src = vtk.vtkSphereSource()
        self.src.SetRadius(radius)
        self.src.SetCenter(center)
        self.src.SetThetaResolution(resolution)
        self.src.SetPhiResolution(resolution)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)

class Cube(CamvtkActor):
    """ a cube"""
    def __init__(self,center=(2,2,0) , length=1, color=(0,1,0) ):
        """ create cube"""
        self.src = vtk.vtkCubeSource()
        self.src.SetCenter(center)
        self.src.SetXLength(length)
        self.src.SetYLength(length)
        self.src.SetZLength(length)
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)

class Cylinder(CamvtkActor):
    """ cylinder """
    def __init__(self,center=(0,-2,0) , radius=0.5, height=2, color=(0,1,1),
                    rotXYZ=(0,0,0), resolution=50 ):
        """ cylinder """
        self.src = vtk.vtkCylinderSource()
        self.src.SetCenter(0,0,0)
        self.src.SetHeight(height)
        self.src.SetRadius(radius)
        self.src.SetResolution(resolution)
        # SetResolution
        # SetCapping(int)
        # CappingOn() CappingOff()
        
        # this transform rotates the cylinder so it is vertical
        # and then translates the lower tip to the center point
        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2]+height/2)
        transform.RotateX(rotXYZ[0])
        transformFilter=vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(self.src.GetOutputPort())
        transformFilter.Update()

        
        self.mapper = vtk.vtkPolyDataMapper()
        #self.mapper.SetInput(self.src.GetOutput())
        self.mapper.SetInput( transformFilter.GetOutput() )
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Line(CamvtkActor):
    """ line """
    def __init__(self,p1=(0,0,0) , p2=(1,1,1), color=(0,1,1) ):   
        """ line """
        self.src = vtk.vtkLineSource()
        self.src.SetPoint1(p1)
        self.src.SetPoint2(p2)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)

class Tube(CamvtkActor):
    """ line with tube filter"""
    def __init__(self,p1=(0,0,0) , p2=(1,1,1), radius=0.1, color=(0,1,1) ):   
        self.src = vtk.vtkLineSource()
        self.src.SetPoint1(p1)
        self.src.SetPoint2(p2)
        
        self.tubefilter = vtk.vtkTubeFilter()
        self.tubefilter.SetInput( self.src.GetOutput() )
        self.tubefilter.SetRadius( radius )
        self.tubefilter.SetNumberOfSides( 30 )
        self.tubefilter.Update()
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection( self.tubefilter.GetOutputPort() )
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Circle(CamvtkActor):
    """ circle"""
    def __init__(self,center=(0,0,0) , radius=1, color=(0,1,1), resolution=50 ):   
        """ create circle """
        lines =vtk.vtkCellArray()
        id = 0
        points = vtk.vtkPoints()
        for n in xrange(0,resolution):
            line = vtk.vtkLine()
            angle1 = (float(n)/(float(resolution)))*2*math.pi
            angle2 = (float(n+1)/(float(resolution)))*2*math.pi
            p1 = (center[0]+radius*math.cos(angle1), center[1]+radius*math.sin(angle1), center[2])
            p2 = (center[0]+radius*math.cos(angle2), center[1]+radius*math.sin(angle2), center[2])
            points.InsertNextPoint(p1)
            points.InsertNextPoint(p2)
            line.GetPointIds().SetId(0,id)
            id=id+1
            line.GetPointIds().SetId(1,id)
            id=id+1
            lines.InsertNextCell(line)
            

        self.pdata = vtk.vtkPolyData()
        self.pdata.SetPoints(points)
        self.pdata.SetLines(lines)
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.pdata)
        self.SetMapper(self.mapper)
        self.SetColor(color)
        
class Tube(CamvtkActor):
    """ a Tube is a line with thickness"""
    def __init__(self, p1=(0,0,0) , p2=(1,1,1), radius=0.2, color=(0,1,1) ):   
        """ tube"""
        points = vtk.vtkPoints()
        points.InsertNextPoint(p1)
        points.InsertNextPoint(p2)
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0,0)
        line.GetPointIds().SetId(1,1)
        lines =vtk.vtkCellArray()
        lines.InsertNextCell(line)
        self.pdata = vtk.vtkPolyData()
        self.pdata.SetPoints(points)
        self.pdata.SetLines(lines)

        tubefilter=vtk.vtkTubeFilter()
        tubefilter.SetInput(self.pdata)
        tubefilter.SetRadius(radius)
        tubefilter.SetNumberOfSides(50)
        tubefilter.Update()
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(tubefilter.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Point(CamvtkActor):
    """ point"""
    def __init__(self, center=(0,0,0), color=(1,2,3) ):   
        """ create point """
        self.src = vtk.vtkPointSource()
        self.src.SetCenter(center)
        self.src.SetRadius(0)
        self.src.SetNumberOfPoints(1)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.src.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)

class Arrow(CamvtkActor):
    """ arrow """
    def __init__(self, center=(0,0,0), color=(0,0,1), rotXYZ=(0,0,0) ):
        """ arrow """
        self.src = vtk.vtkArrowSource()
        #self.src.SetCenter(center)
        
        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2])
        transform.RotateX(rotXYZ[0])
        transform.RotateY(rotXYZ[1])
        transform.RotateZ(rotXYZ[2])
        transformFilter=vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(self.src.GetOutputPort())
        transformFilter.Update()
        

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput( transformFilter.GetOutput() )
        self.SetMapper(self.mapper)
        self.SetColor(color)


class Text(vtk.vtkTextActor):
    """ 2D text, HUD-type"""
    def __init__(self, text="text",size=18,color=(1,1,1),pos=(100,100)):
        """create text"""
        self.SetText(text)
        self.properties=self.GetTextProperty()
        self.properties.SetFontFamilyToArial()
        self.properties.SetFontSize(size)
        
        self.SetColor(color)
        self.SetPos(pos)
    
    def SetColor(self,color):
        """ set color of text """
        self.properties.SetColor(color)
    
    def SetPos(self, pos):
        """ set position on screen """
        self.SetDisplayPosition(pos[0], pos[1])

    def SetText(self, text):
        """ set text to be displayed """
        self.SetInput(text)
        
    def SetSize(self, size):
        self.properties.SetFontSize(size)
        
class Text3D(vtk.vtkFollower):
    """ 3D text rendered in the scene"""
    def __init__(self, color=(1,1,1), center=(0,0,0), text="hello", scale=1, camera=[]):
        """ create text """
        self.src = vtk.vtkVectorText()
        self.SetText(text)
        #self.SetCamera(camera)
        transform = vtk.vtkTransform()
        
        transform.Translate(center[0], center[1], center[2])
        transform.Scale(scale, scale, scale)
        #transform.RotateY(90)
        #transform2 = vtk.vtkTransform()
        #transform.Concatenate(transform2)
        #transformFilter=vtk.vtkTransformPolyDataFilter()
        #transformFilter.SetTransform(transform)
        #transformFilter.SetInputConnection(self.src.GetOutputPort())
        #transformFilter.Update()
        
        #follower = vtk.vtkFollower()
        #follower.SetMapper
        
        self.SetUserTransform(transform)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.src.GetOutputPort())
        self.SetMapper(self.mapper)
        self.SetColor(color)
        
    def SetText(self, text):
        """ set text to be displayed"""
        self.src.SetText(text)
        
    def SetColor(self,color):
        """ set color of text"""
        self.GetProperty().SetColor(color)        

class Axes(vtk.vtkActor):
    """ axes (x,y,z) """
    def __init__(self, center=(0,0,0), color=(0,0,1) ):
        """ create axes """
        self.src = vtk.vtkAxes()
        #self.src.SetCenter(center)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.src.GetOutput())
        self.SetMapper(self.mapper)

        self.SetColor(color)
        self.SetOrigin(center)
        # SetScaleFactor(double)
        # GetOrigin
     

    def SetColor(self, color):
        self.GetProperty().SetColor(color)
    
    def SetOrigin(self, center=(0,0,0)):
        self.src.SetOrigin(center[0], center[1], center[2])

class Toroid(CamvtkActor):
    def __init__(self, r1=1, r2=0.25, center=(0,0,0), rotXYZ=(0,0,0), color=(1,0,0)):
        self.parfun = vtk.vtkParametricSuperToroid()
        self.parfun.SetRingRadius(r1)
        self.parfun.SetCrossSectionRadius(r2)
        self.parfun.SetN1(1)
        self.parfun.SetN2(1)
         
        self.src = vtk.vtkParametricFunctionSource()
        self.src.SetParametricFunction(self.parfun)
        
        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2])
        transform.RotateX(rotXYZ[0])
        transform.RotateY(rotXYZ[1])
        transform.RotateZ(rotXYZ[2])
        transformFilter=vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(self.src.GetOutputPort())
        transformFilter.Update()
        
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(transformFilter.GetOutput())
        self.SetMapper(self.mapper)
        self.SetColor(color)    

"""
class TrilistReader(vtk.vtkPolyDataAlgorithm):
    def __init__(self, triangleList):
        vtk.vtkPolyDataAlgorithm.__init__(self)
        self.FileName = None
        self.SetNumberOfInputPorts(0)
        self.SetNumberOfOutputPorts(1)
        
    def FillOutputPortInfornmation(self, port, info):
        if port == 0:
            info.Set( vtk.vtkDataObject.DATA_TYPE_NAME(), "vtkPolyData")
            return 1
        return 0
        
    def RequestData(self, request, inputVector, outputVector):
        outInfo = outputVector.GetInformationObject(0)
        output = outInfo.Get( vtk.vtkDataObject.DATA_OBJECT() )
        polydata = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        points.InsertNextPoint(0,0,0)
        polydata.SetPoints(points)
        
        output.ShallowCopy(polydata)
        return 1
"""

class STLSurf(CamvtkActor):
    def __init__(self, filename=None, triangleList=[], color=(1,1,1) ):
        self.src=[]
        if filename is None:
            points = vtk.vtkPoints()
            triangles = vtk.vtkCellArray()
            n=0
            for t in triangleList:
                triangle = vtk.vtkTriangle()
                for p in t.getPoints():
                    points.InsertNextPoint(p.x, p.y, p.z)
                triangle.GetPointIds().SetId(0,n)
                n=n+1
                triangle.GetPointIds().SetId(1,n)
                n=n+1
                triangle.GetPointIds().SetId(2,n)
                n=n+1
                triangles.InsertNextCell(triangle)
            polydata= vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetPolys(triangles)
            polydata.Modified()
            polydata.Update()
            self.src=polydata
            self.mapper = vtk.vtkPolyDataMapper()
            self.mapper.SetInput(self.src)
            self.SetMapper(self.mapper)
            
        else: # a filename was specified
            self.src = vtk.vtkSTLReader()
            self.src.SetFileName(filename)
            self.src.Update()
            self.mapper = vtk.vtkPolyDataMapper()
            self.mapper.SetInput(self.src.GetOutput())
            self.SetMapper(self.mapper)

        self.SetColor(color)
        # SetScaleFactor(double)
        # GetOrigin

class PointCloud(CamvtkActor):
    def __init__(self, pointlist=[]):
        points = vtk.vtkPoints()
        cellArr = vtk.vtkCellArray()
        #Colors = vtk.vtkUnsignedCharArray()
        #Colors.SetNumberOfComponents(3)
        #Colors.SetName("Colors")
        self.zheight = 0
        
        
        n=0
        for p in pointlist:
            vert = vtk.vtkVertex()
            points.InsertNextPoint(p.x, p.y, self.zheight)
            vert.GetPointIds().SetId(0,n)
            cellArr.InsertNextCell( vert )
            #col = clColor(p.cc())
            #Colors.InsertNextTuple3( float(255)*col[0], float(255)*col[1], float(255)*col[2] )
            n=n+1
        
        
        polydata= vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetVerts( cellArr )
        #polydata.GetPointData().SetScalars(Colors)

        polydata.Modified()
        polydata.Update()
        self.src=polydata
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.src)
        self.SetMapper(self.mapper)
        #self.SetColor(color)
        

class CLPointCloud(CamvtkActor):
    def __init__(self, pointlist=[]):
        points = vtk.vtkPoints()
        cellArr = vtk.vtkCellArray()
        Colors = vtk.vtkUnsignedCharArray()
        Colors.SetNumberOfComponents(3)
        Colors.SetName("Colors")
        
        n=0
        for p in pointlist:
            vert = vtk.vtkVertex()
            points.InsertNextPoint(p.x, p.y, p.z)
            vert.GetPointIds().SetId(0,n)
            cellArr.InsertNextCell( vert )
            col = clColor(p.cc())
            Colors.InsertNextTuple3( float(255)*col[0], float(255)*col[1], float(255)*col[2] )
            n=n+1
            
        polydata= vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetVerts( cellArr )
        polydata.GetPointData().SetScalars(Colors)

        polydata.Modified()
        polydata.Update()
        self.src=polydata
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.src)
        self.SetMapper(self.mapper)
        #self.SetColor(color)



class Plane(CamvtkActor):
    def __init__(self, center=(0,0,0), color=(0,0,1) ):
        self.src = vtk.vtkPlaneSource()
        #self.src.SetCenter(center)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInput(self.src.GetOutput())
        self.SetMapper(self.mapper)

        self.SetColor(color)
        self.SetOrigin(center)
        # SetScaleFactor(double)
        # GetOrigin
     


# TODO:
# vtkArcSource
# vtkDiskSource
# vtkFrustumSource
# vtkOutlineSource
# vtkParametricFunctionSource
# PlatonicSolid
# ProgrammableSource (?)
# PSphereSource
# RegularPolygon

#----------------------------------------------------------------

#---- misc helper functions
def vtkPolyData2OCLSTL(vtkPolyData,oclSTL):
    """ read vtkPolyData and add each triangle to an ocl.STLSurf """
    for cellId in range(0,vtkPolyData.GetNumberOfCells()):
        cell = vtkPolyData.GetCell(cellId)
        points = cell.GetPoints()
        plist = []
        for pointId in range(0,points.GetNumberOfPoints()):
            vertex = points.GetPoint(pointId)
            p = ocl.Point(vertex[0],vertex[1],vertex[2])
            plist.append(p)
        t = ocl.Triangle(plist[0],plist[1],plist[2])
        oclSTL.addTriangle(t)
