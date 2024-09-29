from pex.extract import *
from multiple_layout_generator import *
from tools.output_file import *

#
clear_output_files()
generate_cm_layouts(75, 75, 1, "N")
generate_dp_layouts(190, 1, "N")


# Run PEX ---------------------------------------------------------
path = 'outputs/'
files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
for i, layouts in enumerate(files):
    file_name = path + layouts.split('.')[0]
    print(file_name)
    failed_pex = 0
    try:
        pex(file_name)
        print(i, file_name, "done!")
    except:
        failed_pex += 1
        print(f"{file_name} can not be extracted")
print(f"{failed_pex} pex failed!")


# file_path = os.path.abspath("outputs/nmos_cm_3x25x1_111_3")
# print(file_path)
# pex(file_path)








