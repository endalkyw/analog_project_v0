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
gm_1 = gm_3 = gm_5 = l_1  = l_3  = l_5  = cdd_3 = cdd_5 = c_self = Itail = vds_0 = vds_1 = vsd_2 = it = 0
# -------------------------------------

t_spec = {

  "gain": 20,
  "ugf": 10e6,
  "cmrr": 20,
  "sr": 1,
  "p": 100e-6,
  "bw": 1e6,
  "cl": 4e-12,
  "vdd": 1.2
}

def initialize(gbw_tol = 0):
    ota = Five_T_OTA()
    params = {
    "GBW_min": t_spec["ugf"] + gbw_tol,    # in Hz
    "Ao_min": t_spec["gain"],       # in dB
    "Po_max": t_spec["p"],   # in W
    "load_C": t_spec["cl"],    # in F
    "supp_V": 1.2,      # in V
    "fin_ref": 10,
    "SR":t_spec["sr"]
    }

    ota.set_target_params(**params)
    return ota

# objective function 
def power_func(TE, gm_3, vdd): # objective function
    return (2*gm_3*vdd/TE[1])

# constraints 
def con_sr(TE,gm_3, c_self): # slew rate
    return (2*gm_3/(TE[1]*(t_spec["cl"] + c_self)))*1e-6 - t_spec["sr"]

def con_gain(TE, l_3, l_5): # gain
    return 20*np.log10(TE[1]/(l_3+l_5)) - t_spec["gain"]

def con_cmrr(TE, l_1, l_3, l_5):   # cmrr
    return 20*np.log10((TE[1]*TE[2])/(l_1*(l_3+l_5)))-t_spec["cmrr"]

def con_bw(TE, gm, l_3, l_5 , cdd_3, cdd_5): # bw
    return (gm/(TE[1]*2*np.pi*(t_spec["cl"] + cdd_3 + cdd_5)))*(l_5 + l_3) - t_spec["bw"]

def con_p2(TE, gm_3, cgg_5): # the non dominant pole should be greater than the GBW
    return (TE[2]/TE[1])*((gm_3)/(2*np.pi*cgg_5)) - 2.7*t_spec["ugf"]

# All the mosfets must operate in saturation region
def con_vdsat0(TE, vds_0): 
    return vds_0 - 2/TE[0] 

def con_vdsat1(TE, vds_1): 
    return vds_1 - 2/TE[1]

def con_vdsat2(TE, vsd_2):
    return vsd_2 - 2/TE[2]
def ch(a):
    if a > 0:
        return True
    return False
def gm_id_optimizer(xk, final=False):
    ota = initialize(0)
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, it, spec_i, Itail, cgg_3, cgg_5,vds_0, vds_1, vsd_2 

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

    Itail = other_res["Itail"]
    cgg_3 = other_res["cgg_1"]
    cgg_5 = other_res["cgg_2"]

    vds_0 = other_res["vds_0"]
    vds_1 = other_res["vds_1"]
    vsd_2 = other_res["vsd_2"]
    
    c_self = (cgg_3)/2 +  cdd_3 + cdd_5

    it += 1
    f = "optimization.csv"


    Gain     = (con_gain(xk, l_3, l_5) + t_spec['gain'])[0]
    UGF      = (other_res['ugf'])[0]
    BW       = (con_bw(xk, gm_3, l_3, l_5, cdd_3, cdd_5)+ t_spec['bw'])[0]
    Power    = (power_func(xk, gm_3, 1.2))[0]
    CMRR     = (con_cmrr(xk, l_1, l_3, l_5) + t_spec['cmrr'])[0]
    SR       = (con_sr(xk,gm_3, c_self) + t_spec['sr'])[0]
    Pole_2   = (con_p2(xk,gm_3, cgg_5) + 2.7*t_spec['ugf'])[0]
    vds      = [vds_0, vds_1, vsd_2]
    vds_sat  = [2/xk[0], 2/xk[1], 2/xk[2]]
    TEs      = xk
    Fins     = fins
    I       = [Is[0], Itail[0]]

    header = f"it,Gain,UGF,BW,Pole_2,Power,CMRR,SR,vds_0,vds_1,vds_2,vds_sat_0,vds_sat_1,vds_sat_2,TEs_0,TEs_1,TEs_2,Fins_0,Fins_1,Fins_2,I_s,I_tail"
    line = f"{it},{Gain},{UGF},{BW},{Pole_2},{Power},{CMRR},{SR},{vds[0]},{vds[1]},{vds[2]},{vds_sat[0]},{vds_sat[1]},{vds_sat[2]},{TEs[0]},{TEs[1]},{TEs[2]},{Fins[0]},{Fins[1]},{Fins[2]},{I[0]},{I[1]}"
    
    if it==1:
        write_log_file(f, header, 'w')
    
    write_log_file(f, line, 'a')
    


    print("f gain   cmrr    sr  pole2   sat0    sat1    sat2")
    print(ch(con_gain(xk, l_3, l_5)), ch(con_cmrr(xk, l_1, l_3, l_5)), ch(con_sr(xk,gm_3, c_self)), ch(con_p2(xk, gm_3, cgg_5)),
          ch(con_vdsat0(xk, vds_0)), ch(con_vdsat1(xk, vds_1)), ch(con_vdsat2(xk, vsd_2)))

    # print(con_p2(xk, gm_3, cgg_5))
    # print((xk[2]/xk[1])*(gm_3/(2*np.pi*cgg_5)) - t_spec["ugf"])
    # print((xk[2]/xk[1])*(gm_3/(2*np.pi*cgg_5)) - t_spec["ugf"])
    # print(" ")
    
    # write_log_file(f, f" iteration {it} ----", 'a')
    # write_log_file(f, f" Gain    {con_gain(xk, l_3, l_5) + t_spec['gain']}", 'a')
    # write_log_file(f, f" UGF     {other_res['ugf']}", 'a')
    # write_log_file(f, f" BW      {con_bw(xk, gm_3, l_3, l_5, CL, cdd_3, cdd_5)+ t_spec['bw']}", 'a')
    # write_log_file(f, f" Power   {power_func(xk, gm_3, 1.2)}", 'a')
    # write_log_file(f, f" CMRR    {con_cmrr(xk, l_1, l_3, l_5) + t_spec['cmrr']}", 'a')
    # write_log_file(f, f" SR      {con_sr(xk,gm_3,CL, c_self) + t_spec['sr']}", 'a')
    # write_log_file(f, f" Pole_2  {con_p2(xk,cgg_5,Itail) + 1.5*t_spec['ugf']}", 'a')
    # write_log_file(f, f" vds     {vds_0} {vds_1}, {vsd_2}", 'a')
    # write_log_file(f, f" vds_sat {2/xk[0]}, {2/xk[1]}, {2/xk[2]}", 'a')
    # write_log_file(f, f" ", 'a')    
    # write_log_file(f, f" TEs     {xk}", 'a')
    # write_log_file(f, f" Fins    {fins}", 'a')
    # write_log_file(f, f" Is      {Is}   Itail {Itail}", 'a')
    # # write_log_file(f, f" cdd_3  {cdd_3}", 'a')
    # # write_log_file(f, f" cdd_5  {cdd_5}", 'a') 
    # write_log_file(f, f"--------------------", 'a')



def my_brute_force():
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, c_self, vds_0, vds_1, vsd_2
    bounds = [(5,  20), (18, 25), (5,  20)]
    min_power = 100
    best_solution = [0, 0, 0]

    min_power_true = 100
    best_solution_true = [0, 0, 0]

    for te1 in np.linspace(bounds[0][0], bounds[0][1], 5):
        for te2 in np.linspace(bounds[1][0], bounds[1][1], 5):
            for te3 in np.linspace(bounds[2][0], bounds[2][1], 5):
                xk = [np.round(te1,3), np.round(te2,3), np.round(te3,3)]
                try:
                    gm_id_optimizer(xk)
                except:
                    print("--xx--")

                print(xk)

                p = power_func(xk, gm_3, t_spec["vdd"])
                if p<min_power:
                    min_power = p
                    best_solution = xk

                if(ch(con_gain(xk, l_3, l_5)) and ch(con_cmrr(xk, l_1, l_3, l_5)) and ch(con_sr(xk, gm_3, c_self)) and
                      ch(con_p2(xk, gm_3, cgg_5)) and ch(con_vdsat0(xk, vds_0)) and ch(con_vdsat1(xk, vds_1)) and ch(con_vdsat2(xk, vsd_2))):
                    min_power_true = p
                    best_solution_true = xk

    print(f"best_solution_true: {best_solution}")
    print(f"best_solution: {best_solution}")
    print(f"min_power_true {min_power_true}")
    print(f"min_power: {min_power}")

def run_optimization():
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, c_self, vds_0, vds_1, vsd_2
    TE0 = [15, 15, 15]
    cons = (
        {'type': 'ineq', 'fun': con_sr, 'args': (gm_3, c_self)},
        {'type': 'ineq', 'fun': con_gain, 'args': (l_3, l_5)},
        {'type': 'ineq', 'fun': con_cmrr, 'args': (l_1, l_3, l_5)},
        {'type': 'ineq', 'fun': con_p2, 'args': (gm_3, cgg_5)},
        {'type': 'ineq', 'fun': con_vdsat0, 'args': ([vds_0])},
        {'type': 'ineq', 'fun': con_vdsat1, 'args': ([vds_1])},
        {'type': 'ineq', 'fun': con_vdsat2, 'args': ([vsd_2])}
    )

    # specifying the gm/id bounds
    bounds = [(5,  20), (18, 25), (5,  20)]

    # trust-constr SLSQP
    result = minimize(power_func, TE0, args=(gm_3, 1.2), method='SLSQP', constraints=cons, bounds=bounds,
                      callback=gm_id_optimizer, options={'disp': True, 'maxiter': 1000, 'gtol': 1e-9})
    return result

def hspice_verification(inp):
    results = get_ota_specs(inp["fins"], inp["stacks"], 0.6, 0.001, inp["Is"], 1.2, t_spec["cl"]) # spice
    print(results)



@timing_decorator
def main():
    f = "optimization.log"
    write_log_file(f, f" - - - -{datetime.now()} - - - - - -", 'w')
    gm_id_optimizer([10, 19, 10])
    res = run_optimization()
    gm_id_optimizer(res.x, final=False)


    print("Optimal value:", res.fun)
    print("Optimal solution:", res.x)
    print("Success:", res.success)
    print("Message:", res.message)


if __name__ == "__main__":
    # main()
    my_brute_force()
# inp = {}
    # inp["fins"] = [6, 16, 2]
    # inp["Is"] =  24e-6
    # inp["stacks"] = [1, 1, 1]
    # hspice_verification(inp)



