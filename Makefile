#*******************************************************************************
# Copyright (C) 2015, CERN
# # This software is distributed under the terms of the GNU General Public
# # License version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# # In applying this license, CERN does not waive the privileges and immunities
# # granted to it by virtue of its status as Intergovernmental Organization
# # or submit itself to any jurisdiction.
# #
# #
# #*******************************************************************************
SPECFILE=python-cern-sso.spec
REPOURL=git+ssh://git@gitlab.cern.ch:7999
# DB gitlab group
REPOPREFIX=/db

REPONAME=cern-sso-python

# Get all the package infos from the spec file
PKGVERSION=$(shell awk '/Version:/ { print $$2 }' ${SPECFILE})
PKGRELEASE=$(shell awk '/Release:/ { print $$2 }' ${SPECFILE} | sed -e 's/\%{?dist}//')
PKGNAME=$(shell awk '/Name:/ { print $$2 }' ${SPECFILE})
PKGID=$(PKGNAME)-$(PKGVERSION)
TARFILE=$(PKGID).tar.gz

sources:
	rm -rf /tmp/$(PKGID)
	mkdir /tmp/$(PKGID)
	cp -rv * /tmp/$(PKGID)/ > /dev/null 2>&1
	pwd ; ls -l
	cd /tmp ; tar --exclude .svn --exclude .git --exclude .gitkeep -czf $(TARFILE) $(PKGID)
	mv /tmp/$(TARFILE) .
	rm -rf /tmp/$(PKGID)

all:    sources

clean:
	rm $(TARFILE)

srpm:   all
	rpmbuild -bs --define '_sourcedir $(PWD)' ${SPECFILE}

rpm:    all
	rpmbuild -ba --define '_sourcedir $(PWD)' ${SPECFILE}

scratch:
	koji build db6 --nowait --scratch  ${REPOURL}${REPOPREFIX}/${REPONAME}.git#${PKGVERSION}
	koji build db7 --nowait --scratch  ${REPOURL}${REPOPREFIX}/${REPONAME}.git#${PKGVERSION}


build:
	koji build db6 --nowait ${REPOURL}${REPOPREFIX}/${REPONAME}.git#${PKGVERSION}
	koji build db7 --nowait ${REPOURL}${REPOPREFIX}/${REPONAME}.git#${PKGVERSION}

tag-qa:
	koji tag-build db6-qa $(PKGID)-$(PKGRELEASE).el6
	koji tag-build db7-qa $(PKGID)-$(PKGRELEASE).el7.cern

tag-stable:
	koji tag-build db6-stable $(PKGID)-$(PKGRELEASE).el6
	koji tag-build db7-stable $(PKGID)-$(PKGRELEASE).el7.cern
