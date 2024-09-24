from layout_gen.utilities.elements_utils import *
from layout_gen.primitives.current_mirror import current_mirror
from layout_gen.primitives.differential_pair import differential_pair
from layout_gen.core.base_fabric import *
import matplotlib.pyplot as plt
import matplotlib
import math
from layout_gen.utilities.via import *

def find_center(rects):
    delta_x = 0
    bigger_rect = 0
    for r in rects:
        if delta_x < r[1][0]-[0][0]:
            bigger_rect = r

    return (bigger_rect[1][0]+bigger_rect[0][0])/2

# five transistor ota

# nmos current mirror
m0 = Mos({'id': 'A', 'fins': 16, 'fingers': 6, 'stack': 1, 'multiplier': 1, 'mos_type': "N"})
m1 = Mos({'id': 'A', 'fins': 16, 'fingers': 6, 'stack': 1, 'multiplier': 1, 'mos_type': "N"})
n_cc = current_mirror(m0, m1, "test_cm")
n_cc.create_layout(4, labels=("d0", "d1", "s"), con=[1, 1, 1], fabric_on=False)
n_cc_b = n_cc.cell.bounding_box()

# pmos current mirror
m0 = Mos({'id': 'A', 'fins': 8, 'fingers': 10, 'stack': 1, 'multiplier': 1, 'mos_type': "P"})
m1 = Mos({'id': 'A', 'fins': 8, 'fingers': 10, 'stack': 1, 'multiplier': 1, 'mos_type': "P"})
p_cc = current_mirror(m0, m1, "test_cm")
p_cc.create_layout(0, labels=("d0", "d1", "s"), con=[1, 1, 1], fabric_on=False)
p_cc_b = n_cc.cell.bounding_box()

# nmos differential pair
m0 = Mos({'id': 'A', 'fins': 20, 'fingers': 30, 'stack': 1, 'multiplier': 2, 'mos_type': "N"})
m1 = Mos({'id': 'A', 'fins': 20, 'fingers': 30, 'stack': 1, 'multiplier': 2, 'mos_type': "N"})
n_dp = differential_pair(m0, m1, "test_dp")
n_dp.create_layout(4, labels=("b", "g0", "g1", "d0", "d1", "s"), con=[2, 2, 2], fabric_on=False) # connectors d0, d1, s
n_dp_b = n_dp.cell.bounding_box()

cell = create_empty_cell("five_t_ota", 1e-9, 1e-12)



c = find_center([p_cc_b,n_cc_b,n_dp_b])

y = 0
x = c-(n_cc_b[1][0]+n_cc_b[0][0])/2
add_transformed_polygons(n_cc.cell, cell, (x, y))

y += n_cc_b[1][1]+200
x = c-(n_dp_b[1][0]+n_dp_b[0][0])/2
add_transformed_polygons(n_dp.cell, cell, (x, y))

y += n_dp_b[1][1]+200
x = c-(p_cc_b[1][0]+p_cc_b[0][0])/2
add_transformed_polygons(p_cc.cell, cell, (x, y))




# -------- poly and fins fabric inclusion ------------------------------------------
p = cell.bounding_box()
poly_n = math.ceil((p[1][0] - p[0][0]) / lp["poly"]["pitch"]) - 1   + 15
fin_n = math.ceil((p[1][1] - p[0][1]) // lp["fins"]["pitch"]) + 15
x_ = 0
y_ = 0

cell_x = create_empty_cell("five_t_ota", 1e-9, 1e-12)
create_fabric(cell_x, poly_n, fin_n)
x_ = (3 + 1) * (lp['poly']['dummies'] - 1) * lp['poly']['pitch'] + 23 + lp['poly']['width'] / 2
y_ = (3 + 1) * lp['fins']['dummies'] * lp["fins"]["pitch"] - (lp['fins']['pitch'] - lp['fins']['width']) / 2
add_transformed_polygons(cell, cell_x, (x_, y_))

# -------- power grid construction ------------------------------------------
c = cell_x.bounding_box()
grd = add_power_grid(cell_x, P(c[0][0], c[0][1]), P(c[1][0], c[1][1]), "M4", "M5", 5*78, 5*78)
# print(grd)
# x = 0
# for v in grd["V"]:
#     for h in grd["H"]:
#         inter = get_intersection(v, h)
#         x, y = inter.exterior.xy
#         add_via(cell_x,(x[0], y[0]), "V3")







plt.rcParams['figure.facecolor'] = 'black'  # Set figure background
plt.rcParams['axes.facecolor'] = 'black'    # Set axes background
show_layout(cell_x, fig_size=(6, 4))


# plt.figure(facecolor='black')  # Sets the figure background color to black
# plt.gca().set_facecolor('black')  # Sets the axes background color to black
# show_layout(cell_x, (5,4))
write_gds(cell_x, "five_transistor_ota")





