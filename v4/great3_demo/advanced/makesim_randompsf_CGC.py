import megalut
import numpy as np
import math

run = megalut.great3.run.Run(
	datadir = "/scratch/kuntzer/GREAT3_DATA/",
	workdir = "/scratch/kuntzer/varpsf/",
	branch = ["control", "ground", "constant"],
	version = "test",
)

run.obssubfields = range(1)
run.simsubfields = range(1)

run.use_galsim = True
run.use_acf = False

run.nsimimages = 1


########################
###   Observations   ###
########################

run.measobs(skipdone=True)


#######################
###   Simulations   ###
#######################

class mySimParams(megalut.simparams.SimParams):

	def get(self, ix, iy, n):				
		if np.random.uniform() > 0.75:
			if np.random.uniform() > 0.5:
				flux = 20.0 + 220.0*np.random.uniform()
			else:
				flux = 20.0 + 140.0*np.random.uniform()
		else:
			flux = 20.0 + 45.0*np.random.uniform()

		if np.random.uniform() > 0.8:
			rad = 1.0 + 8.0*np.random.uniform()
		else:
			rad = 1.0 + 4.0*np.random.uniform()			

		if rad > 5.0 and np.random.uniform() > 0.5:
			flux *= 2.0
		if rad < 5.0 and np.random.uniform() > 0.5:
			flux /= 2.0
			
		if flux < 140.:
			(g1, g2) = np.random.uniform(low=-0.4, high=0.4, size=2)
		else:
			(g1, g2) = np.random.uniform(low=-0.2, high=0.2, size=2)				

		pseudorand = float(iy)/float(n)
		if pseudorand < 0.8:
			sersicn = 0.5 + pseudorand * 1.25
		else:
			normpseudorand = (pseudorand - 0.8)/0.2
			sersicn = 1.0 + normpseudorand * 2.0
		# Lower sersic index = broader, do not randomize becasue of GalSim efficiency !

		return {
			"sig" : self.getsig()/2,
			"rad" : rad,
			"flux" : flux,
			"sersicn" : sersicn,
			"g1" : g1,
			"g2" : g2
		}





mysimparams = mySimParams()
run.makesim(mysimparams, n = 10, skipdone=False, random_psf=False)

run.meassim(skipdone=False)
