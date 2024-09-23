class polygon:
    def __init__(self, points, layer, data, id, text=""):
        self.points = points
        self.layer  = layer
        self.data   = data
        self.id     = id

        if [layer, data] == [15, 20] or [layer, data] == [16, 20]:
            self.orientation = ""
            self.mid = 0
            self.text = text
        else:
            self.mid_point = [(points[0][0] + points[1][0])/2, (points[1][1] + points[2][1])/2]
            if abs(points[0][0] - points[1][0]) > abs(points[1][1] - points[2][1]):
                self.orientation = "h"
                self.mid = (points[1][1] + points[2][1]) / 2
                self.area = abs(points[0][0]-points[1][0])*abs(points[1][1]-points[2][1])
            elif abs(points[0][0] - points[1][0]) < abs(points[1][1] - points[2][1]):
                self.orientation = "v"
                self.mid = (points[0][0] + points[1][0]) / 2
                self.area = abs(points[0][0]-points[1][0])*abs(points[1][1]-points[2][1])
            else:
                self.orientation = "s"
                self.mid = [(points[0][0] + points[1][0]) / 2, (points[1][1] + points[2][1]) / 2]
                self.area = abs(points[0][0]-points[1][0])*abs(points[1][1]-points[2][1])

        self.vt_box = []

class Net:
    def __init__(self):
        self.id     = []
        self.metals = []
        self.vias   = []
        self.label  = []
        self.diffs  = []
        self.cbs    = []
        self.polys  = []
        self.bps    = []


class net_parasitics:
    def __init__(self, net_name, res_list, cap_list):
        self.net_name = net_name
        self.res_list = res_list
        self.cap_list = cap_list


class params:
    param_dict = {"name": "MN0", "l": 14e-9, "fpitch": 48e-9, "nfin": 1,
                  "nf": 1, "nf_pex": 1, "par_nf": 1,
                  "asej": 1, "adej": 1, "psej": 1, "pdej": 1,
                  "sca": 1, "scb": 1, "scc": 1,
                  "lle_sa": 1, "lle_sb": 1,
                  "lle_nwa": 2e-6, "lle_nwb": 2e-6, "lle_nws": 2e-6, "lle_nwn": 2e-6,
                  "lle_rxrxa": 1, "lle_rxrxb": 1, "lle_rxrxs": 1e-06, "lle_rxrxn": 1,
                  "lle_pcrxs": 5.50e-8, "lle_pcrxn": 1.77e-7,
                  "lle_ctne": 1, "lle_ctse": 1, "lle_ctnw": 1, "lle_ctsw": 1,
                  "X": 1, "Y": 1}


class instance_x:
    def __init__(self):
        self.name = ""
        self.S = None
        self.D = None
        self.G = None
        self.B = None