import sparql
import argparse
import re

ENDPOINT="http://beta.sparql.uniprot.org/"

def make_QUERY(fname):
	with open(fname) as fp:
		UniProtIDs = [line.strip() for line in iter(fp.readline,"")]
	values = "\n".join(["(<%s>)" % i for i in UniProtIDs])
	

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

	

if __name__ == "__main__":
	desc = """Get Sequence from Uniprot using uniprot URI."""
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-fname',action="store",dest="fname")
	fname = parser.parse_args().fname
	UniProt = sparql.Service(ENDPOINT)
	result = UniProt.query(make_QUERY(fname))
	for uniprot,seq in result.fetchone():
		print "> %s" % uniprot.value
		print seq.value.sub("[BZJU]","X",seq)
