import argparse
import itertools
import os

from franz.openrdf.sail.allegrographserver import AllegroGraphServer

def make_QUERY(fname,is_rm_mod = False):
	if is_rm_mod:
		mod_phrase = "minus { ?struct dcterms:hasPart ?het_asym; rdf:type obo:MOD_00000. }"
	else:
		mod_phrase = ""
	
       	with open(fname) as fp:
		LigandIDs = [line.strip() for line in iter(fp.readline,"")]
	values = "\n".join(['("%s")' % i for i in LigandIDs])
	QUERY = """PREFIX pdbo:<http://rdf.wwpdb.org/schema/pdbx-v40.owl#>
        PREFIX dcterms:<http://purl.org/dc/terms/>
        PREFIX edam:<http://edamontology.org/>
        PREFIX sio:<http://semanticscience.org/resource/>
        PREFIX obo:<http://purl.obolibrary.org/obo/>

select distinct ?uniprot {
      ?het_res pdbo:atom_site.chem_comp.id ?hetid.
      ?het_asym  dcterms:isPartOf ?het_res;
                 rdf:type sio:SIO_010432;
                 rdfs:seeAlso ?pdb_res.
      ?pdb_res rdf:type edam:data_1756;
               rdfs:seeAlso ?unpres.
      ?unpres rdf:type edam:data_1756;
              dcterms:isPartOf ?uniprot.

%s

      } VALUES ( ?hetid ) {
%s
      }
   """ % (mod_phrase,values)
	return QUERY



def iter_conn(fname,is_mod = False):
	server = AllegroGraphServer(host = "http://tabiteuea.lodac.nii.ac.jp", port=10035)
	catalog = server.openCatalog(None)
	plbsp = catalog.getRepository("PLBSP_residue" ,"Repository.OPEN")
	conn = plbsp.getConnection()
	# Response is Dictionary that have two keys as "names" and "values".
	# "names" is record name. ?conn ?seq1 [res1, ch1, seq2, res2, ch2, dist, type] in this program's query
	# "values" is 2dimensional list. this list contain all records by Query.
	resp = conn.prepareTupleQuery("SPARQL", make_QUERY(fname,is_mod))
	result = resp.evaluate_generic_query()
	keys = result["names"]
	for values in result["values"]:
		yield {k:v.strip('"') for k,v in zip(keys,values)}
	conn.close()


if __name__ == "__main__":
	desc = """Get specific ligand binding protein`s UniProt URI list.
	target ligand is specify using PDB HETATM Code. ex ( GLC, NAG, STR ... )"""	
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-fname',action="store",dest="fname")
	parser.add_argument('-modification',action="store_true",dest="mod")
	if parser.parse_args().mod is None:
		is_mod = False
	else:
		is_mod = parser.parse_args().mod
	fname = parser.parse_args().fname
	for record in iter_conn(fname,is_mod):
		print record["uniprot"].strip("<").strip(">")
