import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import mlparams


cat = megalut.tools.io.readpickle(os.path.join(workdir, "SimpleS1v", "groupmeascat_cases.pkl"))
#print megalut.tools.table.info(cat)


cat = megalut.learn.run.predict(cat,
	os.path.join(workdir, "train1_SimpleS1")
	, mlparams.trainparamslist)

#print megalut.tools.table.info(cat)

megalut.tools.io.writepickle(cat, os.path.join(workdir, "validcat.pkl"))

#exit()

