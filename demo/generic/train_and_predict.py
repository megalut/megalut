"""
We read the measurements from the draw_and_measure_sims.py script, train a FANN, and self-predict the training set to see if it worked.
"""


import logging
logging.basicConfig(level=logging.INFO)

import megalut
import megalut.ml

inputcat = megalut.utils.readpickle("meascat.pkl")

# Important: we don't want to train on badly measured data!

inputcat = inputcat[inputcat["mes_flag"] == 0]

# That's what is available in our catalog:
#print inputcat.colnames

# What to train:
mymlparams = megalut.ml.MLParams(name = "foo", features = ["mes_g1", "mes_g2"], labels = ["tru_g1", "tru_g2"], predlabels = ["pre_g1", "pre_g2"])

# How to train:
myfannparams = megalut.ml.fannwrapper.FANNParams(name = "bar", nhid = [6, 6], max_iterations = 1000)


# Here we go:
myml = megalut.ml.ML(mymlparams, myfannparams, workdir = "myworkdir")

myml.train(inputcat)

outputcat = myml.predict(inputcat)

# Here we are:
#print outputcat


# A quick comparision between truth and predicted:
import matplotlib.pyplot as plt
plt.plot(outputcat["tru_g1"], outputcat["pre_g1"], "b.")
plt.xlabel("tru_g1")
plt.ylabel("pre_g1")
plt.show()


