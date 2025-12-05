'''
ACTION MODULE - Contains the functions related to the action history
(used in order to keep the undo/redo functions working properly).
'''


from classes import Node, Member
import numpy as np
import functions as fn


def newNode(canvas, coords):
    '''
    Adds a new node to the action history.
    '''
    n = Node(canvas, coords[0], coords[1])
    canvas.actions.append(['newnode', n])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def setMaterial(canvas, i):
    '''
    Changes a given member's material.
    '''
    canvas.actions.append(['setMaterial', i, canvas.currentApply[0]])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def setSection(canvas, i):
    '''
    Changes a given member's section.
    '''
    canvas.actions.append(['setSection', i, canvas.currentApply[0]])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def matApplyAll(canvas, matname):
    '''
    Changes all members' materials to a given one.
    '''
    canvas.actions.append(['matApplyAll', matname])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def secApplyAll(canvas, secname):
    '''
    Changes all members' sections to a given one.
    '''
    canvas.actions.append(['secApplyAll', secname])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def newMemberNode(canvas, p):
    '''
    Manages what happens when selecting a member's end node.
    '''
    if canvas.memberNode == 1:
        canvas.memberCoords[0].set(p[0])
        canvas.memberCoords[1].set(p[1])
        canvas.memberNode = 2
        return

    elif canvas.memberNode == 2:
        if '' in [canvas.memberCoords[0].get(), canvas.memberCoords[1].get()]:
            canvas.memberCoords[0].set(p[0])
            canvas.memberCoords[1].set(p[1])
            return

        else:
            canvas.memberCoords[2].set(p[0])
            canvas.memberCoords[3].set(p[1])
            coords = [fn.entryGet(canvas.memberCoords[i], 'float')
                      for i in range(4)]

            if 'error' not in coords:
                material = fn.entryGet(canvas.selectedMaterial, 'string')
                section = fn.entryGet(canvas.selectedSection, 'string')
                newMember(canvas, [coords[0], coords[1]],
                          [coords[2], coords[3]], [material, section])

                coords = ['', '', '', '']
                for i in range(4):
                    canvas.memberCoords[i].set(coords[i])
                canvas.memberNode = 1


def newMember(canvas, p1, p2, properties):
    '''
    Adds a new member to the action history.
    '''
    if p1 == p2 or not properties[0] or not properties[1]:
        return

    canvas.actions.append(['newMember', p1, p2, properties])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def addSupport(canvas, node):
    '''
    Adds nodal restraints to a given node.
    '''
    restr = [0, 0, 0, 0]
    springs = [0, 0, 0, 0]
    pdispl = [0, 0, 0, 0]
    for i in range(4):
        restr[i] = canvas.currentApply[i]
    for i in range(3):
        springs[i] = canvas.currentApply[i+4]
    for i in range(3):
        pdispl[i] = canvas.currentApply[i+7]

    canvas.actions.append(['addSupport', node, restr, springs, pdispl])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def addHinge(canvas, element, _type):
    if _type == 0:
        canvas.actions.append(['addHingeNode', element])
    elif _type == 1:
        canvas.actions.append(['addHingeStart', element])
    elif _type == 2:
        canvas.actions.append(['addHingeEnd', element])
    elif _type == 3:
        canvas.actions.append(['addHingeBoth', element])
    elif _type == 4:
        canvas.actions.append(['removeHingeNode', element])
    else:
        canvas.actions.append(['removeHingeMember', element])
    runActions(canvas)


def addNodal(canvas, node, case):
    '''
    Adds nodal forces to a given node.
    '''
    nodal = [canvas.currentApply[i] for i in range(len(canvas.currentApply))]
    canvas.actions.append(['addNodal', node, case, nodal])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def addImperf(canvas, member):
    '''
    Adds initial imperfections to a given member.
    '''
    imperfections = [canvas.currentApply[0], canvas.currentApply[1]]
    canvas.actions.append(['addImperf', member, imperfections])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def addLoad(canvas, member, case):
    '''
    Adds a distributed load to a given member.
    '''
    load = [canvas.currentApply[i] for i in range(len(canvas.currentApply))]
    canvas.actions.append(['addLoad', member, case, load])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def addThermal(canvas, member, case):
    '''
    Adds a thermal load to a given member.
    '''
    thermal = [canvas.currentApply[i] for i in range(len(canvas.currentApply))]
    canvas.actions.append(['addThermal', member, case, thermal])
    canvas.undone = []
    canvas.fileChanged = 1
    runActions(canvas)


def undo(canvas):
    '''
    Undoes the last registered action.
    '''
    if len(canvas.actions) == 0:
        return

    i = len(canvas.actions) - 1
    action = canvas.actions.pop(i)
    canvas.undone.append(action)
    canvas.fileChanged = 1
    runActions(canvas)


def redo(canvas):
    '''
    Restores the last undone action.
    '''
    if len(canvas.undone) == 0:
        return
    i = len(canvas.undone) - 1
    action = canvas.undone.pop(i)
    canvas.actions.append(action)
    canvas.fileChanged = 1
    runActions(canvas)


def runActions(canvas):
    '''
    Runs every action in the action history.
    '''
    canvas.nodesList = []
    canvas.membersList = []
    for node in canvas.permanent[0]:
        canvas.nodesList.append(node)

    for member in canvas.permanent[1]:
        canvas.membersList.append(member)

    for action in canvas.actions:
        if action[0] == 'newnode':
            xo, yo = action[1].coords[0], action[1].coords[1]
            for node in canvas.nodesList:
                x, y = node.coords[0], node.coords[1]

                if np.absolute(xo-x) < 1e-3 and np.absolute(yo-y) < 1e-3:
                    break

            else:
                canvas.nodesList.append(action[1])

        elif action[0] == 'newMember':
            x1, y1 = action[1][0], action[1][1]
            x2, y2 = action[2][0], action[2][1]
            a1 = 0

            for i in range(len(canvas.nodesList)):
                x = canvas.nodesList[i].coords[0]
                y = canvas.nodesList[i].coords[1]

                if np.absolute(x1-x) < 1e-3 and np.absolute(y1-y) < 1e-3:
                    n1, a1 = i, 1

            if a1 == 0:
                node1 = Node(canvas, x1, y1)
                canvas.nodesList.append(node1)
                n1 = len(canvas.nodesList) - 1

            a2 = 0
            for i in range(len(canvas.nodesList)):
                x = canvas.nodesList[i].coords[0]
                y = canvas.nodesList[i].coords[1]
                if np.absolute(x2-x) < 1e-3 and np.absolute(y2-y) < 1e-3:
                    n2, a2 = i, 1

            if a2 == 0:
                node2 = Node(canvas, action[2][0], action[2][1])
                canvas.nodesList.append(node2)
                n2 = len(canvas.nodesList) - 1

            m = Member(canvas, n1, n2, action[3][0], action[3][1])
            am = 0
            for member in canvas.membersList:
                if member.nodes == [n1, n2] or member.nodes == [n2, n1]:
                    am = 1

            if am == 0:
                canvas.membersList.append(m)

        elif action[0] == 'delSelected':
            todelete = []
            for i in action[1]:
                todelete.append(canvas.membersList[i])

            for member in todelete:
                canvas.membersList.remove(member)

            todelete2, todelete3 = [], []
            for i in action[2]:
                for member in canvas.membersList:
                    if i in member.nodes:
                        todelete2.append(member)
                    else:
                        if member.nodes[0] > i:
                            member.nodes[0] -= 1
                        if member.nodes[1] > i:
                            member.nodes[1] -= 1
                todelete3.append(canvas.nodesList[i])

            for member in todelete2:
                canvas.membersList.remove(member)

            for node in todelete3:
                canvas.nodesList.remove(node)

            for member in canvas.membersList:
                member.update(canvas)

        # Checking for overlapping nodes and members
        for node in canvas.nodesList:
            i = canvas.nodesList.index(node)
            x, y = node.coords[0], node.coords[1]

            for member in canvas.membersList:
                if member.theta != np.pi/2 and member.theta != 3*np.pi/2:
                    m = member.a * x + member.b - y
                    a = 1
                elif (y < member.p1[1] and y > member.p2[1] or
                        y > member.p1[1] and y < member.p2[1]):
                    m = member.p1[0] - x
                    a = 1
                else:
                    a = 0

                if (i not in member.nodes and a == 1):

                    if (np.absolute(m) < 1e-8 and
                            x < member.p1[0] and x > member.p2[0]):
                        temp = member.nodes[1]
                        member.nodes[1] = i
                        member.update(canvas)

                        newmember = Member(canvas, i, temp,
                                           member.material, member.section)
                        canvas.membersList.append(newmember)

                    elif (np.absolute(m) < 1e-8 and
                          x < member.p2[0] and x > member.p1[0]):
                        temp = member.nodes[1]
                        member.nodes[1] = i
                        member.update(canvas)

                        newmember = Member(canvas, i, temp,
                                           member.material, member.section)
                        canvas.membersList.append(newmember)

        for member in canvas.membersList:
            n1, n2 = member.nodes[0], member.nodes[1]
            for other in canvas.membersList:
                if other is not member:
                    if ((other.nodes[0] == n1 and other.nodes[1] == n2) or
                            (other.nodes[1] == n1 and other.nodes[0] == n2)):
                        canvas.membersList.remove(other)

    for action in canvas.actions:
        if action[0] == 'setMaterial':
            canvas.membersList[action[1]].material = action[2]

        elif action[0] == 'setSection':
            canvas.membersList[action[1]].section = action[2]

        elif action[0] == 'matApplyAll':
            for member in canvas.membersList:
                member.material = action[1]

        elif action[0] == 'secApplyAll':
            for member in canvas.membersList:
                member.section = action[1]

        elif action[0] == 'addSupport':
            for i in range(4):
                canvas.nodesList[action[1]].restr[i] = action[2][i]
            for i in range(3):
                canvas.nodesList[action[1]].springs[i] = action[3][i]
            for i in range(3):
                canvas.nodesList[action[1]].pdispl[i] = action[4][i]

        elif action[0] == 'addNodal':
            canvas.nodesList[action[1]].Px[action[2]] = action[3][0]
            canvas.nodesList[action[1]].Py[action[2]] = action[3][1]
            canvas.nodesList[action[1]].Mz[action[2]] = action[3][2]
            canvas.nodesList[action[1]].Pangle[action[2]] = action[3][3]

        elif action[0] == 'addHingeNode':
            canvas.nodesList[action[1]].hinge = 1

        elif action[0] == 'removeHingeNode':
            canvas.nodesList[action[1]].hinge = 0

        elif action[0] == 'addHingeStart':
            canvas.membersList[action[1]].nlib = [1, 0]

        elif action[0] == 'addHingeEnd':
            canvas.membersList[action[1]].nlib = [0, 1]

        elif action[0] == 'addHingeBoth':
            canvas.membersList[action[1]].nlib = [1, 1]

        elif action[0] == 'removeHingeMember':
            canvas.membersList[action[1]].nlib = [0, 0]

        elif action[0] == 'addImperf':
            canvas.membersList[action[1]].tensile = action[2][0]
            canvas.membersList[action[1]].curvature = action[2][1]

        elif action[0] == 'addLoad':
            canvas.membersList[action[1]].qx[action[2]] = action[3][0]
            canvas.membersList[action[1]].qy[action[2]] = action[3][1]
            canvas.membersList[action[1]].qtype[action[2]] = action[3][2]

        elif action[0] == 'addThermal':
            canvas.membersList[action[1]].Tsup[action[2]] = action[3][0]
            canvas.membersList[action[1]].Tinf[action[2]] = action[3][1]

    canvas.whatToDraw()



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
