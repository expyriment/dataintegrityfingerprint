#!/bin/bash

# Testing implementation
# call this script with a data folder as argument

echo "Bash"
time bash bash/dif.sh ${1}
#bash bash/dif.sh -c ${1} > checksums.bash


ABSPATH=$(realpath ${1})

cd python

echo "Python2"
time python2 -m dataintegrityfingerprint.cli ${ABSPATH}

echo "Python3"
time python3 -m dataintegrityfingerprint.cli ${ABSPATH}
#python3 -m dataintegrityfingerprint.cli -f checksums.bash 
#python3 -m dataintegrityfingerprint.gui

cd ..

echo "R"
time Rscript -e "source('R/dif.R');  master_hash(DIF('${1}'))"
#Rscript -e "source('R/dif.R');  write_checksums(DIF('${1}'), filename='checksums.R')"
#Rscript -e "source('R/dif.R');  master_hash(load_checksums('checksums.bash'))"
