import matplotlib.pyplot as plt
from matplotlib import patches

import gdstk
import yaml
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
f = n_file = os.path.join(base_dir, '../layout_gen/layer_param.yml')
import numpy as np

with open(f, 'r') as file:
    lp = yaml.safe_load(file)  # layers properties

# fig, ax = plt.subplots(figsize=fig_size, dpi=300)

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




def show_gds(ax,cell):
    layer_colors = lp['Colors']
    for polygon in cell.polygons:
        points = polygon.points
        layer = polygon.layer
        color = layer_colors.get(layer, 'gray')  # Default color is black if layer not specified
        ax.fill(*zip(*points), color=color, alpha=0.3)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])


def show_nets(ax, nets, vias_on = False):
  color_lst = get_colors(len(nets))
  for ci, net in enumerate(nets):
      for m in net.metals:
          x, y, w, h = xw(m.points)
          rect = patches.Rectangle((x, y), w, h, edgecolor='r', facecolor=color_lst[ci])
          ax.add_patch(rect)
          ax.text(net.label.points[0], net.label.points[1], net.label.text, fontsize=14, color='blue', style='italic',
                      weight='bold', verticalalignment='center', horizontalalignment='center')

      if vias_on:
        for v in net.vias:
            if v.layer == 35:
              ax.plot(v.mid[0], v.mid[1], '*', color = "blue")
            elif v.layer == 16:
              ax.plot(v.mid[0], v.mid[1], '*', color="red")


  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  ax.spines['bottom'].set_visible(False)
  ax.set_aspect('equal')
  ax.set_xticks([])
  ax.set_yticks([])


def show_stk_nets(ax, js, nodes):
    for st in js:
        ax.plot(st.px, st.py, 'k-')
    for i, nd in enumerate(nodes):
        if nd["t"] == "I":
            ax.plot(nd["p"][0], nd["p"][1], 'ok')
        elif nd["t"] == "E":
            ax.plot(nd["p"][0], nd["p"][1], 'og')
        elif nd["t"] == "L":
            ax.plot(nd["p"][0], nd["p"][1], '*r')
        else:
            ax.plot(nd["p"][0], nd["p"][1], 'ob')

        x_r = 10
        y_r = 10#np.random.randint(-20, 20)
        ax.text(nd["p"][0] + x_r, nd["p"][1] + y_r, str(i), fontsize=7, color='red')  # with type
        # ax.text(nd["p"][0] + x_r, nd["p"][1] + y_r, str(i) + " - " + str(nd["t"]), fontsize=7,color='red')  # with type

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])