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
from five_transistor_spice import get_ota_specs
from scipy.optimize import minimize
from design_ota import *
from tools.timing import *
from tools.log_file import *
import re
import gurobipy as gp
from gurobipy import GRB

# -------------------------------------
gm_1 = gm_3 = gm_5 = l_1  = l_3 = c_self = Itail = 0
l_5 = cdd_3 = cdd_5 = vds_0 = vds_1 = vsd_2 = it = 0
# -------------------------------------

t_spec = {
  "gain": 20,
  "ugf": 10e6,
  "cmrr": 20,
  "sr": 1,
  "p": 100e-6,
  "bw": 1e6,
  "cl": 4e-12,
  "vdd": 1.2
}


def initialize(gbw_tol = 0):
    ota = Five_T_OTA()
    params = {
    "GBW_min": t_spec["ugf"] + gbw_tol,    # in Hz
    "Ao_min": t_spec["gain"],       # in dB
    "Po_max": t_spec["p"],   # in W
    "load_C": t_spec["cl"],    # in F
    "supp_V": 1.2,      # in V
    "fin_ref": 10,
    "SR":t_spec["sr"]
    }
    ota.set_target_params(**params)
    return ota


def gm_id_optimizer(model, where):
    print("ese")
    # xk
    #
    # ota = initialize(0)
    # global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, it, spec_i, Itail, cgg_3, cgg_5, vds_0, vds_1, vsd_2
    #
    # vcm = 0.6
    # length = 1  # 14e-9
    # vds_1 = 1.2 / 3
    #
    # fins, Is, other_res = ota.design_ota(xk, 0.6, vds_1, [1, 1, 1])
    # gm_1 = other_res["gm_0"]
    # gm_3 = other_res["gm_1"]
    # gm_5 = other_res["gm_2"]
    # l_1 = other_res["l_0"]
    # l_3 = other_res["l_1"]
    # l_5 = other_res["l_2"]
    # cdd_3 = other_res["cdd_1"]
    # cdd_5 = other_res["cdd_2"]
    #
    # Itail = other_res["Itail"]
    # cgg_3 = other_res["cgg_1"]
    # cgg_5 = other_res["cgg_2"]
    #
    # vds_0 = other_res["vds_0"]
    # vds_1 = other_res["vds_1"]
    # vsd_2 = other_res["vsd_2"]
    #
    # c_self = (cgg_3) / 2 + cdd_3 + cdd_5
    #
    # it += 1
    # f = "optimization.csv"
    #
    # Gain = (con_gain(xk, l_3, l_5) + t_spec['gain'])[0]
    # UGF = (other_res['ugf'])[0]
    # BW = (con_bw(xk, gm_3, l_3, l_5, cdd_3, cdd_5) + t_spec['bw'])[0]
    # Power = (power_func(xk, gm_3, 1.2))[0]
    # CMRR = (con_cmrr(xk, l_1, l_3, l_5) + t_spec['cmrr'])[0]
    # SR = (con_sr(xk, gm_3, c_self) + t_spec['sr'])[0]
    # Pole_2 = (con_p2(xk, gm_3, cgg_5) + 2.7 * t_spec['ugf'])[0]
    # vds = [vds_0, vds_1, vsd_2]
    # vds_sat = [2 / xk[0], 2 / xk[1], 2 / xk[2]]
    # TEs = xk
    # Fins = fins
    # I = [Is[0], Itail[0]]
    #
    # header = f"it,Gain,UGF,BW,Pole_2,Power,CMRR,SR,vds_0,vds_1,vds_2,vds_sat_0,vds_sat_1,vds_sat_2,TEs_0,TEs_1,TEs_2,Fins_0,Fins_1,Fins_2,I_s,I_tail"
    # line = f"{it},{Gain},{UGF},{BW},{Pole_2},{Power},{CMRR},{SR},{vds[0]},{vds[1]},{vds[2]},{vds_sat[0]},{vds_sat[1]},{vds_sat[2]},{TEs[0]},{TEs[1]},{TEs[2]},{Fins[0]},{Fins[1]},{Fins[2]},{I[0]},{I[1]}"
    #
    # if it == 1:
    #     write_log_file(f, header, 'w')
    #
    # write_log_file(f, line, 'a')
    #
    # def ch(a):
    #     if a > 0:
    #         return True
    #     return False
    #
    # print("f gain   cmrr    sr  pole2   sat0    sat1    sat2")
    # print(ch(con_gain(xk, l_3, l_5)), ch(con_cmrr(xk, l_1, l_3, l_5)), ch(con_sr(xk, gm_3, c_self)),
    #       ch(con_p2(xk, gm_3, cgg_5)),
    #       ch(con_vdsat0(xk, vds_0)), ch(con_vdsat1(xk, vds_1)), ch(con_vdsat2(xk, vsd_2)))
    #
    # # print(con_p2(xk, gm_3, cgg_5))
    # # print((xk[2]/xk[1])*(gm_3/(2*np.pi*cgg_5)) - t_spec["ugf"])
    # # print((xk[2]/xk[1])*(gm_3/(2*np.pi*cgg_5)) - t_spec["ugf"])
    # # print(" ")
    #
    # # write_log_file(f, f" iteration {it} ----", 'a')
    # # write_log_file(f, f" Gain    {con_gain(xk, l_3, l_5) + t_spec['gain']}", 'a')
    # # write_log_file(f, f" UGF     {other_res['ugf']}", 'a')
    # # write_log_file(f, f" BW      {con_bw(xk, gm_3, l_3, l_5, CL, cdd_3, cdd_5)+ t_spec['bw']}", 'a')
    # # write_log_file(f, f" Power   {power_func(xk, gm_3, 1.2)}", 'a')
    # # write_log_file(f, f" CMRR    {con_cmrr(xk, l_1, l_3, l_5) + t_spec['cmrr']}", 'a')
    # # write_log_file(f, f" SR      {con_sr(xk,gm_3,CL, c_self) + t_spec['sr']}", 'a')
    # # write_log_file(f, f" Pole_2  {con_p2(xk,cgg_5,Itail) + 1.5*t_spec['ugf']}", 'a')
    # # write_log_file(f, f" vds     {vds_0} {vds_1}, {vsd_2}", 'a')
    # # write_log_file(f, f" vds_sat {2/xk[0]}, {2/xk[1]}, {2/xk[2]}", 'a')
    # # write_log_file(f, f" ", 'a')
    # # write_log_file(f, f" TEs     {xk}", 'a')
    # # write_log_file(f, f" Fins    {fins}", 'a')
    # # write_log_file(f, f" Is      {Is}   Itail {Itail}", 'a')
    # # # write_log_file(f, f" cdd_3  {cdd_3}", 'a')
    # # # write_log_file(f, f" cdd_5  {cdd_5}", 'a')
    # # write_log_file(f, f"--------------------", 'a')


def run_optimization_gurobi():
    global gm_1, gm_3, gm_5, l_1, l_3, l_5, cdd_3, cdd_5, it, spec_i, Itail, cgg_3, cgg_5,vds_0, vds_1, vsd_2

    # Create a new model
    model = gp.Model("nonlinear_optimization")
    model.Params.NonConvex = 2

    # Add decision variables with bounds (equivalent to TE0 in SciPy)
    x1 = model.addVar(lb=5,  ub=20, name="x1")  # Corresponds to TE0[0]
    x2 = model.addVar(lb=18, ub=25, name="x2")  # Corresponds to TE0[1]
    x3 = model.addVar(lb=5,  ub=20, name="x3")  # Corresponds to TE0[2]

    model._x1 = x1
    model._x2 = x2
    model._x3 = x3

    ts = [x1, x2, x3]
    # Set the objective function (similar to power_func)
    # Replace `power_func(x)` with its equivalent formulation for Gurobi variables
    model.setObjective(2*gm_3*t_spec["vdd"]/x2, GRB.MINIMIZE)

    # Add the constraints (equivalent to the `cons` in SciPy)
    # Each of these should be adapted to Gurobi's constraint format
    model.addConstr((2*gm_3/(x2*(t_spec["cl"] + c_self)))*1e-6 - t_spec["sr"] >= 0, "sr_constraint")
    model.addConstr(20*np.log10(x2/(l_3+l_5)) - t_spec["gain"] >= 0, "gain_constraint")
    model.addConstr(20*np.log10((x1*x2)/(l_1*(l_3+l_5)))-t_spec["cmrr"] >= 0, "cmrr_constraint")
    model.addConstr((x2/x1)*((gm_3)/(2*np.pi*cgg_5)) - 2.7*t_spec["ugf"] >= 0, "p2_constraint")
    model.addConstr(vds_0 - 2/x1 >= 0, "vdsat0_constraint")
    model.addConstr(vds_1 - 2/x2 >= 0, "vdsat1_constraint")
    model.addConstr(vsd_2 - 2/x3 >= 0, "vdsat2_constraint")

    # Set optimization parameters (similar to options in SciPy)
    model.Params.OutputFlag = 1  # Display output
    model.Params.MaxIter = 1000  # Max number of iterations
    model.Params.OptimalityTol = 1e-9  # Convergence tolerance

    # Solve the optimization problem
    model.optimize(gm_id_optimizer)

    # Retrieve the results
    if model.status == GRB.OPTIMAL:
        x1_val = x1.X
        x2_val = x2.X
        x3_val = x3.X
        print(f"Optimal solution found: x1={x1_val}, x2={x2_val}, x3={x3_val}")
    else:
        print("No optimal solution found")

    return model

@timing_decorator
def main():
    run_optimization_gurobi()


if __name__ == "__main__":
    main()



