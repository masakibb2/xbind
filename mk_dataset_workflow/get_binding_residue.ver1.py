import argparse
import itertools
import os

from franz.openrdf.sail.allegrographserver import AllegroGraphServer

def make_QUERY(fname,hetid):
	with open(fname) as fp:
		UniProtIDs = [line.strip() for line in iter(fp.readline,"")]
	values = "\n".join(["(<%s>)" % i for i in UniProtIDs])
	QUERY = """PREFIX pdbo:<http://rdf.wwpdb.org/schema/pdbx-v40.owl#>
PREFIX dcterms:<http://purl.org/dc/terms/>
PREFIX edam:<http://edamontology.org/>
PREFIX sio:<http://semanticscience.org/resource/>

select distinct ?uniprot ?sqno ?resname

where{
 ?het_res pdbo:atom_site.chem_comp.id "%s".
 ?het_asym  dcterms:isPartOf ?het_res;
            rdf:type sio:SIO_010432;
            rdfs:seeAlso ?pdb_res.
 ?pdb_res rdf:type edam:data_1756;
          rdfs:seeAlso ?unpres;
          pdbo:atom_site.chem_comp.id ?resname.
 ?unpres rdf:type edam:data_1756;
         dcterms:isPartOf ?uniprot;
         rdfs:label ?sqno.

VALUES ( ?uniprot ) {
%s
} 
} order by ?uniprot ?sqno
""" % (hetid,values)
	return QUERY


def iter_conn(fname,hetid):
	server = AllegroGraphServer(host = "http://tabiteuea.lodac.nii.ac.jp", port=10035, user="masaki070540", password="q6gzay")
	catalog = server.openCatalog(None)
	plbsp = catalog.getRepository("PLBSP_residue" ,"Repository.OPEN")
	conn = plbsp.getConnection()
	# Response is Dictionary that have two keys as "names" and "values".
	# "names" is record name. ?conn ?seq1 [res1, ch1, seq2, res2, ch2, dist, type] in this program's query
	# "values" is 2dimensional list. this list contain all records by Query.
	resp = conn.prepareTupleQuery("SPARQL", make_QUERY(fname,hetid))
	result = resp.evaluate_generic_query()
	keys = result["names"]
	for values in result["values"]:
		yield {k:v.strip('"') for k,v in zip(keys,values)}
	conn.close()


if __name__ == "__main__":
	desc = """Get specific ligand binding protein`s UniProt URI list.
	target ligand is specify using PDB HETATM Code. ex ( GLC, NAG, STR ... )"""	
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-lig',action="store",dest="lig")
	parser.add_argument('-fname',action="store",dest="fname")
	hetid = parser.parse_args().lig
	fname = parser.parse_args().fname
	if 1 <= len(hetid) <= 3:
		for record in iter_conn(fname,hetid):
			print record["uniprot"].strip("<").strip(">"),record["sqno"].split('"')[0],record["resname"]
	else:
		print "-lig option argument`s length must be in the range between 1 ~ 3."
