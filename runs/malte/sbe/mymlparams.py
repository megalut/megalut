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


simpleten = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpleten", hidden_nodes = [10], max_iterations = 500, errfct="msrb", normtype="-11", actfct="tanh")
simpleten_msb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpleten_msb", hidden_nodes = [10], max_iterations = 500, errfct="msb", normtype="-11", actfct="tanh")
simpleten_sig = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpleten_sig", hidden_nodes = [10], max_iterations = 500, errfct="msrb", normtype="-11", actfct="sig")


simpletwenty = megalut.learn.tenbilacwrapper.TenbilacParams(name = "simpletwenty", hidden_nodes = [20], max_iterations = 500, errfct="msrb", normtype="-11", actfct="tanh")
doubleten = megalut.learn.tenbilacwrapper.TenbilacParams(name = "doubleten", hidden_nodes = [10, 10], max_iterations = 500, errfct="msrb", normtype="-11", actfct="tanh")


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


trainparamslist = [(sizemlparams, simpleten), (gmlparams, simpleten)]
trainparamslist = [(sizemlparams, simpleten_msb), (gmlparams, simpleten_msb)]
trainparamslist = [(sizemlparams, doubleten), (gmlparams, doubleten)]


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



