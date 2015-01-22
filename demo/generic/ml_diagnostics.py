"""
We read the ml from the train_and_predict.py script and the measurements from the 
draw_and_measure_sims.py script. Shows a few diagnostics plots.
"""


import logging
logging.basicConfig(level=logging.INFO)

import megalut
import matplotlib.pyplot as plt
import megalut.diagnostics

inputcat = megalut.tools.io.readpickle("meascat.pkl")
myml = megalut.tools.io.readpickle("myml.pkl")

diagnostics = megalut.diagnostics.learn(myml, inputcat)

fig1 = plt.figure()
diagnostics.compare_distrib(fig1)

fig2 = plt.figure()
diagnostics.compare_distrib(fig2, error=True)
plt.show()