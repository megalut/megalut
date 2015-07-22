import megalut.learn

# What to train:


sizemlparams = megalut.learn.MLParams(name = "size",
	features = ["adamom_sigma", "adamom_flux", "adamom_g1", "adamom_g2", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	labels = ["tru_sigma"],
	predlabels = ["pre_sigma"])

gmlparams = megalut.learn.MLParams(name = "g",
	features = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	labels = ["tru_g1", "tru_g2"],
	predlabels = ["pre_g1", "pre_g2"])

g1mlparams = megalut.learn.MLParams(name = "g1",
	features = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	labels = ["tru_g1"],
	predlabels = ["pre_g1"])


simpleten = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpleten", hidden_nodes = [10], max_iterations = 500, errfctname="msrb", normtype="-11", actfctname="tanh")
simpleten_msb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpleten_msb", hidden_nodes = [10], max_iterations = 500, errfctname="msb", normtype="-11", actfctname="tanh")
simpleten_sig = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpleten_sig", hidden_nodes = [10], max_iterations = 500, errfctname="msrb", normtype="-11", actfctname="sig")


simpletwenty = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpletwenty", hidden_nodes = [20], max_iterations = 500, errfctname="msrb", normtype="-11", actfctname="tanh")
doubleten = megalut.learn.tenbilacwrapper.TenbilacParams(name = "doubleten", hidden_nodes = [10, 10], max_iterations = 500, errfctname="msrb", normtype="-11", actfctname="tanh")


#trainparamslist = [(sizemlparams, simpleten), (gmlparams, simpleten), (sizemlparams, doubleten), (gmlparams, doubleten)]

#trainparamslist = [(sizemlparams, simpleten), (gmlparams, simpleten)]

trainparamslist = [
	(sizemlparams, simpleten),
	(sizemlparams, simpleten_msb),
	(sizemlparams, simpleten_sig),
	(sizemlparams, simpletwenty),
	(sizemlparams, doubleten),
	(gmlparams, simpleten),
	(gmlparams, simpleten_msb),
	(gmlparams, simpleten_sig),
	(gmlparams, simpletwenty),
	(gmlparams, doubleten)
]


#trainparamslist = [(sizemlparams, simpleten), (gmlparams, simpleten)]
#trainparamslist = [(sizemlparams, simpleten_msb), (gmlparams, simpleten_msb)]
trainparamslist = [(sizemlparams, doubleten), (gmlparams, doubleten)]


simpletest4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpletest4_nmb", hidden_nodes = [4], max_iterations = 1000, errfctname="msrb", normtype="-11", actfctname="tanh")
simpletest7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpletest7_nmb", hidden_nodes = [7], max_iterations = 1000, errfctname="msrb", normtype="-11", actfctname="tanh")
simpletest10 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpletest10_nmb", hidden_nodes = [10], max_iterations = 1000, errfctname="msrb", normtype="-11", actfctname="tanh")
simpletest15 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpletest15_nmb", hidden_nodes = [15], max_iterations = 1000, errfctname="msrb", normtype="-11", actfctname="tanh")
simpletest20 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpletest20_nmb", hidden_nodes = [20], max_iterations = 1000, errfctname="msrb", normtype="-11", actfctname="tanh")
simpletest2020 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpletest2020_nmb", hidden_nodes = [20, 20], max_iterations = 1000, errfctname="msrb", normtype="-11", actfctname="tanh")

trainparamslist = [
	(g1mlparams, simpletest4), 
	(g1mlparams, simpletest7), 
	(g1mlparams, simpletest10), 
	(g1mlparams, simpletest15), 
	(g1mlparams, simpletest20), 
	(g1mlparams, simpletest2020)	
	]
"""
test7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.2, shuffle=True,
	mbsize=300, mbloops=10, max_iterations=30, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True)

test7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.2, shuffle=True,
	mbsize=500, mbloops=10, max_iterations=50, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True)

test7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.2, shuffle=True,
	mbsize=500, mbloops=10, max_iterations=100, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True)
"""

test7fast1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7fast1", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.1, shuffle=True,
	mbsize=100, mbloops=10, max_iterations=30, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True)
	
test7fast2 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7fast2", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.1, shuffle=True,
	mbsize=200, mbloops=10, max_iterations=30, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True)

test7fast5 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7fast5", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.1, shuffle=True,
	mbsize=500, mbloops=5, max_iterations=30, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True)


test7mini = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7mini", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.1, shuffle=True,
	mbsize=100, mbloops=1, max_iterations=10, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=False, keepdata=True)




"""	
test7dir = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.5, shuffle=True,
	mbsize=None, mbloops=1, max_iterations=5000, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True)


test7fast = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test7fast", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.2, shuffle=True,
	mbsize=100, mbloops=10, max_iterations=30, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True)

test20 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "test20", hidden_nodes = [20],
	errfctname="msrb", valfrac=0.2, shuffle=True,
	mbsize=200, mbloops=10, max_iterations=500, 
	normtype="-11", actfctname="tanh", verbose=False, reuse=True)
"""


trainparamslist = [
	(g1mlparams, test7fast1),
	(g1mlparams, test7fast2),
	(g1mlparams, test7fast5)
]



# Before Tenbilac:
"""
features = ["adamom_flux_mean", "adamom_g1_mean", "adamom_g2_mean", "adamom_sigma_mean",
	"tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"]

gmlparams = megalut.learn.MLParams(name = "g",
	features = features,
	labels = ["tru_g1", "tru_g2"], predlabels = ["pre_g1", "pre_g2"])
sizemlparams = megalut.learn.MLParams(name = "size",
	features = features,
	labels = ["tru_sigma"], predlabels = ["pre_sigma"])
fluxmlparams = megalut.learn.MLParams(name = "flux",
	features = features,
	labels = ["tru_flux"], predlabels = ["pre_flux"])


# How to train:
doubletwenty = megalut.learn.fannwrapper.FANNParams(name = "doubletwenty", hidden_nodes = [20, 20], max_iterations = 1000)
doubleten = megalut.learn.fannwrapper.FANNParams(name = "doubleten", hidden_nodes = [10, 10], max_iterations = 1000)
simpleten = megalut.learn.fannwrapper.FANNParams(name = "simpleten", hidden_nodes = [10], max_iterations = 1000)


#trainparamslist = [(gmlparams, doubletwenty), (sizemlparams, doubletwenty), (fluxmlparams, doubletwenty)]

trainparamslist = [(gmlparams, doubleten), (sizemlparams, doubleten), (fluxmlparams, doubleten)]


"""



"""

# Error training


features_rea0 = ["adamom_flux_rea0", "skymad_rea0", "adamom_g1_rea0", "adamom_g2_rea0", "adamom_sigma_rea0", "adamom_rho4_rea0",
			"psf_adamom_g1", "psf_adamom_g2", "psf_adamom_sigma", "psf_adamom_rho4"]
		

raderrmlparams = megalut.learn.MLParams(name = "raderr",
	features = features_rea0,
	labels = ["pre_rad_std"], predlabels = ["pre_raderr"])

gerrmlparams = megalut.learn.MLParams(name = "gerr",
	features = features_rea0,
	labels = ["pre_g1_std", "pre_g2_std"], predlabels = ["pre_g1err", "pre_g2err"])

sersicnerrmlparams = megalut.learn.MLParams(name = "sersicnerr",
	features = features_rea0,
	labels = ["pre_sersicn_std"], predlabels = ["pre_sersicnerr"])

compmlparams = megalut.learn.MLParams(name = "comp",
	features = features_rea0,
	labels = ["comp"], predlabels = ["pre_comp"])


errtrainparamslist = [(raderrmlparams, doubleten), (gerrmlparams, doubleten), (sersicnerrmlparams, doubleten), (compmlparams, doubleten)]
"""



