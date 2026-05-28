# Makefile to test freeze
# set MYFRPY to path of MyFRpy interpreter to test
MYFRPY=myFRpy
# set OUTDIR to the temp directory for freeze
OUTDIR=outdir

test:
	$(MYFRPY) ../freeze.py -o $(OUTDIR) ok.py
	make -C $(OUTDIR)
	$(OUTDIR)/ok

