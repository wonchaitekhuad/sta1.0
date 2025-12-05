'''
FUNCTIONS MODULE - Contains misc functions used throughout all of the code.
'''


import numpy as np


def linInterp(x1, y1, x2, y2, x):
    '''
    Linearly interpolates a value between two known points.
    '''
    if x2 == x1:
        return y1

    h = x2 - x1
    a = x - x1
    y = y1+a*(y2-y1)/h
    return y


def distance(p1, p2):
    '''
    Returns the euclidean distance between two vectors.
    '''
    d = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    return d


def distPointLine(point, line):
    '''
    Returns the euclidean distance between a point and a line.
    '''
    if line[0] == line[2]:
        return np.absolute(point[0]-line[0])
    else:
        a = (line[3]-line[1])/(line[2]-line[0])
        c = line[1] - a*line[0]
        return np.absolute((a*point[0] - point[1] + c)/np.sqrt(a*a+1))


def findAngle(p2, p1):
    '''
    Returns the angle in radians between two vectors.
    '''
    if p2[0] == p1[0]:
        if p2[1] > p1[1]:
            return np.pi/2
        elif p2[1] < p1[1]:
            return 3*np.pi/2

    theta = np.arctan(np.absolute((p2[1]-p1[1]) / (p2[0]-p1[0])))
    if p2[0] > p1[0]:
        if p2[1] >= p1[1]:
            return theta
        elif p2[1] < p1[1]:
            return (2*np.pi - theta)

    else:
        if p2[1] >= p1[1]:
            return (np.pi - theta)
        else:
            return (np.pi + theta)


def angleSign(theta):
    '''
    Function for keeping consistent positions when supplementar
    angles are used.
    '''
    if theta <= np.pi/2 or theta > 3*np.pi/2:
        return 1
    else:
        return -1


def textAngle(theta):
    '''
    Function for keeping oblique texts within a
    180-degree span (makes reading easier).
    '''
    if theta <= 90 or theta > 270:
        return theta
    elif theta > 90 and theta < 180:
        return theta + 180
    if theta >= 180 and theta <= 270:
        return theta - 180


def rotate(point, center, theta):
    '''
    Takes a given point and rotates it around a center point.
    '''
    p0 = point[0] + 1j*point[1]
    c = center[0] + 1j*center[1]
    rot = np.exp(-theta*1j)
    pf = rot * (p0 - c) + c

    return [np.real(pf), np.imag(pf)]


def findProjection(point, line):
    '''
    Finds the projected coordinate of a given point on a given line.
    '''
    p1p = distance(point, [line[0], line[1]])
    p2p = distPointLine(point, line)

    return np.sqrt(p1p**2 - p2p**2)


def entryGet(var, vartype):
    '''
    Takes a given Tkinter variable and returns its current value, in the
    specified variable type. If not possible, returns 'error'.
    '''
    value = var.get()
    if type(value) is str and len(value) != 0:
        if vartype in ['float', 'int'] and value[0] == '=':
            for element in value:
                if (element not in ['0', '1', '2', '3', '4', '5',
                                    '6', '7', '8', '9', '+', '-',
                                    '*', '/', '^', '=', ')', '(', ' ']):
                    return 'error'
            value = value.replace('^', '**')
            value = value.replace(' ', '')
            value = eval(value.replace('=', ''))

    try:
        if vartype == 'float':
            return float(value)

        elif vartype == 'int':
            return int(value)

        elif vartype == 'string':
            return str(value)

    except ValueError:
        if vartype in ['float', 'int'] and not value:
            return 0
        else:
            return 'error'


def canvasCoords(canvas, p):
    '''
    Converts real input coordinates into the canvas' coordinate system.
    '''
    scale = canvas.scale
    offset = canvas.mouseAnchor
    canvasx = (p[0] - offset[0])*scale + offset[0]
    canvasy = -(p[1] - offset[1])*scale - offset[1]
    return [canvasx, canvasy]



def trueCoords(canvas, p):
    '''
    Converts input coordinates from the canvas into real coordinates.
    '''
    scale = canvas.scale
    offset = canvas.mouseAnchor
    x = (p[0]-offset[0])/scale + offset[0]
    y = (-p[1] - offset[1])/scale + offset[1]
    return [x, y]


def gridSnap(mx, my, canvas):
    '''
    Snaps the cursor position to the closest grid intersection.
    '''
    p = trueCoords(canvas, [mx, my])
    x, y = p[0], p[1]
    hx, hy = canvas.hx, canvas.hy

    a, b = hx*int(x/hx), hy*int(y/hy)

    if (x - a)/hx >= 0.5:
        x += hx
    elif (x - a)/hx <= -0.5:
        x -= hx

    if (y - b)/hy >= 0.5:
        y += hy
    elif (y - b)/hy <= -0.5:
        y -= hy

    a, b = hx*int(x/hx), hy*int(y/hy)

    p = canvasCoords(canvas, [a, b])
    a, b = p[0], p[1]

    xy = [canvas.canvas.canvasx(0), canvas.canvas.canvasy(0)]
    wx0, wy0 = a-xy[0], b-xy[1]
    canvas.canvas.event_generate('<Motion>', warp=True, x=wx0, y=wy0)

    c = canvas.canvas.find_closest(a, b)
    cTags, cCoords = canvas.canvas.gettags(c), canvas.canvas.coords(c)

    if len(cTags) != 0 and cTags[0] == 'node':
        ncoords = [(cCoords[0]+cCoords[2])/2, (cCoords[1]+cCoords[3])/2]
        d = distance([a, b], ncoords)
        if d < 15:
            return [a, b, False]

    return [a, b, True]


def shapeFunction(x, L, d):
    '''
    Returns the displaced position of a member, in its local coordinates.
    '''
    eps = x/L
    N0 = 1 - eps
    N1 = 1 - 3*(eps**2) + 2*(eps**3)
    N2 = L*(eps-2*(eps)**2+eps**3)
    N3 = eps
    N4 = 3*(eps)**2 - 2*(eps)**3
    N5 = L*(-(eps)**2+eps**3)

    ux = N0*d[0] + N3*d[3]
    uy = N1*d[1] + N4*d[4]
    uz = N2*d[2] + N5*d[5]
    return [ux, uy, uz]


def checkSupports(canvas):
    '''
    NEEDS REWORK - Checks if the structure is not unstable due
    to insufficient support conditions.
    '''
    supportNodes = []
    Rx, Ry, Rz = False, False, False
    for node in canvas.nodesList:
        p = rotate([node.restr[0], node.restr[1]], [0, 0], node.restr[3])
        if (p[0]+p[1]+node.restr[2] + node.springs[0]
                + node.springs[1] + node.springs[2]) != 0:
            supportNodes.append(canvas.nodesList.index(node))
            if p[0] != 0 or node.springs[0] != 0:
                Rx = True
            if p[1] != 0 or node.springs[1] != 0:
                Ry = True
            if node.restr[2] != 0 or node.springs[2] != 0:
                Rz = True

    if not Rx or not Ry:
        return False
    elif Rz:
        return True

    n = 0
    for i in supportNodes:
        for j in supportNodes:
            if i != j:
                theta1 = canvas.nodesList[i].restr[3]
                theta2 = findAngle(canvas.nodesList[i].coords,
                                   canvas.nodesList[j].coords)
                p = rotate([node.restr[0]+node.springs[0],
                            node.restr[1]+node.springs[1]], [0, 0], theta1)
                q = p[0]*(-np.sin(theta2)) - p[1]*(np.cos(theta2))
                if q != 0:
                    n += 1
                if n == 2:
                    Rz = True
                    break

    if Rx and Ry and Rz:
        return True
    else:
        return False


def unitConvert(unit1, unit2, value):
    '''
    Converts a given value between two units of measurement.
    '''
    # Quick value check -- If no converting is needed:
    if unit1 == unit2:
        return value

    # Otherwise...
    Lunits = ['mm', 'cm', 'dm', 'm', 'in', 'ft']
    Funits = ['N', 'kN', 'kgf', 'tf', 'lbf', 'kip']
    Munits = ['N.mm', 'N.cm', 'N.dm', 'N.m', 'kN.mm', 'kN.cm', 'kN.dm', 'kN.m',
              'kgf.mm', 'kgf.cm', 'kgf.dm', 'kgf.m', 'tf.mm', 'tf.cm', 'tf.dm',
              'tf.m', 'lbf.in', 'lbf.ft', 'kip.in', 'kip.ft']
    qUnits = ['N/mm', 'N/cm', 'N/dm', 'N/m', 'kN/mm', 'kN/cm', 'kN/dm', 'kN/m',
              'kgf/mm', 'kgf/cm', 'kgf/dm', 'kgf/m', 'tf/mm', 'tf/cm', 'tf/dm',
              'tf/m', 'lbf/in', 'lbf/ft', 'kip/in', 'kip/ft']
    Tunits = ['°C', 'K', '°F']
    Eunits = ['kPa', 'MPa', 'GPa', 'kN/cm²', 'kgf/cm²', 'kgf/mm²', 'kgf/m²',
              'tf/mm²', 'tf/cm²', 'tf/m²', 'kip/ft²', 'lb/ft²', 'ksi', 'psi']
    alphaUnits = ['1/°C', '1/°F', '1/K']
    Aunits = ['mm²', 'cm²', 'dm²', 'm²', 'in²', 'ft²']
    Iunits = ['mm4', 'cm4', 'dm4', 'm4', 'in4', 'ft4']
    angleUnits = ['°', 'rad']
    Kunits = ['N/rad', 'kN/rad', 'kgf/rad', 'tf/rad', 'lbf/rad', 'kip/rad',
              'N/°', 'kN/°', 'kgf/°', 'tf/°', 'lbf/°', 'kip/°']

    KL = [[1, 1/10, 1/100, 1/1000, 1/25.4, 1/304.8],        # mm
          [10, 1, 1/10, 1/100, 1/2.54, 1/30.48],             # cm
          [100, 10, 1, 10, 10/2.54, 10/30.48],               # dm
          [1000, 100, 10, 1, 100/2.54, 100/30.48],           # m
          [25.4, 2.54, 0.254, 0.0254, 1, 12],                # in
          [304.8, 30.48, 3.048, 0.3048, 12, 1]]              # ft

    KF = [[1, 1/1000, 1/9.807, 1/9806.7, 1/4.448, 1/4448],  # N
          [1000, 1, 101.972, 0.101972, 224.809, 1/4.448],    # kN
          [9.807, 1/101.972, 1, 1/1000, 2.205, 453.59],      # kgf
          [9806.7, 9.807, 1000, 1, 2204.62, 2.2046],         # tf
          [4.448, 1/224.809, 1/2.205, 1/2204.62, 1/1000],    # lbf
          [4448, 4.448, 1/453.59, 1/2.2046, 1000]]           # kip

    Ktheta = [[1, np.pi/180], [180/np.pi, 1]]

    KT = [[1, 1, 1.8], [1, 1, 1.8], [1/1.8, 1/1.8, 1]]

    # LENGTH/HEIGHT/DISPLACEMENT:
    if unit1 in Lunits:
        i, j = Lunits.index(unit1), Lunits.index(unit2)
        return value*KL[i][j]

    # FORCE:
    if unit1 in Funits:
        i, j = Funits.index(unit1), Funits.index(unit2)
        return value*KF[i][j]

    # MOMENT:
    if unit1 in Munits:
        u1, u2 = unit1.split('.'), unit2.split('.')
        i1, j1 = Funits.index(u1[0]), Funits.index(u2[0])
        i2, j2 = Lunits.index(u1[1]), Lunits.index(u2[1])
        return value*KF[i1][j1]*KL[i2][j2]

    # DISTRIBUTED LOAD/LINEAR SPRING:
    if unit1 in qUnits:
        u1, u2 = unit1.split('/'), unit2.split('/')
        i1, j1 = Funits.index(u1[0]), Funits.index(u2[0])
        i2, j2 = Lunits.index(u1[1]), Lunits.index(u2[1])
        return value*KF[i1][j1]/KL[i2][j2]

    # TEMPERATURE:
    if unit1 in Tunits:
        i, j = Tunits.index(unit1), Tunits.index(unit2)
        return value*KT[i][j]

    # ELASTICITY/STRESS:
    if unit1 in Eunits:
        others = ['kPa', 'MPa', 'GPa', 'ksi', 'psi']
        correct = ['kN/m²', 'N/mm²', 'kN/mm²', 'kip/in²', 'lbf/in²']
        if unit1 in others:
            x1 = correct[others.index(unit1)]
        else:
            x1 = unit1

        if unit2 in others:
            x2 = correct[others.index(unit2)]
        else:
            x2 = unit2

        u1, u2 = x1.split('/'), x2.split('/')
        i1, j1 = Funits.index(u1[0]), Funits.index(u2[0])
        i2, j2 = Aunits.index(u1[1]), Aunits.index(u2[1])
        return value*KF[i1][j1]/((KL[i2][j2])**2)

    # TEMPERATURE:
    if unit1 in alphaUnits:
        i, j = alphaUnits.index(unit1), alphaUnits.index(unit2)
        return value/KT[i][j]

    # AREA:
    if unit1 in Aunits:
        i, j = Aunits.index(unit1), Aunits.index(unit2)
        return value*(KL[i][j])**2

    # INERTIA:
    if unit1 in Iunits:
        i, j = Iunits.index(unit1), Iunits.index(unit2)
        return value*(KL[i][j])**4

    # ANGLE/ROTATION:
    if unit1 in angleUnits:
        i, j = angleUnits.index(unit1), angleUnits.index(unit2)
        return value*Ktheta[i][j]

    # ROTATION SPRING:
    if unit1 in Kunits:
        u1, u2 = unit1.split('/'), unit2.split('/')
        i1, j1 = Funits.index(u1[0]), Funits.index(u2[0])
        i2, j2 = angleUnits.index(u1[1]), angleUnits.index(u2[1])
        return value*KF[i1][j1]/Ktheta[i2][j2]

    else:
        return value   # Just in case something unexpected happens.



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
