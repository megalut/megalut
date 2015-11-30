"""
These are settings for the machine learning
"""

import megalut.learn


g1mlparams = megalut.learn.MLParams(name = "g1",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	targets = ["tru_s1"],
	predictions = ["pre_s1"])

g2mlparams = megalut.learn.MLParams(name = "g2",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	targets = ["tru_s2"],
	predictions = ["pre_s2"])


v5msrb_4_nomb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5msrb_4_nomb", hidden_nodes = [4],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=None, mbloops=1, max_iterations=50, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

trainparamslist = [
	(g1mlparams, v5msrb_4_nomb),
	(g2mlparams, v5msrb_4_nomb),	
]

