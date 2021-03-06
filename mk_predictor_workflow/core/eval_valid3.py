import sqlite3
import math

def get_log(name,window,c,g):
	db_name = "result/log/%s.%s.%s.%s.log.db" % (name,window,c,g)
	return db_name

class per(object):
	# base class of evaluation method.
	
	def __init__(self):
		self.per = {'TP':0,'TN':0,'FP':0,'FN':0}
		
	def _div(self,x,y):
		if sum(y) == 0 and sum(x) == 0:
			return 0.0
		else:
			return sum(x)/float(sum(y))

	def step(self,pred_score,isans,dec_crit,is_reverse = 0):

		# is_reverse is flag how evalute decsion value
		# "decsion value <= criteria" or "decsion value >= criteria"
		if is_reverse == 1:
			self.dec_comp = lambda pred_score,dec_crit: pred_score <= dec_crit
		else:
			self.dec_comp = lambda pred_score,dec_crit: pred_score > dec_crit
		
		if isans == 1:
			if self.dec_comp(pred_score,dec_crit):
				self.per["TP"]+=1
			else:
				self.per["FN"]+=1
		else:
			if self.dec_comp(pred_score,dec_crit):
				self.per["FP"]+=1
			else:
				self.per["TN"]+=1

class acc(per):
	# evaluate function of accuracy.
	def finalize(self):
		suc = [self.per["TP"],self.per["TN"]]
		err = [self.per["FP"],self.per["FN"]]
		return self._div(suc,suc + err)


class spf(per):
	# evaluate function of specificity.
	def finalize(self):
		return self._div([self.per['TN']],[self.per['TN'],self.per['FP']])


class sns(per):
	# evaluate function of sensitivity.
	def finalize(self):
		return self._div([self.per['TP']],[self.per['TP'],self.per['FN']])


class ppv(per):
	# evaluate function of positive prediction value.
	def finalize(self):
		return self._div([self.per['TP']],[self.per['TP'],self.per['FP']])


class npv(per):
	# evaluate function of negativie prediction value.
	def finalize(self):
		return self._div([self.per['TN']],[self.per['TN'],self.per['FN']])


class mcc(per):
	def finalize(self):
		TP,TN = self.per["TP"],self.per["TN"]
		FP,FN = self.per["FP"],self.per["FN"]
		x = (TP*TN - FP*FN)
		y = math.sqrt((TP + FN)*(TN + FP)*(TP + FP)*(TN + FN))
		if y != 0:
			return x/y
		if x > 0:
			return 0
		else:
			return 0


class numbp(object):
	def __init__(self):
		self.cnt = 0
	
	def step(self,isans):
		if isans == 1:
			self.cnt += 1
	
	def finalize(self):
		return self.cnt


def valid_summary(name,thr = 0,low = 5,up = 25,reverse = 0):
	sql = """ select idch,sns(pred_score,isans,%(thr)s,%(rev)s),spf(pred_score,isans,%(thr)s,%(rev)s),
	mcc(pred_score,isans,%(thr)s,%(rev)s),numbp(isans)
	from valid group by idch;""" % {"thr":thr,"rev":reverse}
	with sqlite3.connect(name) as con:
		con.create_aggregate("sns", 4,sns)
		con.create_aggregate("spf", 4,spf)
		con.create_aggregate("mcc", 4,mcc)
		con.create_aggregate("numbp", 1,numbp)
		cur = con.cursor()
		#con.execute(view)
		for idch,v_sns,v_spf,v_mcc,nbp in cur.execute(sql):
			yield idch,v_sns,v_spf,v_mcc,nbp


