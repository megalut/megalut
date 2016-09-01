"""
This is an example of the simple configuration for the GREAT3 scripts.
Copy this file into config.py, and make changes as appropriate.
"""


# General configuration for MegaLUT
datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3"
trushapedir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3/truth"

# Setting related to the branch, and a workdir
experiment = "control" # This gets used when initiating a new config
obstype = "ground"
sheartype = "constant"
workdir = "/vol/fohlen11/fohlen11_1/mtewes/2016_MegaLUT_GREAT3/cgc" # This determines which existing pkl configs will be read in

# Script configuration
skipdone = True
ncpu = 5
#subfields = [5,6,7]#range(5,7)
subfields = range(0, 200)

loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'

# External paths to libraries
sexpath = "sex"
corr2path = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/presubmission_script"
presubdir = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/presubmission_script"



###### Previous settings:
"""
# General configuration for MegaLUT
datadir = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/great3_data/"
trushapedir = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/great3_true_shape/"
workdir = None
skipdone = True
ncpu = 8
subfields = [5,6,7]#range(5,7)

loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'

# External path to library
sexpath = "sex"
corr2path = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/presubmission_script"
presubdir = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/presubmission_script"
"""
