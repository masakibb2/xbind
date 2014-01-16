#!/bin/bash
#$ -S /bin/bash
#$ -v PATH
#PBS -v PATH


cd /home/ubuntu/galaxy-dist/tools/bilab/modules
./test_large.fasta_60.17464-bl.pl 0&
./test_large.fasta_60.17464-bl.pl 1&
./test_large.fasta_60.17464-bl.pl 2&
./test_large.fasta_60.17464-bl.pl 3&
wait

