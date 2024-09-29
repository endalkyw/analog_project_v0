from LUT.read import lut
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from spice.mos_par import *
from spice.parse_funcs import *
from LUT.fetch_ import *
import os
from tools.output_file import clear_output_files
from tools.log_file import *
from tools.timing import *
import pandas as pd
from scipy.interpolate import CubicSpline
import re

def simulate_differential_pair(target_file, n):
    """
    target_file can be either .sp file or .dspf file
    output file is csv file
    """
    pattern = r'[^/]+(?=\.[^.]+$)'
    name = re.search(pattern, target_file)
    
    header = [
        "*********************************************",
        ".LIB \"/project/ssstudents/TAPO_downloads/GF12_V1.0_4.1/12LP/V1.0_4.1/Models/HSPICE/models/12LP_Hspice.lib\" TT",
        ".option post = 2",
        ".option ingold = 1",
        ".PARAM wireopt=3 pre_layout_sw=0",
        f".include \"{target_file}\"",
        ".param vd1_val = 0.4",
        # ".param vg0_val = 0.4",
        ".param vg1_val = 0.4",
        ".param vs_val  = 0"
     ]
    
    testbench = [                           # id, cdd, gds and gm  
        f"xdp 0 d0 d1 g0 g1 0 {name.group(0)}",            
        "Vd0 d0  0 DC vd1_val",
        "Vd1 d1_ 0 DC vd1_val",
        "Vg0 g0  0 DC vg1_val",
        "Vg1 g1 0 DC vg1_val",
        # "Vs  s  0 DC vs_val",
        "Vd_ac d1 d1_ AC 1",
        " ",

        ".dc Vd1 lin 1 vd1_val vd1_val sweep data=sweep_data",
        ".ac dec 1 1 1e15 sweep data=sweep_data",
        " ",
        ".measure ac I1_1 find I(Vd_ac) at=1",
        ".measure ac I1_2 find I(Vd_ac) at=1e15",
        ".measure ac V_mag find V(d1) at=1",
        # ".measure dc id find i(Vd0) when v(d0)=vd0_val",
        ".measure dc id_0 find i(Vd0) when v(d1)=vd1_val",
        ".measure dc id_1 find i(Vd1) when v(d1)=vd1_val",

        " ",
        ".data sweep_data",
        # "+ vs_val vd1_val vg1_val",
        "+ vd1_val vg1_val",
        "{sources}",
        ".ENDDATA",
        ""
    ]
    
    footer = ".end"

    d = {}
    d["sources"] = ""
    vd1 = np.linspace(0, 0.8, n)
    vg1 = np.linspace(0, 0.8, n)
    # vs  = np.linspace(0.5, 0, n)
    
    # for vs_val in vs:
    for vd1_val in vd1:
      for  vg1_val in vg1:        
        d["sources"]+=f"{str(round(vd1_val,2))} {str(round(vg1_val,2))}\n"
        # d["sources"]+=f"{str(round(vs_val,2))} {str(round(vd1_val,2))} {str(round(vg1_val,2))}\n"


    testbench_  = "\n".join(testbench); 

    spice_file = "\n".join(header) + "\n"*3 +  testbench_.format(**d)  + "\n"*2 + footer 
    with open(f"outputs/{name.group(0)}_tb.sp", "w") as file:
            file.write(spice_file)
            
    # run the simulation
    exit_status = os.system(f'hspice -i outputs/{name.group(0)}_tb.sp -o outputs/nmos_dp/nmos_dp')



@timing_decorator
def simulate_and_parse(name, type = "nfet"):
    n = 21
    simulate_differential_pair(f"outputs/{name}.dspf", n)
  
    data_array = parse_dp_data_ma0("outputs/nmos_dp/nmos_dp.ma0")
    curr_data  = parse_dp_data_ms0("outputs/nmos_dp/nmos_dp.ms0")

    gds = data_array[:,2]/data_array[:,4]
    cdd = data_array[:,3]/(2*np.pi*1e15*data_array[:,4])
    
    vd1_vals = data_array[:,0]
    vg1_vals = data_array[:,1]

    gm = []
    for i in range(0, len(vd1_vals), n):
         x = vg1_vals[i:i+n]
         y = -1*curr_data[i:i+n, 1]
         
         cs_1 = CubicSpline(x, y)
         x_new = np.linspace(0, 0.8, 1000)
         y_new = cs_1(x_new)
         gm_i = np.gradient(y_new, x_new)
         cs_2 = CubicSpline(x_new, gm_i)
         gm_i_downsampled = cs_2(x) 
         gm = np.concatenate((gm, gm_i_downsampled), axis=0)
    
    data = np.column_stack([vd1_vals, vg1_vals, curr_data, gm, gds, cdd])

    data_ = pd.DataFrame(data, columns = ["vd1","vg1", "id0", "id1", "gm", "gds", "cdd"])
    data_.to_csv(f'outputs/{name}.csv', index=False)


def main():
    # name = "nmos_cm_2x9_5"
    # name = "nmos_cm_1.pex"
    name = "nmos_dp"
    simulate_and_parse(name)

if __name__ == '__main__':
     main()
