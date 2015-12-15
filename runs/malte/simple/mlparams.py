

import megalut.learn


# "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma", "skymad"


s1 = megalut.learn.MLParams(name = "s1",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_s1"],
	predictions = ["pre_s1"])

s2 = megalut.learn.MLParams(name = "s2",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_s2"],
	predictions = ["pre_s2"])

msb1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb", hidden_nodes = [1],
	errfctname="msb", valfrac=0.5, shuffle=True,
	ininoisewscale = 0.05, ininoisebscale = 0.05,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

trainparamslist = [
	(s1, msb1),
	(s2, msb1),	
]

