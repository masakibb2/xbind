import argparse

from core import dataset
from core import valid
from core import sampling
from sklearn import svm

def predict(clf,X):
	pred_val = clf.decision_function(X)
	return [float(i) for i in list(pred_val)]
		

def fit_model(fpssm,window,fans,clf,log_dir,log_name,predict,sampling = None,length = 20):
	proteins = dataset.datasets(fpssm,length,fans)
	valid_log = valid.valid_log("valid",log_dir,log_name)
	valid_log.mkTable()
	for cnt,(test_data_label,test_labels,pred_result) in enumerate(
		valid.valid(proteins,clf,window,
					sampling = sampling,
					predict = predict)):
		valid_log.update_db(test_data_label,test_labels,pred_result,cnt)
	valid_log.con.commit()

if __name__ == "__main__":
	desc = """Cross validation for binding site prediction model using linear svm"""

	parser = argparse.ArgumentParser(description=desc)
	# parameters (C,window)
	parser.add_argument('-c',action="store",dest="c",type=int)
	parser.add_argument('-w',action="store",dest="w",type=int)
	# Binding Position
	parser.add_argument('-a',action="store",dest="a")
	# Data File 
	parser.add_argument('-f',action="store",dest="f")
	# name of saved database 
	parser.add_argument('-o',action="store",dest="o")
	parser.add_argument('-len',action="store",dest="len",type = int)
	c = parser.parse_args().c
	window = parser.parse_args().w
	fans = parser.parse_args().a
	fpssm = parser.parse_args().f
	out = parser.parse_args().o
	if parser.parse_args().len is None:
		length = 20
	else:
		length = parser.parse_args().len
	
	clf = svm.LinearSVC(C = 2**c,class_weight = "auto")
	near_bp = sampling.near_bp("dataset/answer_mono.d4.0.txt",low=5,up=25)
	#predict = lambda clf,X:clf.decision_function(X)
	log_name = "%s.%s.lnearSVM.%s" % (out,window,c)
	fit_model(fpssm,window,fans,clf,"result",log_name,predict,near_bp.sampling,length = length)
