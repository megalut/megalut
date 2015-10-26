

import megalut.learn


g1mlparams = megalut.learn.MLParams(name = "g1",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	targets = ["tru_s1"],
	predictions = ["pre_s1"])

g2mlparams = megalut.learn.MLParams(name = "g2",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	targets = ["tru_s2"],
	predictions = ["pre_s2"])


v5test1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5test1", hidden_nodes = [4],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=1, max_iterations=50, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)
	
	
trainparamslist = [
	(g1mlparams, v5test1),
	(g2mlparams, v5test1),	
]
