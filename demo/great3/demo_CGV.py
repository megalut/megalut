"""
A demo that runs on the CGV branch (fields 005-9)

.. note:: this demo is valid for branches C**, R**.
"""

###################################################################################################
# Imports
import megalut.great3
import megalut.meas
import megalut.sim
import megalut.learn
import megalut.tools

# Optional: set the logging level. If omitted, only warnings (and worse) will be shown.
import logging
logging.basicConfig(level=logging.INFO)
import numpy as np

###################################################################################################
# User-defined functions and classes needed for GREAT3
measfct = megalut.meas.galsim_adamom.measure
measfctkwargs = {} # The stamp size is automatically replaced/added to right value

class CGV_simparams(megalut.sim.params.Params):
    def getrad(self):
        return np.random.uniform(0.7, 2.7)
    
    def getflux(self):
        if np.random.uniform() < 0.25:
            return np.random.uniform(70.0, 220.0)
        else:
            return np.random.uniform(10.0, 70.0)
    
    def getg(self):
        theta = np.random.uniform(0.0, 2.0* np.pi) 
        eps = np.random.uniform(0.0, 0.7) 
        return (eps * np.cos(2.0 * theta), eps * np.sin(2.0 * theta))
        
    def getsersicn(self, ix=0, iy=0, n=1):
        return 1.0 + (float(iy)/float(n)) * 2.0    
        # Lower sersic index = broader

learnparams = megalut.learn.MLParams(
        name = "demo",
        features = ["adamom_g1", "adamom_g2", "adamom_flux"],
        labels = ["tru_g1","tru_g2"],
        predlabels = ["pre_g1","pre_g2"],
        )

fannparams=megalut.learn.fannwrapper.FANNParams(
        hidden_nodes = [20, 20],
        max_iterations = 500,
    )
simparam_name="cgv_test_1"
cgv_simparm=CGV_simparams(simparam_name)
###################################################################################################
# Start of the code

# Create an instance of the GREAT3 class
cgv=megalut.great3.great3.Run("control", "ground", "variable",
    datadir="/home/kuntzer/workspace/MegaLUT/great3_data_part",
    subfields=range(5,10))

# Now run the measurements on input images
cgv.meas("obs",measfct,measfctkwargs,ncpu=0)

# Make sim catalogs & images
cgv.sim(cgv_simparm,n=10,ncpu=0)

# Measure the observations with the same methods than the observation
cgv.meas("sim",measfct,measfctkwargs,ncpu=0,simparams=cgv_simparm)

# Train the ML
cgv.learn(learnparams=learnparams, mlparams=fannparams, simparam_name=simparam_name, 
          method_prefix="adamom_")
exit()
# Predict the output
cgv.predict(method_prefix="gs_")

# Write the output catalog
cgv.writeout("ML_FANN_demo_default")

# Prepare the presubmission file
# (This will fail as we work only on a subset of the data)
cgv.presubmit()
