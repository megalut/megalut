

import megalut.learn


g1mlparams = megalut.learn.MLParams(name = "g1",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	targets = ["tru_s1"],
	predictions = ["pre_s1"])

g2mlparams = megalut.learn.MLParams(name = "g2",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	targets = ["tru_s2"],
	predictions = ["pre_s2"])


# Just for a check, removing the PSF:

g1mlparams_nopsf = megalut.learn.MLParams(name = "g1_nopsf",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux"],
	targets = ["tru_s1"],
	predictions = ["pre_s1"])

g2mlparams_nopsf = megalut.learn.MLParams(name = "g2_nopsf",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux"],
	targets = ["tru_s2"],
	predictions = ["pre_s2"])




v5test1_4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5test1", hidden_nodes = [4],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.2, mbloops=1, max_iterations=50, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

v5test2_4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5test2_4", hidden_nodes = [4],
	errfctname="msb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.2, mbloops=5, max_iterations=50, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

v5test2noid_4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5test2noid_4", hidden_nodes = [4],
	errfctname="msb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.2, mbloops=5, max_iterations=50, gtol=1e-20, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


v5test1_7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5test1_7", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.2, mbloops=3, max_iterations=50, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


v5msrb_4_nomb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5msrb_4_nomb", hidden_nodes = [4],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=None, mbloops=1, max_iterations=50, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


v5msrb_7_nomb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5msrb_7_nomb", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=None, mbloops=2, max_iterations=50, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

v5msb_7_nomb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5msb_7_nomb", hidden_nodes = [7],
	errfctname="msb", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=None, mbloops=2, max_iterations=50, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


# Best and simplest for SBE London meeting : v5msrb_4_nomb 

#trainparamslist = [
#	(g1mlparams, v5msrb_4_nomb),
#	(g2mlparams, v5msrb_4_nomb),	
#]

trainparamslist = [
	(g1mlparams_nopsf, v5msrb_4_nomb),
	(g2mlparams_nopsf, v5msrb_4_nomb),	
]


# Attempt with pre-defined weights (pw)

s1pwmlparams = megalut.learn.MLParams(name = "s1pw",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	auxinputs = ["pw"],
	targets = ["tru_s1"],
	predictions = ["pre_s1pw"])

s2pwmlparams = megalut.learn.MLParams(name = "s2pw",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	auxinputs = ["pw"],
	targets = ["tru_s2"],
	predictions = ["pre_s2pw"])


v5pw = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5pw", hidden_nodes = [4],
	errfctname="msbpw", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=None, mbloops=1, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

# experiementing with ininoise...
v5pw_noiseexp = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5pw_noiseexp", hidden_nodes = [4],
	errfctname="msbpw", valfrac=0.25, shuffle=True,
	ininoisewscale = 0.01, ininoisebscale = 0.01,
	mbsize=None, mbfrac=None, mbloops=1, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

v5pw_noiseexp2 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5pw_noiseexp2", hidden_nodes = [4],
	errfctname="msbpw", valfrac=0.25, shuffle=True,
	ininoisewscale = 1.0, ininoisebscale = 1.0,
	mbsize=None, mbfrac=None, mbloops=1, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


pwtrainparamslist = [
	(s1pwmlparams, v5pw_noiseexp2),
	(s2pwmlparams, v5pw_noiseexp2),	
]










## And the post-weights (did not work)
#
#w1mlparams_v1 = megalut.learn.MLParams(name = "wg1_v1",
#	inputs = ["adamom_sigma", "adamom_flux"],
#	auxinputs = ["pre_s1"],
#	targets = ["tru_s1"],
#	predictions = ["pre_w1_v1"])
#
#w2mlparams_v1 = megalut.learn.MLParams(name = "wg2_v1",
#	inputs = ["adamom_sigma", "adamom_flux"],
#	auxinputs = ["pre_s2"],
#	targets = ["tru_s2"],
#	predictions = ["pre_w2_v1"])
#
#
#v5msbw_2_nomb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5msbw_2_nomb", hidden_nodes = [2],
#	errfctname="msbw", valfrac=0.25, shuffle=True,
#	mbsize=None, mbfrac=None, mbloops=1, max_iterations=20, gtol=1e-20, startidentity=False,
#	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
#	verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#v5msbw_2 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "v5msbw_2", hidden_nodes = [2],
#	errfctname="msbw", valfrac=0.5, shuffle=True,
#	mbsize=None, mbfrac=None, mbloops=5, max_iterations=20, gtol=1e-20, startidentity=False,
#	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
#	verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#
#wtrainparamslist = [
#	(w1mlparams_v1, v5msbw_2),
#	(w2mlparams_v1, v5msbw_2),	
#]
