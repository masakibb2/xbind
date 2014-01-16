import argparse

import sqlite3
from core import eval_valid3
import math

class performace(object):
	def __init__(self,TP,TN,FP,FN):
		self.per = {'TP':TP,'TN':TN,'FP':FP,'FN':FN}
	def _div(self,x,y):
			if sum(y) == 0 and sum(x) == 0:
				return 0.0
			else:
				return sum(x)/float(sum(y))
	def acc(self):
		suc = [self.per["TP"],self.per["TN"]]
		err = [self.per["FP"],self.per["FN"]]
		return self._div(suc,err)
	
	def spf(self):
		return self._div([self.per['TN']],[self.per['TN'],self.per['FP']])
	
	def sns(self):
		return self._div([self.per['TP']],[self.per['TP'],self.per['FN']])
	
	def ppv(self):
		return self._div([self.per['TP']],[self.per['TP'],self.per['FP']])

	def npv(self):
		return self._div([self.per['TN']],[self.per['TN'],self.per['FN']])

	def mcc(self):
		TP,TN = self.per["TP"],self.per["TN"]
		FP,FN = self.per["FP"],self.per["FN"]
		x = (TP*TN - FP*FN)
		y = math.sqrt((TP + FN)*(TN + FP)*(TP + FP)*(TN + FN))
		if y != 0:
			return x/y
		else:
			return None
	
	def gm(self):
		return math.sqrt(self.sns()*self.spf())

	def agm(self):
		if self.sns() == 0:
			return 0
		else:
			neg = float(self.per["FP"] + self.per["TN"])/sum(self.per.values())
			return (self.gm() + self.spf()*neg)/(1 + neg)
	
	def f_value(self):
		return (2*self.sns()*self.ppv())/(self.sns()+self.ppv())

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
			
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Cross Validation')
	# parameters (C,gamma,window)
	parser.add_argument('-o',action="store",dest="o")
	parser.add_argument('-mode',action="store",dest="mode")
	# reverse flag
	parser.add_argument('-r',action="store_true",dest="r")
	# Options
	parser.add_argument('-pdbids',action="store",dest="pdbids")
	name = parser.parse_args().o

	if parser.parse_args().r is not None:
		rev = parser.parse_args().r
	else:
		rev = False
	
	if parser.parse_args().pdbids is not None:
		with open(parser.parse_args().pdbids) as fp:
			part_ids = [line.strip() for line in iter(fp.readline,"")]
			print "read %s pdbids ..." % len(part_ids)
	else:
		part_ids = None

	mode = parser.parse_args().mode
	if mode not in ["AUC","thr","hist","mcc","ROC","mcc_by_prot"]:
		print "-mode option must be AUC or thr or hist or mcc"
	
	vlog = valid_log(name)

	if mode == "AUC":
		AUCs = [vlog.AUC(cnt) for cnt in range(5)]
		print name,sum(AUCs)/len(AUCs),AUCs
		#print name,vlog.AUC(cnt = None)
	elif mode == "hist":
		for cnt in range(5):
			for idch,pos,isans,pred_score in vlog.iter_dec(cnt = cnt,rev = rev):
				if part_ids is not None:
					if idch not in part_ids:
						continue
				print idch,pos,pred_score,isans,cnt
	elif mode == "thr":
		result = vlog.optThr(rev,cnt = None)
		print result
		for thr,per in vlog.summary(result,rev,cnt = None):
			print name,thr,"sns",per.sns(),"spf",per.spf(),"ppv",per.ppv(),"npv",per.npv(),"MCC",per.mcc()
	elif mode == "mcc":
		for pred_score,mcc in vlog.iterMCC(cnt = None,rev = rev):
			print pred_score,mcc
	elif mode == "ROC":
		for x,y,pred_score in vlog.iterROC2(cnt = None,rev = rev):
			print x,y,pred_score
	elif mode == "PR":
		for x,y,pred_score in vlog.iterPR(cnt = None,rev = rev):
			print x,y,pred_score
	
	elif mode == "mcc_by_prot":
		result = vlog.optThr(rev,cnt = None)
		for v_thr,per in vlog.summary(result,rev,cnt = None):
			thr = v_thr
		if rev:
			reverse = 1
		else:
			reverse = 0
		for idch,v_sns,v_spf,v_mcc,nbp in eval_valid3.valid_summary(name,thr,reverse = reverse):
			print idch,v_sns,v_spf,nbp,v_mcc
	elif mode == "perform":
		d = {"sensitivity":[],"specificity":[],"accuracy":[],"precision":[],"mcc":[]}
		for cnt in range(5):
			result = vlog.optThr(rev,cnt)
			for thr,per in vlog.summary(result,rev,cnt):
				print thr,"sensitivity",per.sns(),"specficity",per.spf(),"accuracy",per.acc(),"positive prediction value",per.ppv(),"negative prediction value",per.npv(),"MCC",per.mcc()
				d["sensitivity"].append(per.sns())
				d["specificity"].append(per.spf())	
				d["accuracy"].append(per.acc())	
				d["precision"].append(per.ppv())	
				d["mcc"].append(per.mcc())

		print "Average SNS:%s" % (sum(d["sensitivity"])/5.0)
		print "Average SPF:%s" % (sum(d["specificity"])/5.0)
		print "Average ACC:%s" % (sum(d["accuracy"])/5.0)
		print "Average PPV:%s" % (sum(d["precision"])/5.0)
		print "Average MCC:%s" % (sum(d["mcc"])/5.0)
	
	del vlog



