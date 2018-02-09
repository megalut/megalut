


import megalut
import megalut.learn
import os
import numpy as np

import logging
loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'
#loggerformat='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s'
logging.basicConfig(format=loggerformat,level=logging.INFO)

#workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT/fiducial"
workdir = "/vol/euclid5/euclid5_raid3/mtewes/MegaLUT_fiducial"


simdir = os.path.join(workdir, "sim")
simmeasdir = os.path.join(workdir, "simmeas")
traindir = os.path.join(workdir, "train")
valdir = os.path.join(workdir, "val")


for d in [simdir, traindir, valdir]:
	if not os.path.exists(d):
		os.makedirs(d)

stampsize = 64
drawstampsize = stampsize # Used for drawing


datasets = {
	"ts":"ts-1",
	"vs":"vs-2",
	"tw":"tw-1",
	"vo":"vo-1",
	"si":"si-1",
}


shearconflist = [
	("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"), # Uncomment a line to run on only one component
	("mlconfig/ada4s2.cfg", "mlconfig/sum55.cfg")

	#("mlconfig/ada4s1.cfg", "mlconfig/sum5.cfg")
	#("mlconfig/ada4s2.cfg", "mlconfig/sum5.cfg")
	
]

weightconflist = [
	("mlconfig/ada5s1w.cfg", "mlconfig/sum55w.cfg"),
	("mlconfig/ada5s2w.cfg", "mlconfig/sum55w.cfg"),

	
]
