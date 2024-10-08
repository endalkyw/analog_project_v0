import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from LUT.fetch_ import *
from tools.log_file import *


def radial_spyder_web(ax, all_data, metrics, al = 1, th = 2.5):
  output_path = os.path.abspath("outputs")

  num_vars = len(metrics)

  for key, data in all_data.items():
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    data += data[:1]
    angles += angles[:1]
    ax.plot(angles, data,  linewidth=th, alpha = al,  linestyle='solid', label=key)

  ax.set_yticklabels([])
  ax.set_xticks(angles[:-1])
  ax.set_xticklabels(metrics)
  ax.spines['polar'].set_visible(False) 
  # Add a legend and show the plot
  plt.legend(loc='upper right')
  ax.grid(linewidth=0.5, alpha=0.5)

  return ax

# ---------- initialization -----------------------------
VGS = np.linspace(0, 0.8, 41)
VDS = np.linspace(0, 0.8, 41)
VSB = np.array([0])
LEN = np.array([14e-9])
FIN = np.array([2, 6, 10, 20, 40])


class Five_T_OTA():
    def __init__(self) -> None:
        self.tb = fetch_data_1()         # tb is for table

    def get_intersection(self, array1, array2):
        i = np.where(np.isclose(VGS, np.argmin(abs(array1 - array2))))
        return i, VGS[i]

    def interpolate_array(self, x, y, y_value):
        f = CubicSpline(x, y)
        x_dense = np.linspace(0,0.8,1000)
        y_dense = f(x_dense)
        i = np.argmin(abs(y_dense-y_value))
        return x_dense[i]
    
    def set_target_params(self, GBW_min, Ao_min, Po_max, load_C, supp_V, fin_ref, SR):
        self.GBW_min = GBW_min    # in Hz
        self.Ao_min = Ao_min      # in dB
        self.Po_max = Po_max      # in W
        self.load_C = load_C      # in F
        self.supp_V = supp_V      # in V
        self.fin_ref = fin_ref

    def design_ota(self, TE, vcm, vds_1, length):
        cdd_1 = 0
        cdd_2 = 0
        gm_id_0, gm_id_1, gm_id_2 = TE
        for _ in range(20): # DP and Upper PMOS CM 
            # NMOS DIFFERENTIAL PAIR --------------------------------------------------------------
            gm_1_ = self.tb.lookup("gm", length[1], self.fin_ref, "n", vds_val=vds_1)
            id_1_ = self.tb.lookup("id", length[1], self.fin_ref, "n", vds_val=vds_1)
            gm_id_1_ = gm_1_/id_1_
            vgs_1 = self.interpolate_array(VGS, gm_id_1_, gm_id_1)
            vx = vcm - vgs_1
            
            gm_1 = 2*self.GBW_min*np.pi*(self.load_C + cdd_1 + cdd_2)
            id_1 = gm_1/gm_id_1
            fins_1 = (id_1/self.tb.lookup("id", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val = vgs_1))*self.fin_ref

            # PMOS CURRENT MIRROR --------------------------------------------------------------
            vsd_2 = self.supp_V - (vx + vds_1)    
            id_2 = id_1        
            for _ in range(5): # this is for the PMOS
                gm_2_ = self.tb.lookup("gm", length[2], self.fin_ref, "p", vds_val=vsd_2)
                id_2_ = -1*self.tb.lookup("id", length[2], self.fin_ref, "p", vds_val=vsd_2)
                gm_id_2_ = gm_2_/id_2_
                vsg_2 = self.interpolate_array(VGS, gm_id_2_, gm_id_2)
                vsd_2 = vsg_2
            
            fins_2 = -1*(id_2/self.tb.lookup("id", length[2], self.fin_ref, "p", vds_val=vsd_2, vgs_val = vsg_2))*self.fin_ref
            vds_1 = self.supp_V - vx - vsd_2 # updating the drain to source voltage of the diff_pair
            cdd_1 = self.tb.lookup("cdd", length[1], self.fin_ref, "n", vds_val=vds_1,vgs_val=vgs_1)*(fins_1/self.fin_ref)
            cdd_2 = self.tb.lookup("cdd", length[2], self.fin_ref, "n", vds_val=vds_1,vgs_val=vsg_2)*(fins_2/self.fin_ref)



        # NMOS CURRENT MIRROR --------------------------------------------------------------
        id_0 = 2*id_1
        vds_0 = vx

        gm_0_ = self.tb.lookup("gm", length[0], self.fin_ref, "n", vds_val=vds_0)
        id_0_ = self.tb.lookup("id", length[0], self.fin_ref, "n", vds_val=vds_0)
        gm_id_0_ = gm_0_/id_0_
        vgs_0 = self.interpolate_array(VGS, gm_id_0_, gm_id_0)
        fins_0 = (id_0/self.tb.lookup("id", length[0], self.fin_ref, "n", vds_val=vx, vgs_val = vgs_0))*self.fin_ref
        
        Is = self.tb.lookup("id", length[0], self.fin_ref, "n", vds_val=vgs_0, vgs_val=vgs_0)*(fins_0/self.fin_ref)

        # result determination
        gm_0  = self.tb.lookup("gm", length[0], self.fin_ref, "n", vds_val=vds_0, vgs_val=vgs_0)*(fins_0/self.fin_ref)
        gm_1  = self.tb.lookup("gm", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1)*(fins_1/self.fin_ref)
        gm_2  = self.tb.lookup("gm", length[2], self.fin_ref, "p", vds_val=vsd_2, vgs_val=vsg_2)*(fins_2/self.fin_ref)

        gds_0 = self.tb.lookup("gds", length[0], self.fin_ref, "n", vds_val=vds_0, vgs_val=vgs_0)*(fins_0/self.fin_ref)
        gds_1 = self.tb.lookup("gds", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1)*(fins_1/self.fin_ref)
        gds_2 = self.tb.lookup("gds", length[2], self.fin_ref, "p", vds_val=vsd_2, vgs_val=vsg_2)*(fins_2/self.fin_ref)
        cdd_1 = self.tb.lookup("cdd", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1)*(fins_1/self.fin_ref)
        cdd_2 = self.tb.lookup("cdd", length[2], self.fin_ref, "p", vds_val=vsd_2, vgs_val=vsg_2)*(fins_2/self.fin_ref)

        A   = 20*np.log10(gm_1/(gds_1+gds_2)[0])

        GBW = gm_1/(2*np.pi*(self.load_C+cdd_1+cdd_2))[0]

        # f = "design.log"
        # write_log_file(f, f" - - - - - {datetime.now()} - - - - - -", 'w')
        # write_log_file(f,"vx:       "+str(vx), 'a')
        # write_log_file(f,"vy:       "+str(vx+vds_1), 'a')
        # write_log_file(f,"gm_1:     "+str(gm_1), 'a')
        # write_log_file(f,"gds_1:    "+str(gds_1), 'a')
        # write_log_file(f,"gds_2:    "+str(gds_2), 'a')
        # write_log_file(f,"cdd_1:    "+str(cdd_1), 'a')
        # write_log_file(f,"cdd_2:    "+str(cdd_2), 'a')
        # write_log_file(f,"\n"*3, 'a')
        
        # write_log_file(f,f"vds_0 = {vds_0} and vgs_0 = {vgs_0}", 'a')
        # write_log_file(f,f"vds_1 = {vds_1} and vgs_1 = {vgs_1}", 'a')
        # write_log_file(f,f"vsd_2 = {vsd_2} and vsg_0 = {vsg_2}", 'a')
        # write_log_file(f,f"fins_0 = {fins_0}, fins_1 = {fins_1} and fins_2 = {fins_2}  ", 'a')
        
        # power = 2*id_1*self.supp_V
        # write_log_file(f,f"Gain: {A}", 'a')
        # write_log_file(f,f"GBW: {GBW}", 'a')
        # write_log_file(f,f"Is: {Is}", 'a')
        
        # 20*np.log10(A), GBW, power,       
  

        fins = [fins_0[0], fins_1[0], fins_2[0]]
        
        
        # l_1 = gds_1/id_1
        # l_2 = gds_2/id_2
        # print("Gain", TE[1]/(l_2+l_1))


        other_res = {"vx":vx, 
                     "vy":vx+vds_1, 
                     "gm_0": gm_0, 
                     "gm_1": gm_1, 
                     "gm_2": gm_2, 
                     "cdd_1": cdd_1,
                     "cdd_2": cdd_2,
                     "l_0": gds_0/id_0, 
                     "l_1":gds_1/id_1, 
                     "l_2":gds_2/id_2,
                     "ugf":GBW
                     }


        return  fins, Is, other_res

