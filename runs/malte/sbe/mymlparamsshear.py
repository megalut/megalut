"""
This is for the shear-training !

Do not forget:

normtargets = False
startidentity = False



"""

import megalut.learn


#### v3.5 #####


# w1 : very simple:

g1wmlparams1 = megalut.learn.MLParams(name = "g1w1",
	inputs = ["adamom_sigma", "adamom_flux"],
	auxinputs = ["pre_g1"],
	targets = ["tru_s1"],
	predictions = ["pre_g1_w1"])

g2wmlparams1 = megalut.learn.MLParams(name = "g2w1",
	inputs = ["adamom_sigma", "adamom_flux"],
	auxinputs = ["pre_g2"],
	targets = ["tru_s2"],
	predictions = ["pre_g2_w1"])

# v2 : same features as shapes:

g1wmlparams2 = megalut.learn.MLParams(name = "g1w2",
	inputs = ["adamom_sigma", "adamom_flux", "tru_psf_sigma", "adamom_g1", "adamom_g2", "tru_psf_g1", "tru_psf_g2"],
	auxinputs = ["pre_g1"],
	targets = ["tru_s1"],
	predictions = ["pre_g1_w2"])

g2wmlparams2 = megalut.learn.MLParams(name = "g2w2",
	inputs = ["adamom_sigma", "adamom_flux", "tru_psf_sigma", "adamom_g1", "adamom_g2", "tru_psf_g1", "tru_psf_g2"],
	auxinputs = ["pre_g2"],
	targets = ["tru_s2"],
	predictions = ["pre_g2_w2"])


# v3 : in between

g1wmlparams3 = megalut.learn.MLParams(name = "g1w3",
	inputs = ["adamom_sigma", "adamom_flux", "pre_g1", "pre_g2"],
	auxinputs = ["pre_g1"],
	targets = ["tru_s1"],
	predictions = ["pre_g1_w3"])

g2wmlparams3 = megalut.learn.MLParams(name = "g2w3",
	inputs = ["adamom_sigma", "adamom_flux", "pre_g1", "pre_g2"],
	auxinputs = ["pre_g2"],
	targets = ["tru_s2"],
	predictions = ["pre_g2_w3"])


shear1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1", hidden_nodes = [7],
	errfctname="msbw", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False, normtargets=False,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwnonorm4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwnonorm4", hidden_nodes = [4],
	errfctname="msbwnonorm", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=1, max_iterations=50, gtol=1e-15, startidentity=False, normtargets=False,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwsig4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwsig4", hidden_nodes = [4],
	errfctname="msbwsig", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=1, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="sig",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwplain4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwplain4", hidden_nodes = [4],
	errfctname="msbwsig", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


msbwsigtwo4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwsigtwo4", hidden_nodes = [4],
	errfctname="msbwsigtwo", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=1, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="sig",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwsigten4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwsigten4", hidden_nodes = [4],
	errfctname="msbwsigten", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="sig",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


msbwsigthree4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwsigthree4", hidden_nodes = [4],
	errfctname="msbwsigthree", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="sig",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


msbwsigthree42 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwsigthree42", hidden_nodes = [4,2],
	errfctname="msbwsigthree", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="sig",
	verbose=False, reuse=True, keepdata=False, autoplot=True)


msbwplainten4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwplainten4", hidden_nodes = [4],
	errfctname="msbwsigten", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwclip4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwclip4", hidden_nodes = [4],
	errfctname="msbwclip", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwclip8 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwclip8bis", hidden_nodes = [8],
	errfctname="msbwclip", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwsquare4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwsquare4", hidden_nodes = [4],
	errfctname="msbwsquare", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwinvsquare4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwinvsquare4", hidden_nodes = [4],
	errfctname="msbwinvsquare", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwinvsquare8 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwinvsquare8", hidden_nodes = [8],
	errfctname="msbwinvsquare", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

msbwsigten8 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msbwsigten8", hidden_nodes = [8],
	errfctname="msbwsigten", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="sig",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

"""
trainparamslist = [
	(g1wmlparams3, msbwnonorm4),
	(g2wmlparams3, msbwnonorm4),
	(g1wmlparams3, msbwsig4),
	(g2wmlparams3, msbwsig4),
	(g1wmlparams3, msbwsigtwo4),
	(g2wmlparams3, msbwsigtwo4),
	(g1wmlparams3, msbwplain4),
	(g2wmlparams3, msbwplain4),
	(g1wmlparams3, msbwplainten4),
	(g2wmlparams3, msbwplainten4),
	(g1wmlparams3, msbwplainten4),
	(g2wmlparams3, msbwplainten4),
	(g1wmlparams3, msbwsigthree42),
	(g2wmlparams3, msbwsigthree42),
	(g1wmlparams3, msbwsigthree4),
	(g2wmlparams3, msbwsigthree4),
	(g1wmlparams1, msbwsigthree42),
	(g2wmlparams1, msbwsigthree42),
	(g1wmlparams1, msbwsigthree4),
	(g2wmlparams1, msbwsigthree4),
	
	(g1wmlparams3, msbwclip4),
	(g2wmlparams3, msbwclip4),
	(g1wmlparams3, msbwclip8),
	(g2wmlparams3, msbwclip8),

	(g1wmlparams3, msbwsquare4),
	(g2wmlparams3, msbwsquare4),
	(g1wmlparams3, msbwinvsquare4),
	(g2wmlparams3, msbwinvsquare4),

	(g1wmlparams3, msbwinvsquare8),
	(g2wmlparams3, msbwinvsquare8),
	(g1wmlparams3, msbwclip8),
	(g2wmlparams3, msbwclip8),
	(g1wmlparams3, msbwsigten8),
	(g2wmlparams3, msbwsigten8),
	

]	
	

"""
trainparamslist = [
	(g1wmlparams3, msbwplain4),
	(g2wmlparams3, msbwplain4),	
]

"""
trainparamslist = [
	(g1wmlparams3, msbwplain4),
	(g2wmlparams3, msbwplain4),
]
"""


"""

## v3.4 : back at training for shear:
#
#s1mlparams = megalut.learn.MLParams(name = "s1",
#	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
#	targets = ["tru_s1"],
#	predictions = ["pre_s1"])
#
#s2mlparams = megalut.learn.MLParams(name = "s2",
#	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
#	targets = ["tru_s2"],
#	predictions = ["pre_s2"])
#
#
#msb7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb7", hidden_nodes = [7],
#	errfctname="msb", valfrac=0.25, shuffle=True,
#	mbsize=None, mbfrac=0.1, mbloops=10, max_iterations=50, gtol=1e-15, startidentity=True, normtargets=False,
#	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#msb4nomb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb4nomb", hidden_nodes = [4],
#	errfctname="msb", valfrac=0.25, shuffle=True,
#	mbsize=None, mbfrac=None, mbloops=1, max_iterations=50, gtol=1e-15, startidentity=False, normtargets=False,
#	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#msb4nombstartid = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb4nombstartid", hidden_nodes = [4],
#	errfctname="msb", valfrac=0.25, shuffle=True,
#	mbsize=None, mbfrac=None, mbloops=1, max_iterations=50, gtol=1e-15, startidentity=True, normtargets=False,
#	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#
#
#msre7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msre7min1", hidden_nodes = [7],
#	errfctname="msre", valfrac=0.25, shuffle=True,
#	mbsize=None, mbfrac=0.1, mbloops=10, max_iterations=50, gtol=1e-15, startidentity=True, normtargets=False,
#	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#mlsb7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "mlsb7min1", hidden_nodes = [7],
#	errfctname="mlsb", valfrac=0.25, shuffle=True,
#	mbsize=None, mbfrac=0.1, mbloops=10, max_iterations=50, gtol=1e-15, startidentity=False, normtargets=False,
#	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#
#
#mab7 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "mab7", hidden_nodes = [7],
#	errfctname="mab", valfrac=0.25, shuffle=True,
#	mbsize=None, mbfrac=None, mbloops=1, max_iterations=50, gtol=1e-15, startidentity=False, normtargets=False,
#	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#mab4 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "mab4", hidden_nodes = [4],
#	errfctname="mab", valfrac=0.25, shuffle=True,
#	mbsize=None, mbfrac=None, mbloops=1, max_iterations=50, gtol=1e-15, startidentity=False, normtargets=False,
#	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)
#
#"""
#
#trainparamslist = [
#	(s1mlparams, msb7),
#	(s2mlparams, msb7),
#]
#"""
#
#trainparamslist = [
#	(s1mlparams, mab7),
#	(s2mlparams, mab7),	
#]
#








"""
#### v3.3 #####


# w1 : very simple:

g1wmlparams1 = megalut.learn.MLParams(name = "g1w1",
	inputs = ["adamom_sigma", "adamom_flux"],
	auxinputs = ["pre_g1"],
	targets = ["tru_s1"],
	predictions = ["pre_g1_w1"])

g2wmlparams1 = megalut.learn.MLParams(name = "g2w1",
	inputs = ["adamom_sigma", "adamom_flux"],
	auxinputs = ["pre_g2"],
	targets = ["tru_s2"],
	predictions = ["pre_g2_w1"])

# v2 : same features as shapes:

g1wmlparams2 = megalut.learn.MLParams(name = "g1w2",
	inputs = ["adamom_sigma", "adamom_flux", "tru_psf_sigma", "adamom_g1", "adamom_g2", "tru_psf_g1", "tru_psf_g2"],
	auxinputs = ["pre_g1"],
	targets = ["tru_s1"],
	predictions = ["pre_g1_w2"])

g2wmlparams2 = megalut.learn.MLParams(name = "g2w2",
	inputs = ["adamom_sigma", "adamom_flux", "tru_psf_sigma", "adamom_g1", "adamom_g2", "tru_psf_g1", "tru_psf_g2"],
	auxinputs = ["pre_g2"],
	targets = ["tru_s2"],
	predictions = ["pre_g2_w2"])


# v3 : in between

g1wmlparams3 = megalut.learn.MLParams(name = "g1w3",
	inputs = ["adamom_sigma", "adamom_flux", "pre_g1", "pre_g2"],
	auxinputs = ["pre_g1"],
	targets = ["tru_s1"],
	predictions = ["pre_g1_w3"])

g2wmlparams3 = megalut.learn.MLParams(name = "g2w3",
	inputs = ["adamom_sigma", "adamom_flux", "pre_g1", "pre_g2"],
	auxinputs = ["pre_g2"],
	targets = ["tru_s2"],
	predictions = ["pre_g2_w3"])


shear1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1", hidden_nodes = [7],
	errfctname="msbw", valfrac=0.25, shuffle=True,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=50, gtol=1e-15, startidentity=False, normtargets=False,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=False, autoplot=True)

trainparamslist = [
	(g1wmlparams3, shear1),
	(g2wmlparams3, shear1),
]

"""





# What was working ok in Leiden (v2):
"""

g1mlparams = megalut.learn.MLParams(name = "g1",
	features = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	labels = ["tru_s1"],
	predlabels = ["pre_s1"])

g2mlparams = megalut.learn.MLParams(name = "g2",
	features = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"],
	labels = ["tru_s2"],
	predlabels = ["pre_s2"])






# Tenbilac settings:

shear1 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=50, mbloops=10, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)

# hmm, fast convergence, then overfits. Trying a larger mbsize:

shear2 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear2", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=100, mbloops=10, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)

"""


"""
# Taking over a previous shape training:
# Nope, did not work for some reason... maybe the very differnent normers ?
shear1to = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1to", hidden_nodes = [7],
	errfctname="msrb", valfrac=0.25, shuffle=True,
	mbsize=50, mbloops=5, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)

shear1msb = megalut.learn.tenbilacwrapper.TenbilacParams(name = "shear1msb", hidden_nodes = [7],
	errfctname="msb", valfrac=0.25, shuffle=True,
	mbsize=50, mbloops=5, max_iterations=50, startidentity=True,
	normtype="-11", actfctname="tanh", verbose=False, reuse=True, keepdata=True, autoplot=True)
"""


