'''
CLASSES MODULE - Contains all the custom classes used in the code,
except for the DrawingCanvas (which has its separate module).
'''


import numpy as np
import functions as fn
import tkinter as tk


class Node():
    '''
    Nodes are the start/end points of members, and can be subject to nodal
    forces and/or displacement constraints, such as supports or springs.
    '''
    def __init__(self, canvas, x, y):

        self.coords = [x, y]

        # Displacement constraints
        self.restr = [0, 0, 0, 0]       # Rx, Ry, Rz, support angle
        self.springs = [0, 0, 0]        # Kx, Ky, Kz
        self.pdispl = [0, 0, 0]	        # dx, dy, rz
        self.hinge = 0                  # Nodal liberation rz

        # Nodal forces
        self.Px = [0]*len(canvas.loadcasesList)
        self.Py = [0]*len(canvas.loadcasesList)
        self.Mz = [0]*len(canvas.loadcasesList)
        self.Pangle = [0]*len(canvas.loadcasesList)

    def newCase(self):
        '''
        Used when adding a new loadcase to the structure.
        '''
        self.Px.append(0)
        self.Py.append(0)
        self.Mz.append(0)
        self.Pangle.append(0)

    def delCase(self, i):
        '''
        Used when deleting the i-th loadcase from the structure.
        '''
        self.Px.pop(i)
        self.Py.pop(i)
        self.Mz.pop(i)
        self.Pangle.pop(i)


class Member():
    '''
    The core of the direct stiffness method, members are any linear structural
    element, such as beams or columns.
    '''
    def __init__(self, canvas, start, end, material, section):
        # Nodal parameters
        self.nodes = [start, end]
        self.p1 = canvas.nodesList[start].coords
        self.p2 = canvas.nodesList[end].coords
        self.nlib = [0, 0]

        # Member parameters
        self.length = fn.distance(self.p2, self.p1)
        self.theta = fn.findAngle(self.p2, self.p1)
        self.material = material
        self.section = section

        self.a = np.tan(self.theta)
        self.b = self.p1[1] - self.a * self.p1[0]

        # Initial strains
        self.tensile = 0
        self.curvature = 0

        # Member loads
        self.qx = [0]*len(canvas.loadcasesList)
        self.qy = [0]*len(canvas.loadcasesList)
        self.qtype = [0]*len(canvas.loadcasesList)

        self.Tsup = [0]*len(canvas.loadcasesList)
        self.Tinf = [0]*len(canvas.loadcasesList)

    def update(self, canvas):
        '''
        Recalculates everything node-related, in case of a node deletion.
        '''
        self.p1 = canvas.nodesList[self.nodes[0]].coords
        self.p2 = canvas.nodesList[self.nodes[1]].coords

        self.length = fn.distance(self.p2, self.p1)
        self.theta = fn.findAngle(self.p2, self.p1)

    def newCase(self):
        '''
        Used when adding a new loadcase to the structure.
        '''
        self.qx.append(0)
        self.qy.append(0)
        self.qtype.append(0)
        self.Tsup.append(0)
        self.Tinf.append(0)

    def delCase(self, i):
        '''
        Used when deleting the i-th loadcase from the structure.
        '''
        self.qx.pop(i)
        self.qy.pop(i)
        self.qtype.pop(i)
        self.Tsup.pop(i)
        self.Tinf.pop(i)


class Material():
    '''
    Materials are, as the name implies, the constituent materials for
    any given structural element, such as steel or concrete.
    '''
    def __init__(self, name, elasticity, thermal):
        self.name = name
        self.elasticity = elasticity
        self.thermal = thermal


class Section():
    '''
    Element cross-sections are the geometrical shape obtained when 'cutting'
    a certain linear member with a plane orthogonal to its main axis.
    '''
    def __init__(self, name):
        self.name = name
        self.inertia = 0
        self.area = 0
        self.ysup = 0
        self.yinf = 0
        self.type = 'Genérico'
        self.parameters = []

    def generic(self, inertia, area, ysup, yinf):
        '''
        User-input properties.
        '''
        self.inertia = inertia
        self.area = area
        self.ysup = ysup
        self.yinf = yinf
        self.type = 'Genérico'
        self.parameters = [inertia, area, ysup, yinf]

    def circle(self, Dext, Dint):
        '''
        Automatically calculates cross-section properties
        for a cilindrical member.
        '''
        self.inertia = np.pi*(Dext**4 - Dint**4)/64
        self.area = np.pi*(Dext**2 - Dint**2)/4
        self.ysup = Dext/2
        self.yinf = Dext/2
        self.type = 'Circular'
        self.parameters = [Dext, Dint]

    def rectangle(self, b, h):
        '''
        Automatically calculates cross-section properties
        for a rectangular, prismatic member.
        '''
        self.inertia = (b*h**3)/12
        self.area = b*h
        self.ysup = h/2
        self.yinf = h/2
        self.type = 'Retangular'
        self.parameters = [b, h]

    def simmetricI(self, bf, tf, d, t):
        '''
        Automatically calculates cross-section properties
        for a simmetric I-shape member.
        '''
        self.inertia = (bf*(d+2*tf)**3 - (bf-t)*d**3)/12
        self.area = 2*bf*tf + d*t
        self.ysup = tf + d/2
        self.yinf = tf + d/2
        self.type = 'I simétrico'
        self.parameters = [bf, tf, d, t]

    def assimmetricI(self, bf1, tf1, bf2, tf2, d, t):
        '''
        Automatically calculates cross-section properties
        for an assimmetric I-shape member.
        '''
        A = [bf1*tf1,  t*d,  bf2*tf2]
        G = [tf1/2,  tf1+d/2,  tf1+d+tf2/2]
        IN = [(bf1*tf1**3)/12,  (t*d**3)/12,  (bf2*tf2**3)/12]

        self.area = A[0]+A[1]+A[2]
        yg = np.dot(A, G)/self.area
        self.inertia = (IN[0]+A[0]*(G[0]-yg)**2 + IN[1]+A[1]*(G[1]-yg)**2 +
                        [2]+A[2]*(G[2]-yg)**2)
        self.yinf = yg
        self.ysup = tf1 + d + tf2 - yg

        self.type = 'I assimétrico'
        self.parameters = [bf1, tf1, bf2, tf2, d, t]


class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    (based upon code from Stack Overflow)
    '''
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # miliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() - 40
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffff", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw is None
        if tw:
            tw.destroy()


class Scrollable(tk.Frame):
    '''
        Make a frame scrollable with scrollbar on the right.
        After adding or removing widgets to the scrollable frame,
        call the update() method to refresh the scrollable area.
        (based upon code from Stack Overflow)
    '''

    def __init__(self, frame, width=16):

        self.canvas = tk.Canvas(frame)
        self.canvas.grid(row=0, column=0, sticky='nw')

        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.grid(row=0, column=1, sticky='nse')

        Xscrollbar = tk.Scrollbar(frame, orient='horizontal', width=width)
        Xscrollbar.grid(row=1, column=0, sticky='we')

        self.canvas.config(yscrollcommand=scrollbar.set,
                           xscrollcommand=Xscrollbar.set)

        self.frame = tk.Frame(self.canvas)

        scrollbar.config(command=self.canvas.yview)
        Xscrollbar.config(command=self.canvas.xview)

        # base class initialization
        tk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0, 0, window=self.frame,
                                                      anchor='nw')

    def update(self):
        '''Update the canvas and the scrollregion'''
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
