



# How to run on Nicolas' sims:
#python run_allobs.py --imgpath /vol/euclid1/euclid1_raid1/nmartinet/CLUSTERING/condor/simulations/i070_a0_n333070_s0_m0/sim_070_24.5_27.0_a0.fits --incatpath /vol/euclid1/euclid1_raid1/nmartinet/CLUSTERING/condor/simulations/i070_a0_n333070_s0_m0/ingal_070_24.5to27.0.cat --outcatpath test.cat --workdir work --traindir /vol/fohlen11/fohlen11_1/mtewes/backgals-megalut/train_Nico2 --stampsize 64


# Testing if the galaxies on Nicolas' test image are now centered:
#python run_allobs.py --imgpath /vol/fohlen11/fohlen11_1/mtewes/backgals-megalut/obs_Nicolas/sim_001_24.5_27.0_a0.fits --outcatpath test.cat --workdir work --traindir /vol/fohlen11/fohlen11_1/mtewes/backgals-megalut/train_Nico2800 --stampsize 64


#With a real catalog:
python run_allobs.py --imgpath /vol/euclid1/euclid1_raid1/nmartinet/CLUSTERING/condor/simulations/i087_a0_n334087_s0_m0/sim_087_24.5_a0.fits --incatpath /vol/euclid1/euclid1_raid1/nmartinet/CLUSTERING/condor/simulations/i087_a0_n334087_s0_m0/ingal_087_24.5to27.0.cat --outcatpath test.cat --workdir work --traindir /vol/fohlen11/fohlen11_1/mtewes/backgals-megalut/train_Nico3b --stampsize 64 -p
