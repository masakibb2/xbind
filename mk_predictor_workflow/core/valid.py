## Support For Other learning method.

import sqlite3
import os

def valid(dataset,clf,window,k = 5,sampling = None,tr_filter = None,predict = None):
	# clf: classfier object ( scikit-learn )
	# tr_filter : feature selection method ( scikit-learn ) need train.
	# sampling : dataset sampling method ( our definition )

	for test_dataset,train_dataset in dataset.fold(k):
		test_data = test_dataset.get_data(window)
		train_data = train_dataset.get_data(window)

		if sampling is not None:
			# samppling method only use training.
			train_data = sampling(train_data)

		train_data_label,train_labels,train_vectors = train_data.ToArray()
		test_data_label,test_labels,test_vectors = test_data.ToArray()
		
		if tr_filter is not None:
			#tr_filter.fit(train_data)
			train_data = tr_filter.fit_transform(train_vectors)
			test_data = tr_filter.transform(test_vectors)
		
		clf.fit(train_vectors,train_labels)
		pred_result = predict(clf,test_vectors)
		yield test_data_label,test_labels,pred_result


def paralell_valid(dataset,clf,window,k = 5,sampling = None,tr_filter = None,predict = None):
	# clf: classfier object ( scikit-learn )
	# tr_filter : feature selection method ( scikit-learn ) need train.
	# sampling : dataset sampling method ( our definition )
	import multiprocessing
	import time
	
	def _fit_model(q,train_vectors,train_labels):
		clf.fit(train_vectors,train_labels)
		pred_result = predict(clf,test_vectors)
		q.put((test_data_label,test_labels,pred_result))
	
	q = multiprocessing.Queue()
	Processes = []
	num_CPU = multiprocessing.cpu_count()
	for test_dataset,train_dataset in dataset.fold(k):
		while len([i for i in Processes if i.is_alive()]) >= num_CPU:
			time.sleep(30)
		test_data = test_dataset.get_data(window)
		train_data = train_dataset.get_data(window)

		if sampling is not None:
			# samppling method only use training.
			train_data = sampling(train_data)

		train_data_label,train_labels,train_vectors = train_data.ToArray()
		test_data_label,test_labels,test_vectors = test_data.ToArray()
		
		if tr_filter is not None:
			#tr_filter.fit(train_data)
			train_data = tr_filter.fit_transform(train_vectors)
			test_data = tr_filter.transform(test_vectors)
		
		p = multiprocessing.Process(target = _fit_model,args = (q,train_vectors,train_labels))
		Processes.append(p)
		p.start()
	
	for i in range(5):
		test_data_label,test_labels,pred_result = q.get()
		yield test_data_label,test_labels,pred_result


class valid_log(object):
	# Using to write log of cross validation.
	def __init__(self,table_name,dir_name,db_name):
		# iter_record is iterator of yielding records.
		# mktable is sql statement of create table
		# table_name is created table name by mktable().
		
		self._tbl = table_name
		saving_db = "/mnt/%s/log/%s.log.db" % (dir_name,db_name)
		self.db_name = saving_db
		if os.path.exists(saving_db):
			raise Exception,"%s is already exists." % saving_db
		self.con = sqlite3.connect(saving_db)
		
		
	def mkTable(self):
		mktbl = """
		create table valid (
		idch text,
		pos interger,
		isans interger,
		pred_score real,
		cnt interger
			);"""

		self.con.execute(mktbl)

	def update_db(self,tst_d_lbl,tst_lbls,dec_vals,cnt):
		for idch_pos,isans,dec_val in zip(tst_d_lbl,tst_lbls,dec_vals):
			idch,pos = idch_pos
			# For 2class problem
			# convert numpy.int to int
			record = [idch,pos,int(isans),float(dec_val),cnt]
			sql = "insert into %s values ( " % (self._tbl) + ", ".join(["?" for i in range(len(record))]) + ");"
			self.con.execute(sql,record)
		self.con.commit()

class valid_log_prot(valid_log):
	def mkTable(self):
		mktbl = """
		create table valid (
		idch text,
		isans interger,
		pred_score real,
		cnt interger
			);"""

		self.con.execute(mktbl)

	def update_db(self,tst_d_lbl,tst_lbls,dec_vals,cnt):
		for idch,isans,dec_val in zip(tst_d_lbl,tst_lbls,dec_vals):
			record = [idch,int(isans),float(dec_val),cnt]
			sql = "insert into %s values ( " % (self._tbl) + ", ".join(["?" for i in range(len(record))]) + ");"
			self.con.execute(sql,record)
		self.con.commit()
