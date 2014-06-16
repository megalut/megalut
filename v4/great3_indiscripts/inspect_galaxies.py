import megalut
import numpy as np
import matplotlib.pyplot as plt



run = megalut.great3.run.Run(
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3/",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_GREAT3/",
	branch = ["real_galaxy", "ground", "constant"],
	version = "v3"
)



subfield = 116

galaxies = megalut.utils.readpickle(run.obsgalfilepath(subfield))

sel = []
for g in galaxies:
	
	if g.pre_g1 > 0.5 and g.pre_g2 < -0.3:
		sel.append(g)
		print g


g1s = np.array([g.pre_g1 for g in sel])
g2s = np.array([g.pre_g2 for g in sel])


plt.scatter(g1s, g2s)
plt.show()
