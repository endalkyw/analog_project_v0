from .common_libs import *

def write_cells(cells, filepath):
    
    lib = gdstk.Library(unit=1e-9, precision=1e-12)

    # check if the cells input is a list
    if not isinstance(cells, list):
        cells = [cells]    # Convert non-list input into a list
    
    for cell in cells:
        lib.add(cell)
    
    lib.write_gds(filepath)

