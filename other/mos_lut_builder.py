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


clear_output_files()
fins    = [2, 5, 10]
fingers = [1, 1, 1]
stk     = [1, 2, 3, 4]


def create_and_simulate_spice_nfet(fins, fingers, stk, ind):
    type = "nfet"
    p = params()
    header = [
    "*********************************************",
    ".LIB \"/project/ssstudents/TAPO_downloads/GF12_V1.0_4.1/12LP/V1.0_4.1/Models/HSPICE/models/12LP_Hspice.lib\" TT",
    ".option post = 2",
    ".option ingold = 1",
    ".PARAM wireopt=3 pre_layout_sw=0",
    ".param vds_val = 0.5",
    ".param vgs_val = 0.5",
    ".param vsb_val = 0",
    p.get_mos_string("m0", d="drain",  g="gate", s=0, b="bulk", type = type, fins = fins, nf = fingers, stack=stk)
    ]


    testbench_0 = [          # id, cdd, gds and gm              
        "Vds drain_ 0 DC vds_val",
        "Vsb bulk 0 DC vsb_val",
        "Vgs gate 0 DC vgs_val",
        " ",
        "Vd_ac drain drain_ AC 1",
        " ",
        ".dc Vds LIN 1 vds_val vds_val SWEEP DATA=sweep_data",
        ".ac dec 1 1 1e15 sweep data=sweep_data",
        " ",
        ".measure ac I_1 find I(Vd_ac) at=1",
        ".measure ac I_2 find I(Vd_ac) at=1e15",
        ".measure ac V_mag find V(drain) at=1",
        ".measure dc id find i(Vds) when v(drain)=vds_val",
        " ",
        ".data sweep_data",
        "+ vgs_val vds_val ",
        "{sources}",
        ".ENDDATA",
        ""
    ]

    testbench_1 = [         # cgg            
        "Vds drain 0 DC vds_val",
        "Vsb bulk 0 DC vsb_val",
        "Vgs gate_ 0 DC vgs_val",
        "Vg_ac gate gate_ AC 1",
        ".ac dec 1 1e13 1e15 sweep data=sweep_data",
        ".measure ac I_g find I(Vg_ac) at=1e15",
        ".measure ac V_mag find V(gate) at=1e15",
        " ",
        ".data sweep_data",
        "+vgs_val vds_val",
        "{sources}",
        ".ENDDATA",
        " "
    ]

    testbenches = [testbench_0, testbench_1]

    footer = ".end"

    testbench = testbenches[ind]

    d = {}
    d["sources"] = ""
    vgs = np.linspace(0,0.8,41)
    vds = np.linspace(0,0.8,41)
    
    for vds_val in vds:
         for vgs_val in vgs:
              d["sources"]+=f"{str(round(vgs_val,2))} {str(round(vds_val,2))}\n"

    testbench_  = "\n".join(testbench); 

    spice_file = "\n".join(header) + "\n"*3 +  testbench_.format(**d)  + "\n"*2 + footer 
    with open("outputs/nmos_extractor.sp", "w") as file:
            file.write(spice_file)
        
    # run the simulation
    exit_status = os.system('hspice -i outputs/nmos_extractor.sp -o outputs/nmos_extract/')

def create_and_simulate_spice_pfet(fins, fingers, stk, ind):
    type = "pfet"
    p = params()
    header = [
    "*********************************************",
    ".LIB \"/project/ssstudents/TAPO_downloads/GF12_V1.0_4.1/12LP/V1.0_4.1/Models/HSPICE/models/12LP_Hspice.lib\" TT",
    ".option post = 2",
    ".option ingold = 1",
    ".PARAM wireopt=3 pre_layout_sw=0",
    ".param vds_val = 0.5",
    ".param vgs_val = 0.5",
    ".param vsb_val = 0  ",
    ".param vdd_val = 0.8",
    p.get_mos_string("m0", d="drain",  g="gate", s="source", b="bulk", type = type, fins = fins, nf = fingers, stack=stk)
    ]

    testbench_0 = [          # id, cdd, gds and gm   
        "Vdd source 0 DC vdd_val",         
        "Vsd source drain_ DC vds_val",
        "Vsb source bulk DC vsb_val",
        "Vsg source gate 0 DC vgs_val",
        " ",
        "Vd_ac drain_ drain AC 1",
        " ",
        ".dc Vsd LIN 1 vds_val vds_val SWEEP DATA=sweep_data",
        ".ac dec 1 1 1e15 sweep data=sweep_data",
        " ",
        ".measure ac I_1 find I(Vd_ac) at=1",
        ".measure ac I_2 find I(Vd_ac) at=1e15",
        ".measure ac V_mag find V(drain) at=1",
        ".measure dc id find i(Vsd) when v(drain)=\'v(source)-vds_val\'",
        " ",
        ".data sweep_data",
        "+ vgs_val vds_val ",
        "{sources}",
        ".ENDDATA",
        ""
    ]

    testbench_1 = [         # cgg
        "Vdd source 0 DC vdd_val",                     
        "Vsd source drain DC vds_val",
        "Vsb source bulk DC vsb_val",
        "Vsg source gate_ 0 DC vgs_val",
        "Vg_ac gate_ gate AC 1",
        ".ac dec 1 1e13 1e15 sweep data=sweep_data",
        ".measure ac I_g find I(Vg_ac) at=1e15",
        ".measure ac V_mag find V(gate) at=1e15",
        " ",
        ".data sweep_data",
        "+vgs_val vds_val",
        "{sources}",
        ".ENDDATA",
        " "
    ]

    testbenches = [testbench_0, testbench_1]

    footer = ".end"

    testbench = testbenches[ind]

    d = {}
    d["sources"] = ""
    vgs = np.linspace(0,0.8,41)
    vds = np.linspace(0,0.8,41)
    
    for vds_val in vds:
         for vgs_val in vgs:
              d["sources"]+=f"{str(round(vgs_val,2))} {str(round(vds_val,2))}\n"

    testbench_  = "\n".join(testbench); 

    spice_file = "\n".join(header) + "\n"*3 +  testbench_.format(**d)  + "\n"*2 + footer 
    with open("outputs/pmos_extractor.sp", "w") as file:
            file.write(spice_file)
        
    # run the simulation
    exit_status = os.system('hspice -i outputs/pmos_extractor.sp -o outputs/pmos_extract/')


@timing_decorator
def main_nfet():    
    data_x  = np.array([])
    counter = 0
    for fn_index, fin in enumerate(fins): 
        fn = fingers[fn_index]
        for s in stk: 
            create_and_simulate_spice_nfet(fins = fin, fingers = fn, stk = s, ind=0)
            data_array = parse_data_1("outputs/nmos_extract/nmos_extractor.ma0")
            gds = data_array[:,2]/data_array[:,4]
            cdd = data_array[:,3]/(2*np.pi*1e15*data_array[:,4])
            vgs_vals = data_array[:,0]
            vds_vals = data_array[:,1]
            vsb_vals = np.zeros(len(vgs_vals))
            i_d = parse_data_2("outputs/nmos_extract/nmos_extractor.ms0")

            gm = []
            for i in range(0, len(vgs_vals), 41):
                 x = vgs_vals[i:i+41]
                 y = -1*i_d[i:i+41]
                 cs_1 = CubicSpline(x, y)
                 x_new = np.linspace(0, 0.8, 1000)
                 y_new = cs_1(x_new)
                 gm_i = np.gradient(y_new, x_new)
                 cs_2 = CubicSpline(x_new, gm_i)
                 gm_i_downsampled = cs_2(x) 
                 gm = np.concatenate((gm, gm_i_downsampled), axis=0)

            create_and_simulate_spice_nfet(fins = fin, fingers = fn, stk = s, ind=1)
            i_g = parse_data_2("outputs/nmos_extract/nmos_extractor.ma0")
            cgg = i_g/(2*np.pi*1e15)
            data = np.column_stack([vgs_vals, vds_vals, vsb_vals, fin*fn*np.ones(len(vgs_vals)), s*np.ones(len(vgs_vals)), -1*i_d, gm, gds, cdd, cgg])
            
            if len(data_x) == 0:
                data_x = data
            else:
                data_x = np.row_stack([data_x, data])
        
        counter += 1
        print(f"{counter} out of {len(fins)*len(fingers)*len(stk)}")

    data_ = pd.DataFrame(data_x, columns = ["vgs","vds","vsb","fins","length","id","gm","gds","cdd","cgg"])
    data_.to_csv('rvt_nfet.csv', index=False)


@timing_decorator
def main_pfet():
    data_x  = np.array([])
    counter = 0
    for fn_index, fin in enumerate(fins): 
        fn = fingers[fn_index]
        for s in stk: 
            create_and_simulate_spice_pfet(fins = fin, fingers = fn, stk = s, ind=0)
            data_array = parse_data_1("outputs/pmos_extract/pmos_extractor.ma0")
            gds = data_array[:,2]/data_array[:,4]
            cdd = data_array[:,3]/(2*np.pi*1e15*data_array[:,4])
            vgs_vals = data_array[:,0]
            vds_vals = data_array[:,1]
            vsb_vals = np.zeros(len(vgs_vals))
            i_d = parse_data_2("outputs/pmos_extract/pmos_extractor.ms0")

            gm = []
            for i in range(0, len(vgs_vals), 41):
                 x = vgs_vals[i:i+41]
                 y = -1*i_d[i:i+41]
                 cs_1 = CubicSpline(x, y)
                 x_new = np.linspace(0, 0.8, 1000)
                 y_new = cs_1(x_new)
                 gm_i = np.gradient(y_new, x_new)
                 cs_2 = CubicSpline(x_new, gm_i)
                 gm_i_downsampled = cs_2(x) 
                 gm = np.concatenate((gm, gm_i_downsampled), axis=0)

            create_and_simulate_spice_pfet(fins = fin, fingers = fn, stk = s, ind=1)
            i_g = parse_data_2("outputs/pmos_extract/pmos_extractor.ma0")
            cgg = i_g/(2*np.pi*1e15)
            data = np.column_stack([vgs_vals, vds_vals, vsb_vals, fin*fn*np.ones(len(vgs_vals)), s*np.ones(len(vgs_vals)), i_d, gm, gds, cdd, cgg])
            
            if len(data_x) == 0:
                data_x = data
            else:
                data_x = np.row_stack([data_x, data])
        
        counter += 1
        print(f"{counter} out of {len(fins)*len(fingers)*len(stk)}")

    data_ = pd.DataFrame(data_x, columns = ["vsg","vsd","vsb","fins","length","id","gm","gds","cdd","cgg"])
    data_.to_csv('rvt_pfet.csv', index=False)
   

if __name__ == "__main__":
    # main_nfet()
    main_pfet()

