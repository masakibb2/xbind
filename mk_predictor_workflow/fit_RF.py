import argparse

from core import dataset
from core import valid
from core import sampling
from sklearn import ensemble


def predict(clf,X):
	pred_val = clf.predict_proba(X)
	return [float(i) for i,j in list(pred_val)]

def fit_model(fpssm,window,fans,clf,log_dir,log_name,predict,sampling = None):
	proteins = dataset.datasets(fpssm,20,fans)
	valid_log = valid.valid_log("valid",log_dir,log_name)
	valid_log.mkTable()
	for cnt,(test_data_label,test_labels,pred_result) in enumerate(
		valid.valid(proteins,clf,window,
					sampling = sampling,
					predict = predict)):
		valid_log.update_db(test_data_label,test_labels,pred_result,cnt)
	valid_log.con.commit()

if __name__ == "__main__":
	desc = """Cross validation for binding site prediction model using Random Forest"""

	parser = argparse.ArgumentParser(description=desc)
	# parameters (C,window) and kernel type
	parser.add_argument('-nest',action="store",dest="n_est",type=int)
	parser.add_argument('-maxftr',action="store",dest="max_ftr",type=int)
	parser.add_argument('-w',action="store",dest="w",type=int)
	#parser.add_argument('-kernel',action="store",dest="kernel")
	# Binding Position
	parser.add_argument('-a',action="store",dest="a")
	# Data File 
	parser.add_argument('-f',action="store",dest="f")
	# name of saved database 
	parser.add_argument('-o',action="store",dest="o")
	n_est = parser.parse_args().n_est
	max_ftr = parser.parse_args().max_ftr
	window = parser.parse_args().w
	fans = parser.parse_args().a
	fpssm = parser.parse_args().f
	out = parser.parse_args().o

	clf = ensemble.RandomForestClassifier(n_estimators = n_est,max_features = max_ftr)
	near_bp = sampling.near_bp("dataset/answer_mono.d4.0.txt",low=5,up=25)
	u_sampling = lambda X:sampling.under_sampling(near_bp.sampling(X))
	log_name = "%s.%s.RF.%s.%g" % (out,window,n_est,max_ftr)
	
	fit_model(fpssm,window,fans,clf,"result",log_name,predict,u_sampling)
