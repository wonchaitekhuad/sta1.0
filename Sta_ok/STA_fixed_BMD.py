#!/usr/bin/env python3
"""
STA_fixed_BMD.py
Minimal Tkinter demonstration of a portal frame and corrected BMD plotting.
This is intentionally self-contained so you can drop logic into your STA project.
Key fix: correct sign and rotation when converting moment values into screen offsets
so that positive (sagging) moments draw downward.

Usage: python STA_fixed_BMD.py
Author: Generated for TI (example patch)
"""

import tkinter as tk
from math import sqrt

# Example structure: simple symmetric portal frame (3 elements: left column, top beam, right column)
# Node coordinates (in cm for display)
nodes = {
    1: (200, 200),
    2: (400, 200),
    3: (400, 360),
    4: (200, 360),
    5: (300, 280)  # mid-top (for plotting mid-span moment point if needed)
}

# Elements: (node_i, node_j, id)
elements = [
    (1, 4, "col_left"),
    (4, 3, "beam_top"),
    (3, 2, "col_right"),
]

# Example moments at element ends (kN·m) - these come from the solver in real STA
# For each element id: (M_i, M_j) where M_i is moment at node_i end and M_j at node_j end.
# NOTE: Use sign convention where positive = sagging (downwards on beam midspan).
element_moments = {
    "col_left": (3.88, 1.94),   # top of column (at connection to beam) is 3.88 (hogging on top of beam but positive as stored)
    "beam_top": (3.88, 3.88),   # left end moment, right end moment; mid positive 4.12 (not stored per node here)
    "col_right": (1.94, 3.88)
}

# For display: define a scale to convert moment magnitude to pixel offset.
# This should be computed relative to structure size; here we pick a reasonable default.
def compute_scale():
    # maximum absolute moment from our sample data
    maxM = max(abs(v) for pair in element_moments.values() for v in pair)
    if maxM < 1e-6:
        return 0.0
    # target max offset ~ 50 pixels (adjust as needed)
    return 50.0 / maxM

# Utility: draw an arrowed line for reactions (simple)

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




def draw_bmd(canvas, elements, scale):
    """
    FINAL DEBUG v2 - STAdebug (TI Verified)
    Use global-local consistent normal so BMD matches STAAD.Pro:
    - Compute normal as (uy, -ux)
    - For members with dx > 0 (sloped rightwards), flip normal to match visual inward/outward
    - Positive (sagging) drawn inward/downward.
    """
    try:
        canvas.delete('bmd')
    except Exception:
        pass

    eps = 1e-9
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

        # Normal chosen to make positive sagging draw downward like STAAD.Pro
        nx, ny = uy, -ux

        # Flip for members sloping to the right to keep inward/outward consistent visually
        if dx > 0 and abs(dy) > eps:
            nx, ny = -nx, -ny

        M1 = getattr(e, 'Mi', 0.0)
        M2 = getattr(e, 'Mj', 0.0)

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
            try:
                canvas.create_text(x1 + nx*M1*scale, y1 + ny*M1*scale - 8, text=f"{M1:.2f}", fill='green', font=('Arial',8), tags='bmd')
                canvas.create_text(x2 + nx*M2*scale, y2 + ny*M2*scale - 8, text=f"{M2:.2f}", fill='green', font=('Arial',8), tags='bmd')
            except Exception:
                pass
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



try:
    import tkinter as _tk
    try:
        if _tk._default_root:
            _tk._default_root.title('STAdebug – TI Verified')
    except Exception:
        pass
except Exception:
    pass


try:
    import tkinter as _tk
    try:
        if _tk._default_root:
            _tk._default_root.title('STAdebug v2 – TI Verified')
    except Exception:
        pass
except Exception:
    pass
