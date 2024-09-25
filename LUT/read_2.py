import pandas as pd
import numpy as np
from scipy.interpolate import RectBivariateSpline
from joblib import Memory
import numpy as np
import os


class lut:
    def __init__(self, vgs: np.array([float]), vds: np.array([float]), vsb: np.array([float]),
                 length: np.array([float]), fins: np.array([float]), n_file, p_file):

        self.n_file = n_file
        self.p_file = p_file

        self.vgs = vgs
        self.vds = vds
        self.vsb = vsb
        self.fins = fins
        self.length = length

        fins_size =len(fins)
        len_size = len(length)
        vgs_size = len(self.vgs)
        vds_size = len(self.vds)
        vsb_size = len(self.vsb)

        self.params = ['id', 'gm', 'gds', 'cdd', 'cgg']
        self.table_n = {key: np.zeros((len_size, fins_size, vds_size, vsb_size, vgs_size))
                        for key in self.params}
        self.table_p = {key: np.zeros((len_size, fins_size, vds_size, vsb_size, vgs_size))
                        for key in self.params}

        self.read_lut()

    def read_lut(self):

        df_n = pd.read_csv(self.n_file).to_numpy()
        df_p = pd.read_csv(self.p_file).to_numpy()

        for ind in range(len(df_n)):
            n_line = df_n[ind][:]
            p_line = df_p[ind][:]
            # vgs, vds, vsb, fins, length, id, gm, gds, cdd, cgg
            for i, name in enumerate(self.params):
                # order:  length -> fins -> vds -> vsb -> vgs
                self.table_n[name][self.get_index(self.length, n_line[4]), self.get_index(self.fins, n_line[3]),
                self.get_index(self.vds, n_line[1]), self.get_index(self.vsb, n_line[2]),
                self.get_index(self.vgs, n_line[0])] = n_line[i + 5]

                self.table_p[name][self.get_index(self.length, p_line[4]), self.get_index(self.fins, p_line[3]),
                self.get_index(self.vds, p_line[1]), self.get_index(self.vsb, p_line[2]),
                self.get_index(self.vgs, p_line[0])] = p_line[i + 5]

    def get_index(self, array, element):
        return np.where(np.isclose(array, element))[0]

    def linear_interp_funcs(self, func0, func1, fin0, fin1, finx):
        funcx = func0 + ((finx - fin0) / (fin1 - fin0)) * (func1 - func0)
        return funcx

    def lookup(self, par, len_val, fin_val, type, vgs_val=-1, vds_val=-1, vsb_val=0):
        if fin_val in self.fins:
            return self.get_values(par, len_val, fin_val, type, vgs_val, vds_val, vsb_val)
        else:
            for i in range(len(self.fins)):
                if self.fins[i] > fin_val:
                    fin_r = self.fins[i]
                    fin_l = self.fins[i - 1]
                    break
                else:
                    fin_r = self.fins[-1]
                    fin_l = self.fins[-2]

            y0 = self.get_values(par, len_val, fin_l, type, vgs_val, vds_val, vsb_val=0)
            y1 = self.get_values(par, len_val, fin_r, type, vgs_val, vds_val, vsb_val=0)
            y3 = self.linear_interp_funcs(y0, y1, fin_l, fin_r, fin_val)
            return y3

    def get_values(self, par, len_val, fin_val, type, vgs_val=-1, vds_val=-1, vsb_val=0):

        if type == 'n':
            val = self.table_n[par][self.get_index(self.length, len_val), self.get_index(self.fins, fin_val), :,
                self.get_index(self.vsb, vsb_val), :].T
            
            if vds_val != -1 and vgs_val != -1:
                f = RectBivariateSpline(self.vgs, self.vds, val)
                return f(vgs_val, vds_val).reshape(-1)

            elif vgs_val == -1:
                f = RectBivariateSpline(self.vgs, self.vds, val)
                return f(self.vgs, vds_val).reshape(-1)

            if vds_val == -1:
                f = RectBivariateSpline(self.vgs, self.vds, val)
                return f(vgs_val, self.vds).reshape(-1)

        elif type == 'p':
           
            val = self.table_p[par][self.get_index(self.length, len_val), self.get_index(self.fins, fin_val), :,
                self.get_index(self.vsb, vsb_val), :].T         

            if vds_val != -1 and vgs_val != -1:
                f = RectBivariateSpline(self.vgs, self.vds, val)
                return f(vgs_val, vds_val).reshape(-1)

            elif vgs_val == -1:
                f = RectBivariateSpline(self.vgs, self.vds, val)
                return f(self.vgs, vds_val).reshape(-1)

            if vds_val == -1:
                f = RectBivariateSpline(self.vgs, self.vds, val)
                return f(vgs_val, self.vds).reshape(-1)


def get_intersection(array1, array2, x_array):
    i = np.where(np.isclose(x_array, np.argmin(abs(array1 - array2))))
    return i, x_array[i]


class device:
    def __init__(self, vgs = -1, vds = -1, vsb = -1,
                       vsg = -1, vsd = -1,
                       fins = -1, length = -1,
                       gm  = -1, cdd = -1, vth = -1,
                       gds = -1, id = -1, cgg = -1):
        # ---------------------------------------
        self.vgs = vgs
        self.vds = vds
        self.vsb = vsb
        self.vsd = vsd
        self.vsg = vsg
        # ---------------------------------------
        self.fins = fins
        self.len = length
        # ---------------------------------------
        self.gm = gm
        self.gds = gds
        self.id = id
        self.cdd = cdd
        self.vth = vth
        self.cgg = cgg
