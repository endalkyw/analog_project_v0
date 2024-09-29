from LUT.read import lut
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from spice.mos_par import *
from LUT.fetch_ import *
import os
from tools.output_file import clear_output_files
from tools.log_file import *
from spice.parse_funcs import extract_between_x_and_y
from datetime import datetime
import pandas as pd



def choose_the_best_ncm():
   sch_data = pd.read_csv('outputs/nmos_cm.csv')
   cm_primitives = {}
   
   for fl in files:
       if "nmos_cm" in fl and ".csv" in fl:
           data = pd.read_csv(os.path.join(path,fl))
           id_error =  np.abs((1/len(data["i_d"]))*np.sum((data["i_d"] - sch_data["i_d"])/sch_data["i_d"]))
           gm_error =  np.abs((1/len(data["gm"]))*np.sum((data["gm"] - sch_data["gm"])/sch_data["gm"]))
           gds_error =  np.abs((1/len(data["gds"]))*np.sum((data["gds"] - sch_data["gds"])/sch_data["gds"]))
           cdd_error =  np.abs((1/len(data["cdd"]))*np.sum((data["cdd"] - sch_data["cdd"])/sch_data["cdd"]))
           
           g_metrics = {}
           try:
               with open(os.path.join(path,fl.split(".")[0])+".info", 'r') as file:
                   for line in file:
                       key, values = line.strip().split(':',1)
                       g_metrics[key] = float(values)
           except:
               g_metrics = {'Area, nm^2': 0, 'Aspect_ratio': 0, 'Fins': 0, 'Instances': 0, 'Nets': 0}
               
           # print(g_metrics)
           cm_primitives[fl] = [id_error, gm_error, gds_error, cdd_error, g_metrics["Area, nm^2"], g_metrics["Aspect_ratio"]]
           metrics = ["id", "gm", "gds", "cdd", "area", "aspsect_ratio"]
    
#    for key, item in cm_primitives.items():
#     print(key, item)
   
   weights  = [0.6, 0.05, 0.24, 0.1, 0.00001, 0.01]
   result   = {}
   for keys, cm in cm_primitives.items():
       res = np.dot(weights, cm)
       result[keys] = res
   
   res_sorted = dict(sorted(result.items(), key=lambda item: item[1]))
   min_key = ""
   min_val = 1e12
   for key, item in res_sorted.items():
       if item < min_val and item!=0:
           min_val = item
           min_key = key
   
   print(min_key, res_sorted[min_key])
   return min_key

def choose_the_best_pcm():
   sch_data = pd.read_csv('outputs/pmos_cm.csv')
   cm_primitives = {}
   
   for fl in files:
       if "pmos_cm" in fl and ".csv" in fl:
           data = pd.read_csv(os.path.join(path,fl))
           id_error =  np.abs((1/len(data["i_d"][22:]))*np.sum((data["i_d"][22:] - sch_data["i_d"])/sch_data["i_d"][22:]))
           gm_error =  np.abs((1/len(data["gm"][22:]))*np.sum((data["gm"][22:] - sch_data["gm"])/sch_data["gm"][22:]))
           gds_error =  np.abs((1/len(data["gds"][22:]))*np.sum((data["gds"][22:] - sch_data["gds"])/sch_data["gds"][22:]))
           cdd_error =  np.abs((1/len(data["cdd"][22:]))*np.sum((data["cdd"][22:] - sch_data["cdd"])/sch_data["cdd"][22:]))
           
           g_metrics = {}
           try:
               with open(os.path.join(path,fl.split(".")[0])+".info", 'r') as file:
                   for line in file:
                       key, values = line.strip().split(':',1)
                       g_metrics[key] = float(values)
           except:
               g_metrics = {'Area, nm^2': 0, 'Aspect_ratio': 0, 'Fins': 0, 'Instances': 0, 'Nets': 0}
               
           cm_primitives[fl] = [id_error, gm_error, gds_error, cdd_error, g_metrics["Area, nm^2"], g_metrics["Aspect_ratio"]]
           metrics = ["id", "gm", "gds", "cdd", "area", "aspsect_ratio"]
   
#    for key, item in cm_primitives.items():
#      print(key, item)
   
   weights  = [0.6, 0.05, 0.24, 0.1, 0.00001, 0.01]
   result   = {}
   for keys, cm in cm_primitives.items():
       res = np.dot(weights, cm)
       result[keys] = res
   
   res_sorted = dict(sorted(result.items(), key=lambda item: item[1]))
   min_key = ""
   min_val = 1e12
   for key, item in res_sorted.items():
       if item < min_val and item!=0:
           min_val = item
           min_key = key
   
   print(min_key, res_sorted[min_key])
   return min_key

def choose_the_best_dp():
   sch_data = pd.read_csv('outputs/nmos_dp.csv')
   dp_primitives = {}

   for fl in files:
       if "nmos_dp" in fl and ".csv" in fl:
        data = pd.read_csv(os.path.join(path,fl))
        #   print(sch_data["id_0"][305:310])
        #   print(data["id_0"][305:310])
           
        # plt.plot(data["gm"], 'k-')
        # plt.plot(sch_data["gm"], 'r--')
        # plt.savefig("trial.png")
        
        ni = 22
        id_0_error =  np.abs((1/len(data["id_0"][ni:]))*np.sum((data["id_0"][ni:] - sch_data["id_0"])/sch_data["id_0"][ni:]))
        id_1_error =  np.abs((1/len(data["id_1"][ni:]))*np.sum((data["id_1"][ni:] - sch_data["id_1"])/sch_data["id_1"][ni:]))
        gm_error  =   np.abs((1/len(data["gm"][ni:]))*np.sum((data["gm"][ni:] - sch_data["gm"])/sch_data["gm"][ni:]))
        gds_error =  np.abs((1/len(data["gds"][ni:]))*np.sum((data["gds"][ni:] - sch_data["gds"])/sch_data["gds"][ni:]))
        cdd_error =  np.abs((1/len(data["cdd"][ni:]))*np.sum((data["cdd"][ni:] - sch_data["cdd"])/sch_data["cdd"][ni:]))

        g_metrics = {}
        try:
            with open(os.path.join(path,fl.split(".")[0])+".info", 'r') as file:
                for line in file:
                    key, values = line.strip().split(':',1)
                    g_metrics[key] = float(values)
        except:
            g_metrics = {'Area, nm^2': 0, 'Aspect_ratio': 0, 'Fins': 0, 'Instances': 0, 'Nets': 0}
            
        dp_primitives[fl] = [id_0_error, id_1_error, gm_error, gds_error, cdd_error, g_metrics["Area, nm^2"], np.abs(1-g_metrics["Aspect_ratio"])]
        metrics = ["id_0", "id_1", "gm", "gds", "cdd", "area", "aspsect_ratio"]
   
#    for key, item in dp_primitives.items():
#      print(key, item)
   
   weights  = [0.6, 0.6, 0.8, 0.24, 0.1, 0.00001, 40]
   result   = {}
   for keys, dp in dp_primitives.items():
       res = np.dot(weights, dp)
       result[keys] = res
   
   res_sorted = dict(sorted(result.items(), key=lambda item: item[1]))
   min_key = ""
   min_val = 1e12
   for key, item in res_sorted.items():
       if item < min_val and item!=weights[6]:
           min_val = item
           min_key = key
   
   print(min_key, res_sorted[min_key])
   return min_key




def main():
    ncm = choose_the_best_ncm()
    pcm = choose_the_best_pcm()
    ndp = choose_the_best_dp()


# def design(ncm, ndp, pcm):
#     d_ncm = pd.read_csv(ncm)
#     d_pcm = pd.read_csv(pcm)
#     d_ndp = pd.read_csv(ndp)

#     vdd = 1.2
#     TE =[13, 22, 18]
#     vds_1 = vdd/3
#     cdd_1, cdd_2 = 0

#     # NMOS DP
#     vgs_1 = d_ndp["vg1_vals"] - d_ndp["vs_vals"]
#     vds_1 = d_ndp["vd1_vals"] - d_ndp["vs_vals"]
#     gm_1  = d_ndp["gm"]
    
#     # PMOS CM
#     # NMOS CM





if __name__ == "__main__":
    main()
    # radial_spyder_web(cm_primitives, metrics)





# def lookup(param,  file, n):
#     df  = pd.read_csv(file)
#     col = 