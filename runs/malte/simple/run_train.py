import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import mlparams
import plots

ncpu = 3

sp = simparams.Simple1()
sp.name = "Simple0"
traindir = os.path.join(workdir, "train81_" + sp.name)


cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))

#cat["adamom_g"] = np.hypot(cat["adamom_g1"], cat["adamom_g2"])

#print np.tile(np.array(cat["tru_rad"]), (1, 20))

#exit()

#cat["adamom_g1*adamom_sigma"] = cat["adamom_g1"] * cat["adamom_sigma"]#.reshape((1000,1))
#cat["adamom_g1/adamom_sigma"] = cat["adamom_g1"] / cat["adamom_sigma"]#.reshape((1000,1))


#print megalut.tools.table.info(cat)

#exit()
megalut.learn.run.train(cat, traindir, mlparams.trainparamslist, ncpu=ncpu)



# Self-predicting
#cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
#megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "precat.pkl"))
megalut.tools.io.writepickle(cat, os.path.join(traindir, "precat.pkl"))



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


