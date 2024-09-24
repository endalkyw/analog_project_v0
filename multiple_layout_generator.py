import gdstk
from layout_gen.primitives.differential_pair import differential_pair
from layout_gen.utilities.elements_utils import *
from layout_gen.primitives.current_mirror import current_mirror
from layout_gen.core import create_base_layout, create_fabric
import math
import time
from functools import wraps

# patterns 
# 0. CL: (no diffusion break) -- AAAABBBB
# 2. ID: (no diffusion break) -- AABBAABB
# 4. CC: (no diffusion break) -- AABBBBAA

# 1. CL: (diffusion break   ) -- AAAA BBBB
# 3. ID: (diffusion break)    -- A B A B A B A B
# 5. CC: (diffusion break)    -- AA BB BB AA


def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the original function
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
        return result  # Return the result of the original function
    return wrapper

@timing_decorator
def generate_cm_layouts(fins_0: int, fins_1: int, stack: int, type, source_first=True):
    def generate(fins, nf, m, stack, pattern, con, type):
        if type == "N":
            name = "nmos_cm"
        else:
            name = "pmos_cm"
        m0 = Mos({'id': 'A', 'fins': fins, 'fingers': nf, 'multiplier': m, 'stack': stack, 'mos_type': type})
        m1 = Mos({'id': 'B', 'fins': fins, 'fingers': nf, 'multiplier': m, 'stack': stack, 'mos_type': type})

        cell_name = f"{name}_{str(fins)}x{str(nf)}x{m}_{str(con[0]) + str(con[0]) + str(con[0])}_{str(pattern)}"
        c1 = current_mirror(m0, m1, cell_name)
        c1.create_layout(pattern, ("d0", "d1", "s"), con=con, fabric_on=True)
        write_gds(c1.cell, cell_name)
    ff = get_ff(fins_0)
    for f in ff:
        fingers = f[0]
        fins = f[1]

        mult = []
        if fingers < 30:
            range = [1]
            for i in range:
                if not fingers % i:
                    mult.append(i)

        elif 30 < fingers < 60:
            range = [1, 2, 3]
            for i in range:
                if not fingers % i:
                    mult.append(i)

        elif fingers > 60:
            range = [2, 3, 4]
            for i in range:
                if not fingers % i:
                    mult.append(i)
        #
        for m in mult:
        #    fingers = fingers//m
        #    if 2<= fingers < 10 and 5 < fins <= 10:
        #        wires = [[1, 1, 1], [2, 2, 2]]
        #    elif 10 < fingers and fins > 10:
        #        wires = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        #    else:
        #        wires = [[1, 1, 1]]


           wires = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
           for c in wires:
                if fingers % 2:  # if it's odd fingers/2 has reminder   1 and 3
                    generate(fins, fingers, m, stack, 1, c, "N")
                    # generate(fins, fingers, m, stack, 3, c, "N")

                elif not fingers % 4:  # even and divisible by 4 (no diffusion break is needed: 0, 2, 4)
                    generate(fins, fingers, m, stack, 0, c, "N")
                    generate(fins, fingers, m, stack, 2, c, "N")
                    generate(fins, fingers, m, stack, 4, c, "N")

                else:  # even number but not divisible by 4   0, 2, 5
                    generate(fins, fingers, m, stack, 0, c, "N")
                    generate(fins, fingers, m, stack, 2, c, "N")
                    # generate(fins, fingers, m, stack, 5, c, "N")






@timing_decorator
def generate_dp_layouts(fins_01: int, len: float, type, source_first=True):
    if type == "N":
        name = "nmos_dp"
    else:
        name = "pmos_dp"

    ff = get_ff(fins_01)
    print(ff)
  
    for f in ff:
            fingers = f[0]
            fins    = f[1]
            m0 = Mos({'id': 'A', 'fins': fins, 'fingers': fingers, 'multiplier': 1, 'mos_type': type})
            m1 = Mos({'id': 'B', 'fins': fins, 'fingers': fingers, 'multiplier': 1, 'mos_type': type})
            
            if fingers % 2:        # if it's odd fingers/2 has reminder    
                c1 = differential_pair(m0, m1, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(1))
                c1.create_layout(1, ("d0", "d1","g0","g1" ,"s","b"), 0.2, 1, True)
                write_gds(c1.cell, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(1))
                
                c2 = differential_pair(m0, m1, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(3))
                c2.create_layout(3, ("d0", "d1","g0","g1" ,"s","b"), 0.2, 1, True)
                write_gds(c2.cell, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(3))

            elif not fingers % 4:  # even and divisible by 4 (no diffusion break is needed: 0, 2, 4)
                c1 = differential_pair(m0, m1, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(0))
                c1.create_layout(pattern=0, labels=("d0", "d1","g0","g1" ,"s","b"), alpha=0.2, row_number=1, fabric_on=True)
                # show_layout(c.cell,(1,0.5))
                write_gds(c1.cell, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(0))

                c2 = differential_pair(m0, m1, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(2))
                c2.create_layout(pattern=2, labels=("d0", "d1","g0","g1" ,"s","b"), alpha=0.2, row_number=1, fabric_on=True)
                # show_layout(c.cell,(1,0.5))
                write_gds(c2.cell, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(2))

                c3 = differential_pair(m0, m1, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(4))
                c3.create_layout(pattern=4, labels=("d0", "d1","g0","g1" ,"s","b"), alpha=0.2, row_number=1, fabric_on=True)
                # show_layout(c.cell,(1,0.5))
                write_gds(c3.cell, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(4))

            else: # even number but not divisible by 4
                c1 = differential_pair(m0, m1, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(0))
                c1.create_layout(pattern=0, labels=("d0", "d1","g0","g1" ,"s","b"), alpha=0.2, row_number=1, fabric_on=True)
                write_gds(c1.cell, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(0))
                
                c2 = differential_pair(m0, m1, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(2))
                c2.create_layout(pattern=2, labels=("d0", "d1","g0","g1" ,"s","b"), alpha=0.2, row_number=1, fabric_on=True)
                write_gds(c2.cell, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(2))

                c3 = differential_pair(m0, m1, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(5))
                c3.create_layout(pattern=5, labels=("d0", "d1","g0","g1" ,"s","b"), alpha=0.2, row_number=1, fabric_on=True)
                write_gds(c3.cell, name+"_"+str(fingers)+"x"+str(fins)+"_"+str(5))


def lv_nmos_cm():
    ... 

# ----------------------------------------------------

def get_ff(total_number_fins): # get fingers and fins
    factors = set()
    for i in range(1, int(math.sqrt(total_number_fins)) + 1):
        if total_number_fins % i == 0:
            factors.add(i)
            factors.add(total_number_fins // i)

    fingers = list(sorted(factors))
    fins = [int(total_number_fins / finger) for finger in fingers]

    ff = list(zip(fingers,fins))
    return ff[1:-1]


