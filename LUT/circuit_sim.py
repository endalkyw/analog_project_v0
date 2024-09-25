import random

import numpy as np
import pandas as pd
from LUT.read import device
import matplotlib.pyplot as plt
from LUT.fetch_ import fetch_data
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline
from LUT.lut_primitives import n_current_mirror, p_current_mirror, n_differential_pair
from itertools import count


def inverter(vdd, vd_0, vd_1, fins_01, len_01, tb):
    vsd = vdd - vd_1
    return -1*tb.lookup(par="id", len_val=len_01, fin_val=fins_01, type="p", vgs_val=0.5)


def n_cs_with_n_activeload(vdd, vin_dc, fins_0, fins_1, tb, len_0 = 14e-9, len_1 = 14e-9):
    vout  = vdd/10 # initial guess
    vgs_0 = 0
    vgs_1 = 0
    vgs_0 = vin_dc

    for i in range(100):
        vgs_1 = vdd - vout
        id_0_ = tb.lookup(par="id", len_val=14e-9, fin_val=fins_0, type="n", vgs_val=vgs_0)
        id_1_ = tb.lookup(par="id", len_val=14e-9, fin_val=fins_1, type="n", vgs_val=vgs_1)

        f0 = interp1d(tb.vds, id_0_, fill_value="extrapolate")
        f1 = interp1d(tb.vds, id_1_, fill_value="extrapolate")

        vds_dense = np.linspace(tb.vds[0], vdd, 1000)
        index = np.argmin(abs(f0(vds_dense) - f1(vdd - vds_dense)))

        delta = vds_dense[index] - vout
        vout += 0.1 * delta

    vds_1 = vdd - vout
    vds_0 = vout
    id_0  = f0(vout)

    gm_0  = tb.lookup(par="gm",  len_val=len_0, fin_val=fins_0, type="n", vds_val=vds_0, vgs_val=vgs_0)
    gds_0 = tb.lookup(par="gds", len_val=len_0, fin_val=fins_0, type="n", vds_val=vds_0, vgs_val=vgs_0)
    cdd_0 = tb.lookup(par="cdd", len_val=len_0, fin_val=fins_0, type="n", vds_val=vds_0, vgs_val=vgs_0)

    gm_1  = tb.lookup(par="gm",  len_val=len_1, fin_val=fins_1, type="n", vds_val=vds_1, vgs_val=vgs_1)
    gds_1 = tb.lookup(par="gds", len_val=len_1, fin_val=fins_1, type="n", vds_val=vds_1, vgs_val=vgs_1)
    cdd_1 = tb.lookup(par="cdd", len_val=len_1, fin_val=fins_1, type="n", vds_val=vds_1, vgs_val=vgs_1)

    m0 = device(vgs_0, vds_0, 0, fins_0, len_0, id=id_0, gm=gm_0, gds=gds_0, cdd=cdd_0)
    m1 = device(vgs_1, vds_1, 0, fins_1, len_1, id=id_0, gm=gm_1, gds=gds_1, cdd=cdd_1)

    return m0, m1


def five_t_ota(vdd, i_src, vcm, fins_0, fins_1, fins_2, len_0, len_1, len_2, Cl, tb):
    v_x = vdd/3
    v_y = vdd/2
    for k in range(5):
        m0, m1 = n_current_mirror(i_src, v_x, fins_0, fins_0, len_0, tb)
        m4, m5 = p_current_mirror(vdd, m1.id/2, v_y, fins_2, len_2, tb)

        v_y = vdd - m4.vsd
        m2, m3 = n_differential_pair(m1.id, v_y, v_y, fins_1, len_1, 10e-3, vcm, tb)
        v_x = v_y - m2.vds

    # print(f"I source {i_src}")
    # print(f"Id_1     {m1.id}")
    # print(f"Id_23    {m2.id}")
    # print(f"Id_23    {m3.id}")
    # print(f"Id_23    {m2.id+m3.id}")
    # print(f"v_cm     {vcm}")
    # print(f"v_gs     {m2.vgs}")
    # print(f"v_cm-vgs {vcm-m2.vgs}")
    # print(f"v_y-vds  {v_y-m2.vds}")
    # print(f"v_x      {v_x}")

    gm3  = m3.gm
    gds3 = m3.gds
    gds5 = m5.gds
    cdd3 = m3.cdd
    cdd5 = m5.cdd

    A   = 20*np.log10(gm3/(gds3+gds5))
    GBW = gm3/(2*np.pi*(cdd3+cdd5+Cl))
    P   = m1.id*vdd
    SR  = m1.id/Cl

    # print(f"A0: {A[0]} db     GBW: {GBW[0]/1e9} GHz      P: {P/1e-6} uW     SR: {SR*1e-6} v/us")

    return A, GBW, P, SR, v_x, v_y


########################################################################################################################
########################################################################################################################
########################################################################################################################

tb = fetch_data()
# vdd = 1.2
# i_src = [80e-6, 90e-6, 100e-6, 110e-6, 200e-6]
# vcm = [0.5, 0.55, 0.6, 0.7]
# fins_0 = [20, 35, 40, 45]
# fins_1 = [64, 70, 74, 80]
# fins_2 = [20, 24, 30, 40]
# len_0 = len_1 = len_2 = 14e-9
# Cl = 20e-15
#
# A = []
# GBW = []
# P = []
# SR = []
#
# counter = count(0,1)
# for i in i_src:
#     for vc in vcm:
#         for f0 in fins_0:
#             for f1 in fins_1:
#                 for f2 in fins_2:
#
#                     print(f"{next(counter)} -> {i}, {vc}, {f0}, {f1}, {f2}")
#                     A_, GBW_, P_, SR_ = five_t_ota(vdd, i, vc, f0, f1, f2, len_0, len_1, len_2, Cl, tb)
#                     A.append(A_)
#                     GBW.append(GBW_)
#                     P.append(P_)
#                     SR.append(SR_)
# random.shuffle(A)
# random.shuffle(GBW)
# random.shuffle(P)
# random.shuffle(SR)
#
# plt.plot(A)
# plt.show()
#
# plt.plot(GBW)
# plt.show()
#
# plt.plot(P)
# plt.show()
#
# plt.plot(SR)
# plt.show()


########################################################################################################################
########################################################################################################################
########################################################################################################################


A_, GBW_, P_, SR_, vx, vy = five_t_ota(1.2, 100e-6, 0.5, 40, 64,
                                       24, 14e-9, 14e-9, 14e-9, 1e-12, tb)

print(f"{A_=}\n {GBW_=}\n {P_=}\n {SR_=}\n {vx=}\n {vy=}")

########################################################################################################################
########################################################################################################################
########################################################################################################################

# cs_data = pd.read_csv("../cs_amplifier.csv").to_numpy()
# vx_predicted = []
# vx_original  = []
# designs      = []
#
# gain_real = []
# gain_pred = []
#
# for i in range(len(cs_data)):
#     fins_0 = int(cs_data[i,0])
#     fins_1 = int(cs_data[i,1])
#     vi_dc  = cs_data[i,2]
#
#     if cs_data[i,3]>0.4 and cs_data[i,3]<0.8:
#         m0, m1 = n_cs_with_n_activeload(1.2, vi_dc, fins_0, fins_1, tb)
#
#         # print("fins_0   ", cs_data[i,0])
#         # print("fins_1   ", cs_data[i,1])
#         # print("vin_dc   ", cs_data[i,2])
#
#         # print(f"------- {i} ({fins_0} {fins_1})  {vi_dc} ---------")
#         # print(f"Design: {i} vx = {cs_data[i,3]} and vx_pred = {m0.vds}")
#         # print(f"            gm = {cs_data[i,6]} and gm_pred = {m0.gm}")
#         # print(f"          gain = {cs_data[i,9]} and gain_pr = {20*np.log10(m0.gm/(m0.gds+m1.gds+m0.gm))}")
#
#         # print(vx       ", cs_data[i,3], "          ", m0.vds)
#         # print("id       ", cs_data[i,4], "      ", m0.id)
#
#         designs.append(i)
#         vx_predicted.append(cs_data[i,3])
#         vx_original.append(m0.vds)
#
#         gain_real.append(cs_data[i,9])
#         gain_pred.append(20*np.log10(m0.gm/(m0.gds+m1.gds+m1.gm)))
#     # print("gm_0     ", cs_data[i,5], "      ", m0.gm)
#     # print("gds_0    ", cs_data[i,6], "      ", m0.gds)
#     # print("gain     ", cs_data[i,9], "      ", 20*np.log10(cs_data[i,5]/(cs_data[i,6]+cs_data[i,8]+cs_data[i,7])))
#
# # plt.plot(designs, vx_original, 'o')
# # plt.plot(designs, vx_predicted,'*')
# #
# # for i,d in enumerate(designs):
# #     plt.text(d,vx_original[i],str(d))
# #
# # plt.show()
#
#
# plt.plot(designs, gain_real, 'o')
# plt.plot(designs, gain_pred, '*')
#
# for i,d in enumerate(designs):
#     plt.text(d,gain_pred[i], str(d))
#
# plt.show()


########################################################################################################################
########################################################################################################################
########################################################################################################################


# # ----- 5T OTA Simulation (using primitives) --------------------- # from layout_parasitics import wire
# # --------------------------------------------------------------------------------


# vdd = 1.2
# i_src = 110e-6
# vcm = 0.5
# fins_0 = 40
# fins_1 = 64
# fins_2 = 24
# len_0 = len_1 = len_2 = 14e-9
#
#
# net_len = [1e-6, 5e-6, 10e-6, 2e-6]
# net_0 = wire(net_len[0], 3)
# net_1 = wire(net_len[1], 1)
# net_2 = wire(net_len[2], 1)
# net_3 = wire(net_len[3], 3)
#
# v_x = vdd/3  # initial guess
# v_y = vdd/2
#
# for k in range(5):
#     m0, m1 = n_current_mirror(i_src, v_x, fins_0, fins_0, len_0, tb)
#
#     vdd_new = vdd - (m1.id/2)*net_3.R
#     m4, m5 = p_current_mirror(vdd_new, m1.id/2, v_y, fins_2, len_2, tb)
#
#     v_y = vdd_new - m4.vsd - (m1.id/2)*net_2.R
#     m2, m3 = n_differential_pair(m1.id, v_y, v_y, fins_1, len_1, 10e-3, vcm, tb)
#     v_x = v_y - m2.vds - m1.id*net_1.R
#
#
# print(f"I source {i_src}")
# print(f"Id_1     {m1.id}")
# print(f"Id_23    {m2.id}")
# print(f"Id_23    {m3.id}")
# print(f"Id_23    {m2.id+m3.id}")
# print(f"v_cm     {vcm}")
# print(f"v_gs     {m2.vgs}")
# print(f"v_cm-vgs {vcm-m2.vgs}")
# print(f"v_y-vds  {v_y-m2.vds}")
# print(f"v_x      {v_x}")
#
# gm3  = m3.gm
# gds3 = m3.gds
# gds5 = m5.gds
# cdd3 = m3.cdd
# cdd5 = m5.cdd
#
# Cl = 20e-15
# A   = 20*np.log10(gm3/(gds3+gds5))
# GBW = gm3/(2*np.pi*(cdd3+cdd5+Cl))
# P   = m1.id*vdd
#
# print(f"")
# print(f"A0: {A[0]} db     GBW: {GBW[0]/1e9} GHz      P: {P/1e-6} uW ")