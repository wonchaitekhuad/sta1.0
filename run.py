'''
RUN MODULE - Contains the core functions, responsible for the analysis itself.
'''

import numpy as np


def comboFactors(Sta, case):
    '''
    Creates a given combination's factor array, which is dotted with
    the load arrays in order to create the final loads.
    '''
    if case < len(Sta.loadcasesList):
        r = np.zeros(len(Sta.loadcasesList))
        r[case] = 1
    else:
        c = case - len(Sta.loadcasesList)
        r = np.asarray(Sta.comboFactors[c])
    return r


def linear(Sta):
    '''
    Solves the structure using the default Stiffness Method.
    '''
    # ---------------------- INITIAL PARAMETERS -------------------------

    # Numbers of nodes, members and loadcases/COMBINATIONS
    nnodes, nmembers = len(Sta.nodesList), len(Sta.membersList)
    ncases = len(Sta.loadcasesList)+len(Sta.COMBINATIONSList)

    # Number of elements per node:
    nelem = np.zeros(nnodes)
    for member in Sta.membersList:
        n1, n2 = member.nodes[0], member.nodes[1]
        nelem[n1] += 1
        nelem[n2] += 1

    # Nodal hinges
    DOFextras, mdone = np.zeros(nnodes), np.zeros(nnodes)
    for i in range(nnodes):
        if Sta.nodesList[i].hinge == 1 and nelem[i] > 0:
            DOFextras[i] = nelem[i] - 1

    # Internal hinges
    DOFint, mintdone = np.zeros(nnodes), np.zeros(nnodes)
    for member in Sta.membersList:
        n1, n2 = member.nodes[0], member.nodes[1]
        if (member.nlib[0] == 1 and
                Sta.nodesList[n1].hinge == 0 and nelem[n1] > 1):
            DOFint[n1] += 1
        if (member.nlib[1] == 1 and
                Sta.nodesList[n2].hinge == 0 and nelem[n2] > 1):
            DOFint[n2] += 1

    for i in range(nnodes):
        if DOFint[i] == nelem[i] and nelem[i] > 0:
            DOFextras[i] = nelem[i] - 1
            DOFint[i] = 0

    # Springs and prescribed displacement vectors
    springs, pdispl = [], []
    for node in Sta.nodesList:
        i = Sta.nodesList.index(node)
        springs.append(node.springs[0])
        springs.append(node.springs[1])
        springs.append(node.springs[2])

        pdispl.append(node.pdispl[0])
        pdispl.append(node.pdispl[1])
        pdispl.append(node.pdispl[2])

        for j in range(int(DOFextras[i])):
            springs.append(node.springs[2])
            pdispl.append(node.pdispl[2])

        for j in range(int(DOFint[i])):
            springs.append(node.springs[2])
            pdispl.append(node.pdispl[2])

    # DOF vector creation
    DOF, ndof = [], 0
    for node in Sta.nodesList:
        i = Sta.nodesList.index(node)
        if node.restr[0] > 0:
            DOF.append(-1)
        else:
            DOF.append(ndof)
            ndof += 1

        if node.restr[1] > 0:
            DOF.append(-1)
        else:
            DOF.append(ndof)
            ndof += 1

        if (node.restr[2] > 0 and DOFextras[i] == 0
                and DOFint[i] == 0):
            DOF.append(-1)
        else:
            if DOFextras[i] != 0:
                for j in range(int(DOFextras[i])+1):
                    DOF.append(ndof)
                    ndof += 1
            elif DOFint[i] != 0:
                for j in range(int(DOFint[i])+1):
                    DOF.append(ndof)
                    ndof += 1
            else:
                DOF.append(ndof)
                ndof += 1

    # Member DOF lists
    MemberDOF = []
    MDOFIndex = []
    for member in Sta.membersList:
        n1, n2 = member.nodes[0], member.nodes[1]
        a1 = int(DOFextras[0:n1].sum(axis=0)+DOFint[0:n1].sum(axis=0)+3*n1)
        a2 = int(DOFextras[0:n2].sum(axis=0)+DOFint[0:n2].sum(axis=0)+3*n2)

        if DOFextras[n1] != 0:
            b1 = a1 + int(mdone[n1])
        elif DOFint[n1] != 0 and member.nlib[0] != 0:
            mintdone[n1] += 1
            b1 = a1 + int(mintdone[n1])
        else:
            b1 = a1

        if DOFextras[n2] != 0:
            b2 = a2 + int(mdone[n2])
        elif DOFint[n2] != 0 and member.nlib[1] != 0:
            mintdone[n2] += 1
            b2 = a2 + int(mintdone[n2])
        else:
            b2 = a2

        mindex = [a1, a1+1, b1+2, a2, a2+1, b2+2]
        mdof = [DOF[index] for index in mindex]

        if DOFextras[n1] > mdone[n1]:
            mdone[n1] += 1
        if DOFextras[n2] > mdone[n2]:
            mdone[n2] += 1

        MDOFIndex.append(mindex)
        MemberDOF.append(mdof)

    # ---------------------- NODAL FORCES VECTORS ------------------------

    # Converting nodal forces into global coordinates
    PX = [np.zeros(len(Sta.loadcasesList)) for i in range(nnodes)]
    PY = [np.zeros(len(Sta.loadcasesList)) for i in range(nnodes)]
    MZ = [np.asarray(Sta.nodesList[i].Mz) for i in range(nnodes)]

    for node in Sta.nodesList:
        n = Sta.nodesList.index(node)

        for i in range(len(Sta.loadcasesList)):
            cos, sin = np.cos(node.Pangle[i]), np.sin(node.Pangle[i])
            PX[n][i] = node.Px[i]*cos + node.Py[i]*(-sin)
            PY[n][i] = node.Px[i]*sin + node.Py[i]*cos

    # Nodal forces vectors
    forces = [np.zeros(3*nnodes) for i in range(ncases)]
    FN = [np.zeros(ndof) for i in range(ncases)]
    for n in range(ncases):
        cfactors = comboFactors(Sta, n)  # Combination factors for a given case

        for i in range(nnodes):
            # Find the current node's forces for the current case/combination
            Px = np.dot(cfactors, PX[i])
            Py = np.dot(cfactors, PY[i])
            Mz = np.dot(cfactors, MZ[i])

            # Full forces vector (no DOF checking)
            forces[n][3*i] = Px
            forces[n][3*i+1] = Py
            forces[n][3*i+2] = Mz

            # Check whether the DOF's are valid, and if so add the nodal forces
            a = int(DOFextras[0:i].sum(axis=0)+DOFint[0:i].sum(axis=0)+3*i)
            if DOF[a] >= 0:
                FN[n][DOF[a]] += Px
            if DOF[a+1] >= 0:
                FN[n][DOF[a+1]] += Py

            for j in range(int(DOFextras[i])+1):
                if DOF[a+2+j] >= 0:
                    FN[n][DOF[a+2+j]] += Mz

            for j in range(int(DOFint[i])):
                if DOF[a+2+j] >= 0:
                    FN[n][DOF[a+2+j]] += Mz

    # ----------------------- ROTATION MATRICES --------------------------

    # Member rotation matrices
    RotList = []
    for member in Sta.membersList:
        cos, sin = np.cos(member.theta), np.sin(member.theta)
        R = np.array([[cos, sin, 0,   0,   0,  0],
                      [-sin, cos, 0,   0,   0,  0],
                      [0,   0,  1,   0,   0,  0],
                      [0,   0,  0,  cos, sin, 0],
                      [0,   0,  0, -sin, cos, 0],
                      [0,   0,  0,   0,   0,  1]])
        RotList.append(R)

    # Oblique support rotation matrices
    RIList = []
    for member in Sta.membersList:
        start = Sta.nodesList[member.nodes[0]]
        end = Sta.nodesList[member.nodes[1]]

        if start.restr[0]+start.restr[1] == 1:
            theta1 = -start.restr[3]
        else:
            theta1 = 0

        if end.restr[0]+end.restr[1] == 1:
            theta2 = -end.restr[3]
        else:
            theta2 = 0

        cos1, sin1 = np.cos(theta1), np.sin(theta1)
        cos2, sin2 = np.cos(theta2), np.sin(theta2)

        RI = np.array([[cos1, sin1, 0,   0,    0,   0],
                       [-sin1, cos1, 0,   0,    0,   0],
                       [0,    0,   1,   0,    0,   0],
                       [0,    0,   0,  cos2, sin2, 0],
                       [0,    0,   0, -sin2, cos2, 0],
                       [0,    0,   0,   0,    0,   1]])
        RIList.append(RI)

    # ------------------------------- STIFFNESS MATRICES ----------------------

    SList = []                            # Stiffness matrices list
    FPdispl = np.zeros(ndof)            # Prescribed displacement forces list
    SDOF = np.zeros((ndof, ndof))        # Global stiffness matrix

    for m in range(nmembers):
        L = Sta.membersList[m].length

        material = next((material for material in Sta.materialsList if
                         material.name == Sta.membersList[m].material), None)
        section = next((section for section in Sta.sectionsList if
                        section.name == Sta.membersList[m].section), None)

        E, I, A = material.elasticity, section.inertia, section.area

        # Local member stiffness matrix
        a = [E*A/L, 12*E*I/L**3, 6*E*I/L**2, 4*E*I/L, 2*E*I/L]

        SL = np.array([[a[0],  0,     0,   -a[0],  0,     0],
                       [0,   a[1],  a[2],   0,  -a[1],  a[2]],
                       [0,   a[2],  a[3],   0,  -a[2],  a[4]],
                       [-a[0],  0,     0,    a[0],  0,     0],
                       [0,  -a[1], -a[2],   0,   a[1], -a[2]],
                       [0,   a[2],  a[4],   0,  -a[2],  a[3]]])

        # Global member stiffness matrix
        SG = np.dot(RIList[m].T, np.dot(RotList[m].T, SL))
        SG = np.dot(SG, np.dot(RotList[m], RIList[m]))
        SList.append(SG)

        # Prescribed displacements vector
        mdx = MDOFIndex[m]
        mpdispl = np.array([pdispl[mdx[0]], pdispl[mdx[1]], pdispl[mdx[2]],
                            pdispl[mdx[3]], pdispl[mdx[4]], pdispl[mdx[5]]])

        mpdispl = np.dot(RIList[m], mpdispl)

        Fd = np.dot(SG, mpdispl)    # Prescribed displacement forces vector

        # Prescr. displ. forces arrangement
        for i in range(6):
            pr = MemberDOF[m][i]
            if pr >= 0:
                FPdispl[pr] += Fd[i]

        # Member SM arrangement
        for i in range(6):
            for j in range(6):
                pr, pc = MDOFIndex[m][i], MDOFIndex[m][j]
                pr, pc = DOF[pr], DOF[pc]
                if pr >= 0 and pc >= 0:
                    SDOF[pr][pc] += SG[i][j]

    # Spring constants arrangemens
    for i in range(len(DOF)):
        pr = DOF[i]
        if pr >= 0:
            SDOF[pr][pr] += springs[i]

    # ----------------- MEMBER LOAD VECTORS -------------------------
    # Converting member loads into member-local coordinates
    QX = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    QY = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]

    for member in Sta.membersList:
        m = Sta.membersList.index(member)
        cos, sin = np.cos(member.theta), np.sin(member.theta)
        for i in range(len(Sta.loadcasesList)):
            if member.qtype[i] == 0:
                QX[m][i] = member.qx[i]*cos + member.qy[i]*sin
                QY[m][i] = member.qx[i]*(-sin) + member.qy[i]*cos
            else:
                QX[m][i] = member.qx[i]
                QY[m][i] = member.qy[i]

    # Member load vectors
    F0 = [np.zeros(ndof) for i in range(ncases)]
    F0List = [[] for i in range(ncases)]

    for m in range(nmembers):
        material = next((material for material in Sta.materialsList if
                         material.name == Sta.membersList[m].material), None)
        section = next((section for section in Sta.sectionsList if
                        section.name == Sta.membersList[m].section), None)

        L = Sta.membersList[m].length
        E, alpha = material.elasticity, material.thermal
        I, A = section.inertia, section.area
        ysup, yinf = section.ysup, section.yinf
        e, f = member.tensile, member.curvature

        Fimp = np.array([e*E*A/L, 0, 8*E*I*f/L**2,
                        -e*E*A/L, 0, -8*E*I*f/L**2])  # Initial imperf. vector

        for n in range(ncases):
            cfactors = comboFactors(Sta, n)  # Combo factors for a given case

            qx, qy = np.dot(cfactors, QX[m]), np.dot(cfactors, QY[m])
            Tsup = np.dot(cfactors, np.asarray(Sta.membersList[m].Tsup))
            Tinf = np.dot(cfactors, np.asarray(Sta.membersList[m].Tinf))

            T0 = (Tsup*ysup+Tinf*yinf)/(ysup+yinf)
            dT = Tsup-Tinf
            h = ysup+yinf

            Fq = np.array([qx*L/2, qy*L/2, qy*L*L/12,
                           qx*L/2, qy*L/2, -qy*L*L/12])  # Linear loads vector
            FT = np.array([-alpha*E*A*T0, 0, alpha*E*I*dT/h,
                           alpha*E*A*T0, 0, -alpha*E*I*dT/h])  # Thermal vector

            F0L = Fq+FT+Fimp
            F0List[n].append(F0L)

            F0G = np.dot(RIList[m].T, np.dot(RotList[m].T, F0L))

            for i in range(6):
                pr = MemberDOF[m][i]
                if pr >= 0:
                    F0[n][pr] += F0G[i]

    # -------------------------- FINAL RESULTS --------------------------

    d, Fe = [[] for i in range(ncases)], [[] for i in range(ncases)]
    FR = [[[0, 0, 0] for j in range(nnodes)] for i in range(ncases)]

    for n in range(ncases):
        # Final forces vector
        F = F0[n] + FN[n] - FPdispl

        # Displacements vector
        displacements = np.dot(np.linalg.inv(SDOF), F)
        dDOF = []
        for i in range(len(DOF)):
            if DOF[i] < 0:
                dDOF.append(pdispl[i])
            else:
                dDOF.append(displacements[DOF[i]])

        # Internal forces vectors
        for m in range(nmembers):
            n1, n2 = Sta.membersList[m].nodes[0], Sta.membersList[m].nodes[1]
            mdx = MDOFIndex[m]
            dm1 = np.array([dDOF[mdx[0]], dDOF[mdx[1]], dDOF[mdx[2]],
                           dDOF[mdx[3]], dDOF[mdx[4]], dDOF[mdx[5]]])
            dm2 = np.dot(np.dot(RotList[m], RIList[m]), dm1)
            d[n].append(dm2)

            print([dm1[0], dm1[1], dm1[3], dm1[4]])

            FeG = np.dot(SList[m], dm1)
            FeL = np.dot(np.dot(RotList[m], RIList[m]), FeG) - F0List[n][m]
            Fe[n].append(FeL)
            FG = np.dot(RIList[m].T, np.dot(RotList[m].T, FeL))
            for i in range(3):
                if Sta.nodesList[n1].restr[i] == 1:
                    FR[n][n1][i] += FG[i] - forces[n][3*n1+i]
                if Sta.nodesList[n2].restr[i] == 1:
                    FR[n][n2][i] += FG[3+i] - forces[n][3*n2+i]

    for n in range(ncases):
        for i in range(nnodes):
            cos = np.cos(-Sta.nodesList[i].restr[3])
            sin = np.sin(-Sta.nodesList[i].restr[3])
            a = FR[n][i][0]*cos + FR[n][i][1]*(-sin)
            b = FR[n][i][0]*sin + FR[n][i][1]*cos
            FR[n][i][0], FR[n][i][1] = a, b

    return [Fe, d, FR]


def galambos(Sta):
    '''
    Solves the structure using the nonlinear Galambos' method.
    '''

    # ----------------------- INITIAL PARAMETERS -----------------------
    # Numbers of nodes, members and loadcases/COMBINATIONS
    nnodes, nmembers = len(Sta.nodesList), len(Sta.membersList)
    ncases = len(Sta.loadcasesList)+len(Sta.COMBINATIONSList)

    # Number of elements per node:
    nelem = np.zeros(nnodes)
    for member in Sta.membersList:
        n1, n2 = member.nodes[0], member.nodes[1]
        nelem[n1] += 1
        nelem[n2] += 1

    # Nodal hinges
    DOFextras, mdone = np.zeros(nnodes), np.zeros(nnodes)
    for i in range(nnodes):
        if Sta.nodesList[i].hinge == 1 and nelem[i] > 0:
            DOFextras[i] = nelem[i] - 1

    # Internal hinges
    DOFint, mintdone = np.zeros(nnodes), np.zeros(nnodes)
    for member in Sta.membersList:
        n1, n2 = member.nodes[0], member.nodes[1]
        if (member.nlib[0] == 1 and
                Sta.nodesList[n1].hinge == 0 and nelem[n1] > 1):
            DOFint[n1] += 1
        if (member.nlib[1] == 1 and
                Sta.nodesList[n2].hinge == 0 and nelem[n2] > 1):
            DOFint[n2] += 1

    for i in range(nnodes):
        if DOFint[i] == nelem[i]:
            DOFextras[i] = nelem[i] - 1
            DOFint[i] = 0

    # Springs and prescribed displacement vectors
    springs, pdispl = [], []
    for node in Sta.nodesList:
        i = Sta.nodesList.index(node)
        springs.append(node.springs[0])
        springs.append(node.springs[1])
        springs.append(node.springs[2])

        pdispl.append(node.pdispl[0])
        pdispl.append(node.pdispl[1])
        pdispl.append(node.pdispl[2])

        for j in range(int(DOFextras[i])):
            springs.append(node.springs[2])
            pdispl.append(node.pdispl[2])

        for j in range(int(DOFint[i])):
            springs.append(node.springs[2])
            pdispl.append(node.pdispl[2])

    # DOF vector creation
    DOF, ndof = [], 0
    for node in Sta.nodesList:
        i = Sta.nodesList.index(node)
        if node.restr[0] > 0:
            DOF.append(-1)
        else:
            DOF.append(ndof)
            ndof += 1

        if node.restr[1] > 0:
            DOF.append(-1)
        else:
            DOF.append(ndof)
            ndof += 1

        if node.restr[2] > 0 and DOFextras[i] == 0 and DOFint[i] == 0:
            DOF.append(-1)
        else:
            if DOFextras[i] != 0:
                for j in range(int(DOFextras[i])+1):
                    DOF.append(ndof)
                    ndof += 1
            elif DOFint[i] != 0:
                for j in range(int(DOFint[i])+1):
                    DOF.append(ndof)
                    ndof += 1
            else:
                DOF.append(ndof)
                ndof += 1

    # Member DOF lists
    MemberDOF = []
    MDOFIndex = []
    for member in Sta.membersList:
        n1, n2 = member.nodes[0], member.nodes[1]
        a1 = int(DOFextras[0:n1].sum(axis=0)+DOFint[0:n1].sum(axis=0)+3*n1)
        a2 = int(DOFextras[0:n2].sum(axis=0)+DOFint[0:n2].sum(axis=0)+3*n2)

        if DOFextras[n1] != 0:
            b1 = a1 + int(mdone[n1])
        elif DOFint[n1] != 0 and member.nlib[0] != 0:
            mintdone[n1] += 1
            b1 = a1 + int(mintdone[n1])
        else:
            b1 = a1

        if DOFextras[n2] != 0:
            b2 = a2 + int(mdone[n2])
        elif DOFint[n2] != 0 and member.nlib[1] != 0:
            mintdone[n2] += 1
            b2 = a2 + int(mintdone[n2])
        else:
            b2 = a2

        mindex = [a1, a1+1, b1+2, a2, a2+1, b2+2]
        mdof = [DOF[index] for index in mindex]

        if DOFextras[n1] > mdone[n1]:
            mdone[n1] += 1
        if DOFextras[n2] > mdone[n2]:
            mdone[n2] += 1

        MDOFIndex.append(mindex)
        MemberDOF.append(mdof)

    # ---------------------- NODAL FORCES VECTORS ----------------------

    # Converting nodal forces into global coordinates
    PX = [np.zeros(len(Sta.loadcasesList)) for i in range(nnodes)]
    PY = [np.zeros(len(Sta.loadcasesList)) for i in range(nnodes)]
    MZ = [np.asarray(Sta.nodesList[i].Mz) for i in range(nnodes)]
    for node in Sta.nodesList:
        n = Sta.nodesList.index(node)
        for i in range(len(Sta.loadcasesList)):
            cos, sin = np.cos(node.Pangle[i]), np.sin(node.Pangle[i])
            PX[n][i] = node.Px[i]*cos + node.Py[i]*(-sin)
            PY[n][i] = node.Px[i]*sin + node.Py[i]*cos

    # Nodal forces vectors
    FN = [np.zeros(ndof) for i in range(ncases)]
    for n in range(ncases):
        cfactors = comboFactors(Sta, n)  # Combo factors for a given case

        for i in range(nnodes):
            # Find the current node's forces for the current case/combination
            Px = np.dot(cfactors, PX[i])
            Py = np.dot(cfactors, PY[i])
            Mz = np.dot(cfactors, MZ[i])

            # Check whether the DOF's are valid, and if so add the nodal forces
            a = int(DOFextras[0:i].sum(axis=0)+DOFint[0:i].sum(axis=0)+3*i)
            if DOF[a] >= 0:
                FN[n][DOF[a]] += Px
            if DOF[a+1] >= 0:
                FN[n][DOF[a+1]] += Py

            for j in range(int(DOFextras[i])+1):
                if DOF[a+2+j] >= 0:
                    FN[n][DOF[a+2+j]] += Mz
            for j in range(int(DOFint[i])):
                if DOF[a+2+j] >= 0:
                    FN[n][DOF[a+2+j]] += Mz

    # ------------------ ROTATION MATRICES ------------------

    # Member rotation matrices
    RotList = []
    for member in Sta.membersList:
        cos, sin = np.cos(member.theta), np.sin(member.theta)
        R = np.array([[cos, sin, 0,   0,   0,  0],
                      [-sin, cos, 0,   0,   0,  0],
                      [0,   0,  1,   0,   0,  0],
                      [0,   0,  0,  cos, sin, 0],
                      [0,   0,  0, -sin, cos, 0],
                      [0,   0,  0,   0,   0,  1]])
        RotList.append(R)

    # Oblique support rotation matrices
    RIList = []
    for member in Sta.membersList:
        start = Sta.nodesList[member.nodes[0]]
        end = Sta.nodesList[member.nodes[1]]

        if start.restr[0]+start.restr[1] == 1:
            theta1 = -start.restr[3]
        else:
            theta1 = 0

        if end.restr[0]+end.restr[1] == 1:
            theta2 = -end.restr[3]
        else:
            theta2 = 0
        cos1, sin1 = np.cos(theta1), np.sin(theta1)
        cos2, sin2 = np.cos(theta2), np.sin(theta2)

        RI = np.array([[cos1, sin1, 0,   0,    0,  0],
                       [-sin1, cos1, 0,   0,    0, 0],
                       [0,    0,   1,   0,    0,   0],
                       [0,    0,   0,  cos2, sin2, 0],
                       [0,    0,   0, -sin2, cos2, 0],
                       [0,    0,   0,   0,    0,   1]])
        RIList.append(RI)

    # ----------------- MEMBER LOAD VECTORS -------------------

    # Converting member loads into member-local coordinates
    QX = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    QY = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    for member in Sta.membersList:
        m = Sta.membersList.index(member)
        cos, sin = np.cos(member.theta), np.sin(member.theta)
        for i in range(len(Sta.loadcasesList)):
            if member.qtype[i] == 0:
                QX[m][i] = member.qx[i]*cos + member.qy[i]*sin
                QY[m][i] = member.qx[i]*(-sin) + member.qy[i]*cos
            else:
                QX[m][i] = member.qx[i]
                QY[m][i] = member.qy[i]

    # Member load vectors
    F0 = [np.zeros(ndof) for i in range(ncases)]
    F0List = [[] for i in range(ncases)]

    for m in range(nmembers):
        material = next((material for material in Sta.materialsList if
                         material.name == Sta.membersList[m].material), None)
        section = next((section for section in Sta.sectionsList if
                        section.name == Sta.membersList[m].section), None)

        L = Sta.membersList[m].length
        E, alpha = material.elasticity, material.thermal
        I, A = section.inertia, section.area
        ysup, yinf = section.ysup, section.yinf
        e, f = member.tensile, member.curvature

        Fimp = np.array([e*E*A/L, 0, 8*E*I*f/L**2,
                        -e*E*A/L, 0, -8*E*I*f/L**2])  # Initial imperf. vector

        for n in range(ncases):
            cfactors = comboFactors(Sta, n)  # Combo factors for a given case

            qx, qy = np.dot(cfactors, QX[m]), np.dot(cfactors, QY[m])
            Tsup = np.dot(cfactors, np.asarray(Sta.membersList[m].Tsup))
            Tinf = np.dot(cfactors, np.asarray(Sta.membersList[m].Tinf))

            T0 = (Tsup*ysup+Tinf*yinf)/(ysup+yinf)
            dT = Tsup-Tinf
            h = ysup+yinf

            Fq = np.array([qx*L/2, qy*L/2, qy*L*L/12,
                           qx*L/2, qy*L/2, -qy*L*L/12])  # Linear loads vector
            FT = np.array([-alpha*E*A*T0, 0, alpha*E*I*dT/h,
                           alpha*E*A*T0, 0, alpha*E*I*dT/h])  # Thermal vector
            F0L = Fq+FT+Fimp
            F0List[n].append(F0L)

            F0G = np.dot(RIList[m].T, np.dot(RotList[m].T, F0L))

            for i in range(6):
                pr = MemberDOF[m][i]
                if pr >= 0:
                    F0[n][pr] += F0G[i]

    # ------------------- LINEAR ITERATIONS -------------------
    niter, tol = Sta.maxiter, Sta.maxerror

    # Stiffness matrices list
    SList = [[] for i in range(ncases)]
    # Prescribed displacement forces list
    FPdispl = [np.zeros(ndof) for i in range(ncases)]
    # Global stiffness matrices
    SDOF = [np.zeros((ndof, ndof)) for i in range(ncases)]
    # Displacement vectors
    d, Fe = [[] for i in range(ncases)], [[] for i in range(ncases)]
    # Reaction forces
    FR = [[[0, 0, 0] for j in range(nnodes)] for i in range(ncases)]

    for n in range(ncases):
        P2 = np.zeros(nmembers)

        for i in range(niter):
            P1 = np.copy(P2)
            d[n], Fe[n], SList[n] = [], [], []
            SDOF[n] = np.zeros((ndof, ndof))
            FR[n] = [[0, 0, 0] for j in range(nnodes)]

            # Stiffness matrices
            for m in range(nmembers):
                L = Sta.membersList[m].length

                material = next((material for material in Sta.materialsList if
                                 material.name == Sta.membersList[m].material),
                                None)
                section = next((section for section in Sta.sectionsList if
                                section.name == Sta.membersList[m].section),
                               None)

                E, I, A = material.elasticity, section.inertia, section.area

                P = P1[m]

                if np.absolute(P) < 1e-6 or E*I < 1e-6:
                    C, S = 4, 2
                else:
                    bL = np.sqrt(np.absolute(P)/(E*I))*L
                    if P < 0:
                        c = (1-bL/np.tan(bL))/bL**2
                        s = (bL/np.sin(bL) - 1)/bL**2
                    else:
                        c = (bL/np.tanh(bL)-1)/bL**2
                        s = (1-bL/np.sinh(bL))/bL**2
                    C, S = c/(c*c-s*s), s/(c*c-s*s)

                a = [E*A/L, 2*E*I*(C+S)/L**3+P/L,
                     E*I*(C+S)/L**2, C*E*I/L, S*E*I/L]

                # Local member stiffness matrix
                SL = np.array([[a[0],  0,     0,   -a[0],  0,     0],
                               [0,   a[1],  a[2],   0,  -a[1],  a[2]],
                               [0,   a[2],  a[3],   0,  -a[2],  a[4]],
                               [-a[0],  0,     0,    a[0],  0,     0],
                               [0,  -a[1], -a[2],   0,   a[1], -a[2]],
                               [0,   a[2],  a[4],   0,  -a[2],  a[3]]])

                # Global member stiffness matrix
                SG = np.dot(RIList[m].T, np.dot(RotList[m].T, SL))
                SG = np.dot(SG, np.dot(RotList[m], RIList[m]))
                SList[n].append(SG)

                # Prescribed displacements vector
                mdx = MDOFIndex[m]
                mpdispl = np.array([pdispl[mdx[0]], pdispl[mdx[1]],
                                    pdispl[mdx[2]], pdispl[mdx[3]],
                                    pdispl[mdx[4]], pdispl[mdx[5]]])

                mpdispl = np.dot(RIList[m], mpdispl)

                Fd = np.dot(SG, mpdispl)  # Prescribed displ. forces vector

                # Prescr. displ. forces arrangement
                for i in range(6):
                    pr = MemberDOF[m][i]
                    if pr >= 0:
                        FPdispl[n][pr] += Fd[i]

                # Member SM arrangement
                for i in range(6):
                    for j in range(6):
                        pr, pc = MemberDOF[m][i], MemberDOF[m][j]
                        if pr >= 0 and pc >= 0:
                            SDOF[n][pr][pc] += SG[i][j]

            # Spring constants arrangemens
            for i in range(len(DOF)):
                pr = DOF[i]
                if pr >= 0:
                    SDOF[n][pr][pr] += springs[i]

            # Final forces vector
            F = F0[n] + FN[n] - FPdispl[n]

            # Displacements vector
            displacements = np.dot(np.linalg.inv(SDOF[n]), F)

            dDOF = []
            for i in range(len(DOF)):
                if DOF[i] < 0:
                    dDOF.append(pdispl[i])
                else:
                    dDOF.append(displacements[DOF[i]])

            dx = np.zeros(nnodes)
            dy = np.zeros(nnodes)
            rz = np.zeros(nnodes)

            # Internal forces vectors
            for m in range(nmembers):
                n1 = Sta.membersList[m].nodes[0]
                n2 = Sta.membersList[m].nodes[1]

                mdx = MDOFIndex[m]
                dm1 = np.array([dDOF[mdx[0]], dDOF[mdx[1]], dDOF[mdx[2]],
                               dDOF[mdx[3]], dDOF[mdx[4]], dDOF[mdx[5]]])
                dx[n1] = dm1[0]
                dy[n1] = dm1[1]
                rz[n1] = dm1[2]

                dx[n2] = dm1[3]
                dy[n2] = dm1[4]
                rz[n2] = dm1[5]

                dm2 = np.dot(np.dot(RotList[m], RIList[m]), dm1)
                d[n].append(dm2)
                FeG = np.dot(SList[n][m], dm1)

                FeL = np.dot(np.dot(RotList[m], RIList[m]), FeG) - F0List[n][m]
                Fe[n].append(FeL)
                FG = np.dot(RIList[m].T, np.dot(RotList[m].T, FeL))

                P2[m] = FeL[3]

                for i in range(3):
                    if (Sta.nodesList[n1].restr[i] == 1 or
                            Sta.nodesList[n1].springs[i]):
                        FR[n][n1][i] += FG[i]
                    if (Sta.nodesList[n2].restr[i] == 1 or
                            Sta.nodesList[n2].springs[i]):
                        FR[n][n2][i] += FG[3+i]

            # Checking for convergence
            dP = np.add(P2, -P1)
            if np.linalg.norm(dP) < tol:
                break

    for n in range(ncases):
        for i in range(nnodes):
            cos = np.cos(-Sta.nodesList[i].restr[3])
            sin = np.sin(-Sta.nodesList[i].restr[3])
            a = FR[n][i][0]*cos + FR[n][i][1]*(-sin)
            b = FR[n][i][0]*sin + FR[n][i][1]*cos
            FR[n][i][0], FR[n][i][1] = a, b

    return [Fe, d, FR]


def dispLinear(Sta):
    '''
    Finds the member deflections for linear analysis,
    using the direct integration method.
    '''
    ncases = len(Sta.loadcasesList) + len(Sta.COMBINATIONSList)
    nmembers = len(Sta.membersList)

    QX = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    QY = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    for member in Sta.membersList:
        m = Sta.membersList.index(member)
        cos, sin = np.cos(member.theta), np.sin(member.theta)
        for i in range(len(Sta.loadcasesList)):
            if member.qtype[i] == 0:
                QX[m][i] = member.qx[i]*cos + member.qy[i]*sin
                QY[m][i] = member.qx[i]*(-sin) + member.qy[i]*cos
            else:
                QX[m][i] = member.qx[i]
                QY[m][i] = member.qy[i]

    maxdispl = 0
    results = []
    for n in range(ncases):
        results.append([])
        k = comboFactors(Sta, n)
        for m in range(nmembers):
            L = Sta.membersList[m].length
            dn = Sta.results[1][n][m]
            V, M = Sta.results[0][n][m][1], -Sta.results[0][n][m][2]

            qy = np.dot(k, QY[m])

            material = next((material for material in Sta.materialsList if
                             material.name == Sta.membersList[m].material),
                            None)
            section = next((section for section in Sta.sectionsList if
                            section.name == Sta.membersList[m].section),
                           None)
            E, I = material.elasticity, section.inertia

            nsteps = max(100, int(L/20))
            nsteps = min(nsteps, 1000)
            nsteps = 20

            h = L/nsteps

            X = np.array([i*h for i in range(1, nsteps)])
            nn = len(X)

            # Final displacements
            u = np.array([dn[0] + (dn[3]-dn[0])*X[i]/L for i in range(nn)])
            v = np.array([dn[1] + dn[2]*X[i] + 1/(E*I)*((M*X[i]**2)/2 +
                          (V*X[i]**3)/6+(qy*X[i]**4)/24) for i in range(nn)])
            r = np.array([dn[2] + 1/(E*I)*((V*X[i]**2)/2 +
                         (qy*X[i]**3)/6) for i in range(nn)])

            X = np.concatenate([[0], X, [L]])
            u = np.concatenate([[dn[0]], u, [dn[3]]])
            v = np.concatenate([[dn[1]], v, [dn[4]]])
            r = np.concatenate([[dn[2]], r, [dn[5]]])

            maxu = np.amax(np.absolute(u))
            maxv = np.amax(np.absolute(v))
            maxdispl = max(maxu, maxv, maxdispl)

            results[n].append([u, v, r, X])

    if maxdispl == 0:
        Sta.resultsConstant[0] = 1
    else:
        Sta.resultsConstant[0] = 20/maxdispl

    return results


def dispNonlinear(Sta):
    '''
    Finds the member deflections for nonlinear analysis,
    using the finite differences method.
    '''
    ncases = len(Sta.loadcasesList) + len(Sta.COMBINATIONSList)
    nmembers = len(Sta.membersList)

    QX = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    QY = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    for member in Sta.membersList:
        m = Sta.membersList.index(member)
        cos, sin = np.cos(member.theta), np.sin(member.theta)
        for i in range(len(Sta.loadcasesList)):
            if member.qtype[i] == 0:
                QX[m][i] = member.qx[i]*cos + member.qy[i]*sin
                QY[m][i] = member.qx[i]*(-sin) + member.qy[i]*cos
            else:
                QX[m][i] = member.qx[i]
                QY[m][i] = member.qy[i]

    maxdispl = 0
    results = []
    for n in range(ncases):
        results.append([])
        k = comboFactors(Sta, n)
        for m in range(nmembers):

            # Input parameters
            L = Sta.membersList[m].length
            dn = Sta.results[1][n][m]
            N, V = Sta.results[0][n][m][0], Sta.results[0][n][m][1]
            M = Sta.results[0][n][m][2]

            qx = np.dot(k, QX[m])
            qy = np.dot(k, QY[m])
            material = next((material for material in Sta.materialsList if
                             material.name == Sta.membersList[m].material),
                            None)
            section = next((section for section in Sta.sectionsList if
                            section.name == Sta.membersList[m].section),
                           None)
            E, I = material.elasticity, section.inertia

            # Element meshing
            nsteps = max(100, int(L/20))
            nsteps = min(nsteps, 1000)

            h = L/nsteps
            X = np.array([i*h for i in range(1, nsteps)])

            # Vector F (for displacement)
            F = np.array([-M+V*X[i]+qy*X[i]*X[i]/2 for i in range(nsteps-1)])
            F[0] -= E*I*dn[1]/h**2
            F[nsteps-2] -= E*I*dn[4]/h**2

            # Vector F prime (for rotation)
            Fp = np.array([V+qy*X[i] for i in range(nsteps-1)])
            Fp[0] -= E*I*dn[2]/h**2
            Fp[nsteps-2] -= E*I*dn[5]/h**2

            # Coefficients matrix
            a, b = E*I/h**2, N-2*E*I/h**2

            A = np.zeros((nsteps-1, nsteps-1))
            A[0][0], A[0][1] = b + qx*X[0]/2, a
            A[nsteps-2][nsteps-2], A[nsteps-2][nsteps-3] = b + qx*X[0]/2, a

            for i in range(1, nsteps-2):
                A[i][i] = b + qx*X[i]/2
                A[i][i-1] = a
                A[i][i+1] = a

            Ainv = np.linalg.inv(A)

            # Final displacements
            u = np.array([dn[0] + (dn[3]-dn[0])*X[i]/L for i in range(len(X))])
            v = np.dot(Ainv, F)
            r = np.dot(Ainv, Fp)

            X = np.concatenate([[0], X, [L]])
            u = np.concatenate([[dn[0]], u, [dn[3]]])
            v = np.concatenate([[dn[1]], v, [dn[4]]])
            r = np.concatenate([[dn[2]], r, [dn[5]]])

            maxu = np.amax(np.absolute(u))
            maxv = np.amax(np.absolute(v))
            maxdispl = max(maxu, maxv, maxdispl)

            results[n].append([u, v, r, X])

    if maxdispl == 0:
        Sta.resultsConstant[0] = 1
    else:
        Sta.resultsConstant[0] = 20/maxdispl

    return results


def internalForces(Sta, runtype):
    '''
    Finds the internal forces for all members.
    '''
    ncases = len(Sta.loadcasesList) + len(Sta.COMBINATIONSList)
    nmembers = len(Sta.membersList)

    QY = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    QX = [np.zeros(len(Sta.loadcasesList)) for i in range(nmembers)]
    for member in Sta.membersList:
        m = Sta.membersList.index(member)
        cos, sin = np.cos(member.theta), np.sin(member.theta)
        for i in range(len(Sta.loadcasesList)):
            if member.qtype[i] == 0:
                QY[m][i] = member.qx[i]*(-sin) + member.qy[i]*cos
                QX[m][i] = member.qx[i]*(cos) + member.qy[i]*sin
            else:
                QY[m][i] = member.qy[i]
                QX[m][i] = member.qx[i]

    results = []
    if runtype == 0:
        for n in range(ncases):
            results.append([])
            k = comboFactors(Sta, n)
            for m in range(nmembers):
                N = [-Sta.results[0][n][m][0], Sta.results[0][n][m][3]]
                V = [Sta.results[0][n][m][1], -Sta.results[0][n][m][4]]
                M = [-Sta.results[0][n][m][2], Sta.results[0][n][m][5]]
                qy = np.dot(k, QY[m])
                X = Sta.displacements[n][m][3]

                Mx = np.array([M[0]+V[0]*X[i]+0.5*qy*X[i]**2
                               for i in range(len(X))])
                results[n].append([N, V, Mx, X])

    else:
        for n in range(ncases):
            results.append([])
            k = comboFactors(Sta, n)
            for m in range(nmembers):
                N = [-Sta.results[0][n][m][0], Sta.results[0][n][m][3]]
                V = [Sta.results[0][n][m][1], -Sta.results[0][n][m][4]]
                M = [-Sta.results[0][n][m][2], Sta.results[0][n][m][5]]
                v = Sta.displacements[n][m][1]
                r = Sta.displacements[n][m][2]
                qy = np.dot(k, QY[m])
                qx = np.dot(k, QX[m])

                X = Sta.displacements[n][m][3]

                Mx = np.array([M[0] + V[0]*X[i] + 0.5*qy*X[i]**2 +
                              (N[0]+0.5*qx)*(v[i]-v[0])
                              for i in range(len(X)-1)])
                Vx = np.array([V[0]+qy*X[i]+0.5*qx*(v[i]-v[0])-0.5*qx*X[i]*r[i]
                               for i in range(len(X)-1)])

                Mx = np.concatenate([Mx, [M[1]]])
                Vx = np.concatenate([Vx, [V[1]]])
                results[n].append([N, Vx, Mx])
    return results


def maxmin(Sta):
    '''
    Finds the maxima and minima of the internal forces for each member,
    across all COMBINATIONS, all loadcases or both.
    '''
    maxType = Sta.maxType.get()

    if maxType == 0:
        n0 = 0
        n1 = len(Sta.loadcasesList)+len(Sta.COMBINATIONSList)
    elif maxType == 1:
        n0 = 0
        n1 = len(Sta.loadcasesList)
    else:
        n0 = len(Sta.loadcasesList)
        n1 = len(Sta.loadcasesList)+len(Sta.COMBINATIONSList)

    Sta.max = [[] for i in range(len(Sta.membersList))]
    Sta.min = [[] for i in range(len(Sta.membersList))]

    for member in range(len(Sta.membersList)):
        maxnormal = np.zeros(n1-n0)
        minnormal = np.zeros(n1-n0)
        for case in range(n0, n1):
            imax = np.argmax(Sta.forces[case][member][0])
            imin = np.argmin(Sta.forces[case][member][0])

            maxnormal[case-n0] = Sta.forces[case][member][0][imax]
            minnormal[case-n0] = Sta.forces[case][member][0][imin]

        casemax = np.argmax(maxnormal)
        Sta.max[member].append(maxnormal[casemax])
        Sta.max[member].append(casemax)

        casemin = np.argmin(minnormal)

        Sta.min[member].append(minnormal[casemin])
        Sta.min[member].append(casemin)

    for member in range(len(Sta.membersList)):
        maxshear = np.zeros(n1-n0)
        minshear = np.zeros(n1-n0)
        for case in range(n0, n1):
            imax = np.argmax(Sta.forces[case][member][1])
            imin = np.argmin(Sta.forces[case][member][1])

            maxshear[case-n0] = Sta.forces[case][member][1][imax]
            minshear[case-n0] = Sta.forces[case][member][1][imin]

        casemax = np.argmax(maxshear)
        Sta.max[member].append(maxshear[casemax])
        Sta.max[member].append(casemax)

        casemin = np.argmin(minshear)
        Sta.min[member].append(minshear[casemin])
        Sta.min[member].append(casemin)

    for member in range(len(Sta.membersList)):
        maxbend = np.zeros(n1-n0)
        minbend = np.zeros(n1-n0)
        for case in range(n0, n1):
            imax = np.argmax(Sta.forces[case][member][2])
            imin = np.argmin(Sta.forces[case][member][2])

            maxbend[case-n0] = Sta.forces[case][member][2][imax]
            minbend[case-n0] = Sta.forces[case][member][2][imin]

        casemax = np.argmax(maxbend)
        Sta.max[member].append(maxbend[casemax])
        Sta.max[member].append(casemax)

        casemin = np.argmin(minbend)
        Sta.min[member].append(minbend[casemin])
        Sta.min[member].append(casemin)

    nscale = max(np.amax(np.absolute(maxnormal)),
                 np.amax(np.absolute(minnormal)))
    vscale = max(np.amax(np.absolute(maxshear)),
                 np.amax(np.absolute(minshear)))
    mscale = max(np.amax(np.absolute(maxbend)),
                 np.amax(np.absolute(minbend)))

    if nscale == 0:
        Sta.resultsConstant[1] = 1
    else:
        Sta.resultsConstant[1] = np.absolute(20/nscale)

    if vscale == 0:
        Sta.resultsConstant[2] = 1
    else:
        Sta.resultsConstant[2] = np.absolute(20/vscale)

    if mscale == 0:
        Sta.resultsConstant[3] = 1
    else:
        Sta.resultsConstant[3] = np.absolute(20/mscale)
