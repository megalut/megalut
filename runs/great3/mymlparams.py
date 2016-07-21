"""
Reusable sets of Machine Learning parameters
"""
import megalut.learn


s1 = megalut.learn.MLParams(name = "s1",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_s1"],
	predictions = ["pre_s1"])

s2 = megalut.learn.MLParams(name = "s2",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_s2"],
	predictions = ["pre_s2"])

g1 = megalut.learn.MLParams(name = "g1",
	inputs = ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_g1"],
	predictions = ["pre_g1"])

g2 = megalut.learn.MLParams(name = "g2",
	inputs = ["adamom_g2", "adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_g2"],
	predictions = ["pre_g2"])

msb5 = megalut.learn.tenbilacwrapper.TenbilacParams(name = "msb5", hidden_nodes = [5], n=3,
	errfctname="msb", valfrac=0.5, shuffle=True,
	ininoisewscale = 0.05, ininoisebscale = 0.05,
	mbsize=None, mbfrac=0.1, mbloops=5, max_iterations=30, gtol=1e-20, startidentity=True,
	normtargets=False, normtype="-11", actfctname="tanh", oactfctname="iden",
	verbose=False, reuse=True, keepdata=False, autoplot=True)

trainparams = {
	'name':'msb5only',
	'list':[
		(g1, msb5),
		(g2, msb5),	
		]
	}
