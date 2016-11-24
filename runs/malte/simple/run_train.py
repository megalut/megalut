import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import mlparams
import plots

ncpu = 1

sp = simparams.Simple1()
traindir = os.path.join(workdir, "train3_" + sp.name)


cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))
print megalut.tools.table.info(cat)
megalut.learn.run.train(cat, traindir, mlparams.trainparamslist, ncpu=ncpu)


# Self-predicting
cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
#megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "precat.pkl"))
megalut.tools.io.writepickle(cat, os.path.join(workdir, "precat.pkl"))



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


