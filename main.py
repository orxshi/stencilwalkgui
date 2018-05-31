import Tkinter
import vtk
from vtk.tk.vtkTkRenderWidget import vtkTkRenderWidget
from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

def runfnc(start, target):
    print("Starting cell is {}".format(start.get()))
    print("Target is ({},{})".format(target[0].get(), target[1].get()))

class MouseInteractorStyle(vtk.vtkInteractorStyle):

    def __init__(self, parent=None):
        #self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        #self.AddObserver("KeyPressEvent", self.onKeyPress)
        #self.AddObserver("OnChar", self.onChar)
        self.AddObserver("CharEvent", self.onChar)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.currentactor = None
        self.leftag = None
        self.txt_target = None
        self.txt_startp = None
        self.startp = None
        self.target = None


    def onChar(self, obj, event):
        key = self.GetInteractor().GetKeySym();
        if key == "q":
            self.txt_startp = vtk.vtkTextActor()
            self.txt_startp.SetInput("Click on starting cell")
            txtprop = self.txt_startp.GetTextProperty()
            txtprop.SetFontFamilyToArial()
            txtprop.SetFontSize(18)
            txtprop.SetColor(1,1,1)
            self.txt_startp.SetDisplayPosition(0,0)
            self.ren.AddActor(self.txt_startp)
            self.rw.Render()
            self.leftag = self.AddObserver("LeftButtonPressEvent", self.chooseStartingCell)
        if key == "a":
            self.txt_target = vtk.vtkTextActor()
            self.txt_target.SetInput("Click target point")
            txtprop = self.txt_target.GetTextProperty()
            txtprop.SetFontFamilyToArial()
            txtprop.SetFontSize(18)
            txtprop.SetColor(1,1,1)
            self.txt_target.SetDisplayPosition(0,0)
            self.ren.AddActor(self.txt_target)
            self.rw.Render()
            self.leftag = self.AddObserver("LeftButtonPressEvent", self.chooseTarget)

    '''
    def onKeyPress(self, obj, event):

        key = self.GetInteractor().GetKeySym();
        if key == "q":
            print("You pressed q")
        if key == "p":
            print("You pressed p")
        self.OnChar()
    '''

    def chooseStartingCell(self, obj, event):
        self.startp.set(self.leftButtonPressEvent(obj, event))
        self.ren.RemoveActor(self.txt_startp)
        self.rw.Render()


    def chooseTarget(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()
        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToDisplay()
        coordinate.SetValue(clickPos[0], clickPos[1], 0)
        world = coordinate.GetComputedWorldValue(self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer())
        self.target[0].set(world[0])
        self.target[1].set(world[1])

        sphere = vtk.vtkRegularPolygonSource()
        sphere.SetCenter(world[0], world[1], 0.0)
        sphere.SetRadius(2.0)
        sphere.SetNumberOfSides(50)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        mapper.SetScalarVisibility(0)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)

        self.ren.AddActor(actor)
        self.RemoveObserver(self.leftag)

        self.ren.RemoveActor(self.txt_target)
        self.rw.Render()


    def leftButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkCellPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())

        ids = vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        ids.InsertNextValue(picker.GetCellId())

        self.NewPickedActor = picker.GetActor()

        selectionNode = vtk.vtkSelectionNode()
        selectionNode.SetFieldType(vtk.vtkSelectionNode.CELL)
        selectionNode.SetContentType(4)
        selectionNode.SetSelectionList(ids)

        selection = vtk.vtkSelection()
        selection.AddNode(selectionNode)

        extractSelection = vtk.vtkExtractSelection()
        extractSelection.SetInputData(0, self.user_data)
        extractSelection.SetInputData(1, selection)
        extractSelection.Update()
        selected = extractSelection.GetOutput()

        if selected:
            if not self.currentactor:
                newactor = vtk.vtkActor()
                self.currectactor = newactor
            else:
                newactor = self.currentactor

            newmapper = vtk.vtkDataSetMapper()
            newmapper.SetInputData(selected)
            newmapper.SetScalarVisibility(0)
            newactor.SetMapper(newmapper)
            newactor.GetProperty().SetColor(0.0, 1.0, 0.0)
            newactor.GetProperty().EdgeVisibilityOn()
            self.ren.AddActor(newactor)
            self.rw.Render()

            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().SetColor(1.0, 1.0, 1.0)
                self.LastPickedActor.GetProperty().EdgeVisibilityOn()

            self.LastPickedActor = newactor

        self.OnLeftButtonDown()
        self.RemoveObserver(self.leftag)
        return picker.GetCellId()
 
 

reader = vtk.vtkUnstructuredGridReader()
reader.SetFileName("bg.vtk")
reader.Update()

root = Tkinter.Tk()

frame = Tkinter.Frame( root )
frame.pack( fill=Tkinter.BOTH, expand=1, side=Tkinter.TOP )

ren = vtk.vtkRenderer()

renwin = vtk.vtkRenderWindow()
renwin.AddRenderer(ren)

ugrid = reader.GetOutput()
geoFilter = vtk.vtkUnstructuredGridGeometryFilter()
geoFilter.SetInputConnection(reader.GetOutputPort())
geoFilter.Update()

mapper = vtk.vtkDataSetMapper()
mapper.SetInputConnection(geoFilter.GetOutputPort())

mapper.SetScalarVisibility(0)
#mapper.GetInput().GetCellData().SetActiveScalars("oga_cell_status")

actor = vtk.vtkActor()
actor.SetMapper(mapper)

actor.GetProperty().EdgeVisibilityOn()

ren.AddActor(actor)

button = Tkinter.Button(root,text="Quit",command=root.quit)
button.pack(fill='x',expand='t')

start = Tkinter.IntVar()
targetx = Tkinter.DoubleVar()
targety = Tkinter.DoubleVar()
target = [targetx, targety]

but_run = Tkinter.Button(root,text="Run",command= lambda: runfnc(start, target))
but_run.pack(fill='x',expand='t')

interactor = vtkTkRenderWindowInteractor(root, rw=renwin)
interactor.pack(side='top', fill='both', expand=1)
interactor.Initialize()
style = MouseInteractorStyle()
style.SetDefaultRenderer(ren)
style.user_data = ugrid
style.rw = renwin
style.ren = ren
style.startp = start
style.target = target
interactor.SetInteractorStyle(style)
interactor.Start()

root.mainloop()
