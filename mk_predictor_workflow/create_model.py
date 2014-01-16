from core import sampling
from core import dataset

try:
	import cPcikle as pickle
except:
	import pickle

import math
import gzip
import os
import json
import argparse

if __name__ == "__main__":

	desc = """Create Model File as Scikit learn format."""

	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-pssm',action="store",dest="pssm")
	parser.add_argument('-answer',action="store",dest="answer")
	parser.add_argument('-parameter',action="store",dest="parameter")
	parser.add_argument('-model',action="store",dest="name")
	
	# PSSM File
	fpssm = parser.parse_args().pssm
	
	# File of Binding residue information
	fans = parser.parse_args().answer
	
	# model file name
	log_name = parser.parse_args().name
	
	# Open the JSON formatted parameter file.
	with open(parser.parse_args().parameter) as fp:
		model_desc = json.load(fp)
	
	parameters = model_desc["parameter"]
	
	# dataset of pssm.
	window = parameters["window"]
	proteins = dataset.datasets(fpssm,20,fans)
	train_data = proteins.get_data(window)

	method = model_desc["method"]
	
	if method == "sklearn.svm.SVC":
		from sklearn import svm
		c,g,kernel = parameters["C"],parameters["gamma"],parameters["kernel"]
		clf = svm.SVC(C = 2**c,gamma = 2**g,class_weight = "auto")
		near_bp = sampling.near_bp(fans,low=5,up=25)
		train_data = near_bp.sampling(train_data)
		#log_name = "%s.%s.SVC.%s.%s.%s" % (out,window,kernel,math.log(c,2),math.log(g,2))
		
	elif method == "sklearn.svm.LinearSVC":
		from sklearn import svm
		c = parameters["C"]
		clf = svm.LinearSVC(C = c,class_weight = "auto")
		near_bp = sampling.near_bp(fans,low=5,up=25)
		train_data = near_bp.sampling(train_data)
		#log_name = "%s.%s.lnearSVM.%s" % (out,window,math.log(c,2))

	elif method == "sklearn.neighbors.KNeighborsClassifier":
		from sklearn import neighbors
		k = parameters["k"]
		clf = neighbors.KNeighborsClassifier(n_neighbors= k,leaf_size = 30)
		near_bp = sampling.near_bp(fans,low=5,up=25)
		sampling = lambda X:sampling.under_sampling(near_bp.sampling(X))
		train_data = sampling(train_data)
		#log_name = "%s.%s.KNeighbors.%s" % (out,window,k)
		
	elif method == "sklearn.ensemble.RandomForestClassifier":
		from sklearn import ensemble
		n_est = parameters["n_estimators"]
		max_ftr = parameters["max_featues"]
		clf = ensemble.RandomForestClassifier(n_estimators = n_est,
											  max_features = max_ftr)
		near_bp = sampling.near_bp(fans,low=5,up=25)
		u_sampling = lambda X:sampling.under_sampling(near_bp.sampling(X))
		train_data = u_sampling(train_data)
		#log_name = "%s.%s.RF.%s.%g" % (out,window,n_est,max_ftr)

	else:
		raise Exception,"method:%s is not supported now." % method
	
	train_data_label,train_labels,train_vectors = train_data.ToArray()
	clf.fit(train_vectors,train_labels)

	#model_name = "%s.model" % log_name
	model_name = log_name
	with open(model_name,"w") as fp:
		pickle.dump(clf,fp)
