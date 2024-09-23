from matplotlib import patches
import matplotlib.pyplot as plt
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint
import numpy as np
from pex.stick_diagram import *
from pex.data_structs import *
import gdstk

def get_colors(n):
    colors = plt.cm.tab20.colors
    if n <= 20:
        return colors[:n]
    else:
        return colors * (n // 20) + colors[:n % 20]

def xw(points):
    x  = points[0][0]
    y  = points[0][1]
    width = abs(points[0][0]-points[1][0])
    height = abs(points[2][1]-points[1][1])
    return x,y,width,height


def filter_polygons_by_layer_and_type(cells, target_layer, target_data_type):
    filtered_polygons = []
    for polygon in cells.polygons:
        if polygon.layer == target_layer and polygon.datatype == target_data_type:
            filtered_polygons.append(polygon)
    return filtered_polygons


def filter_labels_by_layer_and_type(cells, target_layer, target_data_type):
    filtered_labels = []
    for polygon in cells.get_labels():
        if polygon.layer == target_layer and polygon.texttype == target_data_type:
            filtered_labels.append(polygon)
    return filtered_labels


def to_custome_polygon(gdstk_polygon, type = "polygon"):
    cst_poly = []
    if type == "label":
        for p in gdstk_polygon:
            p = polygon(p.origin, p.layer, p.texttype, -1, p.text)
            cst_poly.append(p)
    else:
        for p in gdstk_polygon:
            p = polygon(p.points, p.layer, p.datatype, -1)
            cst_poly.append(p)

    return cst_poly


def get_polygons(cell):
    ct = filter_polygons_by_layer_and_type(cell, 247, 0)
    c_t = to_custome_polygon(ct)

    metal_1 = filter_polygons_by_layer_and_type(cell, 15, 0)
    m_1 = to_custome_polygon(metal_1)

    metal_2 = filter_polygons_by_layer_and_type(cell, 17, 0)
    m_2 = to_custome_polygon(metal_2)

    metal_3 = filter_polygons_by_layer_and_type(cell, 19, 0)
    m_3 = to_custome_polygon(metal_3)

    via_0 = filter_polygons_by_layer_and_type(cell, 35, 0)
    v_0 = to_custome_polygon(via_0)

    via_1 = filter_polygons_by_layer_and_type(cell, 16, 0)
    v_1 = to_custome_polygon(via_1)

    via_2 = filter_polygons_by_layer_and_type(cell, 18, 0)
    v_2 = to_custome_polygon(via_2)

    active_area = filter_polygons_by_layer_and_type(cell, 2, 0)
    a_a = to_custome_polygon(active_area)

    fins = filter_polygons_by_layer_and_type(cell, 2, 42)
    f_s = to_custome_polygon(fins)

    poly = filter_polygons_by_layer_and_type(cell, 7, 0)
    p_s = to_custome_polygon(poly)

    diff = filter_polygons_by_layer_and_type(cell, 14, 0)
    d_s = to_custome_polygon(diff)

    n_well = filter_polygons_by_layer_and_type(cell, 4, 0)
    n_w = to_custome_polygon(n_well)

    pins_m1 = filter_labels_by_layer_and_type(cell, 15, 20)
    pins_m2 = filter_labels_by_layer_and_type(cell, 16, 20)
    p_i = to_custome_polygon(pins_m1 + pins_m2, "label")

    cb = filter_polygons_by_layer_and_type(cell, 245, 0)
    c_b = to_custome_polygon(cb)

    bp = filter_polygons_by_layer_and_type(cell, 10, 0)
    b_p = to_custome_polygon(bp)

    rvt = filter_polygons_by_layer_and_type(cell, 12, 164)
    r_t = to_custome_polygon(rvt)

    cut_polygons(p_s, c_t)

    # giving id's
    for i, p in enumerate(r_t):
        p.id = i

    # return [m_1, m_2, v_0, v_1, a_a, f_s, p_s, d_s, n_w, p_i, c_b, b_p]
    return {"metal_1":m_1, "metal_2":m_2, "metal_3":m_3, "via_0": v_0, "via_1": v_1, "via_2":v_2, "active_areas": a_a,
            "fins":f_s, "polys":p_s, "diffusions":d_s, "nwell":n_w, "pins":p_i,"cb":c_b,"bp":b_p, "rvt":r_t, "poly_cut":c_t}

def is_point_inside_the_polygon(point, polygon):
    # Convert polygon to shapely polygon
    polygon_shapely = ShapelyPolygon(polygon.points)
    points = ShapelyPoint(point[0], point[1])
    if polygon_shapely.contains(points):
        return True
    return False


def is_touching(polygon_1, polygon_2):
    p1_s = ShapelyPolygon(polygon_1.points) # p1 shapely
    p2_s = ShapelyPolygon(polygon_2.points) # p2 shapely

    # Check for intersection
    if p1_s.intersects(p2_s):
        return True

    return False

def extract_properties_improved(polygons, nets):
    poly_counter = 0
    diff_counter = 0

    # giving ids for all polys and diffs
    for n in nets:
        for poly in n.polys:
            poly.id = poly_counter

            for r in polygons["rvt"]:
                if are_they_connected(r, poly):
                    poly.vt_box.append(r.id)

            poly_counter += 1

        for diff in n.diffs:
            diff.id = diff_counter
            diff_counter += 1

    instances = {}  # np.empty([1,total_poly_no])
    for n in nets:
        for poly in n.polys:
            vt_ind = poly.vt_box[0]
            vt_polygon = polygons["rvt"][vt_ind]
            r_point = [poly.mid + 78 / 2, vt_polygon.mid_point[1]]  # poly pitch/2
            l_point = [poly.mid - 78 / 2, vt_polygon.mid_point[1]]  # poly pitch/2

            # search for diffs
            instance_i = [-1, -1]
            for net in nets:
                for diff in net.diffs:
                    # print(f"-- {l_point}, {diff.mid} --")
                    if is_point_inside_the_polygon(l_point, diff):
                        instance_i[0] = diff.id
                    if is_point_inside_the_polygon(r_point, diff):
                        instance_i[1] = diff.id

            instances[poly.id] = instance_i

    # identifying instances with shared diffusion
    class Diff:
        def __init__(self):
            self.net = -1
            self.instances = []
            self.type = ''
            self.side = ''

    diff_array = {}  # diffs, associated_instances, net_name
    for key in instances:
        inst = instances[key]

        l_diff = inst[0]
        r_diff = inst[1]
        l_diff_i = Diff()
        r_diff_i = Diff()

        if not l_diff in diff_array:
            l_diff_i.instances.append(key)
            l_diff_i.side = 'l'
            diff_array[l_diff] = l_diff_i
        else:
            diff_array[l_diff].side = 'b'
            diff_array[l_diff].instances.append(key)

        if not r_diff in diff_array:
            r_diff_i.instances.append(key)
            r_diff_i.side = 'r'
            diff_array[r_diff] = r_diff_i
        else:
            diff_array[r_diff].side = 'b'
            diff_array[r_diff].instances.append(key)

    # assigning nets to the diffusions
    for n in nets:
        for diff in n.diffs:
            if diff.id in diff_array:
                diff_array[diff.id].net = n.id[0]

    # identifying the first source and drain diffs
    visited = set()
    for key in diff_array:
        if diff_array[key].side == 'l' and len(diff_array[key].instances) == 1:
            diff_array[key].type = 's'
            for k in instances:
                ins = instances[k]
                if ins[0] == key:
                    diff_array[ins[1]].type = 'd'
                    visited.add(ins[0])
                    visited.add(ins[1])

    t = ["s", "d"]
    while len(visited) != len(diff_array):
        for k, ins in instances.items():
            if len(visited.intersection(ins)) == 1:
                # print("visited",visited, "ins", ins, len(visited.intersection(ins)))
                a = visited.intersection(ins)
                i = ins.index(list(a)[0])
                # print("intersection:",a, "index", i)
                diff_array[ins[i ^ 1]].type = t[t.index(diff_array[ins[i]].type) ^ 1]
                visited.update(ins)

    # identifying parallel instances using the net names
    parallel_instances = []
    inst_index = list(instances.keys())
    inst_visit = [False for _ in range(len(inst_index))]
    for i in range(len(inst_index)):
        if i == len(inst_index) - 1:
            parallel_instances.append({inst_index[i]})
            break
        group = set()
        group.add(inst_index[i])
        if inst_visit[inst_index[i]] == False:
            for j in range(i + 1, len(inst_index)):
                diffs_i = instances[inst_index[i]]
                diffs_j = instances[inst_index[j]]

                nets_i = {diff_array[diffs_i[0]].net, diff_array[diffs_i[1]].net}
                nets_j = {diff_array[diffs_j[0]].net, diff_array[diffs_j[1]].net}

                if nets_i == nets_j:
                    group.add(inst_index[j])
                    inst_visit[inst_index[j]] = True

            parallel_instances.append(group)

    # giving actual names (replacing the id's) for the diffusions and polys
    instance_names = []
    for n in nets:
        for poly in n.polys:
            for i, groups in enumerate(parallel_instances):
                if poly.id in groups:
                    groups_list = list(groups)
                    name = "MN" + str(i) + "@" + str(groups_list.index(poly.id))
                    poly.id = name
                    instance_names.append(poly.id)

    for n in nets:
        for diff in n.diffs:
            new_diff_id = []
            if diff.id in diff_array:
                for inst in diff_array[diff.id].instances:
                    for i, groups in enumerate(parallel_instances):
                        if inst in groups:
                            groups_list = list(groups)
                            inst_name = "MN" + str(i) + "@" + str(groups_list.index(inst))
                            new_diff_id.append(inst_name + ":" + diff_array[diff.id].type)
            diff.id = new_diff_id

    def divide_list(original_list, n):
        chunk_size = len(original_list) // n
        chunks = [original_list[i:i + chunk_size] for i in range(0, len(original_list), chunk_size)]
        if len(chunks) > n:
            last_chunk = chunks.pop()  # Remove the last chunk
            chunks[-1].extend(last_chunk)  # Append it to the previous chunk
        return chunks

    h_counter = 0
    for n in nets:
        for d in n.diffs:
            if d.orientation == "h":
                h_counter += 1
    nm = divide_list(instance_names, h_counter)

    counter = 0
    for n in nets:
        for d in n.diffs:
            if d.orientation == "h":
                lst = []
                for i in range(len(nm[counter])):
                    lst.append(nm[counter][i] + ":b")
                d.id = lst
                counter += 1

    return instances, diff_array


def extract_fins(polygons):
    p_s = polygons["polys"]
    f_s = polygons["fins"]
    d_s = polygons["diffusions"]
    a_a = polygons["active_areas"]

    a_i = 0
    aa = 0
    for i, ar in enumerate(a_a):
        if ar.area > aa:
            aa = ar.area
            a_i = i

    fins = 0
    # gate = -2
    #
    # for p in p_s:
    #     if is_touching(p, a_a[a_i]):
    #         gate += 1

    for f in f_s:
        if is_touching(f, a_a[a_i]):
            fins += 1

    # fingers = len(d_s)-2
    # multiplier = len(a_a)-1

    return fins #, fingers, gate, multiplier

def are_they_connected(polygon_1, polygon_2, vias=None):
    p1_s = ShapelyPolygon(polygon_1.points) # p1 shapely
    p2_s = ShapelyPolygon(polygon_2.points) # p2 shapely

    if vias is None:
        if p1_s.intersects(p2_s):
            return True
    else:
        if p1_s.intersects(p2_s):
            if polygon_1.layer == polygon_2.layer:
                return True
            intersection = p1_s.intersection(p2_s)
            if set([polygon_1.layer, polygon_2.layer]) == set([14, 15]):   # checking connection between diffusion and metal 1
                if any(intersection.contains(ShapelyPoint(v.mid_point)) and v.layer == 35 for v in vias):
                    return True

            if set([polygon_1.layer, polygon_2.layer]) == set([15, 245]):   # checking connection between cb and metal 1
                if any(intersection.contains(ShapelyPoint(v.mid_point)) and v.layer == 35 for v in vias):
                    return True

            if set([polygon_1.layer, polygon_2.layer]) == set([15, 17]):   # checking connection between metal 1 and metal 2
                if any(intersection.contains(ShapelyPoint(v.mid_point)) and v.layer == 16 for v in vias):
                    return True

            if set([polygon_1.layer, polygon_2.layer]) == set([17, 19]):  # checking connection between metal 2 and metal 3
                if any(intersection.contains(ShapelyPoint(v.mid_point)) and v.layer == 18 for v in vias):
                    return True
    return False



def cut_polygons(polys, cts):
  for j in range(len(cts)):
    del_index = []
    for i in range(len(polys)):
        p1 = polys[i].points
        p2 = polys[i].points.copy()
        if are_they_connected(polys[i], cts[j]):
            p1[0][1] = cts[j].points[2][1]+20
            p1[1][1] = cts[j].points[2][1]+20
            p2[2][1] = cts[j].points[0][1]-20
            p2[3][1] = cts[j].points[0][1]-20
            polys.append(polygon(p1, layer= polys[i].layer, data= polys[i].data, id = -1))
            polys.append(polygon(p2, layer= polys[i].layer, data= polys[i].data, id = -1))
            del_index.append(i)

    for k in sorted(del_index, reverse=True):
        del polys[k]





def get_nets(polygons):

    metals = polygons["metal_1"]+polygons["metal_2"]+polygons["metal_3"]
    v_0 = polygons["via_0"]
    v_1 = polygons["via_1"]
    v_2 = polygons["via_2"]

    p_i = polygons["pins"]
    c_b = polygons["cb"]
    diff = polygons["diffusions"]
    p_s = polygons["polys"]
    b_p = polygons["bp"]
    rvt = polygons["rvt"]

    e = []
    visited = np.empty_like(metals)
    for i in range(len(metals)):
        for j in range(i + 1, len(metals)):
            if are_they_connected(metals[i], metals[j], v_1+v_2):
                e.append([i, j])
                visited[i] = True
                visited[j] = True

    for i, v in enumerate(visited):
        if not v:
            e.append([i, i])


    changed = True
    while changed:
        changed = False
        for i in range(len(e)):
            for j in range(i + 1, len(e)):
                if set(e[i]).intersection(e[j]):
                    e[i] = list(set(e[i] + e[j]))
                    del e[j]
                    changed = True
                    break
    nets = []
    for r in e:
        mi = []
        for i in r:
            mi.append(metals[i])

        ni = Net()
        ni.metals = mi
        nets.append(ni)

    # print(e)

    # Assigning labels
    all_metals = []
    for i in range(len(nets)):
        all_metals.append(nets[i].metals)

    outer_flag = False
    for p in p_i:
        for i, groups in enumerate(all_metals):
            for ms in groups:
                if ([p.layer, ms.layer] == [16, 17] or [p.layer, ms.layer] == [15, 15]) and is_point_inside_the_polygon(p.points, ms):
                    nets[i].label = p
                    print(i, p.text)
                    nets[i].id.append(p.text)
                    outer_flag = True
                    break  # break innermost loop
            if outer_flag:
                break  # break middle loop
        if outer_flag:
            outer_flag = False  # Reset the flag
            continue  # continue the outermost loop



    # Assigning via_0
    outer_flag = False
    for v in v_0 + v_1:
        for i, groups in enumerate(all_metals):
            for ms in groups:
                if (((v.layer == 35 or v.layer == 16) and ms.layer == 15) or (
                        v.layer == 16 and ms.layer == 17)) and is_point_inside_the_polygon(v.mid, ms):
                    nets[i].vias.append(v)
                    outer_flag = True
                    break  # break innermost loop
            if outer_flag:
                break  # break middle loop
        if outer_flag:
            outer_flag = False  # Reset the flag
            continue  # continue the outermost loop

    # Assigning diffusions
    outer_flag = False
    for p in diff:
        for i, groups in enumerate(all_metals):
            for ms in groups:
                if are_they_connected(p, ms, v_0) and ms.layer == 15:
                    nets[i].diffs.append(p)
                    outer_flag = True
                    break  # break innermost loop
            if outer_flag:
                break  # break middle loop
        if outer_flag:
            outer_flag = False  # Reset the flag
            continue  # continue the outermost loop


    # Assigning cb
    outer_flag = False
    for p in c_b:
        for i, groups in enumerate(all_metals):
            for ms in groups: # gets the metals
                if are_they_connected(p, ms, v_0) and ms.layer == 15:
                    nets[i].cbs.append(p)
                    outer_flag = True
                    break  # break innermost loop
            if outer_flag:
                break  # break middle loop
        if outer_flag:
            outer_flag = False  # Reset the flag
            continue  # continue the outermost loop


    # Assigning bp
    outer_flag = False
    for p in b_p:
        for i, groups in enumerate(all_metals):
            for ms in groups:
                if is_point_inside_the_polygon([(p.points[0][0]+p.points[1][0])/2, (p.points[1][1]+p.points[2][1])/2], ms):
                    nets[i].bps.append(p)
                    outer_flag = True
                    break  # break innermost loop
            if outer_flag:
                break  # break middle loop
        if outer_flag:
            outer_flag = False  # Reset the flag
            continue  # continue the outermost loop

    cbx = []
    for i in range(len(nets)):
        cbx.append(nets[i].cbs)



    # Assigning poly
    outer_flag = False
    for p in p_s:
        for i, groups in enumerate(cbx):
            for ms in groups:
                if is_touching(p, ms):
                    nets[i].polys.append(p)
                    outer_flag = True
                    break  # break innermost loop
            if outer_flag:
                break  # break middle loop
        if outer_flag:
            outer_flag = False  # Reset the flag
            continue  # continue the outermost loop
            
    return nets


def convert_net_to_stick(net, th1, th2):
    sticks = []
    for metal in net.metals:
        if metal.orientation == "v":
            s = [((metal.points[0][0] + metal.points[1][0]) / 2, metal.points[1][1]),
                 ((metal.points[0][0] + metal.points[1][0]) / 2, metal.points[2][1])]
        else:
            s = [(metal.points[0][0], (metal.points[1][1] + metal.points[2][1]) / 2),
                 (metal.points[1][0], (metal.points[1][1] + metal.points[2][1]) / 2)]
        sticks.append(s)

    def is_close(point1, point2, threshold):
        """Check if two points are within the threshold distance."""
        return np.linalg.norm(np.array(point1) - np.array(point2)) <= threshold

    def are_collinear(p1, p2, p3):
        """Check if three points are collinear."""
        return np.cross(np.array(p2) - np.array(p1), np.array(p3) - np.array(p1)) == 0

    def join_sticks(sticks, threshold):
        joined_sticks = []
        used_sticks = [False] * len(sticks)

        for i, (start1, end1) in enumerate(sticks):
            if used_sticks[i]:
                continue
            for j, (start2, end2) in enumerate(sticks):
                if i != j and not used_sticks[j]:
                    # Check if sticks are collinear and connectable without a bend
                    if are_collinear(start1, end1, start2):
                        if is_close(end1, start2, threshold):
                            joined_sticks.append([list(start1), list(end2)])
                            used_sticks[i] = used_sticks[j] = True
                            break
                        elif is_close(start1, end2, threshold):
                            joined_sticks.append([list(end1), list(start2)])
                            used_sticks[i] = used_sticks[j] = True
                            break
                    # Check if sticks can be connected with an additional stick
                    elif is_close(end1, start2, threshold):
                        joined_sticks.append([list(start1), list(start2)])
                        joined_sticks.append([list(end1), list(end2)])
                        used_sticks[i] = used_sticks[j] = True
                        break
            else:
                joined_sticks.append([list(start1), list(end1)])
                used_sticks[i] = True

        return joined_sticks

    joined_sticks = join_sticks(sticks, th1)

    js = []
    for s in joined_sticks:
        js.append(Stick(s[0], s[1]))

    for i in range(len(js)):
        for j in range(len(js)):
            si = js[i]
            sj = js[j]

            if si.alignment == "H" and sj.alignment == "V":
                if si.xi <= sj.xi <= si.xf:
                    if abs(sj.yi - si.yi) < th2:
                        js[j] = Stick([sj.xi, si.yi], [sj.xf, sj.yf])

                    elif abs(sj.yf - si.yi) < th2:
                        js[j] = Stick([sj.xi, sj.yi], [sj.xi, si.yi])

            elif si.alignment == "V" and sj.alignment == "H":
                if si.yi <= sj.yi <= si.yf:
                    if abs(si.xi - sj.xi) < th2:
                        js[j] = Stick([si.xi, sj.yi], [sj.xf, sj.yf])
                    elif abs(si.xi - sj.xf) < th2:
                        js[j] = Stick([sj.xi, sj.yi], [si.xi, sj.yf])

    return js, joined_sticks


def find_all_nodes(sticks, net, node_reduction = False, threshold_in_nm = 10):
    intersections = []
    ends = []
    nodes = []
    for i, st in enumerate(sticks):
        start1 = (st.xi, st.yi)
        end1 = (st.xf, st.yf)

        # Check for ends at the endpoints
        ends.append([st.xi, st.yi])
        ends.append([st.xf, st.yf])

        # Check for intersections with other sticks
        for j, st in enumerate(sticks[i + 1:], start=i + 1):
            start2 = (st.xi, st.yi)
            end2 = (st.xf, st.yf)
            intersection = find_intersection(start1, end1, start2, end2)
            if intersection is not None:
                intersections.append(intersection)

    for point in intersections:
        nd = {}
        nd["p"] = [point[0], point[1]]
        nd["t"] = "I"
        nodes.append(nd)

    for point in ends:
        nd = {}
        nd["p"] = [point[0], point[1]]
        nd["t"] = "E"
        nodes.append(nd)

    for v in net.vias:
        nd = {}
        nd["p"] = [v.mid[0], v.mid[1]]
        nd["t"] = v.layer
        nodes.append(nd)

    nd = {}
    la = net.label
    nd["p"] = [la.points[0], la.points[1]]
    nd["t"] = "L"
    nodes.append(nd)

    i = 0
    if node_reduction:
        while i < len(nodes) - 1:
            j = i + 1
            while j < len(nodes):
                dist = ((nodes[i]["p"][0] - nodes[j]["p"][0]) ** 2 + (nodes[i]["p"][1] - nodes[j]["p"][1]) ** 2) ** 0.5
                if dist <= threshold_in_nm and nodes[i]["t"]!="L" and nodes[j]["t"]!="L":
                    nodes[i]["t"] = [nodes[i]["t"], nodes[j]["t"]]
                    del nodes[j]
                else:
                    j += 1
            i += 1

    return nodes


def find_intersection(p1, p2, p3, p4):
    """Find the intersection point of two line segments if it exists."""
    # Convert points to numpy arrays for vector operations
    p1, p2, p3, p4 = map(np.array, [p1, p2, p3, p4])
    # Line segments are defined as p1 + t*(p2 - p1) and p3 + u*(p4 - p3)
    # We need to find t and u such that the line segments intersect
    d1 = p2 - p1
    d2 = p4 - p3
    denom = d1[0] * d2[1] - d1[1] * d2[0]

    if denom == 0:
        return None  # Lines are parallel or collinear

    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / denom
    u = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        intersection = p1 + t * d1
        return tuple(intersection)

    return None


def adjacent_nodes(nd, nodes, js):
    lines = []
    candidate_nodes = []
    for s in js:
        if is_point_in_stick([nd["p"][0], nd["p"][1]], s):
            lines.append(s)

    for ln in lines:
        for i, nd_ in enumerate(nodes):
            if is_point_in_stick([nd_["p"][0], nd_["p"][1]], ln):
                if nd_["p"] != nd["p"]:
                    candidate_nodes.append(i)

    # print("candidate_nodes: ", candidate_nodes)

    t, b, r, l = [], [], [], []

    for cnd in candidate_nodes:
        dx = nd["p"][0] - nodes[cnd]["p"][0]
        dy = nd["p"][1] - nodes[cnd]["p"][1]
        if abs(dx) <= 10 and dy < 0:
            t.append(cnd)
        elif abs(dx) <= 10 and dy > 0:
            b.append(cnd)
        elif abs(dy) <= 10 and dx < 0:
            r.append(cnd)
        elif abs(dy) <= 10 and dx > 0:
            l.append(cnd)

    # print("Top Nodes:", t)

    t_node, b_node, r_node, l_node = -1, -1, -1, -1

    if len(t) != 0:
        t_node = t[0]
        delta = np.inf
        for ti in t:
            if (nodes[ti]["p"][1] - nd["p"][1]) < delta:
                delta = nodes[ti]["p"][1] - nd["p"][1]
                t_node = ti

    if len(b) != 0:
        b_node = b[0]
        delta = np.inf
        for bi in b:
            if (nd["p"][1] - nodes[bi]["p"][1]) < delta:
                delta = nd["p"][1] - nodes[bi]["p"][1]
                b_node = bi

    if len(r) != 0:
        r_node = r[0]
        delta = np.inf
        for ri in r:
            if (nodes[ri]["p"][0] - nd["p"][0]) < delta:
                delta = nodes[ri]["p"][0] - nd["p"][0]
                r_node = ri

    if len(l) != 0:
        l_node = l[0]
        delta = np.inf
        for li in l:
            if (nd["p"][0] - nodes[li]["p"][0]) < delta:
                delta = nd["p"][0] - nodes[li]["p"][0]
                l_node = li

    res = [t_node, b_node, l_node, r_node]
    ret = []
    for r in res:
        if r != -1:
            ret.append(r)

    return ret


def generate_instance_name(m0_finger, m1_finger, first_d="s"):
    total_fingers = int(m0_finger+m1_finger)
    instances = []
    s_and_d = []

    bo = True
    m0 = 1
    m1 = 1

    for i in range(int(total_fingers / 2)):
        if bo:
            if m0 == 1:
                instances.append("MN0")
                instances.append("MN0" + "@" + str(m0 + 1))
            else:
                instances.append("MN0" + "@" + str(m0))
                instances.append("MN0" + "@" + str(m0 + 1))

            m0 += 2
            bo = not bo

        else:
            if m1 == 1:
                instances.append("MN1")
                instances.append("MN1" + "@" + str(m1 + 1))
            else:
                instances.append("MN1" + "@" + str(m1))
                instances.append("MN1" + "@" + str(m1 + 1))

            m1 += 2
            bo = not bo

    b = True
    for i in range(total_fingers + 1):
        if b:
            s_and_d.append("s")
            b = False
        else:
            s_and_d.append("d")
            b = True

    return s_and_d, instances


def plot_polygons(polygons,xlim=[0,0], ylim=[0,0], size=1000, label = -1):
  fig, ax = plt.subplots()
  for m in polygons:
    x, y, w, h = xw(m.points)
    rect = patches.Rectangle((x, y), w, h, edgecolor='r', facecolor='red')
    ax.add_patch(rect)
    ax.set_xlim(xlim[0],xlim[1])
    ax.set_ylim(ylim[0],ylim[1])
    if label != -1:
        ax.text(label.points[0], label.points[1], label.text, fontsize=14,
                color='blue', style='italic', weight='bold',
                verticalalignment='center', horizontalalignment='center')

  plt.show()


def plot_nets(nets, size = 1000):
  fig, ax = plt.subplots()
  color_lst = get_colors(len(nets))
  for ci, net in enumerate(nets):
      for m in net.metals:
          x, y, w, h = xw(m.points)
          rect = patches.Rectangle((x, y), w, h, edgecolor='r', facecolor=color_lst[ci])
          ax.add_patch(rect)
          ax.set_xlim(0, size)
          ax.set_ylim(0, size)
          ax.text(net.label.points[0], net.label.points[1], net.label.text, fontsize=14, color='blue', style='italic',
                      weight='bold',
                      verticalalignment='center', horizontalalignment='center')

          for v in net.vias:
              if v.layer == 35:
                ax.plot(v.mid[0], v.mid[1], '*', color = "blue")
              elif v.layer == 16:
                ax.plot(v.mid[0], v.mid[1], '*', color="red")

  plt.show()


def plot_sticknets(js, nodes):
    plt.subplot(1, 2, 2)
    # Plotting the sticks
    for st in js:
        plt.plot(st.px, st.py, 'k-')
    for i, nd in enumerate(nodes):
        if nd["t"] == "I":
            plt.plot(nd["p"][0], nd["p"][1], 'ok')
        elif nd["t"] == "E":
            plt.plot(nd["p"][0], nd["p"][1], 'og')
        elif nd["t"] == "L":
            plt.plot(nd["p"][0], nd["p"][1], '*r')
        else:
            plt.plot(nd["p"][0], nd["p"][1], 'ob')

        x_r = 0
        y_r = 0 + np.random.randint(-20, 20)
        # plt.text(nd["p"][0]+x_r,nd["p"][1]+y_r,str(i)+" - "+str(nd["p"]),fontsize=7, color='red') # with coordinates
        plt.text(nd["p"][0] + x_r, nd["p"][1] + y_r, str(i) + " - " + str(nd["t"]), fontsize=7,
                 color='red')  # with type
        # plt.text(nd["p"][0]+x_r,nd["p"][1]+y_r,str(i),fontsize=9, color='red')

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()