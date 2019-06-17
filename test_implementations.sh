#!/bin/bash

# Testing implementation
# call this script with a data folder as argument

echo "Bash"
bash bash/dif.sh ${1}
#bash bash/dif.sh -c ${1} > checksums.bash

cd python

echo "Python2"
python2 -m dataintegrityfingerprint.cli ${1}

echo "Python3"
python3 -m dataintegrityfingerprint.cli ${1}
#python3 -m dataintegrityfingerprint.cli -f checksums.bash 
#python3 -m dataintegrityfingerprint.gui

cd ..

echo "R"
Rscript -e "source('R/dif.R');  master_hash(DIF('${1}'))"
#Rscript -e "source('R/dif.R');  write_checksums(DIF('${1}'), filename='checksums.R')"
#Rscript -e "source('R/dif.R');  master_hash(load_checksums('checksums.bash'))"
