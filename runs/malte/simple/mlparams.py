

import megalut.learn


# "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma", "skymad"

s1 = megalut.learn.MLParams(name = "s1",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma"],
	targets = ["tru_s1"],
	predictions = ["pre_s1"])

#msb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb", hidden_nodes = [3, 3],
#	errfctname="msb", valfrac=0.1, shuffle=True,
#	ininoisewscale = 0.1, ininoisebscale = 0.1,
#	mbsize=None, mbfrac=1.0, mbloops=5, max_iterations=50, gtol=1e-7, startidentity=True,
#	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
#	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbtw = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb", hidden_nodes = [3, 3, 3],
	n = 2,
	errfctname="msb", valfrac=0.1, shuffle=True,
	ininoisewscale = 0.5, ininoisebscale = 0.5, ininoisemultwscale = 0.5,
	mbsize=None, mbfrac=0.3, mbloops=30, max_iterations=40, gtol=1e-7,
	startidentity=True, onlynidentity=None,
	normtargets=False, normtype="sa1",
	actfctname="tanh", oactfctname="iden", multactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


trainparamslist = [
	(s1, msbtw)
]

"""
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

msb5 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb5", hidden_nodes = [5],
	errfctname="msb", valfrac=0.5, shuffle=True,
	ininoisewscale = 0.05, ininoisebscale = 0.05,
	mbsize=None, mbfrac=1.0, mbloops=1, max_iterations=30, gtol=1e-20, startidentity=True,
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
	(s1, msb5)
]

"""
