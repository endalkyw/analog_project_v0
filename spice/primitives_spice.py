from LUT.read import lut
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from spice.mos_par import *
from spice.parse_funcs import *
from LUT.fetch_ import *
import os
from tools.output_file import clear_output_files
from tools.log_file import *
from tools.timing import *
import pandas as pd
from scipy.interpolate import CubicSpline
import re

output_dir = os.path.abspath("outputs")

# create dspf without parasitics
def create_cm_spice(fins_0, fins_1, len_01, type, file_name):
    p = params()
    subckt_name = file_name.split('.')[0]
    m0 = p.get_mos_string("m0", d = "d0",  g = "d0",  s = "s",   b = "s",   type = type, fins = fins_0, stack = len_01)
    m1 = p.get_mos_string("m1", d = "d1",  g = "d0",  s = "s",   b = "s",   type = type, fins = fins_1, stack = len_01)
    
    if type == "nfet":
         name = "nmos"
    elif type == "pfet":
         name = "pmos"

    subckt = [
    f".subckt {subckt_name} d0 d1 s",
    m0,
    m1,
    f".ends {subckt_name}"
    ]

    subckt_string = " \n".join(subckt)
    with open(os.path.join(output_dir, file_name), 'w') as file:
        file.write(subckt_string)

def create_dp_spice(fins_01, len_01, type, file_name):
    p = params()
    subckt_name = file_name.split('.')[0]
    m0 = p.get_mos_string("m0", d = "d0",  g = "g0",  s = "s",   b = "b",   type = type, fins = fins_01, stack = len_01)
    m1 = p.get_mos_string("m1", d = "d1",  g = "g1",  s = "s",   b = "b",   type = type, fins = fins_01, stack = len_01)
    
    if type == "nfet":
         name = "nmos"
    elif type == "pfet":
         name = "pmos"

    subckt = [
    f".subckt {subckt_name} b d0 d1 g0 g1 s",
    m0,
    m1,
    f".ends {subckt_name}"
    ]

    subckt_string = " \n".join(subckt)
    with open(os.path.join(output_dir, file_name), 'w') as file:
        file.write(subckt_string)

# list all other primitives here ...    
