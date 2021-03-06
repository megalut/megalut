"""
We read the measurements from the draw_and_measure_sims.py script, train a FANN, and self-predict
the training set to see if it worked.
"""


import logging
logging.basicConfig(level=logging.INFO)

import megalut
import megalut.learn

inputcat = megalut.tools.io.readpickle("meascat.pkl")

# Important: we don't want to train on badly measured data!

inputcat = inputcat[inputcat["mes_flag"] == 0]

# That's what is available in our catalog:
#print inputcat.colnames

# What to train:
mymlparams = megalut.learn.MLParams(name = "foo", inputs = ["mes_g1", "mes_g2"],
                                    targets = ["tru_g1", "tru_g2"], predictions = ["pre_g1", "pre_g2"])

# How to train:
myfannparams = megalut.learn.fannwrapper.FANNParams(name = "bar", hidden_nodes = [6, 6],
                                                    max_iterations = 1000)


# Here we go:
myml = megalut.learn.ML(mymlparams, myfannparams)

myml.train(inputcat)

# Note the name of the directory that was created to store the trained network!

outputcat = myml.predict(inputcat)

# Here we are:
#print outputcat


# Now we show a quick comparision between truth and predicted.
# The pure matplotlib way :
"""
import matplotlib.pyplot as plt
plt.plot(outputcat["tru_g1"], outputcat["pre_g1"], "b.")
plt.xlabel("tru_g1")
plt.ylabel("pre_g1")
plt.show()
"""

# Alternative to demonstrate the use of megalut.plot:

import matplotlib.pyplot as plt
import megalut.plot

fig = plt.figure()
ax = fig.add_subplot(111)

tru_g1 = megalut.tools.feature.Feature("tru_g1", -0.6, 0.6, "Nice label for true g1")
pre_g1 = megalut.tools.feature.Feature("pre_g1") # Minimal call, just to highlight the default behavior.

megalut.plot.scatter.scatter(ax, outputcat, tru_g1, pre_g1, color="green")
plt.show()
