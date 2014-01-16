cd-hit -i $1    -o tmp_90 -c 0.9 -n 5 -A 0.5  -T 4 > db_90.log
cd-hit -i tmp_90 -o tmp_60 -c 0.6 -n 4 -A 0.5 -T 4 > db_60.log

psi-cd-hit.pl -i tmp_60 -o $2 -c 0.3 -ce 1e-6 -aS 0.5 -aL 0.5 -exec local -core 4