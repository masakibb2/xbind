from core import pssm2feature

import random
import time
import numpy
import itertools

import numpy

def _recur_list(rlist):
	"""
	>>> _recur_list([[1,2,3],4,[5,6,[7,8,9,[10]]]])
	>>> [1,2,3,4,5,6,7,8,9,10]
	"""
	out = []
	for i in rlist:
		if isinstance(i,list):
			out += _recur_list(i)
		else:
			out.append(i)
	return out

def split_dtst(lid,k = 5,seed = None):
	"""
	>>> len([i for i in range(10,1000) if len(split_dtst(range(i))) != 5])
	0
	
	## PASS:split dataset into k part.

	>>> len(_recur_list(split_dtst(range(144))))
	144

	>>> print [len(i) for i in split_dtst(range(144))]
	None
	>>> print [len(i) for i in split_dtst(range(143))]
	None
	>>> print [len(i) for i in split_dtst(range(142))]
	None
	>>> print [len(i) for i in split_dtst(range(141))]
	None
	>>> print [len(i) for i in split_dtst(range(140))]
	None
	"""
	if seed is not None:
		# initalize seed.
		print "Using seed: %f" % seed
		random.seed(seed)
	else:
		random.seed(time.time())

	random.shuffle(lid)
	n,m = divmod(len(lid),k)
	# amari no kazu dake +1 suru.
	_indx = [i*n + min(cnt + 1,m) for cnt,i in enumerate(range(1,k+1))]
	#_indx = [i*n for i in range(k + 1 - m)] + [i*n + 1 for i in range(k + 1 - m,k + 1)]
	#_indx[k] += m - 1 
	# !!! list[start:end] is not contained last element. 
	_indx[-1]+= 1
	start = 0
	divided = []
	for end in _indx:
		divided.append(lid[start:end])
		start = end
	return divided

def fold(ids,k = 5,seed = None):
	# !!! must be same length groups and ngroups !!!
	"""
	>>> [(i,j) for i,j in fold([[i] for i in range(5)])]
	None
	"""
	# split dataset into k part
	groups = split_dtst(ids,k,seed)
	
	for i in range(k):
		test = groups[i]
		train = groups[:i] + groups[i+1:]
		if isinstance(test,list):
			test = _recur_list(test)
		if isinstance(train,list):
			train = _recur_list(train)
		yield test,train

class datasets(object):
	# For Binding Site Prediction using sequence.
	# Negative dataset is non binding residue.
	def __init__(self,fpssm,length,flabel = None,part_ids = None):
		# file name of pssm.
		self._fpssm = fpssm
		self._length = length
		# pssm object.
		self.pssm = pssm2feature.pssm(fpssm,length)
		# file name of labels.
		# if flabel is None. This dataset is non labeled data. (ex.) input dataset of Prediction tools.
		self._flabel = flabel
		if part_ids is None:
			# IDs using dataset.
			self.part_ids = [idch for idch,pssm in self.pssm.parse_pssm()]
		else:
			self.part_ids = part_ids

	def fold(self,k):
		# split dataset for cross_validation.
		for test_ids,train_ids in fold(self.part_ids,k):
			test_data = datasets(self._fpssm,self._length,self._flabel,part_ids = test_ids)
			train_data = datasets(self._fpssm,self._length,self._flabel,part_ids = train_ids)
			yield test_data,train_data

	def get_data(self,window,part_ids = None):
		if part_ids is None:
			part_ids = self.part_ids
		
		# using this data object if you want to do sammpling or feature selection.
		data_label = []
		labels = []
		vectors = []
		for idch,idchs,label,vector in self.pssm.make_dataset(window,answer = self._flabel):
			if idch in part_ids:
				data_label += idchs
				labels += label
				vectors += vector
		
		return data(data_label,labels,vectors)

class prot_datasets(datasets):
	# For Binding Protein Prediction using sequence.
	def __init__(self,fpssm,length,part_ids = None,is_positive = True):
		# file name of pssm.
		self._fpssm = fpssm
		self._length = length
		# pssm object.
		self.pssm = pssm2feature.pssm(fpssm,length)
		self.is_positive = is_positive
		# file name of labels.
		if part_ids is None:
			# IDs using dataset.
			self.part_ids = [idch for idch,pssm in self.pssm.parse_pssm()]
		else:
			self.part_ids = part_ids

	def fold(self,k):
		# split dataset for cross_validation.
		for test_ids,train_ids in fold(self.part_ids,k):
			test_data = prot_datasets(self._fpssm,self._length,part_ids = test_ids,
									  is_positive = self.is_positive)
			train_data = prot_datasets(self._fpssm,self._length,part_ids = train_ids,
								      is_positive = self.is_positive)
			yield test_data,train_data

	def get_data(self,part_ids = None,div = 10):
		if part_ids is None:
			part_ids = self.part_ids
		
		# using this data object if you want to do sammpling or feature selection.
		data_label = []
		labels = []
		vectors = []
		for idch,label,vector in self.pssm.make_prot_dataset(self.is_positive,div = div):
			if idch in part_ids:
				data_label.append(idch)
				labels.append(label)
				vectors.append(vector)

		return data(data_label,labels,vectors)


class data(object):
	def __init__(self,data_label,labels,vectors):
		self.data_label = data_label
		self.labels = labels
		self.vectors = vectors

	def iter_data(self):
		for idch_pos,label,vector in itertools.izip(
			self.data_label,self.labels,self.vectors):
			idch,pos = idch_pos
			yield idch,pos,label,vector

	def iter_data_prot(self):
		for idch,label,vector in itertools.izip(
			self.data_label,self.labels,self.vectors):
			yield idch,label,vector

	def ToArray(self):
		return self.data_label,numpy.array(self.labels),numpy.array(self.vectors)
