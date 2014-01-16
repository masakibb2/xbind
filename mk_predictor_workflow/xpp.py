import itertools
import argparse
import numpy

from sklearn import svm

from core import util
from core import dataset
from core import valid
from math import log

if __name__ == "__main__":
	idch2clust = "dataset/idch2clust_num.txt"
	clust2idch = "dataset/clust2idch.txt"
	blust = util.blust(idch2clust,clust2idch,3)
	kernel = "rbf"

	parser = argparse.ArgumentParser(description='Cross Validation')
	# parameters (C,gamma,window)
	parser.add_argument('-c',action="store",dest="c",type=int)
	parser.add_argument('-g',action="store",dest="g",type=int)
	parser.add_argument('-div',action="store",dest="div",type = int)
	# Data File 
	parser.add_argument('-pos',action="store",dest="pos")
	parser.add_argument('-neg',action="store",dest="neg")
	
	# name of saved database 
	parser.add_argument('-o',action="store",dest="o")
	c = parser.parse_args().c
	g = parser.parse_args().g
	pos = parser.parse_args().pos
	neg = parser.parse_args().neg
	div = parser.parse_args().div
	out = parser.parse_args().o

	clf = svm.SVC(C = 2**c,gamma = 2**g,class_weight = "auto")
	
	pos_proteins = dataset.prot_datasets(pos,20,is_positive = True)
	neg_proteins = dataset.prot_datasets(neg,20,is_positive = False)

	pos_crossed = [i for i in pos_proteins.fold(5)]
	neg_crossed = [i for i in neg_proteins.fold(5)]


	log_name = "%s.SVC.%s.%s.%s" % (out,kernel,c,g)
	valid_log = valid.valid_log_prot("valid","result",log_name)
	valid_log.mkTable()

	for cnt,((pos_tst,pos_tr),(neg_tst,neg_tr)) in enumerate(itertools.izip(pos_crossed,neg_crossed)):

		ptr_d_lbls,ptr_lbls,ptr_fmat = pos_tr.get_data(div=div).ToArray()
		ntr_d_lbls,ntr_lbls,ntr_fmat = neg_tr.get_data(div=div).ToArray()

		train_labels = numpy.hstack([ptr_lbls,ntr_lbls])
		train_features = numpy.vstack([ptr_fmat,ntr_fmat])

		clf.fit(train_features,train_labels)
		
		ptst_d_lbls,ptst_lbls,ptst_fmat = pos_tst.get_data(div=div).ToArray()
		ntst_d_lbls,ntst_lbls,ntst_fmat = neg_tst.get_data(div=div).ToArray()

		test_labels = numpy.hstack([ptst_lbls,ntst_lbls])
		test_features = numpy.vstack([ptst_fmat,ntst_fmat])
		test_data = ptst_d_lbls + ntst_d_lbls

		pred_vals = clf.decision_function(test_features)
		valid_log.update_db(test_data,test_labels,pred_vals,cnt)
	
	valid_log.con.commit()
