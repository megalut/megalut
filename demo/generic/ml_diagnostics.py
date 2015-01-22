"""
We read the ml from the train_and_predict.py script and the measurements from the 
draw_and_measure_sims.py script. Shows a few diagnostics plots.
"""


import logging
logging.basicConfig(level=logging.INFO)

import megalut
import matplotlib.pyplot as plt
import megalut.plot
import megalut.diagnostics

inputcat = megalut.tools.io.readpickle("meascat.pkl")
myml = megalut.tools.io.readpickle("myml.pkl")

diagnostics = megalut.diagnostics.learn(myml, inputcat)

fig1 = plt.figure()
diagnostics.compare_distrib(fig1)

fig2 = plt.figure()
diagnostics.compare_distrib(fig2, error=True)
plt.show()

exit()

traincat = myml.predict(inputcat)
validationcat = traincat[myml.training_set_index:]
traincat = traincat[:myml.training_set_index]

tru_g1 = megalut.plot.feature.Feature("tru_g1", -0.6, 0.6, "Nice label for true g1")
pre_g1 = megalut.plot.feature.Feature("pre_g1") # Minimal call, just to highlight the default behavior.

fig = plt.figure()
ax = fig.add_subplot(111)

res = megalut.plot.qqplot.qqplot(ax, traincat, pre_g1, label="Train", color="b", edgecolor="None")
res = megalut.plot.qqplot.qqplot(ax, validationcat, pre_g1, label="Cross-validation", color="g", edgecolor="None")
plt.grid()
plt.legend(loc=2)

plt.xlabel("Normal distribution quantiles")
plt.ylabel("Data quantiles")

fig = plt.figure()
ax = fig.add_subplot(111)

megalut.plot.qqplot.qqplot2dataset(ax, traincat, validationcat, pre_g1)

plt.show()