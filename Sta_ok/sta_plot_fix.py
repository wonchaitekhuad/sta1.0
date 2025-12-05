#!/usr/bin/env python3
"""
sta_plot_fix.py

Improved plotting for per-element SFD/BMD with orientation and sign handling.
Reads an input JSON (see example_input.json) and outputs:
 - per-element CSV: element_<id>_results.csv  (s, V, M)
 - per-element PNG: element_<id>_bmd.png
 - combined PNG: combined_bmd.png
 - zip: sta_fixed.zip (created by caller)

Usage:
    python sta_plot_fix.py --input example_input.json --out_prefix sta_results

Input JSON structure (example provided in example_input.json):
{
  "elements": [
    {"id": 1, "x1": 0, "y1": 0, "x2": 3, "y2": 0},
    {"id": 2, "x1": 3, "y1": 0, "x2": 3, "y2": 4}
  ],
  "loads": [
    {"type":"point","global":[1.5,0],"w":10,"eid":1},
    {"type":"udl","global_start":[3,0],"global_end":[3,4],"w":2,"eid":2}
  ],
  "element_reactions": {
    "1": {"RA": 5.0, "RB": 5.0},
    "2": {"RA": 4.0, "RB": 4.0}
  },
  "plot_options": {
    "invert_sign_if_needed": true,
    "npts_per_element": 201
  }
}

Notes:
 - If reactions for an element are not provided, the script will compute RA/RB assuming simply-supported
   using vertical load equilibrium and moment equilibrium about node1 (reasonable fallback for single-span).
 - The script **does not** perform a full frame stiffness assembly. It focuses on correct geometric mapping and plotting.
"""

import argparse
import os
import json
import math
import csv
import matplotlib.pyplot as plt

def reaction_for_simply_supported(span, loads):
    total_F = 0.0
    moment_about_A = 0.0
    for ld in loads:
        if ld["type"] == "point":
            P = ld["w"]; x = ld["pos"]
            total_F += P
            moment_about_A += P * x
        elif ld["type"] == "udl":
            w = ld["w"]; a = ld["start"]; b = ld["end"]
            Lw = max(0.0, min(b, span) - max(a, 0.0))
            if Lw <= 0: continue
            F = w * Lw
            centroid = (max(a,0.0) + min(b,span)) / 2.0
            total_F += F
            moment_about_A += F * centroid
    if abs(span) < 1e-12:
        return {"RA":0.0,"RB":0.0}
    RB = moment_about_A / span
    RA = total_F - RB
    return {"RA": RA, "RB": RB, "total_F": total_F}

def shear_and_moment(span, loads, RA, npts=201):
    xs = [span * i / (npts - 1) for i in range(npts)]
    Vs = []
    Ms = []
    for x in xs:
        V = RA
        M = RA * x
        for ld in loads:
            if ld["type"] == "point":
                if ld["pos"] <= x + 1e-12:
                    P = ld["w"]; pos = ld["pos"]
                    V -= P
                    M -= P * (x - pos)
            elif ld["type"] == "udl":
                w = ld["w"]; a = ld["start"]; b = ld["end"]
                left = max(a, 0.0); right = min(b, x)
                Lw = right - left
                if Lw > 0:
                    F = w * Lw
                    centroid = (left + right) / 2.0
                    V -= F
                    M -= F * (x - centroid)
        Vs.append(V); Ms.append(M)
    return xs, Vs, Ms

def project_global_to_local(px, py, x1, y1, x2, y2):
    dx = x2 - x1; dy = y2 - y1
    L = math.hypot(dx, dy)
    if L == 0:
        return 0.0
    ux, uy = dx / L, dy / L
    vx, vy = px - x1, py - y1
    s = vx * ux + vy * uy
    # clamp to [0,L]
    if s < 0: s = 0.0
    if s > L: s = L
    return s

def map_loads_to_element(loads_global, element):
    x1,y1,x2,y2 = element["x1"], element["y1"], element["x2"], element["y2"]
    eid = element["id"]
    L = math.hypot(x2-x1, y2-y1)
    mapped = []
    for ld in loads_global:
        if ld.get("eid") != eid:
            continue
        if ld["type"] == "point":
            gx,gy = ld["global"]
            s = project_global_to_local(gx,gy,x1,y1,x2,y2)
            mapped.append({"type":"point","pos":s,"w":ld["w"]})
        elif ld["type"] == "udl":
            gs = ld["global_start"]; ge = ld["global_end"]
            s1 = project_global_to_local(gs[0], gs[1], x1,y1,x2,y2)
            s2 = project_global_to_local(ge[0], ge[1], x1,y1,x2,y2)
            ss, ee = min(s1,s2), max(s1,s2)
            mapped.append({"type":"udl","start":ss,"end":ee,"w":ld["w"]})
    return mapped

def element_mid_global_x(element):
    # returns the projection of element midpoint onto global X axis (for plotting along plan)
    return (element["x1"] + element["x2"]) / 2.0

def write_csv_element(out_prefix, eid, xs, Vs, Ms):
    path = f"{out_prefix}_element_{eid}.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s_local","V","M"])
        for s,v,m in zip(xs,Vs,Ms):
            w.writerow([f"{s:.6f}", f"{v:.6f}", f"{m:.6f}"])
    return path

def plot_element_bmd(xs, Ms, element, out_prefix, invert_sign=False):
    eid = element["id"]
    # by default plot s (local coordinate) vs M
    s_local = xs
    M_plot = [-m for m in Ms] if invert_sign else Ms  # allow invert sign when desired
    plt.figure(figsize=(6,3))
    plt.plot(s_local, M_plot)
    plt.axhline(0, linewidth=0.6)
    plt.title(f"Element {eid} BMD (local s vs M)")
    plt.xlabel("s (local)")
    plt.ylabel("Moment")
    plt.grid(True)
    png_path = f"{out_prefix}_element_{eid}_bmd.png"
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
    return png_path

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input","-i", default="example_input.json")
    parser.add_argument("--out_prefix","-o", default="sta_results")
    args = parser.parse_args()

    # load input
    if not os.path.exists(args.input):
        print("Input not found:", args.input)
        return
    with open(args.input, "r") as f:
        data = json.load(f)

    elements = data.get("elements", [])
    loads = data.get("loads", [])
    reactions_map = data.get("element_reactions", {})
    plot_opts = data.get("plot_options", {})
    invert_flag = plot_opts.get("invert_sign_if_needed", True)
    npts = plot_opts.get("npts_per_element", 201)

    generated_files = []

    combined_plot_data = []  # tuples (eid, s_list, M_plot, mid_x)

    for e in elements:
        eid = e["id"]
        L = math.hypot(e["x2"]-e["x1"], e["y2"]-e["y1"])
        mapped_loads = map_loads_to_element(loads, e)
        # if reactions provided use them, otherwise compute simply-supported reactions
        rxn = reactions_map.get(str(eid)) or reactions_map.get(eid)
        if rxn is None:
            rxn = reaction_for_simply_supported(L, mapped_loads)
        RA = rxn.get("RA", 0.0)
        RB = rxn.get("RB", 0.0)
        xs, Vs, Ms = shear_and_moment(L, mapped_loads, RA, npts=npts)
        csv_path = write_csv_element(args.out_prefix, eid, xs, Vs, Ms)
        generated_files.append(csv_path)
        png_path = plot_element_bmd(xs, Ms, e, args.out_prefix, invert_sign=False)
        generated_files.append(png_path)
        # also create an inverted-sign plot copy for quick check
        png_inv = plot_element_bmd(xs, Ms, e, args.out_prefix + "_invert", invert_sign=True)
        generated_files.append(png_inv)
        combined_plot_data.append((eid, xs, Ms, element_mid_global_x(e)))

    # combined overlay (local s axis normalized for visibility)
    plt.figure(figsize=(8,4))
    for eid, xs, Ms, midx in combined_plot_data:
        # normalize s to element mid for display (or just plot local s)
        plt.plot([midx + s*0.0 for s in xs], Ms, label=f"E{eid} (local s vs M)")  # plotting at same x for vertical elements
    plt.axhline(0, linewidth=0.6)
    plt.legend()
    plt.title("Combined elements BMD (local s plotted at element mid x projection)")
    plt.xlabel("global x (approx)")
    plt.ylabel("Moment")
    plt.tight_layout()
    combined_png = args.out_prefix + "_combined_bmd.png"
    plt.savefig(combined_png)
    plt.close()
    generated_files.append(combined_png)

    # summary reactions file
    rxn_file = args.out_prefix + "_reactions_summary.txt"
    with open(rxn_file, "w") as rf:
        for e in elements:
            eid = e["id"]
            rxn = reactions_map.get(str(eid)) or reactions_map.get(eid) or reaction_for_simply_supported(math.hypot(e["x2"]-e["x1"], e["y2"]-e["y1"]), map_loads_to_element(loads,e))
            rf.write(f"Element {eid}: RA={rxn.get('RA',0):.6f}, RB={rxn.get('RB',0):.6f}\\n")
    generated_files.append(rxn_file)

    print("Generated files:")
    for p in generated_files:
        print("  ", p)

if __name__ == "__main__":
    main()
