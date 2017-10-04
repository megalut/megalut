import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn
import megalut.tools 
import includes

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(includes.workdir, "train_simple")

conflist = [
		
	("config/ada3s1.cfg", "config/Net.cfg"),
	("config/ada2s1w.cfg", "config/sum3w_1.cfg"),
	
	("config/ada3s2.cfg", "config/Net.cfg"),
	("config/ada2s2w.cfg", "config/sum3w_1.cfg"),
	
]

# Predicting the validation set

valcatpath = os.path.join(includes.simvaldir, "Sersics_statshear", "groupmeascat_cases.pkl")
#valcatpath = os.path.join(includes.simwdir, "Ellipticity", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "valprewcat.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)

print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, valprecatpath)



