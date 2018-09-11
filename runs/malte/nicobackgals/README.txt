In Sep 2018, Nico changed the e distribution, and I update the training for this.

First, generated new sims, with etype2.
tp-1-uni2-etype2 (done)
tw-1-etype2 (done)
tp-1-e-ln-uni2-etype2 (done)
tp-1-e-uni2-etype2 (done) : for a pretraining without ln (just in case that it goes wrong with ln)
vo-1-etype2 (done)


Pretrain:

on tp-1-e-ln-uni2-etype2 :
nice -n 19 python run_21_train.py 100 e

or on tp-1-e-uni2-etype2 :
nice -n 19 python run_21_train.py 10 e <--- yes this worked after 2000 its, so i'll go with this one.



copy training results from tp-1-e-uni2-etype2 in tp-1-uni2-etype2-pretrain


on tp-1-uni2-etype2-pretrain :
nice -n 19 python run_21_train.py 10 s


running for 100 its to see how it goes
it goes well, so restarting with 1000 its

However I have to move to fohlen, as fohlen12 gets too slow.


Training of weights with 150 its.


##### CHANGE
- ZP should be 24.0, not 24.14
- We cut the g at 0.7, not 0.9
I only reapeat the weight training

-> new sims:

si-1-cat-etype2-emaxamp7
tw-1-etype2-emaxamp7
vo-1-etype2-emaxamp7

done, training 150 its, looks ok.





Sim generation
==============

tp-1 (8 M) : done
tp-1-uni2 (8M) : done

tp-1-e-uni2 (1M) : done

vo-1 (20 M) : done


tp-1-ln : done
tp-1-e : done
tw-1 : done

vp-2

vp-1-uni2

Not yet running:

vp-1



Training
==============

ln:
nice -n 19 python run_21_train.py 100 s


normal:
nice -n 19 python run_21_train.py 10 s

e:
nice -n 19 python run_21_train.py 10 e



Todo :
======










Prepare run_allobs.py
