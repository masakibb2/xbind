import argparse

import sqlite3
from core import eval_valid2
import math
import random

class performace(object):
	def __init__(self,TP=0,TN=0,FP=0,FN=0):
		self.per = {'TP':TP,'TN':TN,'FP':FP,'FN':FN}
	def _div(self,x,y):
			if sum(y) == 0 and sum(x) == 0:
				return 0.0
			else:
				return sum(x)/float(sum(y))
	def acc(self):
		suc = [self.per["TP"],self.per["TN"]]
		err = [self.per["FP"],self.per["FN"]]
		all = suc + err
		return self._div(suc,all)
	
	def spf(self):
		return self._div([self.per['TN']],[self.per['TN'],self.per['FP']])
	def sns(self):
		return self._div([self.per['TP']],[self.per['TP'],self.per['FN']])
	
	def ppv(self):
		return self._div([self.per['TP']],[self.per['TP'],self.per['FP']])

	def npv(self):
		return self._div([self.per['TN']],[self.per['TN'],self.per['FN']])

	def ber(self):
		return float(self.per["FP"] + self.per["FN"])/sum(self.per.values())


	def mcc(self):
		TP,TN = self.per["TP"],self.per["TN"]
		FP,FN = self.per["FP"],self.per["FN"]
		x = (TP*TN - FP*FN)
		y = math.sqrt((TP + FN)*(TN + FP)*(TP + FP)*(TN + FN))
		if y != 0:
			return x/y
		else:
			return 0
	
	def f_value(self):
		if self.sns() == 0 and self.ppv() == 0:
			return 0
		return (2*self.sns()*self.ppv())/(self.sns()+self.ppv())

class minmax(object):
	def __init__(self,low,up,con):
		where =  " where dist = 0 or (dist >= %s and dist <= %s)" % (low,up)
		sql = "select idch,max(dec_val),min(dec_val) from valid" + where + " group by idch;"
		self.mxmn = {idch:{"max":vmax,"min":vmin} for idch,vmax,vmin in con.execute(sql)}
	def conv(self,idch,dec_val):
		vmax = self.mxmn[idch]["max"]
		vmin = self.mxmn[idch]["min"]
		return (dec_val - vmin)/(vmax - vmin)

class zscore(object):
	class sd(object):
		def __init__(self):
			self.data = None
		
		def step(self,dec_val):
			if self.data is not None:
				self.data.append(dec_val)
			else:
				self.data = [dec_val]

		def finalize(self):
			avg = sum(self.data)/float(len(self.data))
			sd = math.sqrt(sum([(i - avg)**2  for i in self.data])/float(len(self.data)))
			return sd

	def __init__(self,low,up,con):
		where =  " where dist = 0 or (dist >= %s and dist <= %s)" % (low,up)
		con.create_aggregate("sd", 1, self.sd)
		sql = "select idch,avg(dec_val),sd(dec_val) from valid" + where + " group by idch;"
		self.zscore = {idch:{"avg":avg,"sd":sd} for idch,avg,sd in con.execute(sql)}
		
	def conv(self,idch,dec_val):
		avg = self.zscore[idch]["avg"]
		sd = self.zscore[idch]["sd"]
		return (dec_val - avg)/sd


class rank(object):
	def __init__(self,low,up,con):
		#where =  " where dist = 0 or (dist >= %s and dist <= %s)" % (low,up)
		sql = "select idch,pos,dec_val from valid order by dec_val;"
		self.rank = {}
		for idch,pos,dec_val in con.execute(sql):
			if self.rank.has_key(idch):
				rank = len(self.rank[idch])
				self.rank[idch].update({pos:rank + 1})
			else:
				self.rank.update({idch:{pos:1}})
		
	def conv(self,idch,pos):
		#return self.rank[idch][pos]
		return float(self.rank[idch][pos])/len(self.rank[idch])

class valid_log(object):
	def __init__(self,name):
		self._dbname = name
		self._con = sqlite3.connect(self._dbname)
		
	def __del__(self):
		self._con.close()
		
	def iter_dec(self,cnt,rev = False):
		if cnt is not None:
			sql_end = " where cnt = %s" % cnt
		else:
			sql_end = ""
		
		sql = "select idch,pos,isans,pred_score from valid"
		sql += sql_end
		if rev:
			#sql += " order by pred_score desc;"
			sql += " order by pred_score desc;"

		else:
			#sql += " order by pred_score;"
			sql += " order by pred_score;"


		for idch,pos,isans,pred_score in self._con.execute(sql):
			yield idch,pos,isans,pred_score

	def iterROC(self,rev = False):
		### Start: Answer All Positive ###
		# desition value stored 2length tupple.
		# (isans,decision_value)
		# the desicion_value is positive dataset if isans is True

		# calculate number of data.
		# default: order by increase.
		psize = self._con.execute("select count(*) from valid where isans = 1;").fetchall()[0][0]
		nsize = self._con.execute("select count(*) from valid where isans = -1;").fetchall()[0][0]

		#per = {'TP':psize,'TN':0,'FP':nsize,'FN':0}
		per = performace(TP = psize,TN = 0,FP = nsize,FN = 0)

		for idch,pos,isans,pred_score in self.iter_dec(cnt,rev= rev):
			#x = div(per['FP'],[per['TN'],per['FP']])
			x = 1 - per.spf()
			#y = div(per['TP'],[per['TP'],per['FN']])
			y = per.sns()
			
			yield x,y,pred_score
			
			if isans == 1:
				# Positive Data
				#per['FN']+=1
				per.per['FN']+=1
				#per['TP']-=1
				per.per['TP']+=1
			else:
				# Negative Data
				#per['FP']-=1
				per.per['FP']-=1
				#per['TN']+=1
				per.per['TN']-=1
		else:
			yield x,y,pred_score

	def iterPER(self,cnt,rev = False):
		### Start: Answer All Positive ###
		# desition value stored 2length tupple.
		# (isans,decision_value)
		# the desicion_value is positive dataset if isans is True

		# calculate number of data.
		# default: order by increase.
		if cnt is not None:
			sql_end = " and cnt = %s" % cnt
		else:
			sql_end = ";"
		psize = self._con.execute("select count(*) from valid where isans = 1 " + sql_end).fetchall()[0][0]
		nsize = self._con.execute("select count(*) from valid where isans = -1" + sql_end).fetchall()[0][0]

		#per = {'TP':psize,'TN':0,'FP':nsize,'FN':0}
		per = performace(TP = psize,TN = 0,FP = nsize,FN = 0)

		pred_scores = [(idch,pos,isans,pred_score) for idch,pos,isans,pred_score in self.iter_dec(cnt,rev= rev)]
		#for idch,pos,isans,pred_score in self.iter_dec(cnt,rev= rev):
		for idch,pos,isans,pred_score in sorted(pred_scores,key = lambda x: x[3],reverse = rev):
			yield per,pred_score
			
			if isans == 1:
				# Positive Data
				#per['FN']+=1
				per.per['FN']+=1
				#per['TP']-=1
				per.per['TP']-=1
			else:
				# Negative Data
				#per['FP']-=1
				per.per['FP']-=1
				#per['TN']+=1
				per.per['TN']+=1
		else:
			yield per,pred_score

	def iterROC2(self,cnt,rev = False):
		if rev:
			prev_dec = float("-inf")
		else:
			prev_dec = float("inf")
		
		for per,pred_score in self.iterPER(cnt,rev):
			if prev_dec != pred_score:
				yield 1-per.spf(),per.sns(),pred_score
			prev_dec = pred_score
		else:
			yield 1-per.spf(),per.sns(),pred_score
	
	def _AUC(self,cnt,rev = False):
		x1,y1 = None,None
		AUC = 0
		for x,y,dec in self.iterROC2(cnt,rev = rev):
			if x1 is None or y1 is None:
				x1,y1 = x,y
			AUC += abs(x - x1)*(y + y1)/2.0
			x1,y1 = x,y
		#AUC += abs(1 - x1)*(1 + y1)/2.0
		return AUC
	
	def AUC(self,cnt):
		v_auc = self._AUC(cnt,rev = False)
		return max([v_auc,1 - v_auc])

	def iterMCC(self,cnt,rev = False):
		for per,pred_score in self.iterPER(cnt,rev):
			yield pred_score,per.mcc()
			#f1 = 2*(per.ppv() * per.npv())/(per.ppv() + per.npv())
			#yield pred_score,f1

	def iterAGM(self,cnt,rev = False):
		for per,pred_score in self.iterPER(cnt,rev):
			yield pred_score,per.agm()

	def optThr_AGM(self,rev = False,cnt = None):
		result = {"max_AGM":float("-inf"),"thr":None}
		for pred_score,agm in self.iterAGM(cnt = cnt,rev = rev):
			if result["max_AGM"] < agm:
				result["max_AGM"] = agm
				result["thr"] = [pred_score]
			elif result["max_AGM"] == agm:
				result["thr"].append(pred_score)
		return result

	def optThr(self,rev = False,cnt = None):
		result = {"max_MCC":float("-inf"),"thr":None}
		for pred_score,mcc in self.iterMCC(cnt = cnt,rev = rev):
			if mcc is None:
				continue
			elif result["max_MCC"] < mcc:
				result["max_MCC"] = mcc
				result["thr"] = [pred_score]
			elif result["max_MCC"] == mcc:
				result["thr"].append(pred_score)
		return result

	def summary(self,result,rev = False,cnt = None):
		if not rev:
			crit = lambda pred_score,thr: pred_score >= thr
		else:
			crit = lambda pred_score,thr: pred_score <= thr
		
		for thr in result["thr"]:
			tot = [(pred_score,isans) for idch,pos,isans,pred_score in self.iter_dec(cnt = cnt,rev = rev)]
			TP = len([pred_score for pred_score,isans in tot if isans == 1 and crit(pred_score,thr)])
			FN = len([pred_score for pred_score,isans in tot if isans == 1 and not crit(pred_score,thr)])
			FP = len([pred_score for pred_score,isans in tot if isans == -1 and crit(pred_score,thr)])
			TN = len([pred_score for pred_score,isans in tot if isans == -1 and not crit(pred_score,thr)])
			yield thr,performace(TP = TP,TN = TN,FP = FP,FN = FN)
	
	def iterPR(self,cnt,rev = False):
		# For Presicion Recall curve
		if rev:
			prev_dec = float("-inf")
		else:
			prev_dec = float("inf")
		
		for per,pred_score in self.iterPER(cnt,rev):
			if prev_dec != pred_score:
				yield 1-per.spf(),per.sns(),pred_score
			prev_dec = pred_score
		else:
			yield per.ppv(),per.f_value(),pred_score
