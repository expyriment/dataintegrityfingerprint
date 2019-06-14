#!/bin/bash

# Testing implementation
# call this script with a data folder as argument

echo "Bash"
bash bash/dif.sh ${1}

echo "Python2"
python2 -s python/dif.py ${1}

