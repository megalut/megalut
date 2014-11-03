"""
A demo that runs on the VGV branch (fields 005-9)

.. note:: this demo is valid for branches V**.
"""

###################################################################################################
# Imports
import megalut.great3
import megalut.meas
import megalut.sim
import megalut.learn

# Optional: set the logging level. If omitted, only warnings (and worse) will be shown.
import logging
logging.basicConfig(level=logging.INFO)
import numpy as np

###################################################################################################
# User-defined functions and classes needed for GREAT3
measfct = megalut.meas.galsim_adamom.measure
measfctkwargs = {} # The stamp size is automatically replaced/added to right value

class vgv_simparams(megalut.sim.params.Params):
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
        features = ["adamom_g1", "adamom_g2", "adamom_flux","adamom_sigma"],
        labels = ["tru_g1","tru_g2"],
        predlabels = ["pre_g1","pre_g2"],
        )

psf_features=["tile_x_pos_deg","tile_y_pos_deg"]

fannparams=megalut.learn.fannwrapper.FANNParams(
        hidden_nodes = [30, 30, 30],
        max_iterations = 500,
    )
simparam_name="vgv_test_1"
vgv_simparm=vgv_simparams(simparam_name)
###################################################################################################
# Start of the code
"""
megalut.great3.var_psf_utils.separate("variable_psf", "ground", "variable",
                                      datadir="/home/kuntzer/workspace/MegaLUT/great3_data_part", 
                                      workdir="./vgv_data",subfields=range(5,7))
"""

# Create an instance of the GREAT3 class
vgv=megalut.great3.great3_tiled.Run("variable_psf", "ground", "variable",
    datadir="./vgv_data",
    subfields=[5])

# Now run the measurements on input images
vgv.meas("obs",measfct,measfctkwargs,ncpu=0)

# Make sim catalogs & images
vgv.sim(vgv_simparm,n=20,ncpu=0,nrea=4)

# Measure the observations with the same methods than the observation
vgv.meas("sim",measfct,measfctkwargs,ncpu=0,simparams=vgv_simparm)
exit()
# Train the ML
vgv.learn(learnparams=learnparams, mlparams=fannparams, simparam_name=simparam_name, 
          method_prefix="adamom_",psf_features=psf_features,overwrite=False)

# Predict the output
vgv.predict(overwrite=True)

# Write the output catalog
vgv.writeout("ML_FANN_demo_default")

# Prepare the presubmission file
# (This will fail as we work only on a subset of the data)
vgv.presubmit()
