import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, interp1d
from scipy.misc import derivative
from LUT.fetch_ import *
from tools.log_file import *
from sklearn.linear_model import LinearRegression
import time

# ---------- initialization -----------------------------
VGS = np.linspace(0, 0.8, 41)
VDS = np.linspace(0, 0.8, 41)
VSB = np.array([0])
LEN = np.array([14e-9])
FIN = np.array([2, 6, 10, 20, 40])


def numerical_derivative(x, y):
    dy = np.diff(y)  # Differences in y
    dx = np.diff(x)  # Differences in x
    return dy / dx  # Deriva


def extract_vth(vgs, gm):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    name = f"temp/output_{timestamp}"

    dgm = numerical_derivative(vgs, gm)

    n = 5
    ind = np.argsort(dgm)[::-1]
    model = LinearRegression()
    model.fit(vgs[ind[0]:ind[n]].reshape(-1, 1), gm[ind[0]:ind[n]].reshape(-1, 1))
    y_pred = model.predict(vgs[10:30].reshape(-1, 1))

    m = model.coef_[0]
    b = model.intercept_
    vth = -b / m

    plt.plot(vgs, gm, '*-')
    plt.plot(vgs[1::], dgm)
    plt.plot(vgs[10:30], y_pred)
    plt.plot(vth, 0, 'o')
    plt.savefig(name)

    return vth


class Five_T_OTA():
    def __init__(self) -> None:
        self.tb = fetch_data_1()  # tb is for table

    def get_intersection(self, array1, array2):
        i = np.where(np.isclose(VGS, np.argmin(abs(array1 - array2))))
        return i, VGS[i]

    def interpolate_array(self, x, y, y_value):
        f = CubicSpline(x, y)
        x_dense = np.linspace(0, 0.8, 1000)
        y_dense = f(x_dense)
        i = np.argmin(abs(y_dense - y_value))
        return x_dense[i]

    def set_target_params(self, GBW_min, Ao_min, Po_max, load_C, supp_V, fin_ref, SR):
        self.GBW_min = GBW_min  # in Hz
        self.Ao_min = Ao_min  # in dB
        self.Po_max = Po_max  # in W
        self.load_C = load_C  # in F
        self.supp_V = supp_V  # in V
        self.fin_ref = fin_ref

    def design_ota(self, TE, vcm, vds_1, length):
        cdd_1 = 0
        cdd_2 = 0
        gm_id_0, gm_id_1, gm_id_2 = TE
        for _ in range(10):  # DP and Upper PMOS CM
            # NMOS DIFFERENTIAL PAIR --------------------------------------------------------------
            gm_1_ = self.tb.lookup("gm", length[1], self.fin_ref, "n", vds_val=vds_1)
            id_1_ = self.tb.lookup("id", length[1], self.fin_ref, "n", vds_val=vds_1)
            gm_id_1_ = gm_1_ / id_1_
            vgs_1 = self.interpolate_array(VGS, gm_id_1_, gm_id_1)
            vx = vcm - vgs_1

            gm_1 = 2 * self.GBW_min * np.pi * (self.load_C + cdd_1 + cdd_2)
            id_1 = gm_1 / gm_id_1
            fins_1 = (id_1 / self.tb.lookup("id", length[1], self.fin_ref, "n", vds_val=vds_1,
                                            vgs_val=vgs_1)) * self.fin_ref

            # PMOS CURRENT MIRROR --------------------------------------------------------------
            vsd_2 = self.supp_V - (vx + vds_1)
            id_2 = id_1
            for _ in range(5):  # this is for the PMOS
                gm_2_ = self.tb.lookup("gm", length[2], self.fin_ref, "p", vds_val=vsd_2)
                id_2_ = -1 * self.tb.lookup("id", length[2], self.fin_ref, "p", vds_val=vsd_2)
                gm_id_2_ = gm_2_ / id_2_
                vsg_2 = self.interpolate_array(VGS, gm_id_2_, gm_id_2)
                vsd_2 = vsg_2

            fins_2 = -1 * (id_2 / self.tb.lookup("id", length[2], self.fin_ref, "p", vds_val=vsd_2,
                                                 vgs_val=vsg_2)) * self.fin_ref
            vds_1 = self.supp_V - vx - vsd_2  # updating the drain to source voltage of the diff_pair
            cdd_1 = self.tb.lookup("cdd", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1) * (
                        fins_1 / self.fin_ref)
            cdd_2 = self.tb.lookup("cdd", length[2], self.fin_ref, "n", vds_val=vds_1, vgs_val=vsg_2) * (
                        fins_2 / self.fin_ref)

        # NMOS CURRENT MIRROR --------------------------------------------------------------
        id_0 = 2 * id_1
        vds_0 = vx

        gm_0_ = self.tb.lookup("gm", length[0], self.fin_ref, "n", vds_val=vds_0)
        id_0_ = self.tb.lookup("id", length[0], self.fin_ref, "n", vds_val=vds_0)
        gm_id_0_ = gm_0_ / id_0_
        vgs_0 = self.interpolate_array(VGS, gm_id_0_, gm_id_0)
        fins_0 = (id_0 / self.tb.lookup("id", length[0], self.fin_ref, "n", vds_val=vx, vgs_val=vgs_0)) * self.fin_ref

        Is = self.tb.lookup("id", length[0], self.fin_ref, "n", vds_val=vgs_0, vgs_val=vgs_0) * (fins_0 / self.fin_ref)

        # result determination
        gm_0 = self.tb.lookup("gm", length[0], self.fin_ref, "n", vds_val=vds_0, vgs_val=vgs_0) * (
                    fins_0 / self.fin_ref)
        gm_1 = self.tb.lookup("gm", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1) * (
                    fins_1 / self.fin_ref)
        gm_2 = self.tb.lookup("gm", length[2], self.fin_ref, "p", vds_val=vsd_2, vgs_val=vsg_2) * (
                    fins_2 / self.fin_ref)

        gds_0 = self.tb.lookup("gds", length[0], self.fin_ref, "n", vds_val=vds_0, vgs_val=vgs_0) * (
                    fins_0 / self.fin_ref)
        gds_1 = self.tb.lookup("gds", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1) * (
                    fins_1 / self.fin_ref)
        gds_2 = self.tb.lookup("gds", length[2], self.fin_ref, "p", vds_val=vsd_2, vgs_val=vsg_2) * (
                    fins_2 / self.fin_ref)
        cdd_1 = self.tb.lookup("cdd", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1) * (
                    fins_1 / self.fin_ref)
        cdd_2 = self.tb.lookup("cdd", length[2], self.fin_ref, "p", vds_val=vsd_2, vgs_val=vsg_2) * (
                    fins_2 / self.fin_ref)

        cgg_1 = self.tb.lookup("cgg", length[1], self.fin_ref, "n", vds_val=vds_1, vgs_val=vgs_1) * (
                    fins_1 / self.fin_ref)
        cgg_2 = self.tb.lookup("cgg", length[2], self.fin_ref, "p", vds_val=vsd_2, vgs_val=vsg_2) * (
                    fins_2 / self.fin_ref)
        c_self = (cgg_2 + cgg_1) / 2 + cdd_1 + cdd_2

        A = 20 * np.log10(gm_1 / (gds_1 + gds_2)[0])
        GBW = gm_1 / (2 * np.pi * (self.load_C + cdd_1 + cdd_2))[0]
        fins = [fins_0[0], fins_1[0], fins_2[0]]

        try:
            vth = extract_vth(VGS, self.tb.lookup("gm", length[1], self.fin_ref, "n", vds_val=vds_1))
        except:
            vth = 0.32

        other_res = {"vx": vx,
                     "vy": vx + vds_1,
                     "gm_0": gm_0,
                     "gm_1": gm_1,
                     "gm_2": gm_2,
                     "cdd_1": cdd_1,
                     "cdd_2": cdd_2,
                     "l_0": gds_0 / id_0,
                     "l_1": gds_1 / id_1,
                     "l_2": gds_2 / id_2,
                     "ugf": GBW,
                     "cgg_1": cgg_1,
                     "cgg_2": cgg_2,
                     "Itail": id_0,
                     "vds_0": vds_0,
                     "vds_1": vds_1,
                     "vsd_2": vsd_2,
                     "vth": vth
                     }

        return fins, Is, other_res

    def pltx(self):
        cdd = self.tb.lookup("cdd", 1, 10, "n", vds_val=0.5)
        plt.plot(VGS, cdd)
        cdd = self.tb.lookup("cdd", 1, 20, "n", vds_val=0.5)
        plt.plot(VGS, cdd)
        cdd = self.tb.lookup("cdd", 1, 30, "n", vds_val=0.5)
        plt.plot(VGS, cdd)
        plt.show()


def main():
    ota = Five_T_OTA()
    ota.pltx()
    # params = {
    #     "GBW_min": 45.6e6,  # in Hz
    #     "Ao_min": 20,  # in dB
    #     "Po_max": 100e-6,  # in W
    #     "load_C": 4e-12,  # in F
    #     "supp_V": 1.2,  # in V
    #     "fin_ref": 10,
    #     "SR": 3,
    # }
    #
    # ota.set_target_params(**params)
    # fins, Is, other_res = ota.design_ota([18.5, 23.4, 17.3], 0.6, 0.4, [1, 1, 1])
    #
    # print(fins)
    # print(Is)
    # print(other_res["vx"])
    # print(other_res["vy"])


if __name__ == "__main__":
    main()
