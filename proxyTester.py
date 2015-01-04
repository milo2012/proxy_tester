import httplib
import operator
import timeit
import requests
import sys
import argparse
import requesocks
import multiprocessing

testUrl="http://whatismyipaddress.com/"
resultList=[]
proxyList=[]

socks4List=[]
socks5List=[]
httpList=[]

def execute1(jobs, num_processes=2):
    	work_queue = multiprocessing.Queue()
    	for job in jobs:
        	work_queue.put(job)

    	result_queue = multiprocessing.Queue()

   	worker = []
    	for i in range(num_processes):
        	worker.append(Worker1(work_queue, result_queue))
        	worker[i].start()

    	results = []
    	while len(results) < len(jobs): #Beware - if a job hangs, then the whole program will hang
        	result = result_queue.get()
        	results.append(result)
    	results.sort() # The tuples in result are sorted according to the first element - the jobid
    	return (results)

class Worker1(multiprocessing.Process):
	def __init__(self,work_queue,result_queue,):
        	multiprocessing.Process.__init__(self)
        	self.work_queue = work_queue
        	self.result_queue = result_queue
        	self.kill_received = False
   	def run(self):
        	while (not (self.kill_received)) and (self.work_queue.empty()==False):
           		try:
                		job = self.work_queue.get_nowait()
            		except:
                		break
            		(jobid,proxyHost,proxyHost) = job
            		rtnVal = (jobid,proxyHost,getURL1(proxyHost))
            		self.result_queue.put(rtnVal)

def chunk(input, size):
    	return map(None, *([iter(input)] * size))

def testSocks(proxyHost):
	result = ""
	tempResult=testSocks4(proxyHost)
	if "503" in tempResult:
		tempResult1=testSocks5(proxyHost)
		if "503" in tempResult1:
			result = tempResult1
		else:
			result = tempResult1
			return result
	else:
		result = tempResult
		return result
def testSocks4(proxyHost):
	#print "Testing socks proxy: http://"+proxyHost
	import socks
	import socket
	import urllib2
	hostNo = proxyHost.split(":")[0]
	portNo = proxyHost.split(":")[1]
			
	proxyTypeList=[]
	proxyTypeList.append("socks4")
			
	for proxyType in proxyTypeList:
		session = requesocks.session()
		if proxyType=="socks4":
			session.proxies = {'http': 'socks4://'+hostNo+':'+portNo}
		try:
			session.timeout = 3
			r = session.get('http://www.engadget.com/')

			statusCode = str(r.status_code)

			if statusCode=="200":
				result = ((proxyHost,"",proxyType))
				resultList.append(result)
				if proxyType=="socks4":
					return proxyHost+"\tsocks4\t200"
			else:
				return proxyHost+"\t"+proxyType+"\t"+statusCode
		except Exception as e:
			return proxyHost+"\t"+proxyType+"\t503"

def testSocks5(proxyHost):
	#print "Testing socks proxy: http://"+proxyHost
	import socks
	import socket
	import urllib2
	hostNo = proxyHost.split(":")[0]
	portNo = proxyHost.split(":")[1]
			
	proxyTypeList=[]
	proxyTypeList.append("socks5")
			
	for proxyType in proxyTypeList:
		session = requesocks.session()
		if proxyType=="socks5":
			session.proxies = {'http': 'socks5://'+hostNo+':'+portNo}
		try:
			session.timeout = 3
			r = session.get('http://www.engadget.com/')

			statusCode = str(r.status_code)

			if statusCode=="200":
				result = ((proxyHost,"",proxyType))
				resultList.append(result)
				if proxyType=="socks5":
					return proxyHost+"\tsocks5\t200"
			else:
				return proxyHost+"\t"+proxyType+"\t"+statusCode
		except Exception as e:
			return proxyHost+"\t"+proxyType+"\t503"


def getURL1(proxyHost):
	proxies = {
	  "http": "http://"+proxyHost,
	}
		
	global statusCode
	try:
		#print "Testing http proxy: http://"+proxyHost	
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
		r = requests.head("http://whatismyipaddress.com/", proxies=proxies, timeout=3, headers=headers)
		statusCode=str(r.status_code)
		if statusCode!="200":
			result = testSocks4(proxyHost)
			if "503" in str(result):
				if options.v:
					print result
				result = testSocks5(proxyHost)
				if options.v:
					print result
				return result
			else:
				return result
		else:
			return proxyHost+"\thttp\t200"
	except Exception as e: 
		result = testSocks4(proxyHost)
		if "503" in str(result):
			if options.v:
				print result
			result = testSocks5(proxyHost)
			if options.v:
				print result
			return result
		else:
			return result


if __name__ == '__main__':
    	parser = argparse.ArgumentParser()
    	parser.add_argument('-file',dest='ipFile',action='store',help='[file containing list of proxies]')
    	parser.add_argument('-time', action='store_true', help='[check latency]')
    	parser.add_argument('-v', action='store_true', help='[verbose mode]')
    	options = parser.parse_args()

    	if len(sys.argv)==1:
        	parser.print_help()
        	sys.exit()
    	else:
		with open(options.ipFile) as f:
			proxyList = f.read().splitlines()
			proxyList=list(set(proxyList))

		tempList1 = chunk(proxyList, 50)
		totalCount=len(tempList1)
		count = 1 
		for proxyList in tempList1:
			jobs = [] 
			jobid=0
			print "- Set "+str(count)+" of "+str(len(tempList1))
			for proxyHost in proxyList:
				try:
					print "- Testing: "+proxyHost
					jobs.append((jobid,proxyHost,proxyHost))
					jobid = jobid+1
				except TypeError:
					continue
		
			numProcesses = 50
			resultList = execute1(jobs,numProcesses)
			for result in resultList:
				if result[2]!=None:
					if "503" in result[2]:
						if options.v:
							print result[2]
					else:
						if "socks4" in str(result[2]):
							socks4List.append(result[2])
						if "socks5" in str(result[2]):
							socks5List.append(result[2])
						if "http" in str(result[2]):
							httpList.append(result[2])
						print result[2]
			#statusCode=""
			count+=1

			#totalTime = timeit.timeit(getURL1,number=1)
			#if statusCode=="200":
			#	print proxyHost+"\thttp\t"+statusCode+"\t"+str(totalTime)+"s"
			#	result = ((proxyHost,totalTime,"http"))
			#	resultList.append(result)
			#else:
			#	if options.v:
			#		print proxyHost+"\thttp\t"+statusCode

		print "\n------------------------------------------------------------------"
		if len(socks4List)>0:
			print "\nWorking Socks4 Proxies"
			tempList=[]
			for x in socks4List:
				hostNo =  (x.split("\t"))[0]
				if options.time:
					totalTime = timeit.timeit("testSocks4(hostNo)",number=1, setup="from __main__ import testSocks4, hostNo")					
					print hostNo+"\t"+str(totalTime)
					tempList.append([hostNo,totalTime])
				else:
					print hostNo
			if options.time:
				if len(tempList)>0:
					tempList = sorted(tempList, key=operator.itemgetter(1))
					for x in tempList:
						print x[0]+"\t"+str(x[1])

		if len(socks5List)>0:
			print "\nWorking Socks5 Proxies"
			tempList=[]
			for x in socks5List:
				hostNo =  (x.split("\t"))[0]
				if options.time:
					totalTime = timeit.timeit("testSocks5(hostNo)",number=1, setup="from __main__ import testSocks5, hostNo")					
					#print hostNo+"\t"+str(totalTime)
					tempList.append([hostNo,str(totalTime)])
				else:
					print hostNo
			if options.time:
				if len(tempList)>0:
					tempList = sorted(tempList, key=operator.itemgetter(1))
					for x in tempList:
						print x[0]+"\t"+str(x[1])

		if len(httpList)>0:
			print "\nWorking HTTP Proxies"
			tempList=[]
			for x in httpList:
				hostNo = (x.split("\t"))[0]
				if options.time:
					totalTime = timeit.timeit("getURL1(hostNo)",number=1, setup="from __main__ import getURL1, hostNo")
					#print hostNo+"\t"+str(totalTime)
					tempList.append((hostNo,str(totalTime)))
				else:
					print hostNo
			if options.time:
				if len(tempList)>0:
					tempList = sorted(tempList, key=operator.itemgetter(1))
					for x in tempList:
						print x[0]+"\t"+str(x[1])
