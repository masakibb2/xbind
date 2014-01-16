import sparql
import argparse
ENDPOINT="http://beta.sparql.uniprot.org/"

def make_QUERY(fname):
	with open(fname) as fp:
		UniProtIDs = [line.strip() for line in iter(fp.readline,"")]
	values = "\n".join(["(<%s>)" % i for i in UniProtIDs])
	

	QUERY = """PREFIX up:<http://purl.uniprot.org/core/>
        select ?seq ?uniprot
	{ select ?uniprot ?uniparc ?seq where
	{ ?uniprot a up:Protein ;
                     up:sequence ?s.
          ?s rdf:value ?seq.
	VALUES ( ?uniprot ) {
%s
	}
   }}""" % values

	return QUERY

	#?uniparc up:sequenceFor ?uniprot ; 
        #         <http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?seq .
	}

if __name__ == "__main__":
	desc = """Get Sequence from Uniprot using uniprot URI."""
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-fname',action="store",dest="fname")	
	fname = parser.parse_args().fname
	UniProt = sparql.Service(ENDPOINT)
	result = UniProt.query(make_QUERY(fname))
	for seq,uniprot in result.fetchone():
		print "> %s" % uniprot.value
		print seq.value
