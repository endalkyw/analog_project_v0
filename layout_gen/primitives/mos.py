import gdstk
import numpy as np

from layout_gen.utilities.elements_utils import *
from layout_gen.utilities.pvector import P
from layout_gen.core import create_base_layout, create_fabric
from layout_gen.core.constants import Const as C
from layout_gen.utilities.via import *
from layout_gen.utilities.elements_utils import Contact_region as CR
import math
from shapely.geometry.polygon import Polygon
from layout_gen.utilities.pin import find_best_point as fbp

def create_mos(m, fabric_on = True, con= [1, 1, 1, 1], labels = [0, 0, 0, 0], orientation = "V", gate_connection_type = "cm"):
    cell_i = create_empty_cell("single_nmos", unit=1e-9,  precision=1e-12)
    fin_dummy  = lp['fins']['dummies']
    fing_dummy = lp['poly']['dummies']
    fin_no = m.fins + 4 * fin_dummy - 2
    poly_no = m.stack*m.fingers + 2 * fing_dummy
    poly_height = fin_no * lp['fins']['pitch']
    fin_len = (poly_no - 1) * lp['poly']['pitch']
    points = create_base_layout(cell_i, m.fingers, m.fins, m.mos_type, stack=m.stack, multiplier = m.multiplier, orientation=orientation)
    contact_rects = []

    for pnt in points:
        loc = {"x_span": [pnt["p0"][0][0], pnt["p1"][0][0]], "y_span": [pnt["p0"][0][1], pnt["p1"][0][1]]}
        n0 = m.fingers//2 + int(m.fingers % 2)

        # metal connections
        src_drn_cons = con[0] + con[2]
        avail_v_space = loc["y_span"][1] - loc["y_span"][0]
        sd_space = (src_drn_cons-1) * lp["M2"]["pitch"] + lp["M2"]["width"] + 2*C.m_m_ext
        v_sp  = (avail_v_space - sd_space)
        v_sp2 = avail_v_space - ((con[2]-1) * lp["M2"]["pitch"] + lp["M2"]["width"] + 2*C.m_m_ext)

        # drain metal and via array
        if v_sp < 0:
            add_v_metal_array(cell_i, P(C.rx_m1 + m.stack * lp['M1']['pitch'], v_sp), abs(v_sp - 1), m.stack * 2 * lp['M2']['pitch'], n0, "M1")
            if v_sp2 < 0:
                add_v_metal_array(cell_i, P(C.rx_m1, v_sp2), abs(v_sp2 - 1), m.stack * 2 * lp['M2']['pitch'], n0+(m.fingers+1) % 2, "M1")
        else:
            v_sp /= 2
        for i in range(con[0]):
            add_via_array(cell_i, (pnt["p0"][0][0] + C.rx_m1 + m.stack*lp['M1']['pitch'], pnt["p0"][0][1] + v_sp + i*lp["M2"]['pitch']+ C.m_m_ext),  m.stack*2*lp['M2']['pitch'], n0, 'H', "V1")
            xi, yi = pnt["p0"][0][0] + C.rx_m1 + m.stack*lp['M1']['pitch'] - C.m_v_ext, pnt["p0"][0][1] + v_sp + i*lp["M2"]['pitch']+ C.m_m_ext
            rect_d = [[xi,yi], [xi+m.stack*(n0-1)*2*lp['M2']['pitch']+lp['M1']['width']+2*C.m_v_ext, yi+lp["M1"]["width"]]]
            add_metal(cell_i, P(pnt["p0"][0][0] + C.rx_m1 + m.stack*lp['M1']['pitch'] - C.m_v_ext, pnt["p0"][0][1] + v_sp + i*lp["M2"]['pitch']+ C.m_m_ext), m.stack*(n0-1)*2*lp['M2']['pitch']+lp['M1']['width']+2*C.m_v_ext, "H", "M2")
            contact_rects.append(CR("d", rect_d, metal="M2"))

        # source metal and via array
        for i in range(con[2]):
            xi, yi = loc["x_span"][0], pnt["p0"][0][1] + v_sp + con[0]*lp["M2"]['pitch'] + i*lp["M2"]['pitch']+ C.m_m_ext
            rect_s = [[xi, yi], [xi+loc["x_span"][1]-loc["x_span"][0], yi+lp["M2"]['width']]]
            add_metal(cell_i, P(xi,  yi), loc["x_span"][1]-loc["x_span"][0], "H", "M2")
            add_via_array(cell_i, (pnt["p0"][0][0] + C.rx_m1, pnt["p0"][0][1] + v_sp + con[0]*lp["M2"]['pitch'] + i*lp["M2"]['pitch']+ C.m_m_ext), m.stack*2*lp['M1']['pitch'], m.fingers//2+1, 'H', "V1")
            contact_rects.append(CR("s", rect_s, metal="M2"))


        # gate metal and via array
        rect_g = [(loc["x_span"][0]+C.rx_m1, pnt["g"][0][1]-1), (loc["x_span"][0]+C.rx_m1 + loc["x_span"][1]-loc["x_span"][0]-2*C.rx_m1, pnt["g"][0][1]+lp["M1"]["width"]-1)]
        add_vias_at_intersection(cell_i, rect_g, "M1")
        add_metal(cell_i, P(rect_g[0][0], rect_g[0][1]), loc["x_span"][1]-loc["x_span"][0]-2*C.rx_m1, "H", "M2")
        contact_rects.append(CR("g", rect_g, metal="M2"))

        # bulk metal and via array
        if pnt["b"]:
            rect_b = [(loc["x_span"][0]+C.rx_m1, pnt["b"][0][1]+4), (loc["x_span"][0]+C.rx_m1 + loc["x_span"][1]-loc["x_span"][0]-2*C.rx_m1, pnt["b"][0][1]+lp["M1"]["width"]+4)]
            add_vias_at_intersection(cell_i, rect_b, "M1")
            add_metal(cell_i, P(rect_b[0][0], rect_b[0][1]), loc["x_span"][1]-loc["x_span"][0]-2*C.rx_m1, "H", "M2")
            contact_rects.append(CR("b", rect_b, metal="M2"))


    n = con[0] + con[1] + con[2]
    if orientation == "V":
        x_span  = points[0]["p1"][0][0] - points[0]["p0"][0][0]
        r_space = x_span - ((n-1)*lp["M1"]["pitch"])
        xi = r_space/2

        s = [np.inf, -1*np.inf]
        d = [np.inf, -1*np.inf]
        g = [np.inf, -1*np.inf]

        for c in contact_rects:
            if c.id == "s":
                if c.rect[0][1]<s[0]:
                    s[0] = c.rect[0][1]
                if c.rect[1][1]>s[1]:
                    s[1] = c.rect[1][1]

            if c.id == "d":
                if c.rect[0][1]<d[0]:
                    d[0] = c.rect[0][1]
                if c.rect[1][1]>d[1]:
                    d[1] = c.rect[1][1]

            if c.id == "g":
                if c.rect[0][1] < g[0]:
                    g[0] = c.rect[0][1]
                if c.rect[1][1] > g[1]:
                    g[1] = c.rect[1][1]

        for i in range(con[0]): # drain
            ri = [(xi+i*lp["M1"]["pitch"],d[0]-C.m_m_ext), (xi+i*lp["M1"]["pitch"]+32, d[1]+C.m_m_ext)]
            contact_rects.append(CR("d",ri, metal="M3"))
            add_region(cell_i, ri[0], ri[1], "M3")

        xi += con[0]*lp["M1"]["pitch"]
        for i in range(con[1]): # gate
            ri = [(xi+i*lp["M1"]["pitch"],g[0]-C.m_m_ext), (xi+i*lp["M1"]["pitch"]+32, g[1]+C.m_m_ext)]
            contact_rects.append(CR("g",ri, metal="M3"))
            add_region(cell_i, ri[0], ri[1], "M3")

        xi += con[1] * lp["M1"]["pitch"]
        for i in range(con[2]): # source
            ri = [(xi+i*lp["M1"]["pitch"],s[0]-C.m_m_ext), (xi+i*lp["M1"]["pitch"]+32, s[1]+C.m_m_ext)]
            contact_rects.append(CR("s",ri, metal="M3"))
            add_region(cell_i, ri[0], ri[1], "M3")


        # adding vias at the intersections
        for i in range(len(contact_rects)):
            for j in range(i+1, len(contact_rects)):
                if(contact_rects[i].id == contact_rects[j].id):
                    add_vias_at_recti_v_rectj(cell_i, contact_rects[i].rect, contact_rects[j].rect, "M2")


    elif orientation == "H":
        for i in range(len(contact_rects)):
            for j in range(i+1, len(contact_rects)):
                if(contact_rects[i].id == contact_rects[j].id) and (contact_rects[i].rect[0][1] == contact_rects[j].rect[0][1]):
                    ri = [((contact_rects[i].rect[1][0]+contact_rects[i].rect[0][0])/2,contact_rects[i].rect[0][1]),
                          ((contact_rects[j].rect[1][0]+contact_rects[j].rect[0][0])/2,contact_rects[i].rect[1][1])]
                    add_region(cell_i, ri[0], ri[1], "M2")



    # Adding labels on metal2
    source_rects = []
    drain_rects = []
    gate_rects = []
    bulk_rects = []
    for cr in contact_rects:
        if (cr.rect[1][0] - cr.rect[0][0]) > (cr.rect[1][1] - cr.rect[0][1]): # check if it's horizontal
            if cr.id == "s":
                source_rects.append(cr.rect)
            elif cr.id == "d":
                drain_rects.append(cr.rect)
            elif cr.id == "g":
                gate_rects.append(cr.rect)
            elif cr.id == "b":
                bulk_rects.append(cr.rect)

    best_s, _, _ = fbp(source_rects)
    best_d, _, _ = fbp(drain_rects)
    best_g, _, _ = fbp(gate_rects)
    best_b, _, _ = fbp(bulk_rects)

    # labels: d g s b
    if labels[0]:
        add_label(cell_i, labels[0], P(best_d[0], best_d[1]), "M2LABEL")
    if labels[1]:
        add_label(cell_i, labels[1], P(best_g[0], best_g[1]), "M2LABEL")
    if labels[2]:
        add_label(cell_i, labels[2], P(best_s[0], best_s[1]), "M2LABEL")
    if labels[3]:
        add_label(cell_i, labels[3], P(best_b[0], best_b[1]), "M2LABEL")

    # print(best_point_s)
    # print(best_point_d)
    # print(best_point_g)
    # print(best_point_b)
    #
    # circ_s = gdstk.ellipse(best_point_s, 10)
    # circ_g = gdstk.ellipse(best_point_g, 10)
    # circ_d = gdstk.ellipse(best_point_d, 10)
    # circ_b = gdstk.ellipse(best_point_b, 10)
    #
    # cell_i.add(circ_s)
    # cell_i.add(circ_g)
    # cell_i.add(circ_b)
    # cell_i.add(circ_d)



    # poly and fins fabric inclusion ------------------------------------------
    p = cell_i.bounding_box()
    poly_n = math.ceil((p[1][0] - p[0][0])/lp["poly"]["pitch"])-1
    fin_n = math.ceil((p[1][1] - p[0][1])//lp["fins"]["pitch"])
    x_ = 0
    y_ = 0
    cell = create_empty_cell("cm", 1e-9, 1e-12)
    if fabric_on:
        create_fabric(cell, poly_n, fin_n)
        x_ = (0 + 1) * (lp['poly']['dummies'] - 1) * lp['poly']['pitch'] + 23 + lp['poly']['width'] / 2
        y_ = (0 + 1) * lp['fins']['dummies'] * lp["fins"]["pitch"] - (lp['fins']['pitch'] - lp['fins']['width'])/2
    add_transformed_polygons(cell_i, cell, (x_, y_))


    return cell, contact_rects






