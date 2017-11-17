


import megalut
import megalut.learn
import os
import numpy as np

import logging
loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'
#loggerformat='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s'
logging.basicConfig(format=loggerformat,level=logging.INFO)

workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT/fiducial"


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
	
	"train-shear":"ts-1",

	"valid-shear":"vs-1",

	"train-weight":"tw-1",

	"valid-overall":"vo-1",
	
	"simobscompa":"simobscompa",
}


shearconflist = [
	("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"), # Uncomment a line to run on only one component
	("mlconfig/ada4s2.cfg", "mlconfig/sum55.cfg")
	
]

weightconflist = [
	#("mlconfig/ada2s1w.cfg", "mlconfig/sum55w_test3.cfg"),
	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_test4.cfg"),
	
	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_test3.cfg"),
	#("mlconfig/ada5s2w.cfg", "mlconfig/sum55w_test.cfg"),
	
	("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_huge1.cfg"),#  <--- i guess we want those 
	("mlconfig/ada5s2w.cfg", "mlconfig/sum55w_huge1.cfg"),

	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_tw3.cfg"),#  <--- i guess we want those 
	#("mlconfig/ada5s2w.cfg", "mlconfig/sum55w_tw3.cfg"),
	
	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_huge1iden.cfg"),
	#("mlconfig/ada5s1w.cfg", "mlconfig/sum55w_huge1idennomb.cfg"),
	
]
