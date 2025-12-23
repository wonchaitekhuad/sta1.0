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
