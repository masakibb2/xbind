import argparse

from core import dataset
from core import valid
from core import sampling
from sklearn import svm
from sklearn import preprocessing
def predict(clf,X):
	pred_val = clf.decision_function(X)
	return [float(i) for i in list(pred_val)]
		

def fit_model(fpssm,window,fans,clf,log_dir,log_name,predict,sampling = None,length = 20,tr_filter = None):
	proteins = dataset.datasets(fpssm,length,fans)
	valid_log = valid.valid_log("valid",log_dir,log_name)
	valid_log.mkTable()
	for cnt,(test_data_label,test_labels,pred_result) in enumerate(
		valid.valid(proteins,clf,window,sampling = sampling,tr_filter = tr_filter,predict = predict)):
		valid_log.update_db(test_data_label,test_labels,pred_result,cnt)
	valid_log.con.commit()

if __name__ == "__main__":
	desc = """Cross validation for binding site prediction model using support vector classfier."""

	parser = argparse.ArgumentParser(description=desc)
	# parameters (C,window) and kernel type
	parser.add_argument('-c',action="store",dest="c",type=int)
	parser.add_argument('-g',action="store",dest="g",type=int)
	parser.add_argument('-w',action="store",dest="w",type=int)
	parser.add_argument('-kernel',action="store",dest="kernel")
	# Binding Position
	parser.add_argument('-a',action="store",dest="a")
	# Data File 
	parser.add_argument('-f',action="store",dest="f")
	# name of saved database 
	parser.add_argument('-o',action="store",dest="o")
	parser.add_argument('-len',action="store",dest="len",type = int)
	
	if parser.parse_args().len is None:
		length = 20
	else:
		length = parser.parse_args().len
	
	c = parser.parse_args().c
	g = parser.parse_args().g
	window = parser.parse_args().w
	fans = parser.parse_args().a
	fpssm = parser.parse_args().f
	out = parser.parse_args().o
og_n
	if parser.parse_args().kernel is None:
		kernel = "rbf"
	else:
		kernel = parser.parse_args().kernel
	
	clf = svm.SVC(C = 2**c,gamma = 2**g,class_weight = "auto")
	scale =preprocessing.StandardScaler()
	#scale = preprocessing.MinMaxScaler()
	near_bp = sampling.near_bp("dataset/answer_mono.d4.0.txt",low=5,up=25)
	#predict = lambda clf,X:clf.decision_function(X)
	log_name = "%s.%s.SVC.%s.%s.%s" % (out,window,kernel,c,g)
	fit_model(fpssm,window,fans,clf,"result",log_name,predict,near_bp.sampling,length = length,tr_filter = scale)
