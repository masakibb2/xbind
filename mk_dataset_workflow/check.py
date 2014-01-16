from core import seq2feature
from core import protdb
if __name__ == "__main__":
    answer = {}
    with open("GLC_bind_residue.txt") as fp:
        for line in iter(fp.readline,""):
            uri,resnum,resname = line.strip().split()
            resnum = int(resnum)
            if answer.has_key(uri):
                answer[uri].update({resnum:resname})
                answer[uri]
            else:
                answer.update({uri:{resnum:resname}})
    
    
    for idch,seq in seq2feature.parse_fasta("GLC_bind.fasta"):
        for num,res in enumerate(seq):
            if answer[idch].has_key(num + 1):
                if res != protdb.AMINO[answer[idch][num + 1]]:
                    print idch,num + 1,res,protdb.AMINO[answer[idch][num + 1]]
