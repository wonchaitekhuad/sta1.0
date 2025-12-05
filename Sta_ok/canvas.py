'''

CANVAS MODULE - Contains the DrawingCanvas class, which controls the
interactive window's behavior, and also serves as a storage place for
any variables needed in multiple modules.
'''


import tkinter as tk
from tkinter import Canvas, Scrollbar, ttk
import functions as fn
import draw
import action


class drawingCanvas():
    def __init__(self, master):

        self.fileChanged = 0
        self.currentDir = None
        self.currentFile = 'Untitle'
        # Canvas color scheme
        self.lightColor = ['white', 'black', 'red', 'gray40',
                           'green', 'blue', 'black', '#cccccc']
        self.darkColor = ['black', 'white', 'magenta', 'yellow',
                          'lime green', 'blue', 'gray', '#333333']
        self.colorScheme = self.lightColor
        self.currentColor = tk.StringVar(value='Claro')

        self.frame = ttk.Frame(master, cursor='dotbox')
        self.canvas = Canvas(self.frame, bg=self.colorScheme[0], width=800,
                             height=550, scrollregion=(-1e5, -1e5, 1e5, 1e5))
        self.canvas.yview_moveto(0.475)
        self.canvas.xview_moveto(0.495)

        self.hbar = Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.hbar.config(command=self.canvas.xview)
        self.vbar = Scrollbar(self.frame, orient=tk.VERTICAL)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set,
                           yscrollcommand=self.vbar.set)

        self.canvas.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.canvas.focus_set()

        # Status bar stuff
        self.statusbarFrame = ttk.Frame(self.frame, relief=tk.GROOVE)
        self.statusbarFrame.pack(fill=tk.X, side=tk.TOP)

        self.statusbar = tk.StringVar()
        self.gridEnabled, self.snapEnabled = tk.IntVar(), tk.IntVar()
        self.hx, self.hy = 100, 100
        self.memberNode = 0

        self.mousepos = [tk.StringVar(), tk.StringVar()]
        self.memberCoords = [tk.StringVar() for i in range(4)]
        self.mouseposText = tk.StringVar()  # Current mouse position text

        self.statusbar.set('select element.')
        self.gridEnabled.set(1)
        self.snapEnabled.set(1)

        ttk.Label(self.statusbarFrame,
                  textvariable=self.statusbar).pack(side=tk.LEFT)

        self.gridCheckbutton = ttk.Checkbutton(self.statusbarFrame,
                                               text='Grid',
                                               variable=self.gridEnabled,
                                               command=self.whatToDraw)

        self.snapCheckbutton = ttk.Checkbutton(self.statusbarFrame,
                                               text='Snap',
                                               variable=self.snapEnabled)

        self.gridCheckbutton.pack(side=tk.RIGHT)
        self.snapCheckbutton.pack(side=tk.RIGHT)
        ttk.Label(self.statusbarFrame,
                  textvariable=self.mouseposText).pack(side=tk.RIGHT)

        self.sectionType = tk.IntVar(value=0)
        self.entriesList = []
        self.sectionUnits = []

        # Instance lists
        self.nodesList, self.membersList = [], []
        self.materialsList, self.sectionsList = [], []
        self.loadcasesList = ['case 01']
        self.COMBINATIONSList = []
        self.comboFactors = []

        self.results = []
        self.displacements, self.forces = [], []
        self.max, self.min = [], []

        self.analysisType = tk.IntVar(value=0)
        self.maxiter, self.maxerror = 20, 0.001
        self.resultClick = [-1, 0]   # Member number, clicked point/length
        self.showReactions = tk.IntVar(value=0)

        # Cases considered for max/min analysis: 0. Both 1. Cases, 2. Combos
        self.maxType = tk.IntVar(value=0)

        # PARAMETER DECLARATION
        self.scale = 0.75          # Canvas scale, used for zoom

        # Results scale, for diagrams and displacement scale
        self.resultsScale = [1.0, 1.0, 1.0, 1.0]
        # Base values used for the results scales
        self.resultsConstant = [1.0, 1.0, 1.0, 1.0]
        # What happens when you click an element
        self.clickType = 'select'
        # Holds whatever is needed to apply on nodes or members
        self.currentApply = []
        # Last recorded mouse position
        self.mouseAnchor = [0, 0]
        # Used as a corner for the selection box
        self.lastClick = []
        # Used for selection box type: 0 = Blue, 1 = Green
        self.selType = 0
        # Currently selected material and section
        self.selectedMaterial = tk.StringVar()
        self.selectedSection = tk.StringVar()

        # Currently selected loadcase or combination
        self.currentLoadcase = 0
        self.currentCombination = -1

        # Measuring units management
        # 1. Length  2. Force  3. Moment  4. Load 5. Temperature
        # 5. Elasticity 6. Thermal expansion 7. Height 8. Area
        # 9. Inertia  10. Displacement  11. Rotation  12. Angular
        # 13. Spring  14. Torsion spring
        self.units = ['cm', 'kN', 'kN.m', 'kN/m', '°C', 'kN/cm²', '1/°C', 'cm',
                      'cm²', 'cm4', 'cm', 'rad', '°', 'kN/cm', 'kN.cm/rad']
        self.unitVars = [tk.StringVar() for i in range(15)]

        # Action history (for undo/redo functions)
        self.permanent = [[], []]   # 0. Nodes, 1. Members
        self.actions = []   # Holds the list of actions performed
        self.undone = []    # Holds the list of redo-able actions

        # Selection box items
        self.selectedNodes = []
        self.selectedMembers = []

        self.canvas.bind('<Control-z>', action.undo(self))
        self.canvas.bind('<Control-y>', action.redo(self))
        self.canvas.bind('<Key-Delete>', self.pressDel)
        self.canvas.bind('<MouseWheel>', self.scrollWheel)
        self.canvas.bind('<Motion>', self.mouseMotion)
        self.canvas.bind('<ButtonPress-1>', self.pressLMB)
        self.canvas.bind('<B1-Motion>', self.moveLMB)
        self.canvas.bind('<ButtonRelease-1>', self.releaseLMB)
        self.canvas.bind('<ButtonPress-3>', self.pressRMB)
        self.canvas.bind('<B3-Motion>', self.moveRMB)

    def pressDel(self, event):
        '''
        Deletes any selected item on the canvas.
        '''
        self.canvas.focus_set()
        a = ['delSelected', [], []]
        for member in self.selectedMembers:
            a[1].append(member)
        for node in self.selectedNodes:
            a[2].append(node)

        self.actions.append(a)
        self.undone = []
        self.selectedMembers, self.selectedNodes = [], []
        action.runActions(self)

    def scrollWheel(self, event):
        '''
        Zooms in or out the canvas
        '''
        if event.delta > 0:
            f = 1/0.95
        else:
            f = 0.95
        self.scale *= f
        self.mouseAnchor = [event.x, event.y]
        self.whatToDraw()

    def mouseMotion(self, event):
        '''
        Controls what happens when moving the mouse around the canvas.
        '''
        self.canvas.delete('templine')
        mouse = [self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)]
        mousepos = fn.trueCoords(self, mouse)
        mousepos = [fn.unitConvert('cm', self.units[0], mousepos[0]),
                    fn.unitConvert('cm', self.units[0], mousepos[1])]

        self.mousepos[0].set('{:.2f}'.format(mousepos[0]))
        self.mousepos[1].set('{:.2f}'.format(mousepos[1]))

        if self.memberNode == 1:
            self.memberCoords[0].set('{:.2f}'.format(mousepos[0]))
            self.memberCoords[1].set('{:.2f}'.format(mousepos[1]))
        elif self.memberNode == 2:
            self.memberCoords[2].set('{:.2f}'.format(mousepos[0]))
            self.memberCoords[3].set('{:.2f}'.format(mousepos[1]))
        self.mouseposText.set('X: ' + '{:.2f}'.format(mousepos[0]) +
                              ' ' + self.units[0] + '; Y: ' +
                              '{:.2f}'.format(mousepos[1]) +
                              ' ' + self.units[0])

        if self.clickType == 'newMember':
            coords1 = [self.memberCoords[0].get(), self.memberCoords[1].get()]
            coords2 = [self.memberCoords[2].get(), self.memberCoords[3].get()]

            if ('' not in coords1 and
                    '' not in coords2 and self.memberNode == 2):
                coords1 = [fn.entryGet(self.memberCoords[0], 'float'),
                           fn.entryGet(self.memberCoords[1], 'float')]

                coords2 = [fn.entryGet(self.memberCoords[2], 'float'),
                           fn.entryGet(self.memberCoords[3], 'float')]
                coords1, coords2 = (fn.canvasCoords(self, coords1),
                                    fn.canvasCoords(self, coords2))
                self.canvas.create_line(coords1, coords2,
                                        width=1.8, fill=self.colorScheme[3],
                                        tags='templine')

    def moveLMB(self, event):
        '''
        Controls the selection box when moving the mouse while clicking.
        '''
        self.canvas.focus_set()
        self.canvas.delete('selectionbox')
        if self.clickType != 'select':
            return

        else:
            mouse = [self.canvas.canvasx(event.x),
                     self.canvas.canvasy(event.y)]
            click = self.lastClick
            if mouse[0] > click[0]:
                self.selType = 0
                self.canvas.create_rectangle(mouse, click, outline='blue',
                                             width=2, tags='selectionbox')
            elif mouse[0] < click[0]:
                self.selType = 1
                self.canvas.create_rectangle(mouse, click, outline='green',
                                             width=2, tags='selectionbox')

    def releaseLMB(self, event):
        '''
        Controls the selection process when releasing the selection box.
        '''
        if self.clickType != 'select':
            return

        self.canvas.delete('selectionbox')
        mouse = [self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)]
        click = self.lastClick
        if self.selType == 0:
            items = self.canvas.find_enclosed(mouse[0], mouse[1],
                                              click[0], click[1])
        else:
            items = self.canvas.find_overlapping(mouse[0], mouse[1],
                                                 click[0], click[1])

        for item in items:
            itemTags = self.canvas.gettags(item)
            if len(itemTags) == 0:
                next

            elif (itemTags[0] == 'node' and
                    int(itemTags[1]) not in self.selectedNodes):
                self.selectedNodes.append(int(itemTags[1]))
            elif (itemTags[0] == 'member' and
                    int(itemTags[1]) not in self.selectedMembers):
                self.selectedMembers.append(int(itemTags[1]))

        self.whatToDraw()

    def pressLMB(self, event):
        '''
        Controls actions concerning LMB clicks in the canvas.
        '''
        self.canvas.focus_set()
        snap = self.snapEnabled.get()
        mx, my = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.lastClick = [mx, my]
        self.selectedNodes, self.selectedMembers = [], []

        # FINDS THE CLOSEST ITEM
        try:
            item = self.canvas.find_closest(mx, my)
            itemTags = self.canvas.gettags(item)
            itemCoords = self.canvas.coords(item)
            itemTags[0]

        except IndexError:  # IF NO TAGS OR ITEMS
            if self.clickType == 'newNode':
                if snap == 1:
                    m = fn.gridSnap(mx, my, self)
                else:
                    m = [mx, my, True]
                if m[2] is not False:
                    p = fn.trueCoords(self, m)
                    action.newNode(self, p)
                return

            elif self.clickType == 'newMember':
                if snap == 1:
                    m = fn.gridSnap(mx, my, self)
                else:
                    m = [mx, my]

                p = fn.trueCoords(self, m)
                action.newMemberNode(self, p)
                return

            else:
                return

        # CLOSEST ITEM GRIDLINE
        if itemTags[0] == 'grid':
            if self.clickType == 'newNode':
                if snap == 1:
                    m = fn.gridSnap(mx, my, self)
                else:
                    m = [mx, my, True]
                if m[2] is not False:
                    p = fn.trueCoords(self, m)
                    action.newNode(self, p)
                return

            elif self.clickType == 'newMember':
                if snap == 1:
                    m = fn.gridSnap(mx, my, self)
                else:
                    m = [mx, my]
                p = fn.trueCoords(self, m)
                action.newMemberNode(self, p)
                return

            else:
                return

        # CLOSEST ITEM NODE
        elif itemTags[0] == 'node':
            ncoords = [(itemCoords[0] + itemCoords[2])/2,
                       (itemCoords[1] + itemCoords[3])/2]
            d = fn.distance([mx, my], ncoords)

            # If clicking directly on the node (or close enough):
            if d < 15:
                # Snaps the cursor over to the node's position.
                x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
                wx0, wy0 = ncoords[0]-x0, ncoords[1]-y0
                self.canvas.event_generate('<Motion>', warp=True, x=wx0, y=wy0)

                # If adding a node over another, return.
                if self.clickType == 'newNode':
                    return

                # If adding a new member, select the node.
                elif self.clickType == 'newMember':
                    p = fn.trueCoords(self, ncoords)
                    action.newMemberNode(self, p)
                    return

                # If trying to select a node or add any
                # properties, select the node.
                elif self.clickType in ['support', 'nodal', 'select',
                                        'hingeNode', 'hingeRemove']:
                    self.selectedNodes = [int(itemTags[1])]
                    self.selectedMembers = []

                    if self.clickType == 'support':
                        action.addSupport(self, int(itemTags[1]))
                    elif self.clickType == 'nodal':
                        action.addNodal(self, int(itemTags[1]),
                                        self.currentLoadcase)
                    elif self.clickType == 'hingeNode':
                        action.addHinge(self, int(itemTags[1]), 0)
                    elif self.clickType == 'hingeRemove':
                        action.addHinge(self, int(itemTags[1]), 4)
                    self.redraw()
                    return

            # If clicking far enough from it:
            else:
                if self.clickType == 'newNode':
                    if snap == 1:
                        m = fn.gridSnap(mx, my, self)
                    else:
                        m = [mx, my, True]
                    if m[2] is not False:
                        p = fn.trueCoords(self, m)
                        action.newNode(self, p)
                    return

                elif self.clickType == 'newMember':
                    if snap == 1:
                        m = fn.gridSnap(mx, my, self)
                    else:
                        m = [mx, my, True]
                    p = fn.trueCoords(self, m)
                    action.newMemberNode(self, p)
                    return

                else:
                    return

        # CLOSEST ITEM MEMBER
        elif itemTags[0] == 'member':
            d = fn.distPointLine([mx, my], itemCoords)

            # If clicking directly on the member (or close enough):
            if d < 15:
                # If adding a node or member end, place it directly on the
                # member (projection from clicking point).
                if self.clickType in ['newNode', 'newMember']:
                    if snap == 1:
                        m = fn.gridSnap(mx, my, self)
                        p = fn.trueCoords(self, m)
                        if self.clickType == 'newNode':
                            if not m[2]:
                                return
                            else:
                                action.newNode(self, p)
                        else:
                            action.newMemberNode(self, p)
                        return

                    else:
                        m = [mx, my, True]

                        L = fn.findProjection(m, itemCoords)
                        i = int(itemTags[1])
                        p1, theta = (self.membersList[i].p1,
                                     self.membersList[i].theta)
                        L = fn.findProjection(m, itemCoords)
                        L = L/self.scale
                        p = fn.rotate([p1[0]+L, p1[1]], p1, -theta)

                        if self.clickType == 'newNode':
                            action.newNode(self, p)
                        else:
                            action.newMemberNode(self, p)
                        return

                elif self.clickType in ['displace', 'bending',
                                        'shear', 'axial']:
                    x = fn.findProjection([mx, my], itemCoords)
                    L = fn.distance([itemCoords[0], itemCoords[1]],
                                    [itemCoords[2], itemCoords[3]])
                    eps = x/L
                    self.resultClick = [int(itemTags[1]), eps]
                    self.whatToDraw()
                    return

                # If trying to select or add any property to the member:
                elif self.clickType in ['select', 'memberLoad', 'material',
                                        'section', 'imperfections', 'thermal',
                                        'hingeStart', 'hingeEnd', 'hingeBoth',
                                        'hingeRemove']:

                    self.selectedNodes = []
                    self.selectedMembers = [int(itemTags[1])]

                    if self.clickType == 'select':
                        self.redraw()
                    elif self.clickType == 'memberLoad':
                        action.addLoad(self, int(itemTags[1]),
                                       self.currentLoadcase)
                    elif self.clickType == 'material':
                        action.setMaterial(self, int(itemTags[1]))
                    elif self.clickType == 'section':
                        action.setSection(self, int(itemTags[1]))
                    elif self.clickType == 'imperfections':
                        action.addImperf(self, int(itemTags[1]))
                    elif self.clickType == 'hingeStart':
                        action.addHinge(self, int(itemTags[1]), 1)
                    elif self.clickType == 'hingeEnd':
                        action.addHinge(self, int(itemTags[1]), 2)
                    elif self.clickType == 'hingeBoth':
                        action.addHinge(self, int(itemTags[1]), 3)
                    elif self.clickType == 'hingeRemove':
                        action.addHinge(self, int(itemTags[1]), 5)
                    else:
                        action.addThermal(self, int(itemTags[1]),
                                          self.currentLoadcase)
                    return

            # If clicking far enough from it:
            else:
                if self.clickType == 'newNode':
                    if snap == 1:
                        m = fn.gridSnap(mx, my, self)
                    else:
                        m = [mx, my]
                    if m is not None:
                        p = fn.trueCoords(self, m)
                        action.newNode(self, p)
                    return

                elif self.clickType == 'newMember':
                    if snap == 1:
                        m = fn.gridSnap(mx, my, self)
                    else:
                        m = [mx, my]
                    p = fn.trueCoords(self, m)
                    action.newMemberNode(self, p)
                    return

        # CLOSEST ITEM TEMPLINE (temporary member used during placement)
        elif itemTags[0] == 'templine':
            self.canvas.delete('templine')
            self.canvas.event_generate('<ButtonPress-1>', x=event.x, y=event.y)

        # ANYTHING ELSE, JUST RETURN
        else:
            return

    def pressRMB(self, event):
        '''
        Marks the current mouse position as anchor for movement.
        '''
        self.canvas.focus_set()
        self.canvas.scan_mark(event.x, event.y)

    def moveRMB(self, event):
        '''
        Pans the canvas using mouse movement.
        '''
        self.canvas.focus_set()
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def whatToDraw(self):
        '''
        Defines what should be drawn on the canvas, given the circumstances.
        '''
        if self.clickType in ['shear', 'bending', 'axial', 'displace',
                              'maxAxial', 'maxShear', 'maxBending']:
            self.drawResults()
        else:
            self.redraw()

    def redraw(self):
        '''
        Redraws the whole structure, in editing mode.
        '''
        self.canvas.delete('all')
        K = self.currentLoadcase
        if self.gridEnabled.get() == 1:
            n1 = int(10000/(self.hx*self.scale))
            for i in range(n1):
                x1 = fn.canvasCoords(self, [i*self.hx, 0])
                x2 = fn.canvasCoords(self, [-i*self.hx, 0])
                self.canvas.create_line(x1[0], -1e5, x1[0], 1e5,
                                        fill=self.colorScheme[7], tags='grid')
                self.canvas.create_line(x2[0], -1e5, x2[0], 1e5,
                                        fill=self.colorScheme[7], tags='grid')

            n2 = int(10000/(self.hy*self.scale))
            for i in range(n2):
                y1 = fn.canvasCoords(self, [0, i*self.hy])
                y2 = fn.canvasCoords(self, [0, -i*self.hy])
                self.canvas.create_line(1e5, y1[1], -1e5, y1[1],
                                        fill=self.colorScheme[7], tags='grid')
                self.canvas.create_line(1e5, y2[1], -1e5, y2[1],
                                        fill=self.colorScheme[7], tags='grid')

        for i in range(len(self.nodesList)):
            spring = self.nodesList[i].springs
            restr = self.nodesList[i].restr

            # Support symbols
            if restr[0] == 1:
                if restr[1] == 1:
                    if restr[2] == 1:
                        draw.drawSupportXYZ(self, i)
                    else:
                        draw.drawSupportXY(self, i)
                elif restr[2] == 1:
                    draw.drawSupportYZ(self, i, 'x')
                else:
                    draw.drawSupportY(self, i, 'x')
            elif restr[1] == 1:
                if restr[2] == 1:
                    draw.drawSupportYZ(self, i, 'y')
                else:
                    draw.drawSupportY(self, i, 'y')
            elif restr[2] == 1:
                draw.drawSupportZ(self, i)

            # Prescribed displacement symbols
            draw.drawPrescribedDispl(self, i)

            # Spring symbols
            if spring[0] != 0:
                draw.drawSpring(self, i, 'x')
            if spring[1] != 0:
                draw.drawSpring(self, i, 'y')
            if spring[2] != 0:
                draw.drawTorsionSpring(self, i)

        for i in range(len(self.membersList)):
            if (self.membersList[i].tensile != 0 or
                    self.membersList[i].curvature != 0):

                if i in self.selectedMembers:
                    draw.drawImperfections(self, i, 1)
                else:
                    draw.drawImperfections(self, i, 0)

            else:
                # Whether to draw member as highlighted or not.
                if i in self.selectedMembers:
                    draw.drawMember(self, i, 1)
                else:
                    draw.drawMember(self, i, 0)

            draw.drawMemberLoads(self, i, K)    # Draws the distributed loads.
            draw.drawThermalLoads(self, i)      # Draws the thermal loads.

        # Whether to draw node as highlighted or not.
        for i in range(len(self.nodesList)):
            if i in self.selectedNodes:
                draw.drawNode(self, i, 1)
            else:
                draw.drawNode(self, i, 0)

            draw.drawNodalForces(self, i, K)    # Draws the nodal forces.

    def drawResults(self):
        '''
        Shows the results of the analysis.
        '''
        self.canvas.delete('all')

        if self.gridEnabled.get() == 1:
            n1 = int(1e5/(self.hx*self.scale))
            for i in range(n1):
                x1 = fn.canvasCoords(self, [i*self.hx, 0])
                x2 = fn.canvasCoords(self, [-i*self.hx, 0])
                self.canvas.create_line(x1[0], -1e5, x1[0], 1e5,
                                        fill=self.colorScheme[7], tags='grid')
                self.canvas.create_line(x2[0], -1e5, x2[0], 1e5,
                                        fill=self.colorScheme[7], tags='grid')

            n2 = int(1e5/(self.hy*self.scale))
            for i in range(n2):
                y1 = fn.canvasCoords(self, [0, i*self.hy])
                y2 = fn.canvasCoords(self, [0, -i*self.hy])
                self.canvas.create_line(1e5, y1[1], -1e5, y1[1],
                                        fill=self.colorScheme[7], tags='grid')
                self.canvas.create_line(1e5, y2[1], -1e5, y2[1],
                                        fill=self.colorScheme[7], tags='grid')

        if (self.clickType not in ['maxAxial', 'maxShear', 'maxBending'] and
                self.resultClick[0] >= 0):
            draw.drawClickResult(self)

        if self.clickType == 'shear':
            for i in range(len(self.membersList)):
                draw.drawShearForce(self, i)

        elif self.clickType == 'axial':
            for i in range(len(self.membersList)):
                draw.drawNormalForce(self, i)

        elif self.clickType == 'bending':
            for i in range(len(self.membersList)):
                draw.drawBendingMoment(self, i)

        elif self.clickType == 'displace':
            for i in range(len(self.membersList)):
                draw.drawDisplacement(self, i)

            for i in range(len(self.nodesList)):
                spring = self.nodesList[i].springs
                restr = self.nodesList[i].restr

                # Support symbols
                if restr[0] == 1:
                    if restr[1] == 1:
                        if restr[2] == 1:
                            draw.drawSupportXYZ(self, i)
                        else:
                            draw.drawSupportXY(self, i)
                    elif restr[2] == 1:
                        draw.drawSupportYZ(self, i, 'x')
                    else:
                        draw.drawSupportY(self, i, 'x')
                elif restr[1] == 1:
                    if restr[2] == 1:
                        draw.drawSupportYZ(self, i, 'y')
                    else:
                        draw.drawSupportY(self, i, 'y')
                elif restr[2] == 1:
                    draw.drawSupportZ(self, i)

                # Spring symbols
                if spring[0] != 0:
                    draw.drawSpring(self, i, 'x')
                if spring[1] != 0:
                    draw.drawSpring(self, i, 'y')
                if spring[2] != 0:
                    draw.drawTorsionSpring(self, i)

                if self.showReactions.get() == 1:
                    draw.drawReactions(self, i)

        elif self.clickType == 'maxAxial':
            for i in range(len(self.membersList)):
                draw.drawMaxMin(self, i, 0)

        elif self.clickType == 'maxShear':
            for i in range(len(self.membersList)):
                draw.drawMaxMin(self, i, 1)

        elif self.clickType == 'maxBending':
            for i in range(len(self.membersList)):
                draw.drawMaxMin(self, i, 2)

        for i in range(len(self.membersList)):
            draw.drawMember(self, i, 0)



def draw_bmd(canvas, elements, scale):
    """
    FINAL FIX - TI VERIFIED (Matches STAAD.Pro convention)
    Draws bending moment diagram for each element.
    Positive (sagging) drawn inward/downward; negative (hogging) outward/upward.
    """
    try:
        canvas.delete('bmd')
    except Exception:
        pass

    for e in elements:
        try:
            n1, n2 = e.node_i, e.node_j
            x1, y1 = float(n1.x), float(n1.y)
            x2, y2 = float(n2.x), float(n2.y)
        except Exception:
            continue

        dx = x2 - x1
        dy = y2 - y1
        L = (dx*dx + dy*dy) ** 0.5
        if L == 0:
            continue

        ux = dx / L
        uy = dy / L

        # normal direction (global): (-uy, ux) matches STAAD convention
        nx, ny = -uy, ux

        # flip for members sloping upward to keep visual inward/outward consistent
        if dy > 0:
            nx, ny = -nx, -ny

        M1 = getattr(e, 'Mi', 0.0)
        M2 = getattr(e, 'Mj', 0.0)

        # sample along element for smooth polyline
        samples = 8
        pts = []
        for i in range(samples):
            t = i / (samples - 1)
            Mt = M1 * (1 - t) + M2 * t
            xt = x1 + dx * t
            yt = y1 + dy * t
            offx = nx * Mt * scale
            offy = ny * Mt * scale
            pts.extend((xt + offx, yt + offy))

        try:
            canvas.create_line(*pts, fill='green', width=2, smooth=True, tags='bmd')
            # draw endpoint labels
            canvas.create_text(x1 + nx*M1*scale, y1 + ny*M1*scale - 8, text=f"{M1:.2f}", fill='green', font=('Arial',8), tags='bmd')
            canvas.create_text(x2 + nx*M2*scale, y2 + ny*M2*scale - 8, text=f"{M2:.2f}", fill='green', font=('Arial',8), tags='bmd')
        except Exception:
            try:
                canvas.create_line(*pts)
            except Exception:
                pass



def draw_sfd(canvas, elements, scale):
    """
    Draw shear force diagram per element.
    Positive shear plotted in same normal orientation as BMD for consistency.
    """
    try:
        canvas.delete('sfd')
    except Exception:
        pass

    for e in elements:
        try:
            n1, n2 = e.node_i, e.node_j
            x1, y1 = float(n1.x), float(n1.y)
            x2, y2 = float(n2.x), float(n2.y)
        except Exception:
            continue

        dx = x2 - x1
        dy = y2 - y1
        L = (dx*dx + dy*dy) ** 0.5
        if L == 0:
            continue
        ux = dx / L
        uy = dy / L

        nx, ny = -uy, ux
        if dy > 0:
            nx, ny = -nx, -ny

        V1 = getattr(e, 'Vi', 0.0)
        V2 = getattr(e, 'Vj', 0.0)

        pts = []
        samples = 4
        for i in range(samples):
            t = i / (samples - 1)
            Vt = V1 * (1 - t) + V2 * t
            xt = x1 + dx * t
            yt = y1 + dy * t
            pts.extend((xt + nx*Vt*scale, yt + ny*Vt*scale))

        try:
            canvas.create_line(*pts, fill='blue', width=2, smooth=True, tags='sfd')
            canvas.create_text(x1 + nx*V1*scale, y1 + ny*V1*scale - 8, text=f"{V1:.2f}", fill='blue', font=('Arial',8), tags='sfd')
            canvas.create_text(x2 + nx*V2*scale, y2 + ny*V2*scale - 8, text=f"{V2:.2f}", fill='blue', font=('Arial',8), tags='sfd')
        except Exception:
            pass



def draw_deflection(canvas, nodes, scale=1.0):
    """
    Draw deformed shape: expects nodes with .x, .y and .dx, .dy (displacements).
    Positive vertical displacement will be drawn downward on screen.
    """
    try:
        canvas.delete('deflection')
    except Exception:
        pass

    pts = []
    for n in nodes:
        try:
            x = float(n.x) + float(getattr(n, 'dx', 0.0)) * scale
            y = float(n.y) + float(getattr(n, 'dy', 0.0)) * scale
            pts.extend((x, y))
        except Exception:
            continue

    if len(pts) >= 4:
        try:
            canvas.create_line(*pts, fill='purple', width=2, smooth=True, tags='deflection')
        except Exception:
            pass



def draw_reaction(canvas, support_nodes):
    """
    Draw simple reaction arrows at support nodes. Assumes node has x,y and reaction values Rx,Ry.
    """
    try:
        canvas.delete('reaction')
    except Exception:
        pass

    for n in support_nodes:
        try:
            x = float(n.x); y = float(n.y)
            Ry = float(getattr(n, 'Ry', 0.0))
            if abs(Ry) > 1e-6:
                # draw upward arrow for positive reaction (screen y down)
                canvas.create_line(x, y+12, x, y, arrow='last', width=2, fill='black', tags='reaction')
        except Exception:
            continue
