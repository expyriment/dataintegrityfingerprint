#!/bin/bash
# Produce Data Integrity Fingerprint
#
# Usage:
#	dif.sh [-l] <DATA PATH>
#
# -p: print hash list
#
# O. Lindemann & F. Krause

if [ "$1" = "-p" ]; then
	find $2 -type f -print0 | xargs -0 sha256sum
else
	# find all files
	# make hash list
	# select only hashes
	# sort them
	# remove newlines
	# create master hash
	# print out only the master hash
	find $1 -type f -print0 \
			| xargs -0 sha256sum \
			| cut -d' ' -f1 \
			| sort \
			| tr -d '\n' \
			| sha256sum \
			| cut -d' ' -f1
fi
