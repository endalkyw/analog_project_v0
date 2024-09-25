import os
import subprocess
import time
from functools import wraps
import pandas as pd
import numpy as np

# Run a simple command
# exit_status = os.system('module load hspice/2023.03')
# exit_status = os.system('hspice -v')

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


def simulate_nmos_cm(target_file, name ,output_dir):
   # target file can be .sp file or .dspf file
   # output file 
   template_filepath = "testbenches/nmos_cm_tb_template.txt"
   with open(template_filepath,'r') as file:
      content = file.read()

   vd0 = np.linspace(0,0.8,20)
   vd1 = np.linspace(0,0.8,20)
   v   = []

   for i in range(len(vd0)):
      for j in range(len(vd1)):
         v.append("+ "+str(vd0[i])+" "+str(vd1[j]))
         volts = "\n".join(v)
  

   values   = {"target_file": target_file, "name":name, "sources":volts}
   content_ = content.format(**values)
   
   
   os.system('mkdir '+output_dir)
   with open(output_dir+"/nmos_cm_tb.sp", 'w') as file:
       file.write(content_)
	

   exit_status = os.system('hspice -i '+output_dir+'/nmos_cm_tb.sp -o temp/')
   print(exit_status)


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    
# Function to convert strings to floats, replacing 'failed' with 0
def convert_to_float(arr):
    # Use np.vectorize to apply a function to each element of the array
    to_float = np.vectorize(lambda x: float(x) if is_float(x) else 0)
    return to_float(arr)


def parse_output(file_name, csv_file):
    def find_RandC(vreal,vimag, ireal, iimag, freq):
        w = freq*2*np.pi
        v = vreal + vimag*1j
        i = ireal + iimag*1j
        z = v/i
        RC = z.imag/(z.real*w)
        R  = z.imag*(1+(w*RC)**2)/(w*RC)
        C  = RC/R
        return R, C
    
    # for the dc current measurement
    with open (file_name+"/nmos_cm_tb.ms0","r") as file:
       content_1 = file.read()
       
    # for the ac voltage and current measurements 
    with open (file_name+"/nmos_cm_tb.ma0","r") as file:
       content_2 = file.read()   
       
    lines_1 = content_1.splitlines()
    lines_2 = content_2.splitlines()
    
    data_1 = []
    for i in range(4,len(lines_1),2):
      data_1.append(lines_1[i].split()+[lines_1[i+1].split()[0]])
    
    data_2 = []
    for i in range(5,len(lines_2),3):
      line = lines_2[i].split() + lines_2[i+1].split()
      data_2.append(line)
    
    n_data_1 = convert_to_float(np.array(data_1)) 
    n_data_2 = convert_to_float(np.array(data_2))
    
    data = np.concatenate((n_data_2, n_data_1[:,[-2,-1]].reshape(len(n_data_1),2)),-1)
    
    RC = []
    for i in range(len(data)):
        R, C = find_RandC(data[i,3],data[i,4],data[i,5],data[i,6],10e3)
        RC.append([R,C])
    
    to_write_data = np.concatenate((data[:,[1,2,8,7]],RC), axis=1) 
    
    df = pd.DataFrame(to_write_data, columns = ["Vd0","Vd1","Id0","Id1","Rout","Cout"])
    df.to_csv("output/"+csv_file, index=False)



@timing_decorator
def main():
  for i in range(5):
    name = "nmos_cm_"+str(i)
    #simulate_nmos_cm("../circuits/nmos_cm/"+name+".pex.dspf",name,"output")	
    simulate_nmos_cm("../circuits/nmos_cm/"+name+".sp",name,"output")	
    parse_output("temp", name+".csv")

main()
