


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
#workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT/new_fiducial"


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
	#"ts":"ts-2", # <--- the previosu default, with minrad2
	#"ts":"ts-2-minrad3", #  <--- the one with the best minrad3 (replaces the previous sel-large)
	#"ts":"ts-3-ln",
	#"ts":"ts-2-easy",
	"ts":"ts-2-faint",
	#"ts":"ts-2-faint-p1",
	#"ts":"ts-2-faint-d1",
	#"ts":"ts-2-faint-d2",
	#"ts":"ts-2-faint-ln",
	#"ts":"ts-2-faint20",
	#"ts":"ts-4",
	#"ts":"ts-4-minrad3",
	#"ts":"ts-2-sel-large",
	#"ts":"ts-e-1",
	"vs":"vs-3-faint",
	#"vs":"vs-1-faint",
	#"vs":"ts-2-easy",
	#"vs":"vs-2-easy",	
	#"tw":"tw-3-faint",
	#"tw":"tw-4-faint", #<-- used tuesday
	#"tw":"tw-4-faint-snc",
	"tw":"tw-5-faint",
	
	#"vo":"vo-2",
	#"vo":"vo-3-faint",
	"vo":"vo-3-faint-nosnc",
	
	
	"si":"si-1",
}


shearconflist = [
	
	("mlconfig/ada5s1f.cfg", "mlconfig/sum55.cfg"),
	("mlconfig/ada5s2f.cfg", "mlconfig/sum55.cfg")
	
	#("mlconfig/ada5s1.cfg", "mlconfig/sum55.cfg"),
	#("mlconfig/ada5s2.cfg", "mlconfig/sum55.cfg")
	
	#("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"), # Uncomment a line to run on only one component
	#("mlconfig/ada4s2.cfg", "mlconfig/sum55.cfg")

	#("mlconfig/ada4s1.cfg", "mlconfig/sum5.cfg"),
	#("mlconfig/ada4s2.cfg", "mlconfig/sum5.cfg")
	
	#("mlconfig/ada5s1.cfg", "mlconfig/sum5.cfg"),
	#("mlconfig/ada5s2.cfg", "mlconfig/sum5.cfg")

	
]

weightconflist = [
	#("mlconfig/ada5s1wf.cfg", "mlconfig/sum5w.cfg"),
	#("mlconfig/ada5s2wf.cfg", "mlconfig/sum5w.cfg")

	("mlconfig/ada5s1wf.cfg", "mlconfig/sum55w.cfg"),
	("mlconfig/ada5s2wf.cfg", "mlconfig/sum55w.cfg")
	
]
