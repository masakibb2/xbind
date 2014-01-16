#!/bin/bash

DIR=$1
echo "calclate PSSM in $DIR"

F=($(ls -1 ${DIR}/*.fasta))
cnt=0

echo "$F"


while [ $cnt -lt ${#F[@]} ]
do
  fas=${F[cnt]}
  fname=$(echo $fas | cut -d"/" -f2)
  blastpgp -d /mnt/data/nr -i ${F[cnt]} -Q $1/pssm/$fname.pssm -O $1/out/$fname.out -h 0.001 -j $2 -m 7 -a 4 -J
  #psiblast -db /mnt/data/nr -query ${F[cnt]} -inclusion_ethresh 0.001 -num_iterations 2  -out_ascii_pssm pssm/${fname}.ckp  -outfmt 5 -out $1/out/$fname.out.xml -num_threads 4 -comp_based_stats 1 
  cnt=$((cnt+1))
# 
# -out_pssm pssm/${fname}.ckp
done 
