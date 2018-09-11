


import megalut
import megalut.learn
import os
import numpy as np

import logging
loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'
#loggerformat='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s'
logging.basicConfig(format=loggerformat,level=logging.INFO)

#workdir = "/vol/euclid5/euclid5_raid3/mtewes/MegaLUT_nicobackgals"
#workdir = "/vol/fohlen12/data1/mtewes/MegaLUT/nicobackgals"

workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT/nicobackgals" # Copying stuff here due to fohlen12 disk problems.



simdir = os.path.join(workdir, "sim")
simmeasdir = os.path.join(workdir, "simmeas")
traindir = os.path.join(workdir, "train")
valdir = os.path.join(workdir, "val")


sourcecat = os.path.join(workdir, "cat.pkl")

stampsize = 64 # used for measuring
drawstampsize = stampsize # Used for drawing


datasets = {
	#"tp":"tp-1",
	#"tp":"tp-1-ln",
	#"tp":"tp-1-uni2",
	#"tp":"tp-1-e-uni2",
	#"tp":"tp-1-uni2-pretrain",
	
	#"tp":"tp-1-e-ln-uni2-etype2",
	#"tp":"tp-1-e-uni2-etype2", # We use this one for the pre-training
	
	
	"tp":"tp-1-uni2-etype2-pretrain",
	
	
	
	#"vp":"vp-2",
	"vp":"vp-1-uni2",
	#"vp":"vp-1-uni2-etype2", # This is not needed, we don't care about the e distrib here!


	#"tw":"tw-1",
	"tw":"tw-1-etype2-emaxamp7",


	#"vo":"vo-1",
	"vo":"vo-1-etype2-emaxamp7",
	#"vo":"tw-1-etype2-emaxamp7",

	#"si":"si-1",
	#"si":"si-1-uni",
	#"si":"si-1-uni2",
	#"si":"si-1-uni2-etype2",
	#"si":"si-1-cat-etype2",
	"si":"si-1-cat-etype2-emaxamp7",



}


shearconflist = [
	
	("mlconfig/ada5s1.cfg", "mlconfig/sum55.cfg"), # <--- We use those
	("mlconfig/ada5s2.cfg", "mlconfig/sum55.cfg")
	
	
]

weightconflist = [
	("mlconfig/ada5s1w.cfg", "mlconfig/sum5w.cfg"),
	("mlconfig/ada5s2w.cfg", "mlconfig/sum5w.cfg")
	
	#("mlconfig/ada5s1wf.cfg", "mlconfig/sum5w.cfg"), # As a test, just for w. No, log-flux is slightly better it seems, we keep the above.
	#("mlconfig/ada5s2wf.cfg", "mlconfig/sum5w.cfg")

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
