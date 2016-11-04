

import megalut.learn


# "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma", "skymad"


s1adamom = megalut.learn.MLParams(name = "s1adamom",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_s1"],
	predictions = ["pre_s1_adamom"])

s2adamom = megalut.learn.MLParams(name = "s2adamom",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_s2"],
	predictions = ["pre_s2_adamom"])


s1fourier = megalut.learn.MLParams(name = "s1fourier",
	inputs = ["fourierhann_adamom_g1", "fourierhann_adamom_g2", "fourierhann_adamom_sigma", "adamom_flux", "fourierhann_adamom_rho4"],
	targets = ["tru_s1"],
	predictions = ["pre_s1_fourier"])

s2fourier = megalut.learn.MLParams(name = "s2fourier",
	inputs = ["fourierhann_adamom_g2", "fourierhann_adamom_g1", "fourierhann_adamom_sigma", "adamom_flux", "fourierhann_adamom_rho4"],
	targets = ["tru_s2"],
	predictions = ["pre_s2_fourier"])






msb1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb", hidden_nodes = [1],
	errfctname="msb", valfrac=0.5, shuffle=True,
	ininoisewscale = 0.05, ininoisebscale = 0.05,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msb5 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb5", hidden_nodes = [5],
	errfctname="msb", valfrac=0.3, shuffle=True,
	ininoisewscale = 0.05, ininoisebscale = 0.05,
	mbsize=None, mbfrac=0.3, mbloops=5, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


# new test, with committees: add: n
msb5c = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb5c", hidden_nodes = [5],
	n=10,
	errfctname="msb", valfrac=0.3, shuffle=True,
	ininoisewscale = 0.1, ininoisebscale = 0.1,
	mbsize=None, mbfrac=0.3, mbloops=5, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)



msb5slow = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb5slow", hidden_nodes = [5],
	errfctname="msb", valfrac=0.05, shuffle=True,
	ininoisewscale = 0.1, ininoisebscale = 0.1,
	mbsize=None, mbfrac=0.5, mbloops=10, max_iterations=50, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)



# more noise:

msb5n = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb5n", hidden_nodes = [5],
	errfctname="msb", valfrac=0.5, shuffle=True,
	ininoisewscale = 0.2, ininoisebscale = 0.2,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msb55n = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb55n", hidden_nodes = [5, 5],
	errfctname="msb", valfrac=0.5, shuffle=True,
	ininoisewscale = 0.2, ininoisebscale = 0.2,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

trainparamslist = [
	(s1adamom, msb5c),
	(s2adamom, msb5c),
	(s1fourier, msb5c),
	(s2fourier, msb5c),
		
]


