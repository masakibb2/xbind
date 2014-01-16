from pyevolve import GSimpleGA
from pyevolve import G1DList
from pyevolve import Selectors
from pyevolve import Initializators, Mutators

#import argparse
from core import pssm2feature
from core import dataset
from core import valid
from core import valid_log
from core import sampling

from sklearn import svm
import argparse
import math
import os
import json

## parameter fitting must be design each classfier.
## because fitting paramters is different by each classfier.

class cross_valid(object):
	# base class of evaluation function.
	def __init__(self,data,ans,out,sampling):
		self.data = data
		self.ans = ans
		self.out = out
		self.sampling = sampling

	def eval_xbp(self,chromosome):
		output = self.log_path(chromosome)
		clf,w = self.create_model(chromosome)
		db_name = "/mnt/result/log/" + output + ".log.db"
		if not os.path.exists(db_name):
			# construct univarate filter.
			d = dataset.datasets(self.data,20,self.ans)
			db = valid.valid_log("valid","result",output)
			db.mkTable()
			for cnt,(test_data_label,test_labels,pred_result) in enumerate(
				valid.paralell_valid(d,clf,window = w,k = 5,sampling = self.sampling.sampling,
							predict = predict)):
				db.update_db(test_data_label,test_labels,pred_result,cnt)
		
		vlog = valid_log.valid_log(db_name)
		AUCs = [vlog.AUC(cnt) for cnt in range(5)]
		AUC = sum(AUCs)/len(AUCs)
		return AUC
	
	def log_path(self,gene):
		pass

	def create_model(self,gene):
		pass

	def eval_gene(self,chromosome):
		self.create_model(chromosome)
		return self.eval_xbp(chromosome)

class cross_valid_SVC(cross_valid):
	# For evaluation function of SVC in gene algorithm.
	def __init__(self,data,ans,out,sampling,kernel = "rbf"):
		cross_valid.__init__(self,data,ans,out,sampling)
		self.kernel = kernel

	def log_path(self,chromosome):
		_c,_g,_w = chromosome
		w = 2 * int((abs(_w) + 1))
		c = int(_c)
		g = int( _g + math.log(1/float(w * 20),2))
		return "%s.%s.SVC.%s.%s.%s" % (self.out,w,self.kernel,c,g)

	def create_model(self,chromosome):
		_c,_g,_w = chromosome
		# w: odd value, min 2
		w = 2 * int((abs(_w) + 1))
		c = int( _c)
		g = int( _g + math.log(1/float(w * 20),2))
		clf = svm.SVC(C = 2**c,gamma = 2**g,class_weight = "auto")
		return clf,w
	
	def decode_gene(self,chromosome):
		_c,_g,_w = chromosome
		# w: odd value, min 2
		w = 2 * int((abs(_w) + 1))
		c = int( _c)
		g = int( _g + math.log(1/float(w * 20),2))
		db_name = "/mnt/result/log/" + self.log_path(chromosome) + ".log.db"
		vlog = valid_log.valid_log(db_name)
		AUCs = [vlog.AUC(cnt) for cnt in range(5)]
		AUC = sum(AUCs)/len(AUCs)
		result = vlog.optThr()
		thr,per = vlog.summary(result).next()
		return {"method":"sklearn.svm.SVC",
				"parameter":{"C":c,"gamma":g,"kernel":self.kernel,"window":w},
				"comment":"Predictor is created by scikit-learn. PSSM is created by psi-blast.",
				"performance":{"AUC":AUC,"sensitivity":per.sns(),"specificity":per.spf(),"MCC":per.mcc()},
				"threshold":thr}


def predict(clf,X):
	pred_val = clf.decision_function(X)
	# label_ attribute will be change classes_ in scikit-learn 1.5.
	#label = clf.classes_[0]
	#return [label * float(i) for i in list(pred_val)]
	# scikit -learn 's support label flip.
	return [float(i) for i in list(pred_val)]


def ga_fit(crs_valid):
	# Genome instance
	genome = G1DList.G1DList(3)
	genome.setParams(gauss_mu = 0, gauss_sigma = 1,rangemin = -20,rangemax = 20)

	# Change the initializator to Real values
	genome.initializator.set(Initializators.G1DListInitializatorReal)

	# Change the mutator to Gaussian Mutator
	genome.mutator.set(Mutators.G1DListMutatorRealGaussian)

	# The evaluator function (objective function)
	genome.evaluator.set(crs_valid.eval_gene)

	# Genetic Algorithm Instance
	ga = GSimpleGA.GSimpleGA(genome)
	#ga.selector.set(Selectors.GRouletteWheel)
	ga.selector.set(Selectors.GTournamentSelector)
	ga.setGenerations(3)
	ga.setPopulationSize(25)
	# do the parallel process.
	#ga.setMultiProcessing(True)
	# !! Multiprocess can be used when evaluation function can pickle object.
	# https://groups.google.com/forum/#!msg/pyevolve/nCTKWBFH4a4/nxDTsglgwU0J
	# rate of mutaition
	ga.setMutationRate(0.05)
	# rate of crossover
	ga.setCrossoverRate(0.8)
	# Do the evolution
	ga.evolve(freq_stats=1)

	# Best individual
	print "####",ga.bestIndividual()
	best_gene = ga.bestIndividual()
	return crs_valid.decode_gene(best_gene)


if __name__ == "__main__":
	desc = """Fit prediction model. 
Using machine learning algorithm is Support Vector Machine, 
and parameter fitting algorithm is Genetic Algorithm."""
	
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-pssm',action="store",dest="pssm")
	parser.add_argument('-answer',action="store",dest="answer")
	parser.add_argument('-name',action="store",dest="name")
	parser.add_argument('-out',action="store",dest="out")
	data = parser.parse_args().pssm
	ans = parser.parse_args().answer
	log_name = parser.parse_args().name
	
	nearbp = sampling.near_bp(ans,5,25)
	crs_valid = cross_valid_SVC(data,ans,log_name,nearbp)
	result = ga_fit(crs_valid)
	with open(parser.parse_args().out,"w") as out:
		out.write(json.dumps(result))
