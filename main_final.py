import os
from multiple_layout_generator import *
from pex.extract import *
import sys


def main():
    # Check if there are enough command line arguments
    # if len(sys.argv) < 2:
    #     print("Usage: python script.py <arg1> <arg2> ...")
    #     sys.exit(1)
    #
    # # Access the arguments
    # script_name = sys.argv[0]
    # arguments = sys.argv[1:]  # All arguments except the script name
    #
    # print(f"Arguments: {arguments}")
    arguments = ["-gen","-pex"]
    # arguments = ["-gen"]
    # arguments = ["-pex"]
    #
    if '-gen' in arguments:
        # Generate candidate layouts ----------------------------------------------------
        generate_cm_layouts(18, 18, 14e-9, 'N', source_first=True)
        generate_cm_layouts(8, 8, 14e-9, 'P', source_first=True)
        # generate_dp_layouts(12, 14e-9, 'N', source_first=True)

    if '-pex' in arguments:
        # Run PEX -----------------------------------------------------------------------
        path = 'outputs/'
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        for i,layouts in enumerate(files):
            file_name = path+layouts.split('.')[0]
            failed_pex = 0
            try:
                pex(file_name)
                print(i, file_name, "done!")
            except:
                failed_pex += 1
                print(f"{file_name} can not be extracted")

        print(f"{failed_pex} pex failed!")

if __name__ == "__main__":
    main()