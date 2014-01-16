#!/bin/bash

#PBS -l nodes=1:ppn=1,walltime=72:00:00
#PBS -q default
#PBS -r n

BIN=/raid1/share/tools/blast/executables/blast/blast-2.2.22/bin/

cd $PBS_O_WORKDIR


if test ! -e $fas; then
    cur_dir=$(pwd)
    echo "${cur_dir} is here"
    echo -e "${fas} is not set\n"
    exit
else
    echo "fas is set"
fi
if test ! -e $pssm; then
	echo -e "${pssm} is not set\n"
	exit
else
    echo "pssm is set."
fi
if test ! -e $out; then
	echo -e "${out} is not set\n"
	exit
else
    echo "out is set."
fi

echo ${N1} ${N2} ${N3} ${N4} ${N5}
for i in ${N1} ${N2} ${N3} ${N4} ${N5}
  do
  # loop don't execute if N{i} is empty. [For bash specification]
  if test ! -e ${fas}$i; then
      echo -e "${fas}$i is not set\n"
      exit
  fi
  $BIN/blastpgp -d nr -i ${fas}/$i -Q ${pssm}/$i.pssm -o ${out}/$i.out -j 3 -h 0.001 -m 9
done