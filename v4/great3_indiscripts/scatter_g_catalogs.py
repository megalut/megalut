import numpy as np
import matplotlib.pyplot as plt
import glob
import os

outdir = "/users/mtewes/fohlen/MegaLUT_GREAT3/out-control-ground-constant-v3"


outfiles = glob.glob(os.path.join(outdir, "*.cat"))

for outfile in outfiles:
	
	basename = os.path.basename(outfile)
	#print basename
	
	data = np.loadtxt(outfile)
	
	g1s = data[:,1]
	g2s = data[:,2]
	
	g1s = g1s[g1s < 5.0]
	g2s = g2s[g2s < 5.0]
	
	avgg1 = np.mean(g1s)
	avgg2 = np.mean(g2s)
	print basename, avgg1, avgg2

	plt.clf()
	plt.scatter(data[:,1], data[:,2], lw=0, s = 2)
	
	plt.vlines(avgg1, -1, 1)
	plt.hlines(avgg2, -1, 1)
	
	plt.xlabel("g1")
	plt.ylabel("g2")
	plt.xlim([-2, 2])
	plt.ylim([-2, 2])

	plt.savefig(basename + ".png")

