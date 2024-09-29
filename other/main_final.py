import re
import os
import sys
from Extractor.extract import *
from multiple_layout_generator import *
from utilities.elements_utils import *
from tools.show_layout import *
from tools.write_layout import *
from tools.log_file import *
from tools.output_file import clear_output_files
from tools.common_funcs import *
from Extractor.ext_util import *
from primitives.mos import *
from design_ota import Five_T_OTA
from cm_testbench import simulate_and_parse as cm_sp
from dp_testbench import simulate_and_parse as dp_sp

spice_dir = os.path.abspath("spice")
sys.path.append(dir)
import primitives_spice as ps



@timing_decorator
def main():
    # === Check command line arguments ===========
    if len(sys.argv) < 2:
        sys.exit(1)

    script_name = sys.argv[0]
    arguments   = sys.argv[1:]
    # ============================================

    args = set(arguments)
    print("Arguments:", args)
    
    # clear output file --------------------------
    # clear_output_files()
    
    if '-des' in args:
        ota = Five_T_OTA()
        params = {
         "GBW_min":100e6,    # in Hz
         "Ao_min": 20,       # in dB
         "Po_max": 1e-6,     # in W
         "load_C": 1e-12,    # in F
         "supp_V": 1.2,      # in V
         "fin_ref": 10
         }

        ota.set_target_params(**params)

        gm_id_0 = 15
        gm_id_1 = 23
        gm_id_2 = 15
        vcm     = 0.5
        vds_1 = params["supp_V"]/3
        A, GBW, Power, fins, Is = ota.design_ota(gm_id_0, gm_id_1, gm_id_2, vcm, vds_1, 14e-9)
        q_fins = [round(num) for num in fins]

        q_fins[0] = prime_check(q_fins[0])
        q_fins[1] = prime_check(q_fins[1])
        q_fins[2] = prime_check(q_fins[2])

        # generating spice file
        ps.create_cm_spice(q_fins[0], q_fins[0], 1, "nfet", "nmos_cm.dspf")
        ps.create_dp_spice(q_fins[1], 1, "nfet", "nmos_dp.dspf")
        ps.create_cm_spice(q_fins[2], q_fins[2], 1, "pfet", "pmos_cm.dspf")
        print("Design done!")

    if '-gen' in args: # generate layouts and spice files
        # Generate candidate layouts ----------------------------------------------------
        generate_cm_layouts(q_fins[2], q_fins[2]   , 14e-9, type="P")
        generate_cm_layouts(q_fins[0], q_fins[0]   , 14e-9, type="N")
        generate_dp_layouts(q_fins[1], 14e-9, type="N") 
        print("Layout generation done!")
        
    if '-pex' in args:
        path = 'outputs/'
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        for i,layouts in enumerate(files):
            file_name = path+layouts.split('.')[0]
            failed_pex = 0

            if ".gds" in layouts: 
              try:
                  pex(file_name)
              except:
                  print(f"{file_name}: failed!")
                  failed_pex += 1

              print(i,file_name,"done!")
        
        print(f"PEX done!, {failed_pex} failed!")

    if '-sim' in args:
        path = 'outputs/'
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        dspf_files = []
        for f in files:
            if ".dspf" in f:
                dspf_files.append(f)
        
        for dspfs in dspf_files:
            pattern = r'[^/]+(?=\.[^.]+$)'
            name = re.search(pattern , dspfs)
            name_str = name.group(0)

            # if "nmos_cm" in name_str:
            #     cm_sp(name_str, "nfet")

            if "pmos_cm" in name_str:
                cm_sp(name_str, "pfet")
            
            # if "nmos_dp" in name_str:
            #     dp_sp(name_str, "nfet")

            # if "pmos_dp" in name_str:
            #     dp_sp(name_str, "pfet")
    
    if '-plt' in args:
      def plot_(file_id, plt_name):
            path = 'outputs/'
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]


            plt.subplot(3,1,1)
            for fl in files:
                if file_id in fl and ".csv" in fl:
                    data = pd.read_csv(os.path.join(path,fl))
                    plt.plot(data["vd0"][77:88],data["gds"][77:88],'*-', label = fl)

            plt.title("gds vs vd0")
            plt.tight_layout()

            plt.subplot(3,1,2)
            
            for fl in files:
                if file_id in fl and ".csv" in fl:
                    data = pd.read_csv(os.path.join(path,fl))
                    plt.plot(data["vd0"][77:88],data["i_d"][77:88], label = fl)

            plt.title("id vs vd0")
            plt.tight_layout()

            plt.subplot(3,1,3)
            for fl in files:
                if file_id in fl and ".csv" in fl:
                    data = pd.read_csv(os.path.join(path,fl))
                    plt.plot(data["vd0"][77:88],data["cdd"][77:88], label = fl)

            plt.title("cdd vs vd0")
            plt.legend()
            plt.tight_layout()

            plt.savefig(plt_name)

      plot_("nmos_dp", "pmos_all.png" )    
  
    if '-red' in args:
        pass


if __name__ == "__main__":
    main()

















# def main_2():
#     ota = Five_T_OTA()
#     ota.create_spice(10, 20, 30, 0.5, 0.01,100e-6, 1.2, 15e-15)
#     res = ota.sim_spice(1)
#     print(res)
# =========== clear output and generate multiple layouts ======================================
