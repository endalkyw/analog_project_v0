from LUT.read import lut
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from spice.mos_par import *
from LUT.fetch_ import *
import os
from tools.output_file import clear_output_files
from tools.log_file import *
from spice.parse_funcs import extract_between_x_and_y
from datetime import datetime
from five_transistor_spice import get_ota_specs
from scipy.optimize import minimize, differential_evolution
from design_ota import *
from tools.timing import *
from tools.log_file import *
import re

# -------------------------------------
gm_1 = gm_3 = gm_5 = 0
l_1 = l_3 = l_5 = cdd_3 = 0
cdd_5 = c_self = Itail = 0
vds_0 = vds_1 = vsd_2 = it = 0
# -------------------------------------

t_spec = {

    "gain": 21,
    "ugf": 5e9,
    "cmrr": 50,
    "swing": 0.2,
    "sr": 3,
    "p": 100e-6,
    "bw": 10e6,
    "cl": 0.1e-12,
    "vcm": 0.4,
    "vdd": 1.2
}

def initialize(gbw_tol=0):
    ota = Five_T_OTA()
    params = {
        "GBW_min": t_spec["ugf"] + gbw_tol,  # in Hz
        "Ao_min": t_spec["gain"],  # in dB
        "Po_max": t_spec["p"],  # in W
        "load_C": t_spec["cl"],  # in F
        "supp_V": 1.2,  # in V
        "fin_ref": 10,
        "SR": t_spec["sr"]
    }
    ota.set_target_params(**params)
    return ota

def ch(a):
    if a > 0:
        return True
    return False


def gm_id_optimizer(TE_k):
    ota = initialize(0)
    p = [1e6, 10, 10, 1000, 10, 1e3, 1e4, 1e4, 1e4]
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, it, spec_i, Itail, cgg_3, cgg_5, vds_0, vds_1, vsd_2, vth_3
    global it
    vcm = 0.6
    length = 1
    vds_1 = 1.2 / 3
    try:
        fins, Is, other_res = ota.design_ota(TE_k, 0.6, vds_1, [1, 1, 1])
    except:
        print("failed")
        return 1e6

    gm_1 = other_res["gm_0"]
    gm_3 = other_res["gm_1"]
    gm_5 = other_res["gm_2"]
    l_1 = other_res["l_0"]
    l_3 = other_res["l_1"]
    l_5 = other_res["l_2"]
    cdd_3 = other_res["cdd_1"]
    cdd_5 = other_res["cdd_2"]

    Itail = other_res["Itail"]
    cgg_3 = other_res["cgg_1"]
    cgg_5 = other_res["cgg_2"]

    vds_0 = other_res["vds_0"]
    vds_1 = other_res["vds_1"]
    vsd_2 = other_res["vsd_2"]
    vth_3 = other_res["vth"]

    c_self = (cgg_3) / 2 + cdd_3 + cdd_5

    val_ = [
            p[0]*2 * gm_3 * t_spec["vdd"] / TE_k[1]  + 10*(TE_k[2]/TE_k[1]),
            p[1]*max(0, t_spec["sr"] - (2 * gm_3 / (TE_k[1] * (t_spec["cl"] + c_self))) * 1e-6),
            p[2]*max(0, t_spec["gain"] - 20 * np.log10(TE_k[1] / (l_3 + l_5))),
            p[3]*max(0, t_spec["cmrr"] - 20 * np.log10((TE_k[1] * TE_k[2]) / (l_1 * (l_3 + l_5)))),
            p[4]*max(0, ((2.7 * t_spec["ugf"]) - ((TE_k[2] / TE_k[1]) * ((gm_3) / (2 * np.pi * cgg_5)))))/(2.7 * t_spec["ugf"]),
            p[5]*max(0, t_spec["swing"] - (t_spec["vdd"] - t_spec["vcm"] - 2 / TE_k[2] - vth_3)),
            p[6]*max(0, 2 / TE_k[0] - vds_0),
            p[7]*max(0, 2 / TE_k[1] - vds_1),
            p[8]*max(0, 2 / TE_k[2] - vsd_2)
          ]

    it += 1
    print(f"------------swing----{t_spec['vdd'] - t_spec['vcm'] - 2/TE_k[2] - vth_3}-------------------")
    print("it", it)
    val = sum(val_)
    print(TE_k)
    print(fins)
    print(Is)
    print("-----------------------------------")

    print(val_)

    # print(((TE_k[2] / TE_k[1]) * ((gm_3) / (2 * np.pi * cgg_5))))
    # print(2.7* t_spec["ugf"])

    return val





def get_graph():
    it = 0
    val = []
    bounds = [(5, 25), (5, 25), (5, 25)]
    for te1 in np.linspace(bounds[0][0], bounds[0][1], 20):
        for te2 in np.linspace(bounds[1][0], bounds[1][1], 20):
            for te3 in np.linspace(bounds[2][0], bounds[2][1], 20):
                xk = [np.round(te1, 3), np.round(te2, 3), np.round(te3, 3)]
                try:
                    v = gm_id_optimizer(xk)
                    if type(v) == np.ndarray:
                        print("yes")
                        val.append([it, xk[0], xk[1], xk[2], v[0]])
                        it += 1
                except:
                    print("--xx--")

    write_log_file("graph_2.csv", "index,TE_0,TE_1,TE_3,Val", 'w')
    for v in val:
        write_log_file("graph_2.csv", ",".join(map(str, v)), 'a')



def run_optimization():
    # a = gm_id_optimizer(T)
    # specifying the gm/id bounds
    bounds = [(5, 25), (5, 25), (5, 25)]

    TE_0 = [18, 15, 18]  # Initial guess

    # L - BFGS - B
    result = minimize(gm_id_optimizer, TE_0, method="SLSQP", bounds=bounds)
    # result = minimize(gm_id_optimizer, TE_0, method="L-BFGS-B", bounds=bounds)
    # result = differential_evolution(gm_id_optimizer, bounds, maxiter=5, popsize=5, tol=1e-6)

    print(result)


# def hspice_verification(inp):
#     results = get_ota_specs(inp["fins"], inp["stacks"], 0.6, 0.001, inp["Is"], 1.2, t_spec["cl"])  # spice
#     print(results)


@timing_decorator
def main():
    # a = gm_id_optimizer([16.111,7.222,25.0])
    # print(a)
    run_optimization()
    # get_graph()

if __name__ == "__main__":
    main()
# inp = {}
# inp["fins"] = [6, 16, 2]
# inp["Is"] =  24e-6
# inp["stacks"] = [1, 1, 1]
# hspice_verification(inp)



