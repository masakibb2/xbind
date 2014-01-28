import sparql
import argparse
import re

ENDPOINT="http://beta.sparql.uniprot.org/"
MAXREQUEST=100
def make_QUERY(ID_list):

	values = "\n".join(["(<%s>)" % i for i in ID_list])
	

	QUERY = """PREFIX up:<http://purl.uniprot.org/core/>
        select ?uniprot ?seq where
	{ ?uniprot a up:Protein .
          ?uniparc up:sequenceFor ?uniprot ; 
                   rdf:value ?seq .
        }
	VALUES ( ?uniprot ) {
%s
	}
   """ % values
	return QUERY

def print_fasta(result):
	for uniprot,seq in result.fetchone():
		print "> %s" % uniprot.value
		print re.sub("[BZJ]","X",seq.value)
		#print seq.value

	

if __name__ == "__main__":
	desc = """Get Sequence from Uniprot using uniprot URI."""
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-fname',action="store",dest="fname")
	fname = parser.parse_args().fname
	UniProt = sparql.Service(ENDPOINT)
	
	with open(fname) as fp:
		UniProtIDs = []
		for line in iter(fp.readline,""):
			UniProtID = line.strip()
			UniProtIDs.append(UniProtID)
			if len(UniProtIDs) >= MAXREQUEST:
				result = UniProt.query(make_QUERY(UniProtIDs))
				print_fasta(result)
				UniProtIDs = []
		else:
			if len(UniProtIDs) > 0:
				result = UniProt.query(make_QUERY(UniProtIDs))
				print_fasta(result)
			
