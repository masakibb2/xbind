#import yaml

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

class surf(object):
	# For make positive dataset
	def __init__(self,fsurf):
		with open(fsurf) as fp:
			self.surf = yaml.load(fp.read())

	def get_surf(self,pos,idch):
		# most near residue number for each binding site.
		if not self.surf.has_key(idch):
			return -2
		if self.surf[idch].has_key(pos):
			return self.surf[idch][pos]
		else:
			return -1

class dataset(object):
	# Interface between dataset and libsvm
	
	def __init__(self,pdata,ndata,answer,window):
		# pdata is data source of positive dataset
		self._pfasta = pfasta
		# ndata is data sourcde of negative dataset.
		self._nfasta = nfasta
		# answer is description of position of binding residue
		self._ans = answer

		# list of id in postive dataset
		self.pids = [idch for idch,start,seq in fasta2seq(pfasta)]
		# list of id in negative dataset 
		self.nids = [rec[0] for rec in parse_fasta(nfasta)]

		self._ftr = ftr
		self._window = window

	def mkTest(self,part_pids,part_nids):
		"""
		>>> import feature
		>>> d = dataset(".test.fasta",".test.fasta","..//dataset/answer_monod4.0.cluster1.txt",lambda seq:feature.seq2frq(seq,2),10)
		>>> d.mkTest(['148lE'],['1af6_A_1_421'])
		None
		"""
		pdatasets = {idch:pvec for idch,pvec in mkdtst_test(self._pfasta,self._window,self._ftr,answer = self._ans) if idch in part_pids}
		ndatasets = {idch:pvec for idch,pvec in mkneg_test(self._nfasta,self._window,self._ftr) if idch in part_nids}
		pdatasets.update(ndatasets)

		return pdatasets.items()
	
	def mkTrain(self,part_pids,part_nids,size = 5):
		"""
		>>> import feature
		>>> d = dataset(".test.fasta",".test.fasta","..//dataset/answer_monod4.0.cluster1.txt",lambda seq:feature.seq2frq(seq,2),10)
		>>> d.mkTrain(['148lE'],['1af6_A_1_421'])
		None
		"""
		pdatasets = {idch:pvec for idch,pvec in mkdtst_train(self._pfasta,self._window,self._ftr,answer = self._ans) if idch in part_pids}
		ndatasets = {idch:pvec for idch,pvec in mkneg_train(self._nfasta,self._window,self._ftr,size = size) if idch in part_nids}
		pdatasets.update(ndatasets)

		return pdatasets.items()
