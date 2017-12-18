Sensitivity testing SHE, April 2017

Sims are drawn as EBulgeDisk, using parameter samples from Bryan.

Hard-coded are:
- gain
- noise


------------

TODO for London
 - sim-vo with 10 "datasets", to get 10 (m, c) pairs.




------------


We have 13 different settings:


- redoing the fiducial set
fid: sim-ts, sim-tw, ts1, ts2, tw1, tw2

extra: 
	- sim-ts half-noise: ts-hn-1-large (check adamomfailfrac, make mag-condi-bias plot, see if this does better)
	- sim-vs: vs-1-large (a large full-noise set)
	- train on hn
		- when done, check train ln and train hn agains sim-vs, condi-bias for magnitude
		hmm, both look relatively bad :-(
		-> going for ln, it seems to have a few less outliers at least for the bright galaxies.

	- tw relaunched with mbfrac 0.5 (did run with mbfrac 0.5 the other 4 PSF choices)


- pcode: PSF choices:
pp2: sim-ts, sim-tw, ts1, ts2, tw1, tw2
pp1: sim-ts, sim-tw, ts1, ts2, tw1, tw2
pm1: sim-ts, sim-tw, ts1, ts2, tw1, tw2
pm2: sim-ts, sim-tw, ts1, ts2, tw1, tw2



- ecode: ellipticity distribution:
ep2: sim-ts, sim-tw, ts1, ts2, tw1, tw2
ep1: sim-ts, sim-tw, ts1, ts2, tw1, tw2
em1: sim-ts, sim-tw, ts1, ts2, tw1, tw2
em2: sim-ts, sim-tw, ts1, ts2, tw1, tw2


- scode: sky level
sp2: sim-ts, sim-tw, ts1, ts2, tw1, tw2
sp1: sim-ts, sim-tw, ts1, ts2, tw1, tw2
sm1: sim-ts, sim-tw, ts1, ts2, tw1, tw2
sm2: sim-ts, sim-tw, ts1, ts2, tw1, tw2


------------

p_v1: no weight scaling
p_v2: setting all errors to 0.25
p_v3: setting w_max <-> sigma of 0.2 (multiplying all w by 25) 
p_v4: using wscale, with scalign catalog = entire weight training catalog

e_v1: no weight scaling
e_v4: same as p_v4
e_v5: same as e_v4, but using only the single best net of the weight training committee (no, didn't fix c biases)


s_v4

p_mine_v4: idem as p_v4, but using the first 6th of my vo-mimicdata-6
p_mine6_v4: idem as p_v4, but using all of my vo-mimicdata-6
e_mine6_v4
s_mine6_v4
