import argparse

from core import dataset
from core import valid
from core import sampling
from sklearn import neighbors

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
	desc = """Cross validation for binding site prediction model using k neighbors classifier."""

	parser = argparse.ArgumentParser(description=desc)
	# parameters (K,leaf_size)
	parser.add_argument('-k',action="store",dest="k",type=int)
	#parser.add_argument('-l',action="store",dest="l",type=int)
	parser.add_argument('-w',action="store",dest="w",type=int)
	# Binding Position
	parser.add_argument('-a',action="store",dest="a")
	# Data File 
	parser.add_argument('-f',action="store",dest="f")
	# name of saved database 
	parser.add_argument('-o',action="store",dest="o")
	k = parser.parse_args().k
	#leaf_size = parser.parse_args().l
	window = parser.parse_args().w
	fans = parser.parse_args().a
	fpssm = parser.parse_args().f
	out = parser.parse_args().o
	
	clf = neighbors.KNeighborsClassifier(n_neighbors=k,leaf_size = 30)
	near_bp = sampling.near_bp("dataset/answer_mono.d4.0.txt",low=5,up=25)
	sampling = lambda X:sampling.under_sampling(near_bp.sampling(X))
	log_name = "%s.%s.KNeighbors.%s" % (out,window,k)
	fit_model(fpssm,window,fans,clf,"result",log_name,predict,sampling)
