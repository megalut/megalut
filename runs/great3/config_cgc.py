"""
Configuration for the GREAT3 scripts.
"""

import megalutgreat3 as mg3

loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'


great3 = mg3.great3.GREAT3Run(
	experiment = "control",
	obstype = "ground",
	sheartype = "constant",
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3",
	truthdir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3/truth", # Only needed for final analysis plots
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/2017_MegaLUT_GREAT3/cgc_v2",
	
	#subfields = [0,1,2],
	#subfields = [99],	# CGC best PSF subfields: [99, 156, 42],  worst : [2, 191, 166]

	#subfields = range(0, 200),
	
	subfields = [1099], # Copy of 99, used for manual tests (to avoid messing up 99)

	#subfields = range(0, 50),
	#subfields = range(50, 100),
	#subfields = range(100, 150),
	#subfields = range(150, 200),

	#subfields = range(0, 100),
	#subfields = range(100, 200),

	ncpu = 20,
	skipdone = True
	)


### Script configuration ###


datasets = {
	#"train-shear":"ts-shear-nn-train-snc20",
	#"train-shear":"ts-shear-nn-train-snc100",
	#"train-shear":"ts-ell-n-train-rea100",
	"train-shear":"ts-ell-nn-train-rea10",
	
	"valid-shear":"vs-shear-n-G3-snc1000",
	
	#"train-weight":"tw-20c-2000r",
	#"train-weight":"tw-200c-5000r",
	#"train-weight":"tw-200c-500r",
	#"train-weight":"tw-200c-800r",
	#"train-weight":"tw-500c-200r",
	#"train-weight":"tw-100c-400r",
	#"train-weight":"tw-100c-1000r",
	"train-weight":"tw-200c-1000r",
	
	"valid-overall":"vo-200c-8000r",
	"simobscompa":"simobscompa-G3"
}


shearconflist = [
	#("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"), # Uncomment a line to run on only one component
	#("mlconfig/ada4s2.cfg", "mlconfig/sum55.cfg")

	("mlconfig/ada4g1.cfg", "mlconfig/sum55mass.cfg"), # Uncomment a line to run on only one component
	("mlconfig/ada4g2.cfg", "mlconfig/sum55mass.cfg")
	
	
]

weightconflist = [
	#("mlconfig/ada2s1w.cfg", "mlconfig/sum3w.cfg"),
	
	#("mlconfig/ada4s1w.cfg", "mlconfig/sum55w.cfg"),
	#("mlconfig/ada4s1w.cfg", "mlconfig/sum33w.cfg"),
	
	("mlconfig/ada4s1w.cfg", "mlconfig/sum33wmass.cfg"),
	("mlconfig/ada4s2w.cfg", "mlconfig/sum33wmass.cfg"),

	#("mlconfig/ada4s1w.cfg", "mlconfig/sum33w_nomb.cfg"),
	#("mlconfig/ada4s1w.cfg", "mlconfig/sum3w.cfg"),
]

#weightconflist = []

trainmode = "g" # When training for ellipticity, switch this to "g". It's for the plots.

predcode = "1" # String used in file names of GREAT3 predictions. Allows you to keep several predictions side by side.
