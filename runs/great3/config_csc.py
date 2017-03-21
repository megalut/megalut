"""
Configuration for the GREAT3 scripts.
"""

import megalutgreat3 as mg3

loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'


great3 = mg3.great3.GREAT3Run(
	experiment = "control",
	obstype = "space",
	sheartype = "constant",
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3",
	truthdir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3/truth", # Only needed for final analysis plots
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/2017_MegaLUT_GREAT3/csc_v2",
	
	#subfields = [94],
	#subfields = [45],	# CSC best PSF subfields: [45, 75, 136],  worst : [143, 49, 150], 94 could not be measured!
	
	subfields = [1045],
	
	#subfields = range(0, 200),
	#subfields = range(0, 50),
	#subfields = range(50, 100),
	#subfields = range(100, 150),
	#subfields = range(150, 200),
	
	ncpu = 4,
	skipdone = False
	)



### Script configuration ###

datasets = {
	#"train-shear":"ts-ell-nn-train-rea10",
	"train-shear":"ts-ell-n-train-rea100",
	
		
	"valid-shear":"vs-shear-n-G3-snc1000",
	#"train-weight":"tw-200c-1000r",
	"train-weight":"tw-100c-10000r",
	
	"valid-overall":"vo-200c-8000r",
	"simobscompa":"simobscompa-G3",
	#"simobscompa":"simobscompa-train",
	
}


shearconflist = [
	("mlconfig/ada4g1.cfg", "mlconfig/sum55mass.cfg"), # Comment a line to run on only one component
	("mlconfig/ada4g2.cfg", "mlconfig/sum55mass.cfg")
	#("mlconfig/ada4g1.cfg", "mlconfig/sum55mab.cfg"), # Comment a line to run on only one component
	#("mlconfig/ada4g2.cfg", "mlconfig/sum55mab.cfg")


]

weightconflist = [
	("mlconfig/ada4s1w.cfg", "mlconfig/sum33wmass.cfg"),
	("mlconfig/ada4s2w.cfg", "mlconfig/sum33wmass.cfg"),
	#("mlconfig/ada4s1w.cfg", "mlconfig/sum33wmab.cfg"),
	#("mlconfig/ada4s2w.cfg", "mlconfig/sum33wmab.cfg"),
	
	
]

#weightconflist = []

trainmode = "g" # When training for ellipticity, switch this to "g". It's for the plots.

predcode = "1" # String used in file names of GREAT3 predictions. Allows you to keep several predictions side by side.
