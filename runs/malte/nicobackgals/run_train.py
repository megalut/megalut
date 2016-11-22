import matplotlib
matplotlib.use("AGG")


import megalut
import config
import measfcts
import simparams
import mlparams

import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)


sp = simparams.Nico3()
sp.name = "Nico3b"
addname = "_noc"
#addname = ""
traindir = os.path.join(config.workdir, "train_" + sp.name + addname)


cat = megalut.tools.io.readpickle(os.path.join(config.simdir, sp.name, "groupmeascat_cases.pkl"))
print megalut.tools.table.info(cat)

megalut.learn.run.train(cat, traindir, mlparams.trainparamslist_noc, ncpu=config.ncpu)



# Self-predicting
"""
cat = megalut.tools.io.readpickle(os.path.join(config.simdir, sp.name, "groupmeascat_cases.pkl"))
s = megalut.tools.table.Selector("LowShear", [("in", "tru_s1", -0.05, 0.05), ("in", "tru_s2", -0.05, 0.05)])
cat = s.select(cat)

#cat = megalut.tools.io.readpickle(os.path.join(config.simdir, sp.name, "groupmeascat_cases_small-s.pkl"))

cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist, outtweak=np.ma.median)
megalut.tools.io.writepickle(cat, os.path.join(config.simdir, sp.name, "precat.pkl"))

"""


# Pretict GauShear2:
"""
fakeobs = simparams.GauShear2()
cat = megalut.tools.io.readpickle(os.path.join(workdir, "GauShear2", "groupmeascat.pkl"))
#print megalut.tools.table.info(cat)

cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
megalut.tools.io.writepickle(cat, os.path.join(workdir, "precat.pkl"))

"""

"""
cat = megalut.tools.io.readpickle(os.path.join(workdir, "precat.pkl"))

#plots.shear_true(cat, os.path.join(workdir, "shear_true.png"))
plots.shear_mes(cat, os.path.join(workdir, "shear_mes.png"))

#megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "selfprecat.pkl"))

#print megalut.tools.table.info(cat)
"""


