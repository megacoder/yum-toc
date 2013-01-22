TARGETS=all check clean clobber distclean install uninstall
TARGET=all

PREFIX=${DESTDIR}/opt
BINDIR=${PREFIX}/bin
SUBDIRS=

INSTALL=install

.PHONY: ${TARGETS} ${SUBDIRS}

all::	yum-toc.py

${TARGETS}::

clobber distclean:: clean

check::	yum-toc.py
	./yum-toc.py ${ARGS}

install:: yum-toc.py
	${INSTALL} -D yum-toc.py ${BINDIR}/yum-toc

uninstall::
	${RM} ${BINDIR}/yum-toc

ifneq	(,${SUBDIRS})
${TARGETS}::
	${MAKE} TARGET=$@ ${SUBDIRS}
${SUBDIRS}::
	${MAKE} -C $@ ${TARGET}
endif
