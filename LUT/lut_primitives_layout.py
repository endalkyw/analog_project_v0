import numpy as np
from scipy.interpolate import interp1d
from LUT.read import device
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline



# layout versions --------------------------------------------------------------------------------
def f_mod(x, a: float, b: float, c:float):
    y = b*x*(np.exp(a*x)-c**2)
    return y


def lut_modifier(fins, fingers, inp_func, par, a, b, c, tb):
    if par == "id":
       x_ = np.linspace(0, 40, 41)
       y_ = f_mod(x_, a, b, c)
       new_func = inp_func + y_

    elif par == "cdd":
        ...
    elif par == "gm":
        ...
    elif par ==  "gds":
        ...

    return new_func


def n_current_mirror_(fins,fingers, id_0, vds_1, fins_0, fins_1, len_01, tb):
    # vds_1, vgs_1, id_1, fins_1 -> m0
    # vds_0, vgs_0, id_0, fins_0 -> m1, len_01

    # initial guess values
    vds_0 = vgs_0 = 0.4

    # loop to find the right vgs and vds value that allows the current id_0 to flow
    for i in range(20):
        id_0_ = tb.lookup(par="id", len_val=len_01, fin_val=fins_0, type="n", vds_val=vds_0)
        f = interp1d(id_0_, tb.vgs)
        vgs_0 = f(id_0)
        vds_0 = vgs_0

    # calculating for the second transistor m1
    vgs_1 = vgs_0
    id_1_ = tb.lookup(par="id", len_val=len_01, fin_val=fins_1, type="n", vgs_val=vgs_1)
    f = interp1d(tb.vds, id_1_)
    id_1 = f(vds_1)

    m0 = device(vgs_0, vds_0, 0, fins_0, len_01, id=id_0)
    m1 = device(vgs_1, vds_1, 0, fins_1, len_01, id=id_1)

    return m0, m1


def n_differential_pair_(fins,fingers,id_s, vd_0, vd_1, fins_01, len_01, v_diff,  v_cm, tb):
    # vds_0, vgs_0 ------------------------> m0
    # vds_1, vgs_1 ------------------------> m1
    # fins_01, len_01, v_diff, v_cm, id_s
    vgs_0 = vgs_1 = 0
    vds_0 = vds_1 = 0
    id_0  = id_1  = 0
    e = 1e-8
    # initial guess values
    vds_0 = 0.45

    if vd_0 == vd_1:
        id_0 = id_1 = id_s / 2
        while True:
            # vgs_0 = v_cm - vs
            id_0_ = tb.lookup(par="id", len_val=len_01, fin_val=fins_01, type="n", vds_val=vds_0)
            f = CubicSpline(id_0_, tb.vgs)
            vgs_0 = f(id_0)
            vs = v_cm - vgs_0
            vds_new = vd_0 - vs

            if abs(vds_new - vds_0) < e:
                break

            vds_0 = vds_new
            vs = vd_0 - vds_0

        vgs_1 = vgs_0
        vds_1 = vds_0

    else:
        iter = 0
        while True:
            iter += 1
            if iter > 1000:
                print("Maximum iteration reached!")
                break

            vgs_0 = vgs_1 = v_cm - vs
            vds_0 = vd_0 - vs
            vds_1 = vd_1 - vs

            id_0 = tb.lookup(par="id", len_val=len_01, fin_val=fins_01, type="n", vgs_val=vgs_0, vds_val=vds_0)
            id_1 = tb.lookup(par="id", len_val=len_01, fin_val=fins_01, type="n", vgs_val=vgs_1, vds_val=vds_1)
            delta = id_s - (id_0 + id_1)

            print(f"{iter} --> {vgs_1=}, {vs=}")
            print(f"{delta =}")
            print(f"{delta/id_s =}")

            if abs(delta/id_s) < 0.01:
                break

            elif abs(delta/id_s) > 0.01 and delta/id_s < 0.1:
                vs -= 1e-4*np.sign((delta/id_s))

            elif abs(delta/id_s) > 0.1:
                vs -= 1e-3*np.sign((delta/id_s))

    gm_0 = gm_1   = tb.lookup(par="gm", len_val=len_01, fin_val=fins_01, type="n", vds_val=vds_0, vgs_val=vgs_0)
    gds_0 = gds_1 = tb.lookup(par="gds", len_val=len_01, fin_val=fins_01, type="n", vds_val=vds_0, vgs_val=vgs_1)
    cdd_0 = cdd_1 = tb.lookup(par="cdd", len_val=len_01, fin_val=fins_01, type="n", vds_val=vds_0, vgs_val=vgs_0)

    m0 = device(vgs_0, vds_0, 0, fins_01, len_01, id=id_0, gm=gm_0, gds=gds_0, cdd=cdd_0)
    m1 = device(vgs_1, vds_1, 0, fins_01, len_01, id=id_1, gm=gm_1, gds=gds_1, cdd=cdd_1)
    return m0, m1


def p_current_mirror_(fins,fingers,vdd, id_0, vd_1, fins_01, len_01, tb):
    # vsd_1, vsg_1, id_1, fins_1 -> m0
    # vsd_0, vsg_0, id_0, fins_0 -> m1, len_01

    # initial guess values
    vsd_0 = 0.4

    for i in range(20):
        id_0_ = -1*tb.lookup(par="id", len_val=len_01, fin_val=fins_01, type="p", vds_val=vsd_0)
        f = interp1d(id_0_, tb.vgs)
        vsg_0 = f(id_0)
        vsd_0 = vsg_0

    # for m1
    vsd_1 = vdd - vd_1
    vsg_1 = vsg_0
    id_1 = -1*tb.lookup(par="id", len_val=len_01, fin_val=fins_01, type="p", vds_val=vsd_1, vgs_val=vsg_1)


    gm_0 = gm_1   = tb.lookup(par="gm", len_val=len_01, fin_val=fins_01, type="n", vds_val=vsd_0, vgs_val=vsg_0)
    gds_0 = gds_1 = tb.lookup(par="gds", len_val=len_01, fin_val=fins_01, type="n", vds_val=vsd_0, vgs_val=vsg_1)
    cdd_0 = cdd_1 = tb.lookup(par="cdd", len_val=len_01, fin_val=fins_01, type="n", vds_val=vsd_0, vgs_val=vsg_0)

    m0 = device(vsg=vsg_0, vsd=vsd_0, vsb=0, fins=fins_01, length=len_01, id=id_0, gm=gm_0, gds=gds_0, cdd=cdd_0)
    m1 = device(vsg=vsg_1, vsd=vsd_1, vsb=0, fins=fins_01, length=len_01, id=id_1, gm=gm_1, gds=gds_1, cdd=cdd_1)

    return m0, m1







