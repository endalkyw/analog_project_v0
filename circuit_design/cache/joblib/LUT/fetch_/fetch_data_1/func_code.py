# first line: 12
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
