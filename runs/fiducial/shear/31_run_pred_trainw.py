import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn
import megalut.tools as tls

import includes

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(includes.workdir, "train_simple")

conflist = [
	("config/ada3s1.cfg", "config/Net.cfg"),
]



# Predicting the validation set
spname = "Ellipticity"
valcatpath = os.path.join(includes.simwdir, spname, "groupmeascat_cases.pkl")
valprecatpath = os.path.join(includes.simwdir, spname, "groupmeascat_cases_pre.pkl")

cat = megalut.tools.io.readpickle(valcatpath)


#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)

print tls.table.info(cat)
megalut.tools.io.writepickle(cat, valprecatpath)



