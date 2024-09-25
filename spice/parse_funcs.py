import numpy as np
import os

current_dir = os.path.dirname(__file__)




def extract_between_x_and_y(file_path):
    extracted_content = []
    capturing = False

    with open(file_path, 'r') as file:
        for line in file:
            # Capture the line if within the range
            if capturing:
            # Check if the line contains 'y' and stop capturing
               if line[0]=='y':
                 break
               extracted_content.append(line.strip())

            # Check if the line contains 'x' and start capturing
            if line[0]=='x' in line:
                capturing = True

    return extracted_content


def parse_data_1(f):
    with open(f, 'r') as file:
        data = file.read()


    lines = data.strip().splitlines()
    # Initialize lists for each column
    vds_val = []
    vgs_val = []
    i_1     = []
    i_2     = []
    v_mag   = []
    start   = 5
    step    = 3

    # Process each line with data
    for i in range(start, len(lines), step):
        vgs_val.append(safe_float(lines[i].split()[1]))
        vds_val.append(safe_float(lines[i].split()[2]))
        i_1.append(safe_float(lines[i].split()[3]))
        i_2.append(safe_float(lines[i+1].split()[0]))
        v_mag.append(safe_float(lines[i+1].split()[1]))
        
    # Create a numpy array with all columns
    data_array = np.column_stack([vgs_val, vds_val, i_1, i_2, v_mag])

    return data_array

def parse_data_2(f):
    with open(f, 'r') as file:
        data = file.read()


    lines = data.strip().splitlines()
    # Initialize lists for each column

    id0  = []
    id1  = []
    vg   = []
    start = 4
    step  = 2

    for i in range(start, len(lines), step):
        id0.append(safe_float(lines[i].split()[3]))
        id1.append(safe_float(lines[i+1].split()[0]))
        vg.append(safe_float(lines[i].split()[1]))
    new_data = np.column_stack([id0,id1])

    return new_data











# for 1
def parse_dp_data_ma0(f):
    with open(f, 'r') as file:
        data = file.read()


    lines = data.strip().splitlines()
    # Initialize lists for each column
    vd1_val = []
    vg1_val = []
    i_1     = []
    i_2     = []
    v_mag   = []
    start   = 5
    step    = 3

    # Process each line with data
    for i in range(start, len(lines), step):
        vd1_val.append(safe_float(lines[i].split()[1]))
        vg1_val.append(safe_float(lines[i].split()[2]))
        i_1.append(safe_float(lines[i].split()[3]))

        i_2.append(safe_float(lines[i+1].split()[0]))
        v_mag.append(safe_float(lines[i+1].split()[1]))
        
    # Create a numpy array with all columns
    data_array = np.column_stack([vd1_val, vg1_val, i_1, i_2, v_mag])
    return data_array

# for 2
def parse_dp_data_ms0(f):
    with open(f, 'r') as file:
        data = file.read()


    lines = data.strip().splitlines()
    # Initialize lists for each column

    id_0    = []
    id_1    = []
    start   = 4
    step    = 2

    for i in range(start, len(lines), step):
        id_0.append(safe_float(lines[i].split()[3]))
        id_1.append(safe_float(lines[i+1].split()[0]))

    new_data = np.column_stack([id_0, id_1])
    return new_data


def safe_float(string, alternative=1e-18):
    try:
        return float(string)
    except ValueError:
        return alternative