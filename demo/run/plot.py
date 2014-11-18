"""
A model-example on how to make plots using megalut.plots
"""

import os
import megalut.plot
import matplotlib.pyplot as plt

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)


# Instead of just writing a script, you probably want to prepare your plot in
# form of a function or method somewhere in your project. Let's directly illustrate this.


def myplot(cat, filepath=None):
	"""
	Illustrates some plots
	"""
			
	# Especially if you have the same features to be shown in several panels,
	# start by defining the ranges and nice labels:
	
	g1 = megalut.plot.feature.Feature("adamom_g1_mean", -0.6, 0.6, "Measured g1")
	g2 = megalut.plot.feature.Feature("adamom_g2_mean", -0.6, 0.6, "Measured g2")

	# Specifying the range is not mandatory:
	sersicn = megalut.plot.feature.Feature("tru_sersicn", nicename = "True Sersic index")
	rho4 = megalut.plot.feature.Feature("adamom_rho4_mean", low=0.0) # One can also specify only one of the two limits.
	size = megalut.plot.feature.Feature("adamom_sigma_mean", 0.0, 6.0, nicename = "Measured size")


	fig = plt.figure(figsize=(12, 10))
	#fig.subplots_adjust(bottom=0.05, top=0.90, left=0.05, right=0.95, wspace=0.42)
	# Often not needed anymore (see tight_layout() below)
	
	ax1 = fig.add_subplot(221)	
	megalut.plot.scatter.scatter(ax1, cat, sersicn, rho4, size, title="Hello", text="Auto text", show_id_line=True) # 5th argument is colorbar
	
	ax2 = fig.add_subplot(222)	
	megalut.plot.scatter.scatter(ax2, cat, g1, g2, sidehists=True, title="World!")
	
	# Of course, one can still modify the axes afterwards !
	ax2.text(0.1, 0.3, "Some manually-placed text:\nnote the inverted y axis!", transform=ax2.transAxes)
	ax2.set_ylim(ax2.get_ylim()[::-1])
	

	ax3 = fig.add_subplot(223)
	megalut.plot.hist.hist(ax3, cat[cat["adamom_flag_mean"] == 0], size, color="blue", label="average flag = 0", title="A title")
	megalut.plot.hist.hist(ax3, cat[cat["adamom_flag_mean"] > 0], size, color="red", label="average flag > 0", text="Test")	
	ax3.legend()
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()	
	plt.close(fig) # Helps releasing memory when calling in large loops.


# And we call the function

if not os.path.exists("meascat.pkl"):
	raise RuntimeError("Please first run sim_meas_avg.py")

cat = megalut.tools.io.readpickle("meascat.pkl")
myplot(cat)
