from joblib import Memory
import numpy as np
from LUT.read import lut as lut_spectre   # for spectre
from LUT.read_2 import lut as lut_hspice  #

import os
base_dir = os.path.dirname(os.path.abspath(__file__))

cachedir = './cache'  # Defines the directory to store cache
memory = Memory(cachedir, verbose=0)

@memory.cache
def fetch_data_1():
    VGS = np.linspace(0, 0.8, 41)
    VDS = np.linspace(0, 0.8, 41)
    VSB = np.array([0])
    LEN = np.array([1,2,3,4])
    FIN = np.array([2,5,10])
    n_file = os.path.join(base_dir, "mos_data/rvt_2/rvt_nfet.csv")
    p_file = os.path.join(base_dir, "mos_data/rvt_2/rvt_pfet.csv")
    return lut_hspice(VGS, VDS, VSB, LEN, FIN, n_file, p_file)

@memory.cache
def fetch_data_2():
    VGS = np.linspace(0, 0.8, 41)
    VDS = np.linspace(0, 0.8, 41)
    VSB = np.array([0])
    LEN = np.array([14e-9])
    FIN = np.array([2, 6, 10, 20, 40])
    n_file = os.path.join(base_dir, "mos_data/rvt_nf_1/nfet_data.csv")
    p_file = os.path.join(base_dir, "mos_data/rvt_nf_1/pfet_data.csv")
    return lut_spectre(VGS, VDS, VSB, LEN, FIN, n_file, p_file) 



if __name__ == "__main__":
    fetch_data_1()