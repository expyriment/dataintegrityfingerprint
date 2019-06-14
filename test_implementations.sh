#!/bin/bash

# Testing implementation
# call this script with a data folder as argument

echo "Bash"
bash bash/dif.sh ${1}
bash bash/dif.sh -c ${1} > checksums.bash

echo "Python2"
python2 python/dif.py -s ${1}

