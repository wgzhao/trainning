# Makefile for tex building
#options
ARGS = -interaction=nonstopmode
CMD = /usr/bin/xelatex

TARGET = main.pdf

.PHONY:	everything clean all

everything:	${TARGET}

clean:		
	rm -f *~ *.{log,aux,nav,out,snm,toc,vrb}  ${TARGET} 
all:   	everything
two:	main.tex
	${CMD} ${ARGS} $< && ${CMD} ${ARGS} 
main.pdf: main.tex
	${CMD} ${ARGS} $<
