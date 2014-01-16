#!/bin/sh
MODEL=/home/ubuntu/galaxy-dist/tools/bilab/models
python /home/ubuntu/galaxy-dist/tools/bilab/predict_kspec.py -model $MODEL/2spec.mono.d4.0.sugar.vec.model -thr 0.060 -fname $1 | sed -e "1d" > $2

