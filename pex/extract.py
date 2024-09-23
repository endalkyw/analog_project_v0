from pex.ext_util import *
from visualizer.plot_funcs import *
import numpy as np
from pex.data_structs import *
from pex.mos_param import *
import os
import re
# -----------------------------------------------------------------
current_dir = os.path.dirname(__file__)

def write_dspf(parasitics, instances, file_name):
    """
    Instances : list of params
    Parasitics: list of net_parasitics
    """

    instances_string= "\n".join(instances)

    parasitics_list = []
    R, C = 1, 1
    port_names = []
    for par in parasitics:
        temp_res_list = []
        temp_cap_list = []
        port_names.append(par.net_name)

        for res in par.res_list:
            temp_res_list.append("R"+str(R)+" "+res[0]+" "+res[1]+" "+str(res[2]))
            R+=1

        for cap in par.cap_list:
            temp_cap_list.append("C"+str(C)+" "+cap[0]+" "+cap[1]+" "+str(cap[2]))
            C+=1

        temp_res_string = "\n".join(temp_res_list)
        temp_cap_string = "\n".join(temp_cap_list)
        parasitics_list.append("* Net:"+par.net_name+" ----------------")
        parasitics_list.append(temp_res_string+"\n"+temp_cap_string)


    parasitics_string = "\n\n\n".join(parasitics_list)
    body = parasitics_string + "\n"*3 + instances_string
    pattern = r'[^/]+(?=\.[^.]+$)'
    name = re.search(pattern, file_name)
    contents = {"body":body, "design_name":name.group(0), "ports":" ".join(sorted(port_names))}

    f2 = os.path.join(current_dir, "templates/dspf_wrapper.txt")
    with open(f2, "r") as inp_file:
        wrapper_text = inp_file.read()

    final_output = wrapper_text.format(**contents)

    with open(file_name,"w") as out_file:
        out_file.write(final_output)

def extract_layout(target_net, nets, polygons, cell, img_output = True):
    #  1) convert each nets into a stick diagram
    js, _ = convert_net_to_stick(target_net, th1=50, th2=20)  # th1 - for joining lines and th2 - for min-gap removal
    nodes = find_all_nodes(js, target_net, node_reduction=True)

    if img_output:
        fig, axes = plt.subplots(1, 4, figsize=(12, 4))  # Create a figure with 2 subplots, arranged vertically
        show_gds(axes[0], cell)
        show_nets(axes[1], nets)
        show_nets(axes[2], [target_net])
        show_stk_nets(axes[3], js, nodes)
        plt.tight_layout()
        plt.savefig("temp/img_"+str(target_net.id[0])+".png")
        plt.close()

    graph = np.empty_like(nodes)
    for i, nd in enumerate(nodes):
        adj = adjacent_nodes(nd, nodes, js)
        graph[i] = adj

    def dfs_iterative(graph, start):
        visited = set()
        stack = [start]
        res = []
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                neighbors = []
                for neighbor in graph[vertex]:
                    if neighbor not in visited:
                        neighbors.append(neighbor)

                stack.extend(neighbors)
                res.append([vertex, neighbors])
                # stack.extend(neighbor for neighbor in graph[vertex] if neighbor not in visited)

        return res

    label_index = 0
    for i, nd in enumerate(nodes):
        if nd["t"] == "L":
            label_index = i
            break

    nds = dfs_iterative(graph, label_index)

    label = target_net.label.text
    Resistors = []
    Capacitors = []

    for i in range(len(nds)):
        for j in range(len(nds[i][1])):
            ni = nodes[nds[i][0]]
            nf = nodes[nds[i][1][j]]
            dist = ((ni["p"][0] - nf["p"][0]) ** 2 + (ni["p"][1] - nf["p"][1]) ** 2) ** 0.5

            if ni["t"] == "L":
                r = [label, label + ":" + str(nds[i][1][j]), round(dist * 0.028, 3)]
                Resistors.append(r)
            elif ni["t"] == 35 or type(ni["t"]) == list:
                r1 = [label + ":" + str(nds[i][0]), label + ":" + str(nds[i][1][j]), round(dist * 0.028, 3)]
                c = [label + ":" + str(nds[i][0]), "0", dist * 210e-18, 3]
                Resistors.append(r1)
                Capacitors.append(c)

                # findng the diffusion name(id)
                for df in target_net.diffs:
                    if (is_point_inside_the_polygon(ni["p"], df) and df.orientation == "v"):
                        if len(df.id) > 1:
                            diff_name = df.id[0]
                        else:
                            diff_name = df.id[0]

                        r2 = [label + ":" + str(nds[i][0]), diff_name, 14]
                        Resistors.append(r2)
                        break
                    elif (is_point_inside_the_polygon(ni["p"], df) and df.orientation == "h"):
                        diff_name = df.id[0]
                        r2 = [label + ":" + str(nds[i][0]), diff_name, 14]
                        Resistors.append(r2)
                        break

                # findng the polys name/id
                for cb in target_net.cbs:  # only one cb per net
                    if (is_point_inside_the_polygon(ni["p"], cb)):
                        for poly in target_net.polys:
                            if type(poly.id) != list:
                                poly_name = poly.id
                            else:
                                poly_name = poly.id[0]

                            r2 = [label + ":" + str(nds[i][0]), poly_name + ":" + "g", 342]
                            Resistors.append(r2)
                        break

            elif ni["t"] == 16:
                r2 = [label + ":" + str(nds[i][0]), label + ":" + str(nds[i][1][j]), 14 + round(dist * 0.028, 3)]
                Resistors.append(r2)
                c = [label + ":" + str(nds[i][0]), "0", dist * 210e-18, 3]
                Capacitors.append(c)

            else:
                r = [label + ":" + str(nds[i][0]), label + ":" + str(nds[i][1][j]), round(dist * 0.028, 3)]
                c = [label + ":" + str(nds[i][0]), "0", dist * 210e-18, 3]
                Resistors.append(r)
                Capacitors.append(c)

    for df in target_net.diffs:
        if len(df.id) > 1:
            if df.orientation == "v":
                r = [str(df.id[0]), str(df.id[1]), 0.01]
                Resistors.append(r)

            if df.orientation == "h":
                for i in range(len(df.id) - 1):
                    r = [str(df.id[i]), str(df.id[i + 1]), 0.01]
                    Resistors.append(r)

    # p = net_parasitics(label, Resistors, Capacitors)
    # # for i, r in enumerate(p.res_list):
    # #     print(i, r)

    return net_parasitics(label, Resistors, Capacitors)


def pex(file_path):
    # 1) Read the target gds file
    lib = gdstk.read_gds(file_path+".gds")

    #2) Get desired polygons from the gds file
    polygons = get_polygons(lib.cells[0])
    nets = get_nets(polygons)

    #3) identify arrangements and connection of instances
    instances, diff_array = extract_properties_improved(polygons,nets)

    # 3) Parasitics
    parasitics = []
    for net in nets:
        pi = extract_layout(net, nets, polygons, lib.cells[0], img_output = False)
        parasitics.append(pi)

    fins = extract_fins(polygons)
    inst = []
    for n in nets:
        for rvt in polygons["rvt"]:
            for p in n.polys:
                if are_they_connected(p, rvt):
                    rvt_nw = False

                    for nw in polygons["nwell"]:
                        if is_point_inside_the_polygon(rvt.mid_point, nw):
                            rvt_nw = True

                    if rvt_nw:
                        pr = params()
                        inst_str = pr.get_mos_string(p.id, "pfet", fins, 1, 1)
                        inst.append(inst_str)
                    else:
                        pr = params()
                        inst_str = pr.get_mos_string(p.id, "nfet", fins, 1, 1)
                        inst.append(inst_str)

    write_dspf(parasitics, inst, f"{file_path}.dspf")

    bbox = lib.cells[0].bounding_box()
    lower_left, upper_right = bbox
    width = upper_right[0] - lower_left[0]
    height = upper_right[1] - lower_left[1]
    area = width * height
    aspect_ratio = width/height

    info = [
        f"Area, nm^2: {area}",
        f"Aspect_ratio: {round(aspect_ratio,3)}",
        f"Fins: {fins}",
        f"Instances: {len(instances)}",
        f"Nets: {len(nets)}"
    ]

    with open(f"{file_path}.info", "w") as file:
        file.write("\n".join(info))

def main():
    # file_path = "../outputs/nmos_dp_6x5_2"
    file_path = "../outputs/nmos_cm_x"
    # file_path = "../outputs/nmos_cm"

    pex(file_path)

if __name__ == "__main__":
    main()
