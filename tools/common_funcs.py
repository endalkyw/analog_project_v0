import numpy as np

def prime_check(num):
    prime = True
    if num < 2:
        prime = False
        return num+1
    
    for i in range(2, int(np.sqrt(num)) + 1):
        if num % i == 0:
            return num
    
    return num+1
