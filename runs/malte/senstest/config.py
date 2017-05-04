


import megalut
import megalut.learn
import os
import numpy as np

import logging
loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'
#loggerformat='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s'
logging.basicConfig(format=loggerformat,level=logging.INFO)

workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/senstest"

#sampledir = os.path.join(workdir, "sample_data_2017-03-29") 
#sampleprods = os.path.join(sampledir, "prods")

obsdir = os.path.join(workdir, "sensitivity_testing_1/extracted") 
obsproddir = os.path.join(workdir, "megalut", "obs_1")

truedistdir = os.path.join(workdir, "true_distribs_2017-04-18") 
truedistpath = os.path.join(truedistdir, "table.pkl")

psfdir = os.path.join(workdir, "psf_2017-04-18") 
psfcatpath = os.path.join(psfdir, "psf.cat") 


simdir = os.path.join(workdir, "megalut", "sims")
simmeasdir = os.path.join(workdir, "megalut", "simmeas")
traindir = os.path.join(workdir, "megalut", "train")
valdir = os.path.join(workdir, "megalut", "val")

# Making dirs:
for d in [valdir, obsproddir]:
	if not os.path.exists(d):
		os.makedirs(d)


stampsize = 64
drawstampsize = stampsize # Used for drawing

imgnos = [0]


datasets = {
	
#	"train-shear":"ts-ln-1",
#	"train-shear":"ts-ln-1-large",
#	"train-shear":"ts-fn-1",
	"train-shear":"ts-fn-1-failfrac05",
	
	"valid-shear":"vs-1",

	"train-weight":"tw-1",
#	"train-weight":"tw-1-minmag22",
	
	"valid-overall":"val-1",
	
	"simobscompa":"simobscompa",
}


shearconflist = [
	("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"), # Uncomment a line to run on only one component
	("mlconfig/ada4s2.cfg", "mlconfig/sum55.cfg")
	
]

weightconflist = [
	("mlconfig/ada5s1w.cfg", "mlconfig/sum55w.cfg"),
	("mlconfig/ada5s2w.cfg", "mlconfig/sum55w.cfg"),
]
