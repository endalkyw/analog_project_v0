from layout_gen.utilities.elements_utils import *
from layout_gen.primitives.current_mirror import current_mirror

# ---------------------------------------------------------------------------------------------
# Base Layout Test---------------------------------------------
# cell = create_empty_cell("base_cell",unit=1e-9, precision=1e-12)
# inputs = {
#     "cell"          :   cell,
#     "total_fingers" :   14,
#     "total_fins"    :   10,
#     "mos_type"      :   "N",
#     "stack"         :   1,
#     "multiplier"    :   4,
#     "orientation"   :   "V",
#     "gate_type"     :   "cm",    # "cm" "dp_0" "dp_1" "dp_2"
#     "body_contact"  :   False
# }
# points = create_base_layout(**inputs)
# write_gds(cell, "base_cell")
#
# for i in points:
#     print(i)
## ---------------------------------------------------------------------------------------------


## ---------------------------------------------------------------------------------------------
# # Single MOS Test
# m0 = Mos({'id': 'A', 'fins': 10, 'fingers': 8, 'stack': 1, 'multiplier': 2, 'mos_type': "N"})
# cell, contact_rects = create_mos(m0, labels=["d", "g", "s", "b"], con=[1, 1, 1, 1], orientation="V", fabric_on=True)
# write_gds(cell, "nmos")
#
# plt.rcParams['figure.facecolor'] = 'black'  # Set figure background
# plt.rcParams['axes.facecolor'] = 'black'    # Set axes background
# show_layout(cell, fig_size=(6,4))
# plt.savefig("outputs/trial_nmos.png")
## ---------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------
# For single current mirror test
m0 = Mos({'id': 'A', 'fins': 5, 'fingers': 8, 'stack': 1, 'multiplier': 5, 'mos_type': "N"})
m1 = Mos({'id': 'A', 'fins': 5, 'fingers': 8, 'stack': 1, 'multiplier': 5, 'mos_type': "N"})
c1 = current_mirror(m0, m1, "test_cm")
c1.create_layout(2, labels=("d0", "d1", "s"), con=[1, 1, 1])
write_gds(c1.cell, "nmos_cm_x")


# matplotlib.use('TkAgg')
# plt.rcParams['figure.facecolor'] = 'black'  # Set figure background
# plt.rcParams['axes.facecolor'] = 'black'    # Set axes background
# show_layout(c1.cell, fig_size=(6, 4))
# plt.savefig("outputs/trial_cm2.png")
# ---------------------------------------------------------------------------------------------


# For single differential pair test
# m0 = Mos({'id': 'A', 'fins': 10, 'fingers': 8, 'stack': 2, 'multiplier': 2, 'mos_type': "N"})
# m1 = Mos({'id': 'A', 'fins': 10, 'fingers': 8, 'stack': 2, 'multiplier': 2, 'mos_type': "N"})
# c1 = differential_pair(m0, m1, "test_dp")
# c1.create_layout(1, labels=("b", "g0", "g1", "d0", "d1", "s"), con=[2, 2, 2]) # connectors d0, d1, s
# write_gds(c1.cell, "nmos_dp")


# generate_cm_layouts(10, 10, 2, "N", source_first=True)
