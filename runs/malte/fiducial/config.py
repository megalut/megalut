


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
#workdir = "/vol/fohlen12/data1/mtewes/MegaLUT/fiducial"

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
	#"ts":"ts-2-faint",
	"ts":"ts-2-faint-p1", # <-- selected
	#"ts":"ts-2-faint-d1", # <--- the one for the nice training evolution plot
	#"ts":"ts-2-faint-d2",
	#"ts":"ts-2-faint-ln",
	#"ts":"ts-2-faint20",
	#"ts":"ts-4",
	#"ts":"ts-4-minrad3",
	#"ts":"ts-2-sel-large",
	#"ts":"ts-e-1",
	#"ts":"ts-vp-1-ln",
	#"ts":"ts-vp-1",
	
	"vs":"vs-3-faint", # <-- the default vs
	#"vs":"vs-1-faint",
	#"vs":"ts-2-easy",
	#"vs":"vs-2-easy",	
	#"vs":"vs-vp-1s",
	#"vs":"vs-vp-1-ln",
	
	#"tw":"tw-3-faint",
	#"tw":"tw-4-faint",
	#"tw":"tw-4-faint-snc",
	"tw":"tw-5-faint", # <-- the default tw
	
	#"vo":"vo-2",
	#"vo":"vo-3-faint",
	"vo":"vo-3-faint-nosnc", # <-- the default vo
	#"vo":"vo-3-faint-nosnc-mini",
	
	#"vo":"vs-3-faint", # <--- the one for conditional bias plot with weights
	
	#"si":"si-1",
	"si":"si-vp-1",
}



shearconflist = [
	
	("mlconfig/ada5s1f.cfg", "mlconfig/sum55.cfg"), # <--- We use those
	("mlconfig/ada5s2f.cfg", "mlconfig/sum55.cfg")
	
	
	# vp:
	
	#("mlconfig/ada7s1f-vp-pos.cfg", "mlconfig/sum77.cfg"),
	#("mlconfig/ada7s2f-vp-pos.cfg", "mlconfig/sum77.cfg")
	
	#("mlconfig/ada8s1f-vp-mom.cfg", "mlconfig/sum88.cfg"),
	#("mlconfig/ada8s2f-vp-mom.cfg", "mlconfig/sum88.cfg")
	
	# Old experiemtns:
	
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
	("mlconfig/ada5s1wf.cfg", "mlconfig/sum5w.cfg"), # <--- We use those
	("mlconfig/ada5s2wf.cfg", "mlconfig/sum5w.cfg")

	#("mlconfig/ada5s1wf.cfg", "mlconfig/sum55w.cfg"),
	#("mlconfig/ada5s2wf.cfg", "mlconfig/sum55w.cfg")
	
]


#######################################################################################################################################

# Some automatically generated names, used for saving figures etc depending on your above settings

sconfname = os.path.splitext(os.path.basename(shearconflist[0][1]))[0] # extracts e.g. "sum55"
valname = "{}_with_{}_on_{}".format(datasets["ts"], sconfname, datasets["vs"])
wconfname = os.path.splitext(os.path.basename(weightconflist[0][1]))[0] # extracts e.g. "sum55w"
wvalname = "{}_and_{}_with_{}_{}_on_{}".format(datasets["ts"], datasets["tw"], sconfname, wconfname, datasets["vo"])

