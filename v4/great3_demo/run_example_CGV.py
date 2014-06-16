import megalut
import numpy as np
import math

run = megalut.great3.run.Run(
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3/",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_GREAT3/",
	branch = ["control", "ground", "variable"],
	version = "v4test3",
)

run.obssubfields = [0]
run.simsubfields = [0]

run.use_galsim = True

run.nsimimages = 1



########################
###   Observations   ###
########################

run.measobs()


#######################
###   Simulations   ###
#######################


class mySimParams(megalut.simparams.SimParams):
	def getrad(self):
		return np.random.uniform(0.7, 2.7)
	
	def getflux(self):
		if np.random.uniform() < 0.25:
			return np.random.uniform(70.0, 220.0)
		else:
			return np.random.uniform(10.0, 70.0)
	
	def getg(self):
		theta = np.random.uniform(0.0, 2.0* math.pi) 
		eps = np.random.uniform(0.0, 0.7) 
		return (eps * np.cos(2.0 * theta), eps * np.sin(2.0 * theta))
		
	def getsersicn(self, ix=0, iy=0, n=1):
		return 1.0 + (float(iy)/float(n)) * 2.0	
		# Lower sersic index = broader




mysimparams = mySimParams()
run.makesim(mysimparams, n = 100, skipdone=False)

run.meassim(skipdone=False)

run.plotsimobscompa(run.simsubfields)



####################
###   Training   ###
####################



params = [
	(megalut.ml.MLParams(
		name = "flux",
		features = ["mes_g1", "mes_g2", "mes_size", "mes_flux", "mes_rad30", "mes_rad50", "mes_rad70", "mes_rad90"],
		labels = ["tru_flux"],
		predlabels = ["pre_flux"],
		),
	megalut.fannwrapper.FANNParams(
		nhid = [20, 20],
		max_iterations = 1000,
	)),
	(megalut.ml.MLParams(
		name = "sersicn",
		features = ["mes_g1", "mes_g2", "mes_size", "mes_flux", "mes_rad30", "mes_rad50", "mes_rad70", "mes_rad90"],
		labels = ["tru_sersicn"],
		predlabels = ["pre_sersicn"],
		),
	megalut.fannwrapper.FANNParams(
		nhid = [20, 20],
		max_iterations = 1000,
	)),
	(megalut.ml.MLParams(
		name = "rad",
		features = ["mes_g1", "mes_g2", "mes_size", "mes_flux", "pre_sersicn"],
		labels = ["tru_rad"],
		predlabels = ["pre_rad"],
		),
	megalut.fannwrapper.FANNParams(
		nhid = [20,20],
		max_iterations = 2000,
	)),
	(megalut.ml.MLParams(
		name = "g",
		features = ["mes_g1", "mes_g2", "pre_rad", "pre_flux", "pre_sersicn"],
		labels = ["tru_g1", "tru_g2"],
		predlabels = ["pre_g1", "pre_g2"],
		),
	megalut.fannwrapper.FANNParams(
		nhid = [20,20],
		max_iterations = 5000,
	))
]



"""
params = [
	(megalut.ml.MLParams(
		name = "g",
		features = ["mes_g1", "mes_g2", "mes_size", "mes_flux", "mes_rad30", "mes_rad50", "mes_rad70", "mes_rad90"],
		labels = ["tru_g1", "tru_g2"],
		predlabels = ["pre_g1", "pre_g2"],
		),
	megalut.skynet.SkyNetParams(
		nhid = [30],
		max_iter = 200,
	))

]
"""



run.train(params, skipdone=False)

run.plotpresummary(run.simsubfields)



#######################
###   Predictions   ###
#######################


#run.predict(params)


#run.writeout()

#run.presubmission(corr2path="/users/mtewes/GREAT3/mjarvis-read-only/corr2")

#run.plotsimobscompa(run.simsubfields)
#run.plotpresummary(run.simsubfields)
#run.final_plots()


