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
gm_1 = 0
gm_3 = 0
gm_5 = 0
l_1  = 0
l_3  = 0
l_5  = 0
cdd_3 = 0
cdd_5 = 0
# CL = 0.1e-12
c_self = 0
# -------------------------------------

it = 0
# t_spec = { 
#   "gain": 21,
#   "ugf": 5.3e9,
#   "cmrr": 47,
#   "sr": 500,
#   "p": 100e-6,
#   "bw": 350e6
# }

t_spec = { 
  "gain": 21,
  "ugf": 5e6,
  "cmrr": 30,
  "sr": 3,
  "p": 100e-6,
  "bw": 0.5e6
}
CL = 20e-12


def radial_spyder_(ax, all_data, keys, metrics, al = 1, th = 2.5):
  output_path = os.path.abspath("outputs")

  num_vars = len(metrics)

  for i, data in enumerate(all_data):
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    data += data[:1]
    angles += angles[:1]
    ax.plot(angles, data,  linewidth=th, alpha = al,  linestyle='solid', label=keys[i])

  ax.set_yticklabels([])
  ax.set_xticks(angles[:-1])
  ax.set_xticklabels(metrics)
  ax.spines['polar'].set_visible(False) 
  plt.legend(loc='upper right')
  ax.grid(linewidth=0.5, alpha=0.5)
  return ax


def initialize(gbw_tol = 0):
    ota = Five_T_OTA()
    params = {
    "GBW_min": t_spec["ugf"] + gbw_tol,    # in Hz
    "Ao_min": t_spec["gain"],       # in dB
    "Po_max": t_spec["p"],   # in W
    "load_C": CL,    # in F
    "supp_V": 1.2,      # in V
    "fin_ref": 10,
    "SR":t_spec["sr"]
    }

    ota.set_target_params(**params)
    return ota

def power_func(TE, gm, vdd): # objective function
    return (2*gm*vdd/TE[1])

def con_1(TE,gm_1,CL, c_self): # slew rate
    return (2*gm_1/(TE[1]*(CL + c_self)))*1e-6 - t_spec["sr"]

def con_2(TE, l_3, l_5): # gain
    return 20*np.log10(TE[1]/(l_3+l_5)) - t_spec["gain"]

def con_3(TE): 
    return 20 - TE[0]   # upper bound

def con_4(TE): 
    return TE[0] - 5   # lower bound

def con_5(TE): 
    return 25 - TE[1]   # upper bound

def con_6(TE): 
    return TE[1] - 18   # lower bound

def con_7(TE): 
    return 28 - TE[2]   # upper bound

def con_8(TE): 
    return TE[2] - 10   # lower bound

def con_9(TE, l_1, l_3, l_5):   # cmrr
    return 20*np.log10((TE[1]*TE[2])/(l_1*(l_3+l_5)))-t_spec["cmrr"]

def con_10(TE, gm, l_3, l_5, CL, cdd_3, cdd_5): # bw
    return (gm/(TE[1]*2*np.pi*(CL + cdd_3 + cdd_5)))*(l_5 + l_3) - t_spec["bw"]


def gm_id_optimizer(xk, final=False):
    ota = initialize(0)

    print("-----------------", ota.GBW_min)
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, it, spec_i, CL
    vcm     = 0.6
    length  = 1   # 14e-9    
    vds_1 = 1.2/3
    fins, Is, other_res = ota.design_ota(xk, 0.6, vds_1, [1,1,1])   
    gm_1 = other_res["gm_0"]
    gm_3 = other_res["gm_1"]
    gm_5 = other_res["gm_2"]
    l_1  = other_res["l_0"]
    l_3  = other_res["l_1"]
    l_5  = other_res["l_2"]
    cdd_3= other_res["cdd_1"]
    cdd_5= other_res["cdd_2"]

    cgg_3 = other_res["cgg_1"]
    cgg_5 = other_res["cgg_2"]


    c_self = (cgg_3)/2 +  cdd_3 + cdd_5

    it += 1
    f = "optimization.log"
    # if final:
    #    write_log_file(f, f" iteration Final ----", 'a')
    # else:
    write_log_file(f, f" iteration {it} ----", 'a')

    print(it)
    write_log_file(f, f" Gain   {con_2(xk, l_3, l_5) + t_spec['gain']}", 'a')
    write_log_file(f, f" UGF    {other_res['ugf']}", 'a')
    write_log_file(f, f" BW     {con_10(xk, gm_3, l_3, l_5, CL, cdd_3, cdd_5)+ t_spec['bw']}", 'a')
    write_log_file(f, f" Power  {power_func(xk, gm_3, 1.2)}", 'a')
    write_log_file(f, f" CMRR   {con_9(xk, l_1, l_3, l_5) + t_spec['cmrr']}", 'a')
    write_log_file(f, f" SR     {con_1(xk,gm_3,CL, c_self) + t_spec['sr']}", 'a')
    write_log_file(f, f" ", 'a')    
    # write_log_file(f, f" cdd_3  {cdd_3}", 'a')
    # write_log_file(f, f" cdd_5  {cdd_5}", 'a') 
    write_log_file(f, f" TEs     {xk}", 'a')
    write_log_file(f, f" Fins    {fins}", 'a')
    write_log_file(f, f" Is      {Is}", 'a')
    write_log_file(f, f"--------------------", 'a')



def run_optimization():
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, c_self
    TE0 = [15, 19, 15]
    cons = (
        {'type': 'ineq', 'fun': con_1, 'args': (gm_3,CL,c_self)},
        {'type': 'ineq', 'fun': con_2, 'args': (l_3, l_5)},
        {'type': 'ineq', 'fun': con_3},
        {'type': 'ineq', 'fun': con_4},
        {'type': 'ineq', 'fun': con_5},
        {'type': 'ineq', 'fun': con_6},
        {'type': 'ineq', 'fun': con_7},
        {'type': 'ineq', 'fun': con_8},
        {'type': 'ineq', 'fun': con_9, 'args': (l_1, l_3, l_5)}
    )
    # trust-constr SLSQP
    result = minimize(power_func, TE0,args= (gm_3, 1.2), method='trust-constr', constraints=cons, callback = gm_id_optimizer, options={'disp': True}, tol=1e-9)
    return result

def hspice_verification(inp):
    results = get_ota_specs(inp["fins"], inp["stacks"], 0.6, 0.001, inp["Is"], 1.2, CL) # spice
    print(results)



@timing_decorator
def main():
    f = "optimization.log"
    write_log_file(f, f" - - - -{datetime.now()} - - - - - -", 'w')
    gm_id_optimizer([15,19,15])    
    res = run_optimization()

    gm_id_optimizer(res.x, final=False)
    # print(res)
    # print(res.x)
    
    # print("-------")
    # print(spec_i)
    # plt.plot(spec_i[:][0], 'o')
    # plt.savefig("p0.png")

    # plt.plot(spec_i[:][1], 'o')
    # plt.savefig("p1.png")

    # plt.plot(spec_i[:][2], 'o')
    # plt.savefig("p2.png")

    # plt.plot(spec_i[:][3], 'o')
    # plt.savefig("p3.png")
    
    # plt.plot(spec_i[:][4], 'o')
    # plt.savefig("p4.png")
    
    # fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))    
    # radial_spyder_(ax, spec_i,["0","1","2","3","4"], ["P","U","s","s","a"])
    # plt.savefig("tria.png")



if __name__ == "__main__":
    main()
   
    # inp = {}
    
    # inp["fins"] = [51, 212, 155]
    # inp["fins"] = [20, 80, 40]

    # inp["Is"] =  0.000307
    # inp["stacks"] = [3, 3, 3]
    # hspice_verification(inp)



