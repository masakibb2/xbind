for cnt in $(seq 0 9)
do
    wget "ftp://ftp.ncbi.nih.gov:21/blast/db/nr.0$cnt.tar.gz"
done

wget "ftp://ftp.ncbi.nih.gov:21/blast/db/nr.10.tar.gz"

