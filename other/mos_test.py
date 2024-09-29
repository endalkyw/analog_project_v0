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
import pandas as pd
   

def create_spice(fins, fingers, vds, vgs, vsb, type):
        header = [
        "*********************************************",
        ".LIB \"/project/ssstudents/TAPO_downloads/GF12_V1.0_4.1/12LP/V1.0_4.1/Models/HSPICE/models/12LP_Hspice.lib\" TT",
        ".option post = 2",
        ".option ingold = 1",
        ".PARAM wireopt=3 pre_layout_sw=0"]

        p = params()
        m = p.get_mos_string("m0", d="drain",  g="gate", s=0, b="bulk", type = type, fins = fins, nf = fingers, stack=1)

        testbench_1 = [
            ".op",
            "Vds drain 0 "+str(vds),
            "Vgs gate 0 "+str(vgs),
            "Vsb bulk 0 "+str(vsb),
            ".dc Vds 0 0.8 0.02",
            ".print dc v(drain) i(Vds)",
            # ".measure dc idrain i(Vds) when v(vd) = 0.256"
            # ".measure dc gm   find gm(xm0) when v(vd) =  '0.256",
            # ".measure dc gds  find gds(xm0) when v(vd) =  0.256"
            ""
        ]

        testbench_2 = [                         # output capacitance and resistance
            ".param vd_val = 0.5",
            ".param vg_val = 0.5",

            "Vd drain_ 0 DC vd_val",
            "Vg gate 0 DC vg_val",
            "Vac drain drain_ AC 1" ,
            " ",
            ".ac dec 1 1 1e15 sweep data=sweep_data",
            " ",
            ".measure ac I_1 find I(Vac) at=1",
            ".measure ac I_2 find I(Vac) at=1e15",
            ".measure ac V_mag find V(drain) at=1",
            # ".alter sweep_data",
            " ",
            ".data sweep_data",
            "+ vd_val vg_val",
            "{sources}",
            ".ENDDATA",
            ""
        ]
        footer = ".end"

        d = {}
        d["sources"] = "+ 0.3 0.2\n+ 0.2 0.1\n+ 0.6 0.2"
        testbench_2_  = "\n".join(testbench_2);
        testbench_2_1 = testbench_2_.format(**d) 
        
        # for vd_val in range(0, 0.8, 0.1):
        #    vg_val = 0

        # spice_file = "\n".join(header) + "\n"*3 + m + "\n"*3 +  "\n".join(testbench_1) + "\n"*2 + footer 
        spice_file = "\n".join(header) + "\n"*3 + m + "\n"*3 +  testbench_2_1 + "\n"*2 + footer 
        with open("outputs/nmos_test.sp", "w") as file:
            file.write(spice_file)
        

def sim_spice():
    exit_status = os.system('hspice -i outputs/nmos_test.sp -o outputs/nmos_temp/')
    content = []
    # with open("outputs/nmos_temp/five_transistor_ota.ma0", 'r') as file:
    #     for line in file:
    #         content.append(line)
    
    # res = np.array(content[4].split())
    # return res.astype(float)

def main():
    # clear_output_files()
    # create_spice(20, 1, 0.2554, 0.5,0, "nfet")
    # sim_spice()

    # extracted_content = extract_between_x_and_y('outputs/nmos_temp/nmos_test.lis')
    # data = []
    # for content in extracted_content:
    #     data.append(content.split())
    # x = np.array(data[3:])
    # y = x.astype(float)
    




    tb_1 = fetch_data_1()
    tb_2 = fetch_data_2()

    # -------------- spectre and hspice comparison ------------------
    gm_1 = tb_1.lookup("gds", 1, 10, "p", vds_val = 0.2)
    gm_2 = tb_2.lookup("gds", 14e-9, 10, "p", vds_val = 0.2)
    
    plt.plot(gm_1,'k-*')
    plt.plot(gm_2,'r-.')

    gm_1 = tb_1.lookup("gds", 1, 10, "p", vds_val = 0.7)
    gm_2 = tb_2.lookup("gds", 14e-9, 10, "p", vds_val = 0.7)
    plt.plot(gm_1,'k-')
    plt.plot(gm_2,'r-.')

    plt.savefig("t1.png")

    # --------------- effect of stacking on gds -------------------
    # gds_1 = tb_1.lookup("gds", 1, 10, "n", vgs_val = 0.4)
    # gds_2 = tb_1.lookup("gds", 2, 10, "n", vgs_val = 0.4)
    # gds_3 = tb_1.lookup("gds", 3, 10, "n", vgs_val = 0.4)
    # gds_4 = tb_1.lookup("gds", 4, 10, "n", vgs_val = 0.4)
    
    # plt.plot(1/gds_1,'k-')
    # plt.plot(1/gds_2,'r-.')
    # plt.plot(1/gds_3,'b-')
    # plt.plot(1/gds_4,'g-.')    
    # plt.savefig("gds.png")

    # --------------- effect of stacking on Ai -------------------
    # gds_1 = tb_1.lookup("gds", 1, 10, "n", vgs_val = 0.4)
    # gds_2 = tb_1.lookup("gds", 2, 10, "n", vgs_val = 0.4)
    # gds_3 = tb_1.lookup("gds", 3, 10, "n", vgs_val = 0.4)
    # gds_4 = tb_1.lookup("gds", 4, 10, "n", vgs_val = 0.4)
    
    # gm_1 = tb_1.lookup("gm", 1, 10, "n", vgs_val = 0.4)
    # gm_2 = tb_1.lookup("gm", 2, 10, "n", vgs_val = 0.4)
    # gm_3 = tb_1.lookup("gm", 3, 10, "n", vgs_val = 0.4)
    # gm_4 = tb_1.lookup("gm", 4, 10, "n", vgs_val = 0.4)

    # plt.plot(gm_1/gds_1,'k-')
    # plt.plot(gm_2/gds_2,'r-.')
    # plt.plot(gm_3/gds_3,'b-')
    # plt.plot(gm_4/gds_4,'g-.')    
    # plt.savefig("ai.png")

    # --------------- effect of transient frequency Ft -------------------
    # gm_1 = tb_1.lookup("gm", 1, 10, "n", vgs_val = 0.4)
    # gm_2 = tb_1.lookup("gm", 2, 10, "n", vgs_val = 0.4)
    # gm_3 = tb_1.lookup("gm", 3, 10, "n", vgs_val = 0.4)
    # gm_4 = tb_1.lookup("gm", 4, 10, "n", vgs_val = 0.4)

    # cgg_1 = tb_1.lookup("cgg", 1, 10, "n", vgs_val = 0.4)
    # cgg_2 = tb_1.lookup("cgg", 2, 10, "n", vgs_val = 0.4)
    # cgg_3 = tb_1.lookup("cgg", 3, 10, "n", vgs_val = 0.4)
    # cgg_4 = tb_1.lookup("cgg", 4, 10, "n", vgs_val = 0.4)
    
    # plt.plot(gm_1/(2*np.pi*cgg_1),'k-')
    # plt.plot(gm_2/(2*np.pi*cgg_2),'r-.')
    # plt.plot(gm_3/(2*np.pi*cgg_3),'b-')
    # plt.plot(gm_4/(2*np.pi*cgg_4),'g-.')    
    # plt.savefig("ft.png")


    # --------------- frequency Ft vs gain -------------------
    # plt.scatter(gm_1/gds_1,gm_1/(2*np.pi*cgg_1))
    # plt.scatter(gm_2/gds_2,gm_2/(2*np.pi*cgg_2))
    # plt.scatter(gm_3/gds_3,gm_3/(2*np.pi*cgg_3))
    # plt.scatter(gm_4/gds_4,gm_4/(2*np.pi*cgg_4))    
    # plt.savefig("ai_ft.png")

if __name__ == "__main__":
    main()
