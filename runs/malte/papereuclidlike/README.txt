en -

todo: 


- train w with SNC
	(and still test without): does this improve things ?
	trainings on tw-1-snc are running, to see. It might lower the amplitude of the selection effect, as low-snr gals with get lower weights ?
	trainings on tw-1-snc-snr-above-10 are also running DONE
	Still hope that we can avoid this.


STRANGE: train s2w has valfac 0.7, while train s1w is more around 1.4
Is this due to problems with tp ?
	
- see if tp with sizes down to 0.5 is helpful, or much worse. Modify tp in accordance.
	Training e is running (done)	
	Start training shear once done with e and sims (done).
	
	Yes, it is worse and degrades result. -> Put in paper: we have tested a training with smaller galaxies, without improving results.


- see if retraining w for a few its after updating the predictions with final tp is better.

YES

- see if a slightly better vo (with 2 times more data) makes plot look nicer (especially after the snrcut...)
	-	sim vo-2 is running (ec7)
YES


--> to show / determine the cut, make plot resi, with panel bottom right x = adamom_sigma, y = hlr, c = as current.
Sho wthi snext to bottom left panel, unchanged
DONE



--> launch a larger tw, try to push it to maximum size ?
tw2 running
