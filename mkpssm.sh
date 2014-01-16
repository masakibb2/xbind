# set user name of tosto.

mkdir .mkpssm
mkdir .mkpssm/out .mkpssm/pssm

python /home/ubuntu/galaxy-dist/tools/bilab/split_fasta.py $1 .mkpssm
sudo /home/ubuntu/galaxy-dist/tools/bilab/calc_pssm.sh .mkpssm $2

python /home/ubuntu/galaxy-dist/tools/bilab/joinpsm.py .mkpssm/pssm > $1.pssm

#rm -r .mkpssm