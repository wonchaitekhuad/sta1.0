'''
DRAW MODULE - Contains all the functions related to the drawing of objects
in the canvas.
'''

import tkinter as tk
import numpy as np
import functions as fn


def drawNode(canvas, i, selected):
    '''
    Takes the given node's coordinates from the list and draws
    it on the canvas.
    '''
    r = 2.5
    p = canvas.nodesList[i].coords
    p = fn.canvasCoords(canvas, p)

    colors = [canvas.colorScheme[1], canvas.colorScheme[2],
              canvas.colorScheme[0]]

    if canvas.nodesList[i].hinge == 1:
        if selected == 1:
            canvas.canvas.create_oval(p[0]-1.5*r, p[1]+1.5*r, p[0]+1.5*r,
                                      p[1]-1.5*r, fill=colors[2],
                                      outline=colors[1], width=2,
                                      tags=('node', i))
            canvas.canvas.create_text([p[0]+8, p[1]-8], text=str(i),
                                      fill=colors[1])
        else:
            canvas.canvas.create_oval(p[0]-1.5*r, p[1]+1.5*r, p[0]+1.5*r,
                                      p[1]-1.5*r,  fill=colors[2],
                                      outline=colors[0], width=2,
                                      tags=('node', i))

    else:
        if selected == 1:
            canvas.canvas.create_text([p[0]+8, p[1]-8],
                                      text=str(i), fill=colors[1])
            canvas.canvas.create_oval(p[0]-r, p[1]+r, p[0]+r, p[1]-r,
                                      fill=colors[1], tags=('node', i))
        else:
            canvas.canvas.create_oval(p[0]-r, p[1]+r, p[0]+r, p[1]-r,
                                      fill=colors[0], tags=('node', i))


def drawMember(canvas, i, selected):
    '''
    Takes the given member's coordinates from the list and draws
    it on the canvas.
    '''
    w = 1.8
    p1 = canvas.membersList[i].p1
    p2 = canvas.membersList[i].p2
    p1 = fn.canvasCoords(canvas, p1)
    p2 = fn.canvasCoords(canvas, p2)

    L = fn.distance(p1, p2)
    theta = canvas.membersList[i].theta
    tAngle = fn.textAngle(theta*180/np.pi)
    k = fn.angleSign(theta)

    material = canvas.membersList[i].material
    section = canvas.membersList[i].section
    length = fn.unitConvert('cm', canvas.units[0],
                            canvas.membersList[i].length)

    colors = [canvas.colorScheme[3], canvas.colorScheme[4],
              canvas.colorScheme[0], canvas.colorScheme[6]]

    if selected == 1:
        canvas.canvas.create_line(p1, p2, fill=colors[1],
                                  width=w, tags=('member', i))
        pt1 = fn.rotate([p1[0], p1[1]-k*10], p1, theta)
        pt2 = fn.rotate([p1[0] + L, p1[1]-k*10], p1, theta)
        pt3 = fn.rotate([p1[0] + L/2, p1[1]-k*10], p1, theta)

        canvas.canvas.create_text(pt1, text=material, fill=colors[1],
                                  angle=tAngle, anchor=tk.W)
        canvas.canvas.create_text(pt2, text=section, fill=colors[1],
                                  angle=tAngle, anchor=tk.E)
        canvas.canvas.create_text(pt3, text='{:.2f}'.format(length)+' ' +
                                  canvas.units[0], fill=colors[1],
                                  angle=tAngle)
    else:
        canvas.canvas.create_line(p1, p2, fill=colors[0],
                                  width=w, tags=('member', i))

    if canvas.membersList[i].nlib[0] == 1:
        pa = fn.rotate([p1[0] + 7, p1[1]], p1, theta)
        canvas.canvas.create_oval(pa[0] - 4.5, pa[1] - 4.5, pa[0] + 4.5,
                                  pa[1] + 4.5, fill=colors[2], width=1.5,
                                  outline=colors[3], tags=('member', i))

    if canvas.membersList[i].nlib[1] == 1:
        pb = fn.rotate([p1[0] + L - 7, p1[1]], p1, theta)
        canvas.canvas.create_oval(pb[0]-4.5, pb[1] - 4.5, pb[0] + 4.5,
                                  pb[1] + 4.5, fill=colors[2], width=1.5,
                                  outline=colors[3], tags=('member', i))


def drawMemberLoads(canvas, member, loadcase):
    '''
    Draws the distributed loads on a member.
    '''
    p1 = canvas.membersList[member].p1
    p2 = canvas.membersList[member].p2
    theta = canvas.membersList[member].theta
    k = fn.angleSign(theta)
    tAngle = fn.textAngle(theta*180/np.pi)

    qx = fn.unitConvert('kN/cm', canvas.units[3],
                        canvas.membersList[member].qx[loadcase])
    qy = fn.unitConvert('kN/cm', canvas.units[3],
                        canvas.membersList[member].qy[loadcase])
    qtype = canvas.membersList[member].qtype[loadcase]

    p1 = fn.canvasCoords(canvas, p1)
    p2 = fn.canvasCoords(canvas, p2)
    Lcanvas = fn.distance(p1, p2)

    color = canvas.colorScheme[2]

    if Lcanvas != 0:
        n = int(Lcanvas/20)
    else:
        n = 1

    if qtype == 1:
        if qy != 0:
            if qy > 0:
                arrow = tk.LAST
            else:
                arrow = tk.FIRST

            for i in range(n+1):
                x = i*Lcanvas/n
                px = fn.rotate([p1[0]+x, p1[1]-k*5], p1, theta)
                pq = fn.rotate([p1[0]+x, p1[1]-k*30], p1, theta)
                canvas.canvas.create_line(px, pq, arrow=arrow, fill=color)

            textpos = fn.rotate([p1[0]+Lcanvas/2, p1[1]-k*40], p1, theta)
            pq1, pq2 = (fn.rotate([p1[0], p1[1]-k*30], p1, theta),
                        fn.rotate([p1[0]+Lcanvas, p1[1]-k*30], p1, theta))
            canvas.canvas.create_line(pq1, pq2, fill=color)
            canvas.canvas.create_text(textpos,
                                      text='{:.2f}'.format(np.absolute(qy))+' '
                                      + canvas.units[3], fill=color,
                                      angle=tAngle)

        if qx != 0:
            if qx > 0:
                arrow = tk.LAST
            else:
                arrow = tk.FIRST

            for i in range(1, n):
                x = i*Lcanvas/n+1
                px = fn.rotate([p1[0]+x, p1[1]], p1, theta)
                pq = fn.rotate([p1[0]+x+1, p1[1]], p1, theta)
                canvas.canvas.create_line(px, pq, arrow=arrow, fill=color)

            textpos = fn.rotate([p1[0]+Lcanvas/2, p1[1]+k*15], p1, theta)
            canvas.canvas.create_text(textpos,
                                      text='{:.2f}'.format(np.absolute(qx))+' '
                                      + canvas.units[3], fill=color,
                                      angle=tAngle)

    else:
        if qy != 0:
            if theta == np.pi/2 or theta == 3*np.pi/2:
                if ((theta == np.pi/2 and qy > 0) or
                        (theta == 3*np.pi/2 and qy < 0)):
                    arrow = tk.LAST
                else:
                    arrow = tk.FIRST

                for i in range(1, n):
                    x = i*Lcanvas/n+1
                    px = fn.rotate([p1[0]+x, p1[1]], p1, theta)
                    pq = fn.rotate([p1[0]+x+1, p1[1]], p1, theta)
                    canvas.canvas.create_line(px, pq, arrow=arrow, fill=color)

                textpos = fn.rotate([p1[0]+Lcanvas/2, p1[1]+k*15], p1, theta)
                canvas.canvas.create_text(textpos,
                                          text='{:.2f}'.format(np.absolute(qy))
                                          + ' ' + canvas.units[3], fill=color,
                                          angle=tAngle)

            else:
                if qy > 0:
                    arrow = tk.LAST
                else:
                    arrow = tk.FIRST

                for i in range(n+1):
                    x = i*Lcanvas/n
                    px = fn.rotate([p1[0]+x, p1[1]], p1, theta)
                    px = [px[0], px[1]-5]
                    pq = [px[0], px[1]-30]
                    canvas.canvas.create_line(px, pq, arrow=arrow, fill=color)

                textpos = fn.rotate([p1[0]+Lcanvas/2, p1[1]], p1, theta)
                textpos = [textpos[0], textpos[1]-45]
                pq1, pq2 = [p1[0], p1[1]-35], [p2[0], p2[1]-35]
                canvas.canvas.create_line(pq1, pq2, fill=color)
                canvas.canvas.create_text(textpos,
                                          text='{:.2f}'.format(np.absolute(qy))
                                          + ' '+canvas.units[3], fill=color,
                                          angle=tAngle, justify=tk.CENTER)

        if qx != 0:
            if theta == 0 or theta == np.pi:
                if (theta == 0 and qx > 0) or (theta == np.pi and qx < 0):
                    arrow = tk.LAST
                else:
                    arrow = tk.FIRST

                for i in range(1, n):
                    x = i*Lcanvas/n+1
                    px = fn.rotate([p1[0]+x, p1[1]], p1, theta)
                    pq = fn.rotate([p1[0]+x+1, p1[1]], p1, theta)
                    canvas.canvas.create_line(px, pq, arrow=arrow, fill=color)

                textpos = fn.rotate([p1[0]+Lcanvas/2, p1[1]+k*15], p1, theta)
                canvas.canvas.create_text(textpos,
                                          text='{:.2f}'.format(np.absolute(qx))
                                          + ' ' + canvas.units[3], fill=color,
                                          angle=tAngle)

            else:
                if (theta > np.pi/2 and theta < np.pi) or theta > 3*np.pi/2:
                    a = -1
                else:
                    a = 1

                if (a == 1 and qx > 0) or (a == -1 and qx < 0):
                    arrow = tk.LAST
                elif (a == 1 and qx < 0) or (a == -1 and qx > 0):
                    arrow = tk.FIRST

                for i in range(n+1):
                    x = i*Lcanvas/n
                    px = fn.rotate([p1[0]+x, p1[1]], p1, theta)
                    px = [px[0]+a*5, px[1]]
                    pq = [px[0]+a*30, px[1]]
                    canvas.canvas.create_line(px, pq, arrow=arrow, fill=color)

                textpos = fn.rotate([p1[0]+Lcanvas/2, p1[1]], p1, theta)
                textpos = [textpos[0]+a*50, textpos[1]]
                pq1, pq2 = [p1[0]+a*35, p1[1]], [p2[0]+a*35, p2[1]]
                canvas.canvas.create_line(pq1, pq2, fill=color)
                canvas.canvas.create_text(textpos,
                                          text='{:.2f}'.format(np.absolute(qx))
                                          + ' '+canvas.units[3], fill=color,
                                          angle=tAngle, justify=tk.CENTER)


def drawNodalForces(canvas, i, loadcase):
    '''
    Draws the nodal forces Px, Py and Mz for a given node and a given loadcase.
    '''
    p = canvas.nodesList[i].coords
    Px = fn.unitConvert('kN', canvas.units[1],
                        canvas.nodesList[i].Px[loadcase])
    Py = fn.unitConvert('kN', canvas.units[1],
                        canvas.nodesList[i].Py[loadcase])
    Mz = fn.unitConvert('kN.cm', canvas.units[2],
                        canvas.nodesList[i].Mz[loadcase])
    theta = canvas.nodesList[i].Pangle[loadcase]
    tAngle = fn.textAngle(theta)

    p = fn.canvasCoords(canvas, p)

    color = canvas.colorScheme[5]

    if Px < 0:
        thetaX = theta
    else:
        thetaX = theta + np.pi
    if Py < 0:
        thetaY = theta
    else:
        thetaY = theta + np.pi

    if Px != 0:
        p1 = fn.rotate([p[0]+3, p[1]], p, thetaX)
        p2 = fn.rotate([p[0]+63, p[1]], p, thetaX)
        textpos = fn.rotate([p[0]+63, p[1]-10], p, thetaX)

        canvas.canvas.create_line(p1, p2, arrow=tk.FIRST, fill=color,
                                  width=2, arrowshape=(12, 15, 4.5))
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(Px)) + ' ' +
                                  canvas.units[1], fill=color, angle=tAngle)

    if Py != 0:
        p1 = fn.rotate([p[0], p[1]-3], p, thetaY)
        p2 = fn.rotate([p[0], p[1]-63], p, thetaY)
        textpos = fn.rotate([p[0]+10, p[1]-68], p, thetaY)

        canvas.canvas.create_line(p1, p2, arrow=tk.FIRST, fill=color,
                                  width=2, arrowshape=(12, 15, 4.5))
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(Py)) + ' ' +
                                  canvas.units[1], fill=color, angle=tAngle)

    if Mz != 0:
        curve = []
        for i in range(20):
            angle = np.pi*(-1/6 + (5/6)*i/20)
            p1 = fn.rotate([p[0]+25, p[1]], p, angle)
            curve.append(p1)
        if Mz > 0:
            canvas.canvas.create_line(curve, arrow=tk.LAST, fill=color)
            textpos = fn.rotate([p[0]+35, p[1]], p, 2*np.pi/3)
        else:
            canvas.canvas.create_line(curve, arrow=tk.FIRST, fill=color)
            textpos = fn.rotate([p[0]+35, p[1]], p, np.pi/30)
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(Mz)) + ' ' +
                                  canvas.units[2], fill=color)


def drawSupportY(canvas, i, type):
    '''
    Draws a 1-direction triangle support, fixed at the given node and rotated
    by the given angle.
    '''
    p = canvas.nodesList[i].coords
    p = fn.canvasCoords(canvas, p)
    q = [[p[0]+15, p[1]+20], [p[0]-15, p[1]+20],
         [p[0]+15, p[1]+25], [p[0]-15, p[1]+25]]
    theta = canvas.nodesList[i].restr[3]

    color = canvas.colorScheme[6]
    if type == 'x':
        theta -= np.pi/2
    for i in range(4):
        q[i] = fn.rotate(q[i], p, theta)

    canvas.canvas.create_polygon(p, q[0], q[1],
                                 fill=color, tags=('support', i))
    canvas.canvas.create_line(q[2], q[3], fill=color, tags=('support', i))


def drawSupportZ(canvas, i):
    '''
    Draws a z-direction rotation fix, fixed at the given node and rotated by
    the given angle.
    '''
    p = canvas.nodesList[i].coords
    p = fn.canvasCoords(canvas, p)
    q = [[p[0]+10, p[1]-10], [p[0]+10, p[1]+10],
         [p[0]-10, p[1]+10], [p[0]-10, p[1]-10]]
    theta = canvas.nodesList[i].restr[3]
    color = canvas.colorScheme[6]

    for i in range(4):
        q[i] = fn.rotate(q[i], p, theta)

    canvas.canvas.create_polygon(q[0], q[1], q[2], q[3],
                                 fill=color, tags=('support', i))


def drawSupportXY(canvas, n):
    '''
    Draws a 2-direction triangle support, fixed at the given node and rotated
    by the given angle.
    '''
    p = canvas.nodesList[n].coords                      # original point
    p = fn.canvasCoords(canvas, p)

    q = [[p[0]+15, p[1]+20], [p[0]-15, p[1]+20]]        # triangle vertices
    r1 = [[p[0]-9, p[1]+20], [p[0]-3, p[1]+20],
          [p[0]+3, p[1]+20], [p[0]+9, p[1]+20]]
    r2 = [[p[0]-15, p[1]+26], [p[0]-9, p[1]+26],
          [p[0]-3, p[1]+26], [p[0]+3, p[1]+26]]

    theta = canvas.nodesList[n].restr[3]
    color = canvas.colorScheme[6]

    for i in range(2):
        q[i] = fn.rotate(q[i], p, theta)
        r1[i] = fn.rotate(r1[i], p, theta)
        r1[i+2] = fn.rotate(r1[i+2], p, theta)
        r2[i] = fn.rotate(r2[i], p, theta)
        r2[i+2] = fn.rotate(r2[i+2], p, theta)
        canvas.canvas.create_line(r1[i], r2[i],
                                  fill=color, tags=('support', n))
        canvas.canvas.create_line(r1[i+2], r2[i+2],
                                  fill=color, tags=('support', n))

    canvas.canvas.create_polygon(p, q[0], q[1],
                                 fill=color, tags=('support', n))


def drawSupportXYZ(canvas, n):
    '''
    Draws a 3-direction encastre support, fixed at the given node and rotated
    by the given angle.
    '''
    p = canvas.nodesList[n].coords          # original point
    p = fn.canvasCoords(canvas, p)
    q = [[p[0]+15, p[1]], [p[0]-15, p[1]]]
    r1 = [[p[0]-9, p[1]], [p[0]-3, p[1]], [p[0]+3, p[1]], [p[0]+9, p[1]]]
    r2 = [[p[0]-15, p[1]+6], [p[0]-9, p[1]+6],
          [p[0]-3, p[1]+6], [p[0]+3, p[1]+6]]
    theta = canvas.nodesList[n].restr[3]
    color = canvas.colorScheme[6]

    for i in range(2):
        q[i] = fn.rotate(q[i], p, theta)
        r1[i] = fn.rotate(r1[i], p, theta)
        r1[i+2] = fn.rotate(r1[i+2], p, theta)
        r2[i] = fn.rotate(r2[i], p, theta)
        r2[i+2] = fn.rotate(r2[i+2], p, theta)

        canvas.canvas.create_line(r1[i], r2[i],
                                  fill=color, tags=('support', n))
        canvas.canvas.create_line(r1[i+2], r2[i+2],
                                  fill=color, tags=('support', n))

    canvas.canvas.create_line(q[0], q[1], width=1.5,
                              fill=color, tags=('support', n))


def drawSupportYZ(canvas, n, type):
    '''
    Draws a 2-direction moving encastre support, fixed at the given node and
    rotated by the given angle.
    '''
    p = canvas.nodesList[n].coords              # original point
    p = fn.canvasCoords(canvas, p)
    q = [[p[0]+15, p[1]], [p[0]-15, p[1]],
         [p[0]+15, p[1]+7], [p[0]-15, p[1]+7]]

    r1 = [[p[0]-9, p[1]+7], [p[0]-3, p[1]+7],
          [p[0]+3, p[1]+7], [p[0]+9, p[1]+7]]

    r2 = [[p[0]-15, p[1]+13], [p[0]-9, p[1]+13],
          [p[0]-3, p[1]+13], [p[0]+3, p[1]+13]]

    theta = canvas.nodesList[n].restr[3]
    color = canvas.colorScheme[6]

    if type == 'x':
        theta -= np.pi/2

    for i in range(4):
        q[i] = fn.rotate(q[i], p, theta)
        r1[i] = fn.rotate(r1[i], p, theta)
        r2[i] = fn.rotate(r2[i], p, theta)

        canvas.canvas.create_line(r1[i], r2[i],
                                  fill=color, tags=('support', n))

    canvas.canvas.create_line(q[0], q[1], width=1.5,
                              fill=color, tags=('support', n))
    canvas.canvas.create_line(q[2], q[3], width=1.5,
                              fill=color, tags=('support', n))


def drawSpring(canvas, n, type):
    '''
    Draws the spring symbol.
    '''
    p = canvas.nodesList[n].coords
    k = [fn.unitConvert('kN/cm', canvas.units[13],
                        canvas.nodesList[n].springs[0]),
         fn.unitConvert('kN/cm', canvas.units[13],
                        canvas.nodesList[n].springs[1])]
    p = fn.canvasCoords(canvas, p)
    x = p[0]
    y = p[1]

    if type == 'x':
        theta = -np.pi/2
    else:
        theta = 0

    spring = [[x, y], [x, y+8], [x-7.5, y+10.5], [x+7.5, y+15.5],
              [x-7.5, y+21.5], [x, y+24], [x, y+30]]
    ground1 = [[x-15, y+30], [x-9, y+30], [x-3, y+30],
               [x+3, y+30], [x+9, y+30], [x+15, y+30]]
    ground2 = [[x-21, y+36], [x-15, y+36], [x-9, y+36],
               [x-3, y+36], [x+3, y+36], [x+9, y+36]]

    for i in range(6):
        spring[i] = fn.rotate(spring[i], p, theta)
        ground1[i] = fn.rotate(ground1[i], p, theta)
        ground2[i] = fn.rotate(ground2[i], p, theta)
        canvas.canvas.create_line(ground1[i], ground2[i])
    textpos = fn.rotate([x-20, y+50], p, theta)
    spring[6] = fn.rotate(spring[6], p, theta)
    canvas.canvas.create_line(ground1[0], ground1[5], width=1.5)

    if theta == 0:
        canvas.canvas.create_text(textpos, text='{:.2f}'.format(k[1]) +
                                  ' ' + canvas.units[13])
    else:
        canvas.canvas.create_text(textpos, text='{:.2f}'.format(k[0]) +
                                  ' ' + canvas.units[13])

    canvas.canvas.create_line(spring)


def drawPrescribedDispl(canvas, n):
    '''
    Draws a given node's prescribed displacement.
    '''
    p = canvas.nodesList[n].coords
    p = fn.canvasCoords(canvas, p)
    pdispl = [fn.unitConvert('cm', canvas.units[10],
                             canvas.nodesList[n].pdispl[0]),
              fn.unitConvert('cm', canvas.units[10],
                             canvas.nodesList[n].pdispl[1]),
              fn.unitConvert('rad', canvas.units[11],
                             canvas.nodesList[n].pdispl[2])]

    theta = canvas.nodesList[n].restr[3]
    tAngle = fn.textAngle(theta)

    if pdispl[0] != 0:
        p1, p2 = [p[0]-10, p[1]+10], [p[0]-45, p[1]+10]
        textpos = [p[0]-45, p[1]+25]

        p1 = fn.rotate(p1, p, theta)
        p2 = fn.rotate(p2, p, theta)
        textpos = fn.rotate(textpos, p, theta)
        if pdispl[0] > 0:
            canvas.canvas.create_line(p1, p2, fill=canvas.colorScheme[4],
                                      width=1.5, arrow=tk.FIRST)
        else:
            canvas.canvas.create_line(p1, p2, fill=canvas.colorScheme[4],
                                      width=1.5, arrow=tk.LAST)

        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(pdispl[0]))
                                  + ' '+canvas.units[10],
                                  fill=canvas.colorScheme[4], angle=tAngle)

    if pdispl[1] != 0:
        p1, p2, textpos = [p[0], p[1]+40], [p[0], p[1]+85], [p[0]-5, p[1]+90]
        p1 = fn.rotate(p1, p, theta)
        p2 = fn.rotate(p2, p, theta)
        if pdispl[0] > 0:
            canvas.canvas.create_line(p1, p2,
                                      fill=canvas.colorScheme[4],
                                      width=1.5, arrow=tk.FIRST)
        else:
            canvas.canvas.create_line(p1, p2,
                                      fill=canvas.colorScheme[4],
                                      width=1.5, arrow=tk.LAST)

        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(pdispl[1]))
                                  + ' ' + canvas.units[10],
                                  fill=canvas.colorScheme[4], angle=tAngle,
                                  justify=tk.RIGHT)

    if pdispl[2] != 0:
        p1, p2 = [p[0], p[1]+5], [p[0], p[1]+35]
        p3 = [p[0]-np.sign(pdispl[2])*10, p[1]+2],
        textpos = [p[0]-np.sign(pdispl[2])*5, p[1]+40]

        p1 = fn.rotate(p1, p, theta)
        p2 = fn.rotate(p2, p, theta)
        p3 = fn.rotate(p3, p, theta)
        canvas.canvas.create_line(p1, p2, fill=canvas.colorScheme[4])
        canvas.canvas.create_line(p2, p3, width=2, fill=canvas.colorScheme[4])
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(pdispl[2]))
                                  + ' ' + canvas.units[11],
                                  fill=canvas.colorScheme[4], angle=tAngle,
                                  justify=tk.RIGHT)


def drawTorsionSpring(canvas, n):
    '''
    Draws the torsion spring symbol.
    '''
    p1 = canvas.nodesList[n].coords
    p1 = fn.canvasCoords(canvas, p1)
    k = fn.unitConvert('kN.cm/rad', canvas.units[14],
                       canvas.nodesList[n].springs[2])
    array = []
    for i in range(24):
        R = 0.8*i
        theta = -4*np.pi*i/25
        p = fn.rotate([p1[0]+R, p1[1]], p1, theta)
        array.append(p)
    x = p[0]+15
    y = p[1]
    array.append([x, y])
    ground1 = [[x, y-15], [x, y-7.5], [x, y], [x, y+7.5], [x, y+15]]
    ground2 = [[x+4, y-19], [x+4, y-11.5],
               [x+4, y-4], [x+4, y+3.5], [x+4, y+11.5]]

    canvas.canvas.create_line(ground1[0], ground1[4], width=1.5)
    for i in range(5):
        canvas.canvas.create_line(ground1[i], ground2[i])

    canvas.canvas.create_line(array)
    canvas.canvas.create_text(p1[0]+20, p1[1]+20,
                              text='{:.2f}'.format(k)+' '+canvas.units[14])


def drawImperfections(canvas, member, selected):
    '''
    Draws a given member's initial imperfections.
    '''
    p1 = fn.canvasCoords(canvas, canvas.membersList[member].p1)
    p2 = fn.canvasCoords(canvas, canvas.membersList[member].p2)

    L = fn.distance(p1, p2)
    theta = canvas.membersList[member].theta
    tAngle = fn.textAngle(theta*180/np.pi)

    material = canvas.membersList[member].material
    section = canvas.membersList[member].section
    length = fn.unitConvert('cm', canvas.units[0],
                            canvas.membersList[member].length)

    e = fn.unitConvert('cm', canvas.units[10],
                       canvas.membersList[member].tensile)
    f = fn.unitConvert('cm', canvas.units[10],
                       canvas.membersList[member].curvature)

    if selected == 0:
        color = canvas.colorScheme[3]
    else:
        color = canvas.colorScheme[4]

    color2 = canvas.colorScheme[6]

    if selected == 1:
        pt1 = fn.rotate([p1[0], p1[1]-10], p1, theta)
        pt2 = fn.rotate([p1[0]+L, p1[1]-10], p1, theta)
        pt3 = fn.rotate([p1[0]+L/2, p1[1]-10], p1, theta)
        canvas.canvas.create_text(pt1, text=material, fill=color,
                                  angle=tAngle, anchor=tk.W)
        canvas.canvas.create_text(pt2, text=section, fill=color,
                                  angle=tAngle, anchor=tk.E)
        canvas.canvas.create_text(pt3, text='{:.2f}'.format(length) +
                                  ' '+canvas.units[0], fill=color,
                                  angle=tAngle)

    if e != 0 and f == 0:
        textpos = fn.rotate([p1[0]+0.9*L, p1[1]+8], p1, theta)
        pa = fn.rotate([p1[0]+0.8*L, p1[1]], p1, theta)
        canvas.canvas.create_line(p1, pa, fill=color, width=2.5,
                                  tags=('member', member))

        string = str(e) + ' ' + canvas.units[10]
        if e > 0:
            arrow = tk.LAST
        else:
            arrow = tk.FIRST
        canvas.canvas.create_line(pa, p2, fill=canvas.colorScheme[1],
                                  width=1, dash=(5, 8), arrow=arrow,
                                  tags=('member', member))
        canvas.canvas.create_text(textpos, fill=canvas.colorScheme[1],
                                  text=string, angle=tAngle)

    elif e == 0 and f != 0:
        d = 0.03*L
        R = 0.125*(4*d*d+L*L)/d
        p0 = [L/2, -(L*L)/(8*d)+d/2]

        string = str(f) + ' ' + canvas.units[10]

        curve = []
        for i in range(16):
            xL = i*L/15
            Q = np.sqrt(-(p0[0]**2) + 2*p0[0]*xL + R**2 - (xL**2))

            if f > 0:
                yL = -p0[1] - Q
            else:
                yL = + p0[1] + Q

            p = fn.rotate([p1[0]+xL, p1[1]+yL], p1, theta)
            curve.append(p)

        canvas.canvas.create_line(curve, fill=color, width=2.5,
                                  tags=('member', member))
        canvas.canvas.create_line(p1, p2, fill=canvas.colorScheme[1],
                                  width=1, dash=(5, 8),
                                  tags=('member', member))

        textpos = fn.rotate([p1[0]+L/2, p1[1]-d/2], p1, theta)
        canvas.canvas.create_text(textpos, fill=canvas.colorScheme[1],
                                  text=string, angle=tAngle)

    elif e != 0 and f != 0:
        d = 0.03*L
        R = 0.125*(4*d*d+L*L)/d
        p0 = [L/2, -(L*L)/(8*d)+d/2]
        if e > 0:
            arrow = tk.LAST
        else:
            arrow = tk.FIRST

        string1 = str(e) + ' ' + canvas.units[10]
        string2 = str(f) + ' ' + canvas.units[10]

        curve1, curve2 = [], []
        for i in range(12):
            xL = i*L/15
            Q = np.sqrt(-(p0[0]**2) + 2*p0[0]*xL + R**2 - (xL**2))

            if f > 0:
                yL = -p0[1] - Q
            else:
                yL = + p0[1] + Q

            p = fn.rotate([p1[0]+xL, p1[1]+yL], p1, theta)
            curve1.append(p)
        for i in range(11, 16):
            xL = i*L/15
            Q = np.sqrt(-(p0[0]**2) + 2*p0[0]*xL + R**2 - (xL**2))

            if f > 0:
                yL = -p0[1] - Q
            else:
                yL = + p0[1] + Q
            p = fn.rotate([p1[0]+xL, p1[1]+yL], p1, theta)
            curve2.append(p)
        canvas.canvas.create_line(curve1, fill=color,
                                  width=2.5, tags=('member', member))
        canvas.canvas.create_line(curve2, fill=canvas.colorScheme[1],
                                  width=1, dash=(5, 8), arrow=arrow,
                                  tags=('member', member))

        canvas.canvas.create_line(p1, p2, fill=canvas.colorScheme[1], width=1,
                                  dash=(5, 8), tags=('member', member))

        textpos1 = fn.rotate([p1[0]+0.9*L, p1[1]+8], p1, theta)
        textpos2 = fn.rotate([p1[0]+L/2, p1[1]+np.sign(f)*d/2], p1, theta)

        canvas.canvas.create_text(textpos1, fill=canvas.colorScheme[1],
                                  text=string1, angle=tAngle)
        canvas.canvas.create_text(textpos2, fill=canvas.colorScheme[1],
                                  text=string2, angle=tAngle)

    if canvas.membersList[member].nlib[0] == 1:
        pa = fn.rotate([p1[0]+7, p1[1]], p1, theta)
        canvas.canvas.create_oval(pa[0]-4.5, pa[1]-4.5, pa[0]+4.5, pa[1]+4.5,
                                  fill=color, width=1.5, outline=color2,
                                  tags=('member', member))

    if canvas.membersList[member].nlib[1] == 1:
        pb = fn.rotate([p1[0]+L-7, p1[1]], p1, theta)
        canvas.canvas.create_oval(pb[0]-4.5, pb[1]-4.5, pb[0]+4.5, pb[1]+4.5,
                                  fill=color, width=1.5, outline=color2,
                                  tags=('member', member))


def drawThermalLoads(canvas, n):
    '''
    Draws the thermal loads on a member.
    '''
    case = canvas.currentLoadcase
    p1 = canvas.membersList[n].p1
    p2 = canvas.membersList[n].p2

    theta = canvas.membersList[n].theta

    tAngle = fn.textAngle(theta*180/np.pi)

    p1 = fn.canvasCoords(canvas, p1)
    p2 = fn.canvasCoords(canvas, p2)
    Lcanvas = fn.distance(p1, p2)

    colors = [canvas.colorScheme[2],
              canvas.colorScheme[5], canvas.colorScheme[1]]

    textpos1 = fn.rotate([p1[0]+Lcanvas/2, p1[1]-10], p1, theta)
    textpos2 = fn.rotate([p1[0]+Lcanvas/2, p1[1]+10], p1, theta)

    if canvas.membersList[n].Tsup[case] != 0:
        pa = fn.rotate([p1[0], p1[1]-3], p1, theta)
        pb = fn.rotate([p1[0]+Lcanvas, p1[1]-3], p1, theta)
        string = str(canvas.membersList[n].Tsup[case]) + ' ' + canvas.units[4]

        canvas.canvas.create_text(textpos1, fill=colors[2],
                                  text=string, angle=tAngle)

        if (canvas.membersList[n].Tsup[case] >=
                canvas.membersList[n].Tinf[case]):
            canvas.canvas.create_line(pa, pb, fill=colors[0], width=3)
        else:
            canvas.canvas.create_line(pa, pb, fill=colors[1], width=3)

    if canvas.membersList[n].Tinf[case] != 0:
        pa = fn.rotate([p1[0], p1[1]+3], p1, theta)
        pb = fn.rotate([p1[0]+Lcanvas, p1[1]+3], p1, theta)
        string = str(canvas.membersList[n].Tinf[case]) + ' ' + canvas.units[4]
        canvas.canvas.create_text(textpos2, fill=colors[2],
                                  text=string, angle=tAngle)

        if (canvas.membersList[n].Tinf[case] >=
                canvas.membersList[n].Tsup[case]):
            canvas.canvas.create_line(pa, pb, fill=colors[0], width=3)
        else:
            canvas.canvas.create_line(pa, pb, fill=colors[1], width=3)


def drawShearForce(canvas, member):
    '''
    Draws the shear force diagram for a given member.
    Direction-independent: handles columns/beams drawn in any orientation.
    '''
    elem = canvas.membersList[member]
    p1_orig = fn.canvasCoords(canvas, elem.p1)
    p2_orig = fn.canvasCoords(canvas, elem.p2)
    L = elem.length
    
    # Make copies for potential reversal
    p1 = list(p1_orig)
    p2 = list(p2_orig)
    Lcanvas = fn.distance(p1, p2)

    theta = elem.theta
    k = fn.angleSign(theta)
    tAngle = fn.textAngle(theta*180/np.pi)

    f = k*canvas.resultsScale[2]
    
    # Detect if member is drawn in reverse direction
    reverse = p2[0] < p1[0] or (p2[0] == p1[0] and p2[1] < p1[1])
    if reverse:
        p1, p2 = p2, p1

    if canvas.currentLoadcase != -1:
        case = canvas.currentLoadcase
    else:
        case = (len(canvas.loadcasesList) + canvas.currentCombination)

    V = canvas.forces[case][member][1]
    X = canvas.displacements[case][member][3]
    
    # Reverse arrays if member was drawn backwards
    if reverse:
        V = list(reversed(V))
        X = [L - x for x in reversed(X)]
    
    V0, V1 = V[0], V[-1]
    V0t = fn.unitConvert('kN', canvas.units[1], V0)
    V1t = fn.unitConvert('kN', canvas.units[1], V1)

    if np.absolute(V0) > 0.1:
        p1p = fn.rotate([p1[0], p1[1]-f*V0], p1, theta)
        if np.absolute(V0-V1) > 0.01:
            textpos = fn.rotate([p1[0],
                                 p1[1]-f*V0-k*np.sign(V0)*12], p1, theta)
        else:
            textpos = fn.rotate([p1[0]+Lcanvas/2,
                                 p1[1]-f*V0-k*np.sign(V0)*12], p1, theta)

        canvas.canvas.create_line(p1p, p1, fill='red')
        canvas.canvas.create_text(textpos, text='{:.2f}'.format(V0t),
                                  fill='red', angle=tAngle)
    else:
        p1p = p1

    if np.absolute(V1) > 0.1:
        p2p = fn.rotate([p1[0]+Lcanvas, p1[1]-f*(V1)], p1, theta)
        if np.absolute(V0-V1) > 0.01:
            textpos = fn.rotate([p1[0]+Lcanvas,
                                 p1[1]-f*V1-k*np.sign(V1)*12], p1, theta)
        else:
            textpos = fn.rotate([p1[0]+Lcanvas/2,
                                 p1[1]-f*V0-k*np.sign(V0)*12], p1, theta)

        canvas.canvas.create_line(p2p, p2, fill='red')
        canvas.canvas.create_text(textpos, text='{:.2f}'.format(V1t),
                                  fill='red', angle=tAngle)
    else:
        p2p = p2

    if len(V) == 2:
        canvas.canvas.create_line(p1p, p2p, fill='red')

    else:
        curve = []

        for i in range(41):
            x = int(i*L/40)
            a = np.argmin(np.absolute(X-x))
            p = fn.rotate([p1[0]+x*canvas.scale, p1[1]-f*V[a]], p1, theta)
            curve.append(p)

        canvas.canvas.create_line(curve, fill='red')

        imax = np.argmax(np.absolute(V))
        xmax = X[imax]
        Vmax = V[imax]
        Vmaxt = fn.unitConvert('kN', canvas.units[1], Vmax)

        px = fn.rotate([p1[0]+xmax*canvas.scale, p1[1]], p1, theta)
        pm = fn.rotate([p1[0]+xmax*canvas.scale, p1[1]-f*Vmax], p1, theta)
        textpos = fn.rotate([p1[0]+xmax*canvas.scale,
                             p1[1]-f*Vmax-k*np.sign(Vmax)*12], p1, theta)

        canvas.canvas.create_line(px, pm, fill='red')
        canvas.canvas.create_text(textpos, text='{:.2f}'.format(Vmaxt),
                                  fill='red', angle=tAngle)


def drawNormalForce(canvas, member):
    '''
    Draws the normal force diagram for a given member.
    Direction-independent: handles columns/beams drawn in any orientation.
    '''
    elem = canvas.membersList[member]
    p1_orig = fn.canvasCoords(canvas, elem.p1)
    p2_orig = fn.canvasCoords(canvas, elem.p2)

    # Make copies for potential reversal
    p1 = list(p1_orig)
    p2 = list(p2_orig)
    Lcanvas = fn.distance(p1, p2)

    theta = elem.theta
    k = fn.angleSign(theta)
    tAngle = fn.textAngle(theta*180/np.pi)

    f = canvas.resultsScale[1] * k
    
    # Detect if member is drawn in reverse direction
    reverse = p2[0] < p1[0] or (p2[0] == p1[0] and p2[1] < p1[1])
    if reverse:
        p1, p2 = p2, p1

    if canvas.currentLoadcase != -1:
        case = canvas.currentLoadcase
    else:
        case = (len(canvas.loadcasesList) + canvas.currentCombination)

    N = canvas.forces[case][member][0]
    
    # Reverse array if member was drawn backwards
    if reverse:
        N = list(reversed(N))

    if np.absolute(N[0]) > 0.1:
        p1p = fn.rotate([p2[0]-Lcanvas, p2[1]-f*N[0]], p2, theta)
        canvas.canvas.create_line(p1p, p1, fill='blue')

    else:
        p1p = [p1[0], p1[1]]

    if np.absolute(N[1]) > 0.1:
        p2p = fn.rotate([p2[0], p2[1]-f*N[1]], p2, theta)
        canvas.canvas.create_line(p2p, p2, fill='blue')

    else:
        p2p = [p2[0], p2[1]]

    N0t = fn.unitConvert('kN', canvas.units[1], N[0])
    N1t = fn.unitConvert('kN', canvas.units[1], N[1])

    if np.absolute(N[0]-N[1]) < 1e-5:
        textpos = fn.rotate([p1[0]+Lcanvas/2,
                             p1[1]-f*N[0]-np.sign(k*N[0])*12], p1, theta)
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(N0t),
                                  fill='blue', angle=tAngle)

    else:
        textpos1 = fn.rotate([p2[0]-Lcanvas,
                              p2[1]-f*N[0]-np.sign(k*N[0])*12], p2, theta)
        textpos2 = fn.rotate([p2[0],
                              p2[1]-f*N[1]-np.sign(k*N[1])*12], p2, theta)

        canvas.canvas.create_text(textpos1, text='{:.2f}'.format(N0t),
                                  fill='blue', angle=tAngle)
        canvas.canvas.create_text(textpos2, text='{:.2f}'.format(N1t),
                                  fill='blue', angle=tAngle)

    canvas.canvas.create_line(p1p, p2p, fill='blue')


def drawBendingMoment(canvas, member):
    '''
    Draws the bending moment diagram for a given member.
    Direction-independent: handles columns/beams drawn in any orientation.
    '''
    # Get element data
    elem = canvas.membersList[member]
    p1_orig = fn.canvasCoords(canvas, elem.p1)
    p2_orig = fn.canvasCoords(canvas, elem.p2)
    L = elem.length
    
    # Make copies for potential reversal
    p1 = list(p1_orig)
    p2 = list(p2_orig)
    Lcanvas = fn.distance(p1, p2)
    
    theta = elem.theta
    k = fn.angleSign(theta)
    tAngle = fn.textAngle(theta*180/np.pi)
    
    f = canvas.resultsScale[3]*k
    
    # Detect if member is drawn in reverse direction (bottom-to-top or right-to-left)
    # This ensures consistent plotting regardless of drawing direction
    reverse = p2[0] < p1[0] or (p2[0] == p1[0] and p2[1] < p1[1])
    if reverse:
        p1, p2 = p2, p1
    
    # Get load case
    if canvas.currentLoadcase != -1:
        case = canvas.currentLoadcase
    else:
        case = (len(canvas.loadcasesList) + canvas.currentCombination)
    
    # Get moment array
    M = canvas.forces[case][member][2]
    X = canvas.displacements[case][member][3]
    
    # Reverse moment array if member was drawn backwards
    if reverse:
        M = list(reversed(M))
        X = [L - x for x in reversed(X)]
    
    M0, M1 = M[0], M[-1]
    M0t = fn.unitConvert('kN.cm', canvas.units[2], M0)
    M1t = fn.unitConvert('kN.cm', canvas.units[2], M1)
    
    # Draw moment values at start point
    if np.absolute(M0) > 0.1:
        p1p = fn.rotate([p1[0], p1[1]+f*M0], p1, theta)
        textpos = fn.rotate([p1[0], p1[1]+f*M0-np.sign(-M0)*12], p1, theta)
        
        canvas.canvas.create_line(p1p, p1, fill='green')
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(M0t)),
                                  fill='green', angle=tAngle)
    
    # Draw moment values at end point
    if np.absolute(M1) > 0.1:
        p2p = fn.rotate([p1[0]+Lcanvas, p1[1]+f*(M1)], p1, theta)
        textpos = fn.rotate([p1[0]+Lcanvas,
                             p1[1]+f*(M1)-np.sign(-M1)*12], p1, theta)
        
        canvas.canvas.create_line(p2p, p2, fill='green')
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(M1t)),
                                  fill='green', angle=tAngle)
    
    # Draw moment curve
    curve = []
    for i in range(21):
        x = int(i*L/20)
        a = np.argmin(np.absolute(X-x))
        p = fn.rotate([p1[0]+x*canvas.scale, p1[1]+f*M[a]], p1, theta)
        curve.append(p)
    
    canvas.canvas.create_line(curve, fill='green')
    
    # Draw maximum moment value
    imax = np.argmax(np.absolute(M))
    xmax, Mmax = X[imax], M[imax]
    Mmaxt = fn.unitConvert('kN.cm', canvas.units[2], Mmax)
    
    px = fn.rotate([p1[0]+xmax*canvas.scale, p1[1]], p1, theta)
    pm = fn.rotate([p1[0]+xmax*canvas.scale, p1[1]+f*Mmax], p1, theta)
    textpos = fn.rotate([p1[0]+xmax*canvas.scale,
                         p1[1]+f*Mmax-np.sign(-Mmax)*12], p1, theta)
    
    canvas.canvas.create_line(pm, px, fill='green')
    canvas.canvas.create_text(textpos,
                              text='{:.2f}'.format(np.absolute(Mmaxt)),
                              fill='green', angle=tAngle)


def drawDisplacement(canvas, member):
    '''
    Draws the deformed structure.
    Direction-independent: handles columns/beams drawn in any orientation.
    '''
    elem = canvas.membersList[member]
    p1_orig = fn.canvasCoords(canvas, elem.p1)
    p2_orig = fn.canvasCoords(canvas, elem.p2)
    L = elem.length

    # Make copies for potential reversal
    p1 = list(p1_orig)
    p2 = list(p2_orig)
    Lcanvas = fn.distance(p1, p2)

    theta = elem.theta

    f = canvas.resultsScale[0]
    
    # Detect if member is drawn in reverse direction
    reverse = p2[0] < p1[0] or (p2[0] == p1[0] and p2[1] < p1[1])
    if reverse:
        p1, p2 = p2, p1

    if canvas.currentLoadcase != -1:
        case = canvas.currentLoadcase
    else:
        case = (len(canvas.loadcasesList) + canvas.currentCombination)

    u = canvas.displacements[case][member][0]
    v = canvas.displacements[case][member][1]
    X = canvas.displacements[case][member][3]
    
    # Reverse arrays if member was drawn backwards
    if reverse:
        u = list(reversed(u))
        v = list(reversed(v))
        X = [L - x for x in reversed(X)]

    p0 = fn.rotate([p1[0]+f*canvas.scale*u[0],
                    p1[1]-f*canvas.scale*v[0]], p1, theta)

    curve = [p0]
    nsteps = max(20, int(L/20))

    for i in range(nsteps):
        x = int(i*L/nsteps)
        a = np.argmin(np.absolute(X-x))
        x = X[a]
        ux = u[a]
        vx = v[a]
        pd = fn.rotate([p1[0]+x*canvas.scale+f*canvas.scale*ux,
                        p1[1]-f*canvas.scale*vx], p1, theta)
        curve.append(pd)

    pL = fn.rotate([p1[0]+Lcanvas+f*canvas.scale*u[len(u)-1],
                    p1[1]-f*canvas.scale*v[-1]], p1, theta)

    curve.append(pL)
    canvas.canvas.create_line(curve, width=1.3, fill='purple')


def drawClickResult(canvas):
    if canvas.currentLoadcase != -1:
        case = canvas.currentLoadcase
    else:
        case = (len(canvas.loadcasesList) + canvas.currentCombination)

    member, eps = canvas.resultClick[0], canvas.resultClick[1]

    p1, p2 = canvas.membersList[member].p1, canvas.membersList[member].p2
    L = canvas.membersList[member].length
    theta = canvas.membersList[member].theta
    xL = eps*L

    k = fn.angleSign(theta)
    tAngle = fn.textAngle(theta*180/np.pi)

    p1 = fn.canvasCoords(canvas, p1)
    p2 = fn.canvasCoords(canvas, p2)
    rType = canvas.clickType

    X = canvas.displacements[case][member][3]

    closest = np.argmin(np.absolute(X - xL))
    if xL > X[closest]:
        lower = closest
    else:
        lower = closest-1

    if rType == 'displace':
        f = canvas.resultsScale[0]
        U = canvas.displacements[case][member][0]
        V = canvas.displacements[case][member][1]
        R = canvas.displacements[case][member][2]

        u = fn.linInterp(X[lower], U[lower], X[lower+1], U[lower+1], xL)
        v = fn.linInterp(X[lower], V[lower], X[lower+1], V[lower+1], xL)
        r = fn.linInterp(X[lower], R[lower], X[lower+1], R[lower+1], xL)

        px = fn.rotate([p1[0]+xL*canvas.scale, p1[1]], p1, theta)
        pd = fn.rotate([p1[0]+xL*canvas.scale+f*canvas.scale*u,
                        p1[1]-f*canvas.scale*v], p1, theta)

        textpos = fn.rotate([p1[0]+xL*canvas.scale+f*canvas.scale*u,
                            p1[1]-f*canvas.scale*v-np.sign(v)*12],
                            p1, theta)

        temp = fn.rotate([u, v], [0, 0], -theta)
        displ = [fn.unitConvert('cm', canvas.units[10], temp[0]),
                 fn.unitConvert('cm', canvas.units[10], temp[1]),
                 fn.unitConvert('rad', canvas.units[11], r)]

        string = ('(' + '{:.2f}'.format(displ[0]) + ' ' +
                  canvas.units[10] + ', ' + '{:.2f}'.format(displ[1]) +
                  ' ' + canvas.units[10] + ', ' + '{:.2f}'.format(displ[2]) +
                  ' ' + canvas.units[11] + ')')

        canvas.canvas.create_line(px, pd, fill='red')
        canvas.canvas.create_text(textpos, text=string,
                                  fill='red', angle=tAngle)

    elif rType == 'bending':
        f = canvas.resultsScale[3]
        M = canvas.forces[case][member][2]

        Mx = fn.linInterp(X[lower], M[lower], X[lower+1], M[lower+1], xL)
        Mxt = fn.unitConvert('kN.cm', canvas.units[2], Mx)

        px = fn.rotate([p1[0]+xL*canvas.scale, p1[1]], p1, theta)
        pm = fn.rotate([p1[0]+xL*canvas.scale, p1[1]-f*(-k*Mx)], p1, theta)
        textpos = fn.rotate([p1[0]+xL*canvas.scale,
                             p1[1]-f*(-k*Mx)-np.sign(-k*Mx)*12], p1, theta)

        canvas.canvas.create_line(px, pm, fill='red')
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(Mxt)),
                                  fill='red', angle=tAngle)

    elif rType == 'shear':
        f = canvas.resultsScale[2]
        V = canvas.forces[case][member][1]

        if len(V) <= 2:
            Vx = V[0] + (xL/L)*(V[1]-V[0])
        else:
            Vx = fn.linInterp(X[lower], V[lower], X[lower+1], V[lower+1], xL)

        Vxt = fn.unitConvert('kN', canvas.units[1], Vx)

        px = fn.rotate([p1[0]+xL*canvas.scale, p1[1]], p1, theta)
        pv = fn.rotate([p1[0]+xL*canvas.scale, p1[1]-f*k*Vx], p1, theta)
        textpos = fn.rotate([p1[0]+xL*canvas.scale,
                             p1[1]-f*k*Vx-np.sign(k*Vx)*12], p1, theta)

        canvas.canvas.create_line(px, pv, fill='red')
        canvas.canvas.create_text(textpos, text='{:.2f}'.format(Vxt),
                                  fill='red', angle=tAngle)

    else:
        f = canvas.resultsScale[1]
        N = canvas.forces[case][member][0]

        Nx = N[0] + (xL/L)*(N[1]-N[0])
        Nxt = fn.unitConvert('kN', canvas.units[1], Nx)

        px = fn.rotate([p1[0]+xL*canvas.scale, p1[1]], p1, theta)
        pv = fn.rotate([p1[0]+xL*canvas.scale, p1[1]-f*k*Nx], p1, theta)
        textpos = fn.rotate([p1[0]+xL*canvas.scale,
                             p1[1]-f*k*Nx-np.sign(k*Nx)*12], p1, theta)

        canvas.canvas.create_line(px, pv, fill='red')
        canvas.canvas.create_text(textpos, text='{:.2f}'.format(Nxt),
                                  fill='red', angle=tAngle)


def drawReactions(canvas, node):
    '''
    Draws the support reactions for a given node.
    '''
    if canvas.currentLoadcase >= 0:
        case = canvas.currentLoadcase
    else:
        case = len(canvas.loadcasesList) + canvas.currentCombination

    p = canvas.nodesList[node].coords
    Px = fn.unitConvert('kN', canvas.units[1],
                        canvas.results[2][case][node][0])
    Py = fn.unitConvert('kN', canvas.units[1],
                        canvas.results[2][case][node][1])
    Mz = fn.unitConvert('kN.cm', canvas.units[2],
                        canvas.results[2][case][node][2])

    theta = canvas.nodesList[node].restr[3]
    tAngle = fn.textAngle(theta)

    color = canvas.colorScheme[5]
    p = fn.canvasCoords(canvas, p)

    if Px < 0:
        thetaX = theta
    else:
        thetaX = theta + np.pi
    if Py < 0:
        thetaY = theta
    else:
        thetaY = theta + np.pi

    if np.absolute(Px) > 0.01:
        p1 = fn.rotate([p[0]+3, p[1]+15], p, thetaX)
        p2 = fn.rotate([p[0]+63, p[1]+15], p, thetaX)
        textpos = fn.rotate([p[0]+63, p[1]+5], p, thetaX)

        canvas.canvas.create_line(p1, p2, arrow=tk.FIRST, fill=color,
                                  width=2, arrowshape=(12, 15, 4.5))
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(Px)) +
                                  ' '+canvas.units[1], fill=color,
                                  angle=tAngle)

    if np.absolute(Py) > 0.01:
        p1 = fn.rotate([p[0], p[1]-13], p, thetaY)
        p2 = fn.rotate([p[0], p[1]-73], p, thetaY)
        textpos = fn.rotate([p[0]+10, p[1]-78], p, thetaY)

        canvas.canvas.create_line(p1, p2, arrow=tk.FIRST, fill=color,
                                  width=2, arrowshape=(12, 15, 4.5))
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(Py)) +
                                  ' '+canvas.units[1], fill=color,
                                  angle=tAngle)

    if np.absolute(Mz) > 0.01:
        curve = []
        for i in range(20):
            angle = np.pi*(-1/6 + (5/6)*i/20)
            p1 = fn.rotate([p[0]+25, p[1]], p, angle)
            curve.append(p1)
        if Mz > 0:
            canvas.canvas.create_line(curve, arrow=tk.LAST, fill=color)
            textpos = fn.rotate([p[0]+35, p[1]], p, 2*np.pi/3)
        else:
            canvas.canvas.create_line(curve, arrow=tk.FIRST, fill=color)
            textpos = fn.rotate([p[0]+35, p[1]], p, np.pi/30)
        canvas.canvas.create_text(textpos,
                                  text='{:.2f}'.format(np.absolute(Mz)) +
                                  ' '+canvas.units[2], fill=color)


def drawMaxMin(canvas, member, ftype):
    '''
    Draws the max/min values of the given force type for every element.
    '''
    if ftype == 0:
        fmax = fn.unitConvert('kN', canvas.units[1], canvas.max[member][0])
        fmin = fn.unitConvert('kN', canvas.units[1], canvas.min[member][0])
        cmax = canvas.max[member][1]
        cmin = canvas.min[member][1]
        unit = canvas.units[1]
    elif ftype == 1:
        fmax = fn.unitConvert('kN', canvas.units[1], canvas.max[member][2])
        fmin = fn.unitConvert('kN', canvas.units[1], canvas.min[member][2])
        cmax = canvas.max[member][3]
        cmin = canvas.min[member][3]
        unit = canvas.units[1]
    else:
        fmax = fn.unitConvert('kN.cm', canvas.units[2], canvas.max[member][4])
        fmin = fn.unitConvert('kN', canvas.units[1], canvas.min[member][4])
        cmax = canvas.max[member][5]
        cmin = canvas.min[member][5]
        unit = canvas.units[2]

    maxType = canvas.maxType.get()

    if maxType == 0 and cmax < len(canvas.loadcasesList) or maxType == 1:
        maxname = canvas.loadcasesList[cmax]
        a = 'Case'
    elif maxType == 0 and cmax >= len(canvas.loadcasesList):
        maxname = canvas.COMBINATIONSList[cmax-len(canvas.loadcasesList)]
        a = 'COMB.'
    elif maxType == 2:
        maxname = canvas.COMBINATIONSList[cmax]
        a = 'COMB.'

    stringmax = ('MÁX: ' + '{:.2f}'.format(fmax)
                 + ' ' + unit + ' (' + a + ':' + maxname + ')')

    if maxType == 0 and cmin < len(canvas.loadcasesList) or maxType == 1:
        minname = canvas.loadcasesList[cmin]
        a = 'Case'
    elif maxType == 0 and cmin >= len(canvas.loadcasesList):
        minname = canvas.COMBINATIONSList[cmin-len(canvas.loadcasesList)]
        a = 'COMB.'
    elif maxType == 2:
        minname = canvas.COMBINATIONSList[cmin]
        a = 'COMB.'
    stringmin = ('MÍN: ' + '{:.2f}'.format(fmin)
                 + ' ' + unit + ' (' + a + ':' + minname + ')')

    p1 = canvas.membersList[member].p1
    p2 = canvas.membersList[member].p2

    theta = canvas.membersList[member].theta

    tAngle = fn.textAngle(theta*180/np.pi)

    p1 = fn.canvasCoords(canvas, p1)
    p2 = fn.canvasCoords(canvas, p2)
    Lcanvas = fn.distance(p1, p2)

    textpos1 = fn.rotate([p1[0]+Lcanvas/2, p1[1]-10], p1, theta)
    textpos2 = fn.rotate([p1[0]+Lcanvas/2, p1[1]+10], p1, theta)

    canvas.canvas.create_text(textpos1, fill='blue',
                              text=stringmax, angle=tAngle)
    canvas.canvas.create_text(textpos2, fill='red',
                              text=stringmin, angle=tAngle)
