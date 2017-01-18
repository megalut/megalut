
import megalut.learn


g1ada4 = megalut.learn.MLParams(name = "g1ada4",
	inputs = ["adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_adamom"])

g1ada5 = megalut.learn.MLParams(name = "g1ada5",
	inputs = ["adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4", "adamom_g2"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_adamom"])

g1ada3 = megalut.learn.MLParams(name = "g1ada3",
	inputs = ["adamom_g1", "adamom_sigma", "adamom_rho4"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_adamom"])

g2ada3 = megalut.learn.MLParams(name = "g2ada3",
	inputs = ["adamom_g2", "adamom_sigma", "adamom_rho4"],
	targets = ["tru_g2"],
	predictions = ["pre_g2_adamom"])

g1ada2 = megalut.learn.MLParams(name = "g1ada2",
	inputs = ["adamom_g1", "adamom_sigma"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_adamom"])

g1ada4 = megalut.learn.MLParams(name = "g1ada-4", # old one, just used for the ref
	inputs = ["adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_adamom"])

	
g1fou3 = 	megalut.learn.MLParams(name = "g1fou3",
	inputs = ["fourierhann_adamom_g1", "fourierhann_adamom_sigma", "fourierhann_adamom_rho4"],
	targets = ["tru_g1"],
	predictions = ["pre_g1_fourier"])

#net = megalut.learn.tenbilacwrapper.TenbilacParams("tbl/Nico4/test.cfg")
net = megalut.learn.tenbilacwrapper.TenbilacParams("tbl/Nico4/MultNet.cfg")
#net = megalut.learn.tenbilacwrapper.TenbilacParams("tbl/Nico4/Net.cfg")

trainparamslist = [
	#(g1fou3, net)
	#(g1ada3, net),
	(g1ada4, net)
]

"""

g2adamom = megalut.learn.MLParams(name = "g2adamom",
	inputs = ["adamom_g2", "adamom_sigma"],
	targets = ["tru_g2"],
	predictions = ["pre_g2_adamom"])





s1adamom = megalut.learn.MLParams(name = "s1adamom",
	inputs = ["adamom_g1", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_s1"],
	predictions = ["pre_s1_adamom"])

s2adamom = megalut.learn.MLParams(name = "s2adamom",
	inputs = ["adamom_g2", "adamom_sigma", "adamom_flux", "adamom_rho4"],
	targets = ["tru_s2"],
	predictions = ["pre_s2_adamom"])




s1adamom = megalut.learn.MLParams(name = "g1only",
	inputs = ["adamom_g1"],
	targets = ["tru_s1"],
	predictions = ["pre_s1_adamom"])

#net = megalut.learn.tenbilacwrapper.TenbilacParams("tbl-MultNet-2.cfg")
#net = megalut.learn.tenbilacwrapper.TenbilacParams("tbl-Net-1.cfg")
net = megalut.learn.tenbilacwrapper.TenbilacParams("tbl-test.cfg")


trainparamslist = [
	(s1adamom, net),
	#(s2adamom, net)
]

"""







"""
s1fourier = megalut.learn.MLParams(name = "s1fourier",
	inputs = ["fourierhann_adamom_g1", "fourierhann_adamom_g2", "fourierhann_adamom_sigma", "adamom_flux", "fourierhann_adamom_rho4"],
	targets = ["tru_s1"],
	predictions = ["pre_s1_fourier"])

s2fourier = megalut.learn.MLParams(name = "s2fourier",
	inputs = ["fourierhann_adamom_g2", "fourierhann_adamom_g1", "fourierhann_adamom_sigma", "adamom_flux", "fourierhann_adamom_rho4"],
	targets = ["tru_s2"],
	predictions = ["pre_s2_fourier"])
"""
