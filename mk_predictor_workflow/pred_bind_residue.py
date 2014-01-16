import argparse
import json

try:
	import cPcikle as pickle
except:
	import pickle

from core import dataset

if __name__ == "__main__":
	desc = """Create Model File as Scikit learn format."""

	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-model',action="store",dest="model")
	parser.add_argument('-pssm',action="store",dest="pssm")
	parser.add_argument('-parameter',action="store",dest="parameter")

	fmodel = parser.parse_args().model
	fpssm = parser.parse_args().pssm
	model_desc = parser.parse_args().parameter

	with open(parser.parse_args().parameter) as fp:
		model_desc = json.load(fp)
	
	parameters = model_desc["parameter"]
	window = parameters["window"]
	threshold = model_desc["threshold"]

	with open(fmodel) as fp:
		model = pickle.load(fp)
	in_proteins = dataset.datasets(fpssm,20)
	label = model.classes_[0]
	if model.__class__.__name__ == "SVC":
		## this model is sklearn.svm.SVC
		data_label,labels,vectors = in_proteins.get_data(window).ToArray()
		result = model.decision_function(vectors)
		for i,j in zip(data_label,result):
			prot_ID,sqno = i
			dec_val = j[0]
			if threshold < dec_val*label:
				isbp = 1
			else:
				isbp = 0
			print prot_ID,sqno,isbp,dec_val
