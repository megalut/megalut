************************************************************************************
SkyNet v1.0
Copyright Philip Graff, Farhan Ferox, Michael P. Hobson
Release September 2013
************************************************************************************

Installation:

First set the directory where you would like to install SkyNet:  PREFIX=/your/install/directory

Then run:
1) ./configure --prefix=${PREFIX} (--enable-mpi)
2) make
3) make install

You should then add ${PREFIX}/bin to your PATH and ${PREFIX}/lib/pkgconfig to your PKG_CONFIG_PATH.

"--enable-mpi" is optional and only if you would like the MPI version.

************************************************************************************

Data:

You need to provide 2 sets of data:
(i) Training data to be given in <input_root>train.txt
(ii) Test data to be given in <input_root>test.txt

Data files should have comma separated entries. First line should have nin (no. of inputs), second nout (no. of outputs). For classification problems, nout should be the number of classes. If there are more than one categories (e.g. colour and gender) to be predicted then second line should be nout1, nout2, ... where nout1 is the no. of classes incategory 1 & so on.

After the first two lines, rest of the file consists of data entries with inputs for a given entry on one line & outputs on the line below the inputs. The output for classification problems consists of an integer value specifying the correct class with 0 meaning the first class.

See data/sinc* and data/cdata* for examples of data for regression and classiciation networks respectively.

************************************************************************************

Input File:

See inputs/sinc.inp & inputs/cdata.inp for example input files. The entries in input file are described below:

--------------------------------------------------------------------------
	Data-Handling options
--------------------------------------------------------------------------
input_root					root of the data files
classification_network		set it to 1 for classification nets, 0 for regression nets
mini-batch_fraction			what fraction of training data to be used?
validation_data				is there validation data to test against? (existence of <input_root>test.txt)
whitenin					whether to whiten the inputs and the transform to use
whitenout					whether to whiten the outputs and the transform to use

--------------------------------------------------------------------------
	Network and Training options
--------------------------------------------------------------------------
nhid						no. of nodes in the hidden layer. For multiple hidden layers, define nhid
							multiple times with the no. of nodes required in each hidden layer in order.
linear_layers				manually set (non-)linearity of layer connections
prior						set it to 1 if prior is to be used, 0 otherwise. Using prior is highly recommended
noise_scaling				set it to 1 if noise level (standard deviation of outputs) has to be estimated, 0 otherwise
set_whitened_noise			whether the noise is to be set on whitened data?
sigma						initial noise level, set on whitened data if set_whitened_noise=1, otherwise set on the unwhitened data.
confidence_rate				dimensionless distance limit, higher values are more aggressive. Recommended value is 0.1
confidence_rate_minimum		minimum confidence rate allowed, recommended value of 0.01
max_iter					max no. of iterations allowed
startstdev					the standard deviation of the initial random weights
convergence_function		the function to use for convergence testing, default is 4=error squared
historic_maxent				experimental implementation of MemSys's historic maxent option if required
resume						resume from a previous job

--------------------------------------------------------------------------
	Output options
--------------------------------------------------------------------------
output_root					root where the resultant network will be written to
verbose						verbosity level of feedback sent to stdout
iteration_print_frequency	After how many iterations, the feedback should be given to the user
calculate_evidence			whether to calculate the evidence at the convergence

--------------------------------------------------------------------------
	Autoencoder options
--------------------------------------------------------------------------
pretrain					perform pre-training?
nepoch						number of epochs to use in pre-training
autoencoder					make autoencoder network - inputs are outputs as well

--------------------------------------------------------------------------
	RNN options
--------------------------------------------------------------------------
recurrent					whether to use a RNN
norbias						whether to use a bias for the recurrent hidden layer connections

--------------------------------------------------------------------------
	BAMBI options
--------------------------------------------------------------------------
logL_range					range of logL values for determining whether or not to train in BAMBI
reset_alpha					reset hyperparameter upon resume
reset_sigma					reset hyperparameters upon resume
randomise_weights			add random factor to saved weights upon resume

--------------------------------------------------------------------------
	Debug options
--------------------------------------------------------------------------
fix_seed					whther to use a fixed seed?
fixed_seed					what seed to use if fix_seed=1

************************************************************************************

Running:

In setial modes:
./SkyNet <input file>
e.g.
./SkyNet inputs/sinc.inp

In parallel mode

mpirun -np n ./SkyNet <input file>
e.g.
mpirun -np n ./SkyNet inputs/sinc.inp

************************************************************************************

RNN:

Recurrent Neural Network has data at various time steps. Data consists of nin input & nout outputs. The data for RNN should still have nin followed by nout on the first line but the data entries should have inputs for all timesteps for a given data entry on one line followed by outputs for all timesteps for a given data entry.



