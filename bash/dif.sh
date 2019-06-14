#!/bin/bash
# Produce Data Integrity Fingerprint
#
# Usage:
#	dif.sh [-l] <DATA PATH>
#
# -c: print checksums 
#
# O. Lindemann & F. Krause


if [ "$1" = "-c" ]; then
	cd $2
	find . -type f -print0 | xargs -0 shasum -a 256 | sort | sed 's/\.\///'
else
	# find all files
	# make hash list
	# sort them
	# remove '.\' before each file
	# create master hash
	# print out only the master hash
	cd $1
	find . -type f -print0 \
			| xargs -0 shasum -a 256 \
			| sort \
			| sed 's/\.\///' \
			| shasum -a 256 \
			| cut -d' ' -f1
fi
