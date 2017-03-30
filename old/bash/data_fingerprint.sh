#!/bin/bash
# Produce data_checksums and data fingerprint
#
# Usage:
#	data_fingerprint.sh [-l] <DATA PATH>
#
# -l: print hash list
#
# O. Lindemann

if [ "$1" = "-l" ]; then
	cd $2
	find . -type f -print0 | xargs -0 sha1sum
else
	cd $1
	LC_ALL=C
	find . -type f -print0 | xargs -0 sha1sum | sort | sha1sum | sed -e 's/ //g' -e 's/-//g'
fi
