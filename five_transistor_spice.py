from LUT.read import lut
from spice.mos_par import *
from spice.parse_funcs import *
from LUT.fetch_ import *
from tools.output_file import clear_output_files
from tools.log_file import *
from tools.timing import *
import re
import os
from tools.timing import *
from tools.log_file import *
import matplotlib.pyplot as plt

def create_spice(fins, stacks, vcm, vd,  Is, vdd, load_c, tb_index=0):
    # vin_m vin_p vdd is gnd
    spice_wrapper = ".subckt five_transistor_ota vin_m vin_p nx1 is vdd g \n {ckt} \n .ends"
    p = params()
    m0 = p.get_mos_string("m0", d = "is",  g = "is",    s = "g",   b = "g",   type = "nfet", fins = fins[0], stack = stacks[0])
    m1 = p.get_mos_string("m1", d = "ny",  g = "is",    s = "g",   b = "g",   type = "nfet", fins = fins[0], stack = stacks[0])
    m2 = p.get_mos_string("m2", d = "nx0", g = "vin_p", s = "ny",  b = "g",   type = "nfet", fins = fins[1], stack = stacks[1])
    m3 = p.get_mos_string("m3", d = "nx1", g = "vin_m", s = "ny",  b = "g",   type = "nfet", fins = fins[1], stack = stacks[1])
    m4 = p.get_mos_string("m4", d = "nx0", g = "nx0",   s = "vdd", b = "vdd", type = "pfet", fins = fins[2], stack = stacks[2])
    m5 = p.get_mos_string("m5", d = "nx1", g = "nx0",   s = "vdd", b = "vdd", type = "pfet", fins = fins[2], stack = stacks[2])   
    ckt = {"ckt":"\n".join([m0, m1, m2, m3, m4, m5])}
    subckt = spice_wrapper.format(**ckt)

    # ********************************************************************************************
    header = [
    "*********************************************",
    ".LIB \"/project/ssstudents/TAPO_downloads/GF12_V1.0_4.1/12LP/V1.0_4.1/Models/HSPICE/models/12LP_Hspice.lib\" TT",
    ".option post = 2",
    ".option ingold = 1",
    ".PARAM wireopt=3 pre_layout_sw=0"]
    footer = ".end"

    # gain, bw, pm, power
    ac_1_tb = [
        "xota vin_m vin_p vout is vdd 0 five_transistor_ota",
        "C vout 0 " + str(load_c),
        "Vdd vdd 0 "+str(vdd),
        "Is 0 is "+str(Is),
        "Vcm c 0 "+str(vcm),
        f"Vdm vd 0 AC 1",
        "Ene vin_m c vd 0 -0.5",
        "Epo vin_p c vd 0 0.5",
        "",
        "* ---- Analysis part ----- ",
        ".ac dec 5 1 100G    * Frequency sweep from 10 Hz to 100 kHz, 20 points per decade",
        ".noise v(vout) vdm 100",
        ".print ac vdb(vout) vp(vout) * Print the AC magnitude and phase at node 2 (Vout)",
        ".measure ac gain max vdb(vout)",
        ".measure ac bw when vdb(vout) = \'gain - 3\'",
        ".measure ac ugf when vdb(vout) = 0 cross=1",
        ".measure ac Phase_at_0db find vp(vout) when vdb(vout)=0",
        ".measure ac Phase_Margin param=\'180 + Phase_at_0db\'",
        ""
    ]

    cmrr_tb = [
        "xota vin_m vin_p vout is vdd 0 five_transistor_ota",
        "C vout 0 " + str(load_c),
        "Vdd vdd 0 "+str(vdd),
        "Is 0 is "+str(Is),
        "Vcm c 0 "+str(vcm),
        f"Vdm vd 0 AC 1",
        "Ene vin_m c vd 0 0.5",
        "Epo vin_p c vd 0 0.5",
        "",
        "* ---- Analysis part ----- ",
        ".ac dec 5 1 100G    * Frequency sweep from 10 Hz to 100 kHz, 20 points per decade",
        ".print ac vdb(vout) vp(vout) * Print the AC magnitude and phase at node 2 (Vout)",
        ".measure ac gain max vdb(vout)",
        ""
    ]


    slew_rate = [        # for slew rate measurement
        ".param v1=0.15v v2=-0.15v td=50ns tr=1ns tf=1ns pw=200ns per=400ns",
        "xota vout vin_p vout is vdd 0 five_transistor_ota",
        "C vout 0 " + str(load_c),
        "Vdd vdd 0 "+str(vdd),
        "Is 0 is "+str(Is),
        "Vcm c 0 "+str(vcm),
        "vpulse vin_p c pulse( v1 v2 td tr tf pw per )",
        "",
        "* ---- Analysis part ----- ",
        ".tran 1n 1000n",
        # ".print tran v(vin_p) v(vout)",
        ".measure tran max_v max v(vout)",
        ".measure tran min_v min v(vout)",
        ".measure tran del param = \'max_v - min_v\'",
        ".measure tran vout10 param = \'0.1*del + min_v\'",
        ".measure tran vout90 param = \'0.9*del + min_v\'",
        ".measure tran t10 when v(vout) = \'vout10\' rise=1",
        ".measure tran t90 when v(vout) = \'vout90\' rise=1",
        ".measure tran slew_rate param = \'(vout90-vout10)/(t90-t10)\'",
        # ".measure tran max_slew_rate MAX deriv(v(out))", - this doesn't work
        ".print tran v(vout)",
        ""
    ]

    testbench = [ac_1_tb, cmrr_tb, slew_rate]

    spice_file   = "\n".join(header) + "\n"*3 + subckt + "\n"*3 +  "\n".join(testbench[tb_index]) + "\n"*2 + footer 
    with open("outputs/five_transistor_ota.sp", "w") as file:
        file.write(spice_file)

def simulate(dir_name):
    exit_status = os.system(f'hspice -mt 16 -i outputs/five_transistor_ota.sp -o outputs/{dir_name}/')

def parse_outputs(tb_index):
    # 0: gain, ugf, pm, power 
    # 1: common_mode_gain
    # 2: slew_rate

    if tb_index == 0:
        # gain, ugf and pm
        content = []
        with open("outputs/fivetota/five_transistor_ota.ma0", 'r') as file:
             for line in file:
               c = line.split()
               if len(c)==4 or len(c)==3:
                 content.append(line.split())

        # for power
        get = False
        noise_get = False
        content_2 = []
        reg = 0
        with open("outputs/fivetota/five_transistor_ota.lis", 'r') as file:
            for line in file:
                if "**** voltage sources" in line:
                    get = True
                if "**** current sources" in line:
                    get = False
                    # break                    
                
                if get:
                    c = line.split()
                    if len(c)==4:
                        content_2.append(c)
                
                # if "equivalent input noise at vdm" in line:
                #     noise_get = True

                # if noise_get:
                #     content_2.append(line.strip().split())

                if "region" in line:
                    reg = line.strip().split()[1::]


        return {"A": float(content[2][0]), "BW":content[2][1], "UGF": float(content[2][2]), "PM": float(content[3][0]), "P": float(content_2[3][2]), "reg":reg}

    elif tb_index == 1:
        content = []
        with open("outputs/fivetota/five_transistor_ota.ma0", 'r') as file:
             for line in file:
               c = line.split()
               if len(c)==3:
                 content.append(line.split())

        return {"A_CM": float(content[1][0])}

    elif tb_index == 2:
        content = []
        # with open("outputs/fivetota/five_transistor_ota.mt0", 'r') as file:
        #      for line in file:
        #        c = line.split()
        #        if len(c)==4:
        #          content.append(line.split())
        # SR = float(content[3][3])/1e6

        val_list = extract_between_x_and_y("outputs/fivetota/five_transistor_ota.lis")
        v_list = []
        for val in val_list[3::]:
           t, v = val.split()
           v_list.append([float(t), float(v)]) 

        v_l = np.array(v_list)
        sr  = np.diff(v_l[:,1])/np.diff(v_l[:,0])
        SR  = np.round(max(sr)/1e6, decimals=3)

        return {"SR": SR} #in volt/us

def get_ota_specs(fins, stacks, vcm, vd, Is, vdd, load_c):
    # this function returns all the required specs of the circuit
    results = {}
    for test in [0,1,2]:
        create_spice(fins, stacks, vcm, vd, Is, vdd, load_c, test)
        simulate("fivetota")
        os.system('clear')
        results.update(parse_outputs(test))

    cmrr =  results["A"] - results["A_CM"]
    results["cmrr"] = cmrr

    del results["A_CM"]
    return results 



@timing_decorator
def main():

    # result_1 = get_ota_specs(10, 20, 10, 0.5, 0.001, 10e-6, 1.2, 1e-12, 1)
    # result_2 = get_ota_specs(8, 20, 20, 0.5, 0.001, 10e-6, 1.2, 1e-12, 1)  
    # result_3 = get_ota_specs(6, 30, 18, 0.5, 0.001, 10e-6, 1.2, 1e-12, 1)
    # result_4 = get_ota_specs(4, 40, 12, 0.5, 0.001, 10e-6, 1.2, 1e-12, 1)
    # result_5 = get_ota_specs(2, 50, 8, 0.5, 0.001, 10e-6, 1.2, 1e-12, 1)

    # print(result_1)    
    # print(result_2)    
    # print(result_3)    
    # print(result_4)    
    # print(result_5)    
    

    # inputs = {"fins": [20, 40, 18], 
    #           "stacks": [1, 1, 1], 
    #           "vcm": 0.6, 
    #           "vd": 0.001, 
    #           "Is": 100e-6, 
    #           "vdd": 1.2, 
    #           "load_c": 20e-12}


    sr = []
    cx  = np.arange(0.1e-12, 10e-12, 0.5e-12)
    for c in cx:
        inputs = {"fins": [10, 20, 12], 
                  "stacks": [1, 1, 1], 
                  "vcm": 0.6, 
                  "vd": 0.0001, 
                  "Is": 100e-6, 
                  "vdd": 1.2, 
                  "load_c": c}

        result = get_ota_specs(**inputs)
        sr.append(result["SR"])
    

    plt.plot(cx, sr, 'o-')
    plt.savefig("sr.png")
        # write_log_file("result.txt","------------------------------------------\n", "a")
        # write_log_file("result.txt",str(inputs), "a")
        # write_log_file("result.txt", str(result), "a")
        # write_log_file("result.txt","------------------------------------------\n", "a")

        # print(result)








if __name__ == '__main__':
    main()
