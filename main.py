from pex.extract import *


# Run PEX -----------------------------------------------------------------------
path = 'outputs/'
files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

for i, layouts in enumerate(files):
    file_name = path + layouts.split('.')[0]
    failed_pex = 0
    try:
        pex(file_name)
        print(i, file_name, "done!")
    except:
        failed_pex += 1
        print(f"{file_name} can not be extracted")
    print(f"{failed_pex} pex failed!")
