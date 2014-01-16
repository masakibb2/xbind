#!/bin/sh

#/home/ubuntu/galaxy-dist/tools/bilab/mkpssm.sh $1
python /home/ubuntu/galaxy-dist/tools/bilab/predict_pssm.py -i $1 > $2
#awk '{ print "Hello " $0 "!" }' < $1 > $2
