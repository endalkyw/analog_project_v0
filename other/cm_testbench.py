from LUT.read import lut
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from spice.mos_par import *
from spice.parse_funcs import *
from LUT.fetch_ import *
from tools.output_file import clear_output_files
from tools.log_file import *
from tools.timing import *
import pandas as pd
from scipy.interpolate import CubicSpline
import re


import sys
import os
module_dir = os.path.abspath('spice')
sys.path.append(module_dir)
import primitives_spice as ps

# import dspf and create testbench
def create_tb_and_simulate(target_file, type="nfet"):
    """
    This function  
    1: imports the dspf file from the outputs dir
    2: creates a testbench file(.sp file)
    3: simulate the file
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
        ".param vd0_val = 0.4",
        ".param vd1_val = 0.4",
        ".param vdd_val = 1.2"
     ]
    
    if type == "nfet":
      testbench = [                       # id, cdd, gds and gm  
          f"xcm d0 d1 0 {name.group(0)}",             
          "Vd0 d0  0 DC vd0_val",
          "Vd1 d1_ 0 DC vd1_val",
          "Vd_ac d1 d1_ AC 1",
          " ",
          ".dc Vd1 lin 1 vd1_val vd1_val sweep data=sweep_data",
          ".ac dec 1 1 1e15 sweep data=sweep_data",
          " ",
          ".measure ac I_1 find I(Vd_ac) at=1",
          ".measure ac I_2 find I(Vd_ac) at=1e15",
          ".measure ac V_mag find V(d1) at=1",
          ".measure dc id0 find i(Vd0) when v(d1)=vd1_val",
          ".measure dc id1 find i(Vd1) when v(d1)=vd1_val",
          " ",
          ".data sweep_data",
          "+ vd0_val vd1_val",
          "{sources}",
          ".ENDDATA",
          ""
      ]
      
      footer = ".end"
    
      d = {}
      d["sources"] = ""
      vd0 = np.linspace(0,0.8,21)
      vd1 = np.linspace(0,0.8,21)
      
      for vd1_val in vd1:
           for vd0_val in vd0:
                d["sources"]+=f"{str(round(vd0_val,2))} {str(round(vd1_val,2))}\n"
    
      testbench_  = "\n".join(testbench); 
    
      spice_file = "\n".join(header) + "\n"*3 +  testbench_.format(**d)  + "\n"*2 + footer 
      with open(f"outputs/{name.group(0)}_tb.sp", "w") as file:
              file.write(spice_file)           
      
      # run the simulation
      exit_status = os.system(f'hspice -i outputs/{name.group(0)}_tb.sp -o outputs/nmos_cm/nmos_cm')
    
    elif type == "pfet":
      testbench = [                           # id, cdd, gds and gm 
          "Vdd s 0 vdd_val",
          f"xcm d0 d1 s {name.group(0)}",            
          "Vd0 s d0 DC vd0_val",
          "Vd1 s d1_ DC vd1_val",
          "Vd_ac d1_ d1 AC 1",
          " ",
          ".dc Vd1 lin 1 vd1_val vd1_val sweep data=sweep_data",
          ".ac dec 1 1 1e15 sweep data=sweep_data",
          " ",
          ".measure ac I_1 find I(Vd_ac) at=1",
          ".measure ac I_2 find I(Vd_ac) at=1e15",
          ".measure ac V_mag find V(d1) at=1",
          ".measure dc id0 find i(Vd0) when v(d1) = \'v(s) - vd1_val\'",
          ".measure dc id1 find i(Vd1) when v(d1) = \'v(s) - vd1_val\'",
          " ", 
          ".data sweep_data",
          "+ vd0_val vd1_val",
          "{sources}",
          ".ENDDATA",
          ""
      ]   
      
      footer = ".end"
    
      d = {}
      d["sources"] = ""
      vd0 = np.linspace(0,0.8,21)
      vd1 = np.linspace(0,0.8,21)
      
      for vd1_val in vd1:
           for vd0_val in vd0:
                d["sources"]+=f"{str(round(vd0_val,2))} {str(round(vd1_val,2))}\n"
    
      testbench_  = "\n".join(testbench); 
    
      spice_file = "\n".join(header) + "\n"*3 +  testbench_.format(**d)  + "\n"*2 + footer 
      with open(f"outputs/{name.group(0)}_tb.sp", "w") as file:
              file.write(spice_file)
              
      # run the simulation
      exit_status = os.system(f'hspice -i outputs/{name.group(0)}_tb.sp -o outputs/pmos_cm/pmos_cm')
    
    else:
       print("Error: mos-type is neither \'nfet\' nor \'pfet\'")  


@timing_decorator
def simulate_and_parse(name, type):
    n = 21
    create_tb_and_simulate(f"outputs/{name}.dspf", type)
    
    if type == "nfet":
        data_array = parse_data_1("outputs/nmos_cm/nmos_cm.ma0")
        ids = parse_data_2("outputs/nmos_cm/nmos_cm.ms0")

    elif type == "pfet":
        data_array = parse_data_1("outputs/pmos_cm/pmos_cm.ma0")
        ids = parse_data_2("outputs/pmos_cm/pmos_cm.ms0")        

    gds = data_array[:,2]/data_array[:,4]
    cdd = data_array[:,3]/(2*np.pi*1e15*data_array[:,4])
    vd0_vals = data_array[:,0]
    vd1_vals = data_array[:,1]
    gm = []
    for i in range(0, len(vd0_vals), n):
         x = vd0_vals[i:i+n]
         y = -1*ids[i:i+n,1]
         cs_1 = CubicSpline(x, y)
         x_new = np.linspace(0, 0.8, 1000)
         y_new = cs_1(x_new)
         gm_i = np.gradient(y_new, x_new)
         cs_2 = CubicSpline(x_new, gm_i)
         gm_i_downsampled = cs_2(x) 
         gm = np.concatenate((gm, gm_i_downsampled), axis=0)
    

    data = np.column_stack([vd0_vals, vd1_vals, ids[:,0], ids[:,1], gm, gds, cdd])
    data_ = pd.DataFrame(data, columns = ["vd0","vd1","id0", "id1", "gm", "gds", "cdd"])
    data_.to_csv(f'outputs/{name}.csv', index=False)


def main():
    name = "nmos_cm"
    # name = "pmos_cm"
    # # simulate_base_schematic(8, 8, 1, 1, "pfet")
    # simulate_base_schematic(18, 18, 1, 1, "nfet")
    # simulate_current_mirror(name,"nfet")
    # simulate_and_parse(name, "nfet")

    ps.create_cm_spice(6, 6, 1, "nfet", "nmos_cm.dspf")
    simulate_and_parse(name, "nfet")


if __name__ == '__main__':
     main()