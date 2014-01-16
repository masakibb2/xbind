import argparse
import itertools
import os

from franz.openrdf.sail.allegrographserver import AllegroGraphServer

QUERY= lambda chebi_ID:"""PREFIX pdbo:<http://rdf.wwpdb.org/schema/pdbx-v40.owl#>
PREFIX dcterms:<http://purl.org/dc/terms/>
PREFIX edam:<http://edamontology.org/>
PREFIX sio:<http://semanticscience.org/resource/>
PREFIX up:<http://purl.uniprot.org/core/>
prefix obo:<http://purl.obolibrary.org/obo/> 

select distinct ?cc {
 ?chem_comp pdbo:link_to_chem_comp ?cc.   
 ?cc rdf:type obo:%s.
}
""" % chebi_ID

def iter_conn(chebi_ID):
	server = AllegroGraphServer(host = "http://tabiteuea.lodac.nii.ac.jp", port=10035, user="masaki070540", password="q6gzay")
	catalog = server.openCatalog(None)
	plbsp = catalog.getRepository("PLBSP_residue" ,"Repository.OPEN")
	conn = plbsp.getConnection()
	# Response is Dictionary that have two keys as "names" and "values".
	# "names" is record name. ?conn ?seq1 [res1, ch1, seq2, res2, ch2, dist, type] in this program's query
	# "values" is 2dimensional list. this list contain all records by Query.
	resp = conn.prepareTupleQuery("SPARQL", QUERY(chebi_ID))
	# Turned inferd mode ON 
	resp.setIncludeInferred(True)
	result = resp.evaluate_generic_query()
	keys = result["names"]
	for values in result["values"]:
		yield {k:v.strip('"') for k,v in zip(keys,values)}
	conn.close()


if __name__ == "__main__":
	desc = """Get specific HETATM Code from chebi Class."""
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-chebi',action="store",dest="chebi")
	chebi_ID = parser.parse_args().chebi
	for record in iter_conn(chebi_ID):
		print record["cc"].strip("<").strip(">").replace("http://rdf.wwpdb.org/cc/","")

