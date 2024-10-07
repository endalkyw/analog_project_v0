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
from scipy.optimize import minimize
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
    "ugf": 1e9,
    "cmrr": 50,
    "sr": 50,
    "p": 100e-6,
    "bw": 1e6,
    "cl": 4e-12,
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
    p = [1e6, 10, 10, 1000, 10, 1e4, 1e4, 1e4]
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, it, spec_i, Itail, cgg_3, cgg_5, vds_0, vds_1, vsd_2
    global it
    vcm = 0.6
    length = 1  # 14e-9
    vds_1 = 1.2 / 3

    fins, Is, other_res = ota.design_ota(TE_k, 0.6, vds_1, [1, 1, 1])
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

    c_self = (cgg_3) / 2 + cdd_3 + cdd_5


    val_ = [
            p[0]*2 * gm_3 * t_spec["vdd"] / TE_k[1],
            p[1]*max(0, t_spec["sr"] - (2 * gm_3 / (TE_k[1] * (t_spec["cl"] + c_self))) * 1e-6),
            p[2]*max(0, t_spec["gain"] - 20 * np.log10(TE_k[1] / (l_3 + l_5))),
            p[3]*max(0, t_spec["cmrr"] - 20 * np.log10((TE_k[1] * TE_k[2]) / (l_1 * (l_3 + l_5)))),
            p[4]*max(0, ((2.7 * t_spec["ugf"]) - ((TE_k[2] / TE_k[1]) * ((gm_3) / (2 * np.pi * cgg_5)))))/(2.7 * t_spec["ugf"]),
            p[5]*max(0, 2 / TE_k[0] - vds_0),
            p[6]*max(0, 2 / TE_k[1] - vds_1),
            p[7]*max(0, 2 / TE_k[2] - vsd_2)
          ]

    it += 1
    val = sum(val_)
    print("it", it)
    print(TE_k)
    print(val_)

    # print(((TE_k[2] / TE_k[1]) * ((gm_3) / (2 * np.pi * cgg_5))))
    # print(2.7* t_spec["ugf"])

    return val


def run_optimization():
    # a = gm_id_optimizer(T)
    # specifying the gm/id bounds
    bounds = [(5, 20), (18, 25), (5, 20)]

    TE_0 = [15, 15, 15]  # Initial guess

    # L - BFGS - B
    result = minimize(gm_id_optimizer, TE_0, method="SLSQP", bounds=bounds)
    print(result)



# def hspice_verification(inp):
#     results = get_ota_specs(inp["fins"], inp["stacks"], 0.6, 0.001, inp["Is"], 1.2, t_spec["cl"])  # spice
#     print(results)


@timing_decorator
def main():
    # a = gm_id_optimizer([9, 20, 9])
    # print(a)
    run_optimization()


if __name__ == "__main__":
    main()
# inp = {}
# inp["fins"] = [6, 16, 2]
# inp["Is"] =  24e-6
# inp["stacks"] = [1, 1, 1]
# hspice_verification(inp)



