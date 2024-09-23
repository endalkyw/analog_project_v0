import numpy as np


class Stick:
    def __init__(self, point_1: list, point_2: list):
        self.xi = point_1[0]
        self.yi = point_1[1]
        self.xf =  point_2[0]
        self.yf =  point_2[1]
        self.update()
        self.order()

    def update(self):
        if self.xi == self.xf:
            self.alignment = "V"
        elif self.yi == self.yi:
            self.alignment = "H"

        self.points = [[self.xi, self.yi],[self.xf,self.yf]]

        self.px = [self.xi, self.xf]
        self.py = [self.yi, self.yf]

    def order(self):
        temp = 0
        if self.xi > self.xf:
            temp = self.xf
            self.xf = self.xi
            self.xi = temp

        if self.yi > self.yf:
            temp = self.yf
            self.yf = self.yi
            self.yi = temp



def are_collinear(A, B):
    """Check if three points are collinear."""
    return np.cross(np.array(A.points[1]) - np.array(A.points[0]), np.array(B.points[0]) - np.array(A.points[0])) == 0


def join_collinear_sticks(s1, s2):
    i = [min(s1.xi,s2.xi), min(s1.yi,s2.yi)]
    f = [max(s1.xf,s2.xf), max(s1.yf,s2.yf)]
    return Stick(i,f)


def is_point_in_stick(point: list, stick):
    tol = 10
    if (abs(point[0] - stick.xi))<=tol and (stick.yi<=point[1]<=stick.yf): # vertical scenario
        return True
    elif (abs(point[1] - stick.yi))<=tol and (stick.xi<=point[0]<=stick.xf): # horizontal scenario
        return True

    return False

# A = Stick([0,0],[0,5],)
# B = Stick([0,3],[0,7])
# C = join_collinear_sticks(A,B)
#
# import matplotlib.pyplot as plt
#
# plt.plot(A.px,A.py,'r-')
# plt.plot(B.px,B.py,'--')
# plt.show(block=False)
# plt.pause(10)
#
# plt.plot(C.px,C.py,'k-')
# plt.show(block=False)
#
# plt.pause(10)