import random
import itertools

from core import util
from core import dataset

## method for under sampling.

class near_bp(object):
	def __init__(self,fans,low,up):
		self.answer = util.ans(fans)
		self.low = low
		self.up = up

	def sampling(self,data):
		data_label = []
		labels = []
		vectors = []
		for idch,pos,label,vector in data.iter_data():
			dist = self.answer.get_dist(pos,idch)
			if self.low <= dist <= self.up or dist == 0:
				data_label.append((idch,pos))
				labels.append(label)
				vectors.append(vector)
	
		return dataset.data(data_label,labels,vectors)


def under_sampling(data):
		data_label = []
		labels = []
		vectors = []
		all_data = data.iter_data()
		for idch,iter_data in itertools.groupby(all_data,key= lambda x:x[0]):
			data_by_prot = [(idch,pos,label,vector) for idch,pos,label,vector in iter_data]
			num_bp = len([label for idch,pos,label,vector in list(data_by_prot) if label == 1])
			indx = [pos for pos,(idch,pos,label,vector) in enumerate(list(data_by_prot)) if label == -1]
			random.shuffle(indx)
			indx = indx[:num_bp]
			for idch,pos,label,vector in data_by_prot:
				if pos in indx or label == 1:
					data_label.append((idch,pos))
					labels.append(label)
					vectors.append(vector)
		
		return dataset.data(data_label,labels,vectors)
