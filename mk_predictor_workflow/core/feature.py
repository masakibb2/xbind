import random
import util

class _feature(object):
	# Interface of feature vectors of a protein.
	def __init__(self,pdbid):
		self.pdbid = pdbid
		self.feature = []
	
	def append(self,vec):
		self.feature.append(vec)

class feature(object):
	# handler of feature vector file.
	def __init__(self,fname):
		self._fname = fname
		# self.size := a number of  dataset.
		self.size = 0
	
	def parse_feature(self):
		# parse feature
		"""
		>>> {k:v for k,v in parse_feature(".test.feature")}
		True
		"""
		prot_feature = None
		with open(self._fname) as fp:
			for rec in (line.strip() for line in iter(fp.readline,"")):
				if len(rec) == 0:
					continue
				if rec[0] == '>':
					if prot_feature is not None:
						yield prot_feature
					#
					idch = rec[1:].strip()
					prot_feature = _feature(idch)
					# count size of datasets.
					size += 1
				else:
					try:
						prot_feature.append([float(i) for i in rec.split()])
					except Exception:
						print prot_feature.append([float(i) for i in rec.split()])
						print prot_feature.idch
						exit()
			else:
				yield prot_feature



class label(object):
	def __init__(self,fsurf):
		with open(fsurf) as fp:
			# labels is stored as yaml.
			# FORMAT: { idch: [ label(int) for each residue] }
			# label is used for regression or clustering (multi class or single class).
			self.labels = yaml.load(fp.read())
	
	def get_label(self,pos,idch):
		# pos is sequensial residue number of feature vector.
		# NOT auth seq number.
		return labels[idch][pos]
	


class surf(label):
	def get_surf(self,pos,idch):
		# most near residue number for each binding site.
		if not self.surf.has_key(idch):
			# if input protein cannot calculate surface by Naccess, return -2
			return -2
		if not self.surf[idch].has_key(pos):
			# if input residue cannot calculate surface by Naccess, return -1
			return -1
		else:
			return self.surf[idch][pos]


class ans(object):
	# For make positive dataset
	def __init__(self,fans):
            with open(fans) as fp:
				self._ans = {i[0]:[int(pos) for pos in i[1:]]
                             for i in (line.strip().split() for line in iter(fp.readline,""))}

	def isans(self,pdbid,nsq):
            if not self._ans.has_key(pdbid):
                # not in ID => Negative set
                return False
            if nsq in self._ans[pdbid]:
                return True
            else:
                return False
	def get_pos(self,pdbid):
		if not self._ans.has_key(pdbid):
			print "## warnings pdbid = %s doesn't exists" % (pdbid)
			return None
		else:
			return self._ans[pdbid]
	
	def get_dist(self,pos,idch):
		# most near residue number for each binding site.
		if self.get_pos(idch) is None:
			return None
		near = min(self.get_pos(idch),key = lambda x:abs(x - pos))
		return abs(pos - near)

if __name__ == "__main__":
	import doctest
	doctest.testmod()

