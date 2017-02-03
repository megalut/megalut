import megalut
import megalut.tools as tools
import includes
import measfcts
import glob
import os
import numpy as np

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

def savefig(fname,fig,fancy=False,pdf_transparence=True):
	import subprocess

	directory=os.path.dirname(os.path.abspath(fname))
	if not os.path.exists(directory):
		os.makedirs(directory)

	fig.savefig(fname+'.png',dpi=300)

	if fancy: 
		fig.savefig(fname+'.pdf',transparent=pdf_transparence)
		#fig.savefig(fname+'.eps',transparent=True)
		#os.system("epstopdf "+fname+".eps")
		command = 'pdfcrop %s.pdf' % fname
		#subprocess.check_output(command, shell=True)
		#os.system('mv '+fname+'-crop.pdf '+fname+'.pdf')
	

def set_fancy(txtsize=14):
	from matplotlib import rc
	#rc('font',**{'family':'serif','serif':['Palatino'],'size':16})
	rc('font',**{'size':txtsize})
	rc('font',**{'family':'sans-serif','sans-serif':['TeX Gyre Adventor']})#['Computer Modern Sans serif']})
	rc('text',**{'color':'white'})
	rc('axes',**{'labelcolor':'white', 'edgecolor':'white'})
	rc('xtick',**{'color':'white'})
	rc('ytick',**{'color':'white'})
	
set_fancy(22)

is_mse = True

if is_mse:
	traindir = os.path.join(includes.workdir, "train_simple_mse")
	note = "mse"
	note_full = "mean square error"
else:
	traindir = os.path.join(includes.workdir, "train_simple")
	note = "msb"
	note_full = "mean square bias"

component = "1"
main_pred = "s{}".format(component)
main_feat = Feature("tru_{}".format(main_pred))





outdirplots = "plots_specials"
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)
valprecatpath = os.path.join(traindir, "valprecat.pkl")
cat = megalut.tools.io.readpickle(valprecatpath)

print megalut.tools.table.info(cat)


cat["pre_g1"] = cat["pre_g1_adamom"]
#cat["pre_g1"] = cat["pre_g1_fourier"]

megalut.tools.table.addstats(cat, "pre_g1")
megalut.tools.table.addstats(cat, "adamom_g1")
megalut.tools.table.addrmsd(cat, "pre_g1", "tru_s1")
megalut.tools.table.addrmsd(cat, "adamom_g1", "tru_s1")
megalut.tools.table.addstats(cat, "snr")



cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])

s = megalut.tools.table.Selector("ok", [
	("in", "snr_mean", 20, 150),
	#("in", "tru_rad", 0, 11),
	("max", "adamom_frac", 0.01)
	]
	)

cat = s.select(cat)


ebarmode = "scatter"
#--------------------------------------------------------------------------------------------------
fig1 = plt.figure()
ax = plt.subplot()

if is_mse:
	color1 = "red"
else:
	color1 = "gold"
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_bias".format(component)), color=color1, alpha=0.5)
cat["res"] = cat["pre_g1_mean"] - cat["tru_s1"]
md = tools.metrics.metrics(cat,
						tools.feature.Feature("pre_g1_mean"), # Redefining those to get rid of any rea settings that don't apply to cbindata
						tools.feature.Feature("res"),
						pre_is_res=True)
print "MegaLUT",
if is_mse:
	print 'MSE', 
else:
	print 'MSB',
print md["m"] * 1e3 
val =  (np.abs((np.round(md["m"] * 100. / 1,1)) * 1))
print "MegaLUT val", val

ax.axhline(lw=2, color="white", ls="--")
ax.plot(np.linspace(np.amin(cat["tru_s1"]), np.amax(cat["tru_s1"])), np.linspace(np.amin(cat["tru_s1"]), np.amax(cat["tru_s1"]))*md["m"] + md["c"], lw =4, c=color1)

# Hide the right and top spines
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_ylim([-0.04, 0.04])
ax.set_xlabel("shear")
ax.set_ylabel("bias")
plt.text(0.75, 0.9, "{}\n{}%".format(note_full, val),
     horizontalalignment='center',
     verticalalignment='center',
     transform = ax.transAxes, color=color1)

fig2 = plt.figure()
ax = plt.subplot()
color2 = 'grey'
ax.axhline(lw=2, color="white", ls="--")
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("adamom_g{}_bias".format(component)), color=color2, alpha=0.5)

cat["res"] = cat["adamom_g1_mean"] - cat["tru_s1"]
md = tools.metrics.metrics(cat,
						tools.feature.Feature("adamom_g1_mean"), # Redefining those to get rid of any rea settings that don't apply to cbindata
						tools.feature.Feature("res"),
						pre_is_res=True)
print "adamom", md["m"] * 1e3 
ax.plot(np.linspace(np.amin(cat["tru_s1"]), np.amax(cat["tru_s1"])), np.linspace(np.amin(cat["tru_s1"]), np.amax(cat["tru_s1"]))*md["m"] + md["c"], lw =4, c=color2)
# Hide the right and top spines
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_ylim([-0.04, 0.04])
ax.set_xlabel("shear")
ax.set_ylabel("bias")
val =  int(np.abs((np.round(md["m"] * 100. / 5.0)) * 5))
print "amamom val", val
plt.text(0.75, 0.9, "crude measurements\n{}%".format(val),
     horizontalalignment='center',
     verticalalignment='center',
     transform = ax.transAxes, color=color2)

savefig(os.path.join(outdirplots, note), fig1, fancy=True, pdf_transparence=True)
savefig(os.path.join(outdirplots, "adamom"), fig2, fancy=True, pdf_transparence=True)
plt.show()



