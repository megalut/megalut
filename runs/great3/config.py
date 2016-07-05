"""
This is an example of the configuration for great3
"""

# General configuration for MegaLUT
datadir = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/great3_data"
workdir = None
skipdone = True
ncpu = 8
subfields = [5,6,7]#range(5,7)

loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'

# External path to library
sexpath = "sex"
corr2path = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/presubmission_script"
presubdir = "/home/kuntzer/workspace/MegaLUT/MegaLUT-github/presubmission_script"
