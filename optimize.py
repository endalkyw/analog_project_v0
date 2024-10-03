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
  "ugf": 40e6,
  "cmrr": 20,
  "sr": 2,
  "p": 100e-6,
  "bw": 1e6,
  "cl": 4e-12
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
def con_1(TE,gm_3, c_self): # slew rate
    return (2*gm_3/(TE[1]*(t_spec["cl"] + c_self)))*1e-6 - t_spec["sr"]

def con_2(TE, l_3, l_5): # gain
    return 20*np.log10(TE[1]/(l_3+l_5)) - t_spec["gain"]

def con_3(TE, l_1, l_3, l_5):   # cmrr
    return 20*np.log10((TE[1]*TE[2])/(l_1*(l_3+l_5)))-t_spec["cmrr"]

def con_4(TE, gm, l_3, l_5 , cdd_3, cdd_5): # bw
    return (gm/(TE[1]*2*np.pi*(t_spec["cl"] + cdd_3 + cdd_5)))*(l_5 + l_3) - t_spec["bw"]

def con_5(TE, cgg_5, Itail): # the non dominant pole should be greater than the GBW
    return TE[2]*(Itail/2)/(2*cgg_5) - 1.5*t_spec["ugf"]

# All the mosfets must operate in saturation region
def con_6(TE, vds_0): 
    return vds_0 - 2/TE[0] 

def con_7(TE, vds_1): 
    return vds_1 - 2/TE[1]

def con_8(TE, vsd_2):
    return vsd_2 - 2/TE[2]


def gm_id_optimizer(xk, final=False):
    ota = initialize(5e6)
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
    f = "optimization.log"


    Gain     = (con_2(xk, l_3, l_5) + t_spec['gain'])[0]
    UGF      = (other_res['ugf'])[0]
    BW       = (con_4(xk, gm_3, l_3, l_5, cdd_3, cdd_5)+ t_spec['bw'])[0]
    Power    = (power_func(xk, gm_3, 1.2))[0]
    CMRR     = (con_3(xk, l_1, l_3, l_5) + t_spec['cmrr'])[0]
    SR       = (con_1(xk,gm_3, c_self) + t_spec['sr'])[0]
    Pole_2   = (con_5(xk,cgg_5,Itail) + 1.5*t_spec['ugf'])[0]
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
    

    def ch(a):
        if a > 0:
            return True
        return False
    print("f gain   cmrr    sr  pole2   sat0    sat1    sat2")
    print(ch(con_2(xk, l_3, l_5)), ch(con_3(xk, l_1, l_3, l_5)), ch(con_1(xk,gm_3, c_self)), ch(con_5(xk,cgg_5,Itail)), 
          ch(con_6(xk, vds_0)), ch(con_7(xk, vds_1)), ch(con_8(xk, vsd_2)))
    
    print(" ")

    
    # write_log_file(f, f" iteration {it} ----", 'a')
    # write_log_file(f, f" Gain    {con_2(xk, l_3, l_5) + t_spec['gain']}", 'a')
    # write_log_file(f, f" UGF     {other_res['ugf']}", 'a')
    # write_log_file(f, f" BW      {con_4(xk, gm_3, l_3, l_5, CL, cdd_3, cdd_5)+ t_spec['bw']}", 'a')
    # write_log_file(f, f" Power   {power_func(xk, gm_3, 1.2)}", 'a')
    # write_log_file(f, f" CMRR    {con_3(xk, l_1, l_3, l_5) + t_spec['cmrr']}", 'a')
    # write_log_file(f, f" SR      {con_1(xk,gm_3,CL, c_self) + t_spec['sr']}", 'a')
    # write_log_file(f, f" Pole_2  {con_5(xk,cgg_5,Itail) + 1.5*t_spec['ugf']}", 'a')
    # write_log_file(f, f" vds     {vds_0} {vds_1}, {vsd_2}", 'a')
    # write_log_file(f, f" vds_sat {2/xk[0]}, {2/xk[1]}, {2/xk[2]}", 'a')
    # write_log_file(f, f" ", 'a')    
    # write_log_file(f, f" TEs     {xk}", 'a')
    # write_log_file(f, f" Fins    {fins}", 'a')
    # write_log_file(f, f" Is      {Is}   Itail {Itail}", 'a')
    # # write_log_file(f, f" cdd_3  {cdd_3}", 'a')
    # # write_log_file(f, f" cdd_5  {cdd_5}", 'a') 
    # write_log_file(f, f"--------------------", 'a')



def run_optimization():
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, c_self, vds_0, vds_1, vsd_2
    TE0 = [18, 23, 17]
    cons = (
        {'type': 'ineq', 'fun': con_1, 'args': (gm_3, c_self)},
        {'type': 'ineq', 'fun': con_2, 'args': (l_3, l_5)},
        {'type': 'ineq', 'fun': con_3, 'args': (l_1, l_3, l_5)},
        {'type': 'ineq', 'fun': con_5, 'args': (cgg_5, Itail)},
        {'type': 'ineq', 'fun': con_6, 'args': ([vds_0])},
        {'type': 'ineq', 'fun': con_7, 'args': ([vds_1])},
        {'type': 'ineq', 'fun': con_8, 'args': ([vsd_2])}
    )



    # specifying the gm/id bounds
    bounds = [(5,  15), (18, 25), (5,  15)] 

    # trust-constr SLSQP
    result = minimize(power_func, TE0,args= (gm_3, 1.2), method='trust-constr', constraints=cons, bounds = bounds,
                      callback = gm_id_optimizer, options={'disp': True, 'maxiter': 1000, 'gtol': 1e-6}
)
    return result

def hspice_verification(inp):
    results = get_ota_specs(inp["fins"], inp["stacks"], 0.6, 0.001, inp["Is"], 1.2, t_spec["cl"]) # spice
    print(results)



@timing_decorator
def main():
    f = "optimization.log"
    write_log_file(f, f" - - - -{datetime.now()} - - - - - -", 'w')
    gm_id_optimizer([10,19,10])    
    res = run_optimization()
    gm_id_optimizer(res.x, final=False)


    print("Optimal value:", res.fun)
    print("Optimal solution:", res.x)
    print("Success:", res.success)
    print("Message:", res.message)


if __name__ == "__main__":
    main()

    # inp = {}
    # inp["fins"] = [26, 84, 49]
    # inp["Is"] =  0.000452
    # inp["stacks"] = [1, 1, 1]
    # hspice_verification(inp)
   




