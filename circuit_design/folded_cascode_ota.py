import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, interp1d
from scipy.misc import derivative
from LUT.fetch_ import *
from tools.log_file import *
from sklearn.linear_model import LinearRegression
import time
from common_functions import *

# ---------- initialization -----------------------------
VGS = np.linspace(0, 0.8, 41)
VDS = np.linspace(0, 0.8, 41)
VSB = np.array([0])
LEN = np.array([14e-9])
FIN = np.array([2, 6, 10, 20, 40])
v_margin = 0.05

class folded_cascode_ota():
    def __init__(self) -> None:
        self.tb = fetch_data_1()  # tb is for table

    def set_target_params(self, GBW_min, Ao_min, Po_max, load_C, supp_V, fin_ref, SR):
        self.GBW_min = GBW_min  # in Hz
        self.Ao_min = Ao_min  # in dB
        self.Po_max = Po_max  # in W
        self.load_C = load_C  # in F
        self.supp_V = supp_V  # in V
        self.fin_ref = fin_ref

    def get_vgs(self, length, vds_val, gm_id, type = "n"):
        gm = self.tb.lookup("gm", length, self.fin_ref, type, vds_val=vds_val)
        id = self.tb.lookup("id", length, self.fin_ref, type, vds_val=vds_val)
        if type == "p":
            id = -1*id
        gm_id_ = gm/id
        vgs = interpolate_array(VGS, gm_id_, gm_id)
        return vgs

    def design_ota(self, TE, vcm, vds_1, length):
        cdd_1 = 0
        cdd_2 = 0
        gm_id_0, gm_id_1, gm_id_2, gm_id_3, gm_id_4, gm_id_5 = TE

        for i in range(10):
            # Input Differential Pair ----------------------------------------------------------------------------------
            vgs_1 = self.get_vgs(length[1], 0.4, TE[1])
            vx = vcm - vgs_1

            gm_1 = 2 * self.GBW_min * np.pi * (self.load_C + cdd_1 + cdd_2)
            id_1 = gm_1 / gm_id_1
            fins_1 = (id_1 / self.tb.lookup("id", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1)) * self.fin_ref

            # Top PMOS Pair --------------------------------------------------------------------------------------------
            vy = (vx + vds_1)
            vsd_2 = self.supp_V - vy
            id_2 = 2*id_1
            vsg_2 = self.get_vgs(length[2], vsd_2, TE[2], "p")
            vb1 = self.supp_V - vsg_2
            fins_2 = -1 * (id_2 / self.tb.lookup("id", length[2], self.fin_ref, "p", vds_val=vsd_2,vgs_val=vsg_2)) * self.fin_ref

            vds_1 = self.supp_V - vx - vsd_2  # updating the drain to source voltage of the diff_pair
            cdd_1 = self.tb.lookup("cdd", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1) * (fins_1 / self.fin_ref)
            cdd_2 = self.tb.lookup("cdd", length[2], self.fin_ref, "n", vds_val=vds_1, vgs_val=vsg_2) * (fins_2 / self.fin_ref)

        # NMOS Current Mirror --------------------------------------------------------------
        id_0 = 2 * id_1
        vds_0 = vx
        vgs_0 = self.get_vgs(length[2], vds_0, TE[0], "n")
        fins_0 = (id_0 / self.tb.lookup("id", length[0], self.fin_ref, "n", vds_val=vx, vgs_val=vgs_0)) * self.fin_ref
        Is = self.tb.lookup("id", length[0], self.fin_ref, "n", vds_val=vgs_0, vgs_val=vgs_0) * (fins_0 / self.fin_ref)

        id_4 = id_1
        id_3 = id_1
        id_5 = id_1

        # Bottom NMOS pair in the LV Cascode CM -------------------------------------------
        vz = self.supp_V/3
        vds_5 = vz
        # for _ in range(5):
        vgs_5 = self.get_vgs(length[5], vds_5, TE[5], "n")
        vw = vgs_5

        # approximation
        vz = 2/TE[5] + v_margin

        # Top NMOS pair for the LV Cascode CM ---------------------------------------------
        vds_4 = vw - vz
        vgs_4 = self.get_vgs(length[4], vds_4, TE[4], "n")
        vb3 = vz + vgs_4

        fins_4 = (id_4 / self.tb.lookup("id", length[4], self.fin_ref, "n", vds_val=vds_4, vgs_val=vgs_4)) * self.fin_ref
        fins_5 = (id_5 / self.tb.lookup("id", length[5], self.fin_ref, "n", vds_val=vds_5, vgs_val=vgs_5)) * self.fin_ref

        # M3 PMOS -------------------------------------------------------------
        vsd_3 = vy - vw
        vsg_3 = self.get_vgs(length[3], vsd_3, TE[3], "p")
        fins_3 = -1*(id_3 / self.tb.lookup("id", length[3], self.fin_ref, "p", vds_val=vsd_3, vgs_val=vsg_3)) * self.fin_ref
        vb2 = vw + vsg_3


        gm_0  = self.tb.lookup("gm", length[0], self.fin_ref, "n", vgs_val=vgs_0, vds_val=vds_0) * (fins_0 / self.fin_ref)
        gm_1  = self.tb.lookup("gm", length[1], self.fin_ref, "n", vgs_val=vgs_1, vds_val=vds_1) * (fins_1 / self.fin_ref)
        gm_2  = self.tb.lookup("gm", length[2], self.fin_ref, "p", vgs_val=vsg_2, vds_val=vsd_2) * (fins_2 / self.fin_ref)
        gm_3  = self.tb.lookup("gm", length[3], self.fin_ref, "p", vgs_val=vsg_3, vds_val=vsd_3) * (fins_3 / self.fin_ref)

        gds_0 = self.tb.lookup("gds", length[0], self.fin_ref, "n", vgs_val=vgs_0, vds_val=vds_0) * (fins_0 / self.fin_ref)
        gds_1 = self.tb.lookup("gds", length[1], self.fin_ref, "n", vgs_val=vgs_1, vds_val=vds_1) * (fins_1 / self.fin_ref)
        gds_2 = self.tb.lookup("gds", length[2], self.fin_ref, "p", vgs_val=vsg_2, vds_val=vsd_2) * (fins_2 / self.fin_ref)
        gds_3 = self.tb.lookup("gds", length[3], self.fin_ref, "p", vgs_val=vsg_3, vds_val=vsd_3) * (fins_3 / self.fin_ref)

        print(gm_0)
        print(gm_1)
        print(gm_2)
        print(gm_3)
        print(gds_0)
        print(gds_1)
        print(gds_2)
        print(gds_3)

        print(fins_0)
        print(fins_1)
        print(fins_2)
        print(fins_3)
        print(fins_4)
        print(fins_5)

        print("----------------------------------")
        print(vx, vy, vw, vz)
        print(id_1, id_2, id_3, id_4, id_5)
        print(vb1, vb2, vb3)
        print(Is,"----------------------------------")

# def get_outputs():

def main():
    ota = folded_cascode_ota()
    ota.set_target_params(11.8e6, 50, 100e6, 20e-12, 1.2, 10, 155e6)
    ota.design_ota([4.72, 17.796, 14.889, 26.52, 25.1, 19.05], 0.6, 0.6, [1, 1, 1, 1, 1, 1])

if __name__ == "__main__":
    main()
