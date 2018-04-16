


import megalut
import megalut.learn
import os
import numpy as np

import logging
loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'
#loggerformat='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s'
logging.basicConfig(format=loggerformat,level=logging.INFO)

workdir = "/vol/fohlen12/data1/mtewes/MegaLUT/papereuclidlike"
gemsdir = "/vol/fohlen12/data1/mtewes/GEMS"
spectrumpath = "/vol/fohlen12/data1/mtewes/Pickles_spectra/pickles_uk_27.fits"


simdir = os.path.join(workdir, "sim2")
simmeasdir = os.path.join(workdir, "simmeas2")
traindir = os.path.join(workdir, "train")
valdir = os.path.join(workdir, "val")


sourcecat = os.path.join(workdir, "cat.pkl")

stampsize = 64 # used for measuring
drawstampsize = stampsize # Used for drawing

psfoversampling = 5
psfstampsize = 64


datasets = {
	"tp":"tp-1",
	"vp":"vp-1",
	
	"tw":"tw-1",
	"vo":"vo-1",

	#"si":"si-1-gems",
	"si":"si-1-uni",
	
}


shearconflist = [
	
	("mlconfig/ada5s1.cfg", "mlconfig/sum55.cfg"), # <--- We use those
	("mlconfig/ada5s2.cfg", "mlconfig/sum55.cfg")
	
	
]

weightconflist = [
	("mlconfig/ada5s1w.cfg", "mlconfig/sum5w.cfg"),
	("mlconfig/ada5s2w.cfg", "mlconfig/sum5w.cfg")

]


#######################################################################################################################################

# Some automatically generated names, used for saving figures etc depending on your above settings.
# Not meant to be changed by the user...

sconfname = os.path.splitext(os.path.basename(shearconflist[0][1]))[0] # extracts e.g. "sum55"
valname = "{}_with_{}_on_{}".format(datasets["tp"], sconfname, datasets["vp"])
wconfname = os.path.splitext(os.path.basename(weightconflist[0][1]))[0] # extracts e.g. "sum55w"
wvalname = "{}_and_{}_with_{}_{}_on_{}".format(datasets["tp"], datasets["tw"], sconfname, wconfname, datasets["vo"])

for d in [simdir, traindir, valdir]:
	if not os.path.exists(d):
		os.makedirs(d)
