#!/bin/sh
MODEL=/home/ubuntu/galaxy-dist/tools/bilab/models
python /home/ubuntu/galaxy-dist/tools/bilab/predict_kspec.py -model $MODEL/lipid_bind_pro_2spec.model -thr 0.153 -fname $1 | sed -e "1d" > $2

