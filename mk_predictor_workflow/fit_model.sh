t=$(date "+%s")
python /home/ubuntu/galaxy-dist/tools/bilab/mk_predictor_workflow/fit_model_paralell.py -pssm $1 -answer $2 -name $3.$t -out $4 > $5