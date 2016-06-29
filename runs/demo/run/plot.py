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
	
	g1 = megalut.tools.feature.Feature("adamom_g1_mean", -0.6, 0.6, "Measured g1")
	g2 = megalut.tools.feature.Feature("adamom_g2_mean", -0.6, 0.6, "Measured g2")

	# Specifying the range is not mandatory:
	sersicn = megalut.tools.feature.Feature("tru_sersicn", nicename = "True Sersic index")
	rho4 = megalut.tools.feature.Feature("adamom_rho4_mean", low=0.0) # One can also specify only one of the two limits.
	size = megalut.tools.feature.Feature("adamom_sigma_mean", 0.0, 6.0, nicename = "Measured size")

	# Adding error bars is as simple as specifying a column name:
	g1_witherr = megalut.tools.feature.Feature("adamom_g1_mean", -0.6, 0.6, "Measured g1", errcolname="adamom_g1_std")
	g2_witherr = megalut.tools.feature.Feature("adamom_g2_mean", -0.6, 0.6, "Measured g2", errcolname="adamom_g2_std")

	fig = plt.figure(figsize=(17, 10))
	#fig.subplots_adjust(bottom=0.05, top=0.90, left=0.05, right=0.95, wspace=0.42)
	# Often not needed anymore (see tight_layout() below)
	
	ax = fig.add_subplot(2, 3, 1)	
	megalut.plot.scatter.scatter(ax, cat, sersicn, rho4, size, title="Hello", text="Auto text", show_id_line=True) # 5th argument is colorbar
	
	ax = fig.add_subplot(2, 3, 2)	
	megalut.plot.scatter.scatter(ax, cat, g1, g2, sidehists=True, title="World!")
	
	# Of course, one can still modify the axes afterwards !
	ax.text(0.1, 0.3, "Some manually-placed text:\nnote the inverted y axis!", transform=ax.transAxes)
	ax.set_ylim(ax.get_ylim()[::-1])
	

	ax = fig.add_subplot(2, 3, 3)
	megalut.plot.hist.hist(ax, cat[cat["adamom_flag_mean"] == 0], size, color="blue", label="average flag = 0", title="A title")
	megalut.plot.hist.hist(ax, cat[cat["adamom_flag_mean"] > 0], size, color="red", label="average flag > 0", text="Test")	
	ax.legend()
	
	ax = fig.add_subplot(2, 3, 4)
	megalut.plot.scatter.scatter(ax, cat, g1_witherr, g2_witherr, size, title="Demo using Features with errors",
		text="To get errorbars, simply specify errcolnames.\nEverything can be customized with kwargs.", s=20)
	
	ax = fig.add_subplot(2, 3, 5)
	megalut.plot.hexbin.hexbin(ax, cat, g1, g2, size, gridsize=15) # See the doc for many further options
	
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
