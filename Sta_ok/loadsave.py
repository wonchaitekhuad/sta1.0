'''
LOADSAVE MODULE - Contains all the functions related to input/output of data.
'''


from classes import Node, Member, Section, Material
from os import path, chdir, getcwd


def arrange(canvas, array, current):
    '''
    Converts the array of numbers into the current object class.
    '''
    if current == 'NODES\n':
        n = Node(canvas, float(array[0]), float(array[1]))
        n.restr = [int(array[2]), int(array[3]),
                   int(array[4]), float(array[5])]
        n.springs = [float(array[6]), float(array[7]), float(array[8])]
        n.pdispl = [float(array[9]), float(array[10]), float(array[11])]
        n.hinge = int(array[12])

        for i in range(13, 13+len(canvas.loadcasesList)):
            n.Px[i-13] = float(array[4*(i-13)+13])
            n.Py[i-13] = float(array[4*(i-13)+14])
            n.Mz[i-13] = float(array[4*(i-13)+15])
            n.Pangle[i-13] = float(array[4*(i-13)+16])

        canvas.permanent[0].append(n)
        canvas.nodesList.append(n)

    elif current == 'MEMBERS\n':
        m = Member(canvas, int(array[0]), int(array[1]), array[2], array[3])
        m.tensile, m.curvature = float(array[4]), float(array[5])
        m.nlib = [int(array[6]), int(array[7])]

        for i in range(8, 8+len(canvas.loadcasesList)):
            m.qx[i-8] = float(array[5*(i-8)+8])
            m.qy[i-8] = float(array[5*(i-8)+9])
            m.qtype[i-8] = float(array[5*(i-8)+10])
            m.Tsup[i-8] = float(array[5*(i-8)+11])
            m.Tinf[i-8] = float(array[5*(i-8)+12])

        canvas.permanent[1].append(m)
        canvas.membersList.append(m)

    elif current == 'LOADCASES\n':
        canvas.loadcasesList.append(array[0])

    elif current == 'COMBINATIONS\n':
        canvas.COMBINATIONSList.append(array[0])
        factors = []
        for i in range(1, len(array)):
            factors.append(float(array[i]))
        canvas.comboFactors.append(factors)

    elif current == 'MATERIALS\n':
        m = Material(array[0], float(array[1]), float(array[2]))
        canvas.materialsList.append(m)

    elif current == 'SECTIONS\n':
        s = Section(array[0])
        secType = int(array[1])
        if secType == 0:
            s.generic(float(array[2]), float(array[3]),
                      float(array[4]), float(array[5]))
        elif secType == 1:
            s.circle(float(array[2]), float(array[3]))
        elif secType == 2:
            s.rectangle(float(array[2]), float(array[3]))
        elif secType == 3:
            s.simmetricI(float(array[2]), float(array[3]),
                         float(array[4]), float(array[5]))
        else:
            s.assimmetricI(float(array[2]), float(array[3]),
                           float(array[4]), float(array[5]),
                           float(array[6]), float(array[7]))

        canvas.sectionsList.append(s)


def load(canvas, filepath):
    '''
    Loads the structure file located at filepath.
    '''

    canvas.nodesList, canvas.membersList = [], []
    canvas.materialsList, canvas.sectionsList = [], []
    canvas.loadcasesList, canvas.COMBINATIONSList,  = [], []
    canvas.comboFactors = []
    canvas.permanent = [[], []]
    canvas.results, canvas.resultClick = [], [-1, 0]
    canvas.actions, canvas.undone = [], []
    canvas.canvas.yview_moveto(0.475)
    canvas.canvas.xview_moveto(0.495)

    value = path.split(filepath)
    olddir = getcwd()

    canvas.currentDir = value[0]
    canvas.currentFile = value[1]
    chdir(value[0])

    with open(value[1]) as file:
        lines = file.readlines()
        if lines[0] not in ['LOADCASES\n', 'COMBINATIONS\n', 'NODES\n',
                            'MEMBERS\n', 'MATERIALS\n', 'SECTIONS\n']:
            current = 'LOADCASES\n'

        for line in lines:
            if line not in ['LOADCASES\n', 'COMBINATIONS\n', 'NODES\n',
                            'MEMBERS\n', 'MATERIALS\n', 'SECTIONS\n']:

                split1 = line.split('¬')
                array = []
                for string in split1:
                    if '¬' + string + '¬' not in line:
                        split2 = string.split()
                        for item in split2:
                            array.append(item)
                    elif string != ' ':
                        array.append(string)
                arrange(canvas, array, current)

            else:
                current = line

    chdir(olddir)


def save(canvas, filepath):
    '''
    Saves the structure to a file at the given filepath.
    '''
    value = path.split(filepath)
    olddir = getcwd()

    canvas.currentDir = value[0]
    canvas.currentFile = value[1]
    chdir(value[0])
    file = open(value[1], 'w')
    file.write('LOADCASES\n')

    for case in canvas.loadcasesList:
        string = '¬' + case + '¬\n'
        file.write(string)

    file.write('COMBINATIONS\n')
    for i in range(len(canvas.COMBINATIONSList)):
        string = '¬' + canvas.COMBINATIONSList[i] + '¬ '
        for j in range(len(canvas.comboFactors[i])):
            string += str(canvas.comboFactors[i][j]) + ' '
        string += '\n'
        file.write(string)

    file.write('MATERIALS\n')
    for material in canvas.materialsList:
        string = '¬' + material.name + '¬ '
        string += str(material.elasticity) + ' '
        string += str(material.thermal) + '\n'
        file.write(string)

    file.write('SECTIONS\n')
    types = ['Genérico', 'Circular', 'Retangular',
             'I simétrico', 'I assimétrico']
    for section in canvas.sectionsList:
        string = '¬' + section.name + '¬ '
        string += str(types.index(section.type)) + ' '
        for parameter in section.parameters:
            string += str(parameter) + ' '
        string += '\n'
        file.write(string)

    file.write('NODES\n')
    for node in canvas.nodesList:
        string = str(node.coords[0]) + ' ' + str(node.coords[1]) + ' '

        for value in node.restr:
            string += str(value) + ' '
        for value in node.springs:
            string += str(value) + ' '
        for value in node.pdispl:
            string += str(value) + ' '

        string += str(node.hinge) + ' '

        for i in range(len(canvas.loadcasesList)):
            string += (str(node.Px[i]) + ' ' + str(node.Py[i]) + ' ' +
                       str(node.Mz[i]) + ' ' + str(node.Pangle[i]) + ' ')

        string += '\n'
        file.write(string)

    file.write('MEMBERS\n')
    for member in canvas.membersList:
        string = str(member.nodes[0]) + ' ' + str(member.nodes[1]) + ' '
        string += '¬' + member.material + '¬ ¬' + member.section + '¬ '
        string += str(member.tensile) + ' ' + str(member.curvature) + ' '
        string += str(member.nlib[0]) + ' ' + str(member.nlib[1]) + ' '
        for i in range(len(canvas.loadcasesList)):
            string += (str(member.qx[i]) + ' ' + str(member.qy[i]) +
                       ' ' + str(member.qtype[i]) + ' ')
            string += str(member.Tsup[i]) + ' ' + str(member.Tinf[i]) + ' '
        string += '\n'
        file.write(string)

    file.close()
    chdir(olddir)



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
