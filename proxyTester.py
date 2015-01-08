import httplib
import operator
import timeit
import requests
import sys
import argparse
import requesocks
import multiprocessing
import extraction
import random
import time

urlType="https"
timeoutTime=10
numThreads=35
resultList=[]
proxyList=[]

socks4List=[]
socks5List=[]
httpList=[]
httpsList=[]

urlList = []
urlList.append(["https://www.tracemyip.org/","Trace My IP"])
urlList.append(["http://whatismyipaddress.com/","What Is My IP Address?"])


textFormat = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ProxifierProfile version="101" platform="Windows" product_id="0" product_minver="310">
  <Options>
    <Resolve>
      <AutoModeDetection enabled="true" />
      <ViaProxy enabled="false">
        <TryLocalDnsFirst enabled="false" />
      </ViaProxy>
      <ExclusionList>%ComputerName%; localhost; *.local</ExclusionList>
    </Resolve>
    <Encryption mode="disabled" />
    <HttpProxiesSupport enabled="false" />
    <HandleDirectConnections enabled="false" />
    <ConnectionLoopDetection enabled="true" />
    <ProcessServices enabled="false" />
    <ProcessOtherUsers enabled="false" />
  </Options>
  <ProxyList>\n"""


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
            		(jobid,urlType,proxyHost) = job
            		rtnVal = (jobid,proxyHost,getURL2(proxyHost,"head",urlType))
            		self.result_queue.put(rtnVal)
def execute2(jobs, num_processes=2):
    	work_queue = multiprocessing.Queue()
    	for job in jobs:
        	work_queue.put(job)

    	result_queue = multiprocessing.Queue()
	
	worker = []
    	for i in range(num_processes):
       		worker.append(Worker2(work_queue, result_queue))
       	 	worker[i].start()

	results = []
    	while len(results) < len(jobs): #Beware - if a job hangs, then the whole program will hang
       	 	result = result_queue.get()
       		results.append(result)
    	results.sort() # The tuples in result are sorted according to the first element - the jobid
    	return (results)
	
class Worker2(multiprocessing.Process):
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
            		(jobid,urlType,proxyHost) = job
            		rtnVal = (jobid,proxyHost,getURL2(proxyHost,"get",urlType))
            		self.result_queue.put(rtnVal)

def chunk(input, size):
    	return map(None, *([iter(input)] * size))

def testSocks4(proxyHost,urlType):
	global timeoutTime
	start_time = time.time()
	
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
		session.timeout = timeoutTime
		if proxyType=="socks4":
			if urlType=="https":
				session.proxies = {'https': 'socks4://'+hostNo+':'+portNo}
				urlPosition = urlList[0]
			else:
				session.proxies = {'http': 'socks4://'+hostNo+':'+portNo}
				urlPosition = urlList[1]

		try:
			url = urlPosition[0]
			urlTitle = urlPosition[1]
			r = session.get(url)

			statusCode = str(r.status_code)

			if statusCode=="200":
				result = ((proxyHost,"",proxyType))
				resultList.append(result)
				if proxyType=="socks4":
					end_time = time.time() - start_time
					return proxyHost+"\tsocks4\t200\t"+str(end_time)
			else:
				return proxyHost+"\t"+proxyType+"\t"+statusCode
		except Exception as e:
			return proxyHost+"\t"+proxyType+"\t503"

def testSocks5(proxyHost,urlType):
	start_time = time.time()
	global timeoutTime
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
		session.timeout = timeoutTime
		if proxyType=="socks5":
			if urlType=="https":
				urlPosition = urlList[0]
				session.proxies = {'https': 'socks5://'+hostNo+':'+portNo}
			else:
				urlPosition = urlList[1]
				session.proxies = {'http': 'socks5://'+hostNo+':'+portNo}
		try:
	
			url = urlPosition[0]
			urlTitle = urlPosition[1]

			r = session.get(url)

			statusCode = str(r.status_code)

			if statusCode=="200":
				result = ((proxyHost,"",proxyType))
				resultList.append(result)
				if proxyType=="socks5":
					end_time = time.time() - start_time
					return proxyHost+"\tsocks5\t200\t"+str(end_time)
			else:
				return proxyHost+"\t"+proxyType+"\t"+statusCode
		except Exception as e:
			return proxyHost+"\t"+proxyType+"\t503"


def getURL1(proxyHost,requestType,urlType):
	global timeoutTime
	#print "Testing socks proxy: http://"+proxyHost
	import socks
	import socket
	import urllib2
	hostNo = proxyHost.split(":")[0]
	portNo = proxyHost.split(":")[1]
			
	#urlList = []
	#urlList.append(["https://www.tracemyip.org/","Trace My IP"])
	#urlList.append(["https://www.wikipedia.org/","Wikipedia"])
	#urlList.append(["http://whatismyipaddress.com/","What Is My IP Address?"])

	global statusCode
	try:
		#print "Testing http proxy: http://"+proxyHost	
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

		hostNo = proxyHost.split(":")[0]
		portNo = proxyHost.split(":")[1]

		session = requesocks.session()
		session.timeout = timeoutTime
		if urlType=="https":
			urlPosition = urlList[0]
			session.proxies = {'https': 'https://'+hostNo+':'+portNo}
		if urlType=="http":
			urlPosition = urlList[1]
			session.proxies = {'http': 'http://'+hostNo+':'+portNo}
		url = urlPosition[0]
		urlTitle = urlPosition[1]
		
		if requestType=="get":
			r = session.get(url)
			#try:
			extracted = extraction.Extractor().extract(r.text, source_url=url)
			if urlTitle not in extracted.title:
				return proxyHost+"\t"+urlType+"\t503"			
		elif requestType=="head":
			r = session.head(url)
		statusCode=str(r.status_code)

		result2 = proxyHost+"\t"+urlType+"\t"+statusCode

		if statusCode!="200":
			result1 = testSocks4(proxyHost,urlType)
			if "503" in str(result1):
				#if options.v:
				#	print result
				result = testSocks5(proxyHost,urlType)
				return result2+"\n"+results1+"\n"+result
			else:
				return result1
		else:
			return proxyHost+"\t"+urlType+"\t"+statusCode

	except requests.exceptions.ConnectionError as e:
		return proxyHost+"\t"+urlType+"\t503"	

	except Exception as e: 
		result2 = proxyHost+"\t"+urlType+"\t503"

		#if options.v:
		#	print proxyHost+"\t"+urlType+"\t503"	
		result1 = testSocks4(proxyHost,urlType)
		if "503" in str(result1):
			#if options.v:
			#	print result
			result = testSocks5(proxyHost,urlType)
			#if options.v:
			#	print result
			return result2+"\n"+result1+"\n"+result
		else:
			if options.v:
				print result1
			return result1
def getURL2(proxyHost,requestType,urlType):
	start_time = time.time()
	import socks
	import socket
	import urllib2
	hostNo = proxyHost.split(":")[0]
	portNo = proxyHost.split(":")[1]
			
	global statusCode
	try:
		#print "Testing http proxy: http://"+proxyHost	
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

		hostNo = proxyHost.split(":")[0]
		portNo = proxyHost.split(":")[1]

		session = requesocks.session()
		session.timeout = timeoutTime
		if urlType=="https":
			urlPosition = urlList[0]
			session.proxies = {'https': 'https://'+hostNo+':'+portNo}
		if urlType=="http":
			urlPosition = urlList[1]
			session.proxies = {'http': 'http://'+hostNo+':'+portNo}
		url = urlPosition[0]
		urlTitle = urlPosition[1]
		
		if requestType=="get":
			r = session.get(url)
			#try:
			extracted = extraction.Extractor().extract(r.text, source_url=url)
			if urlTitle not in extracted.title:
				return proxyHost+"\t"+urlType+"\t503"			
		elif requestType=="head":
			r = session.head(url)
		statusCode=str(r.status_code)

		result2 = proxyHost+"\t"+urlType+"\t"+statusCode

		if statusCode!="200":
			result1 = testSocks4(proxyHost,urlType)
			if "503" in str(result1):
				result = testSocks5(proxyHost,urlType)
				return result2+"\n"+results1+"\n"+result
			else:
				return result1
		else:
			end_time = time.time() - start_time
			return proxyHost+"\t"+urlType+"\t"+statusCode+"\t"+str(end_time)

	except requests.exceptions.ConnectionError as e:
		return proxyHost+"\t"+urlType+"\t503"	

	except Exception as e: 
		result2 = proxyHost+"\t"+urlType+"\t503"

		result1 = testSocks4(proxyHost,urlType)
		if "503" in str(result1):
			result = testSocks5(proxyHost,urlType)
			return result2+"\n"+result1+"\n"+result
		else:
			if options.v:
				print result1
			return result1


if __name__ == '__main__':
    	parser = argparse.ArgumentParser()
    	parser.add_argument('-i',dest='ipFile',action='store',help='[file containing list of proxies]')
    	parser.add_argument('-o',dest='outFile',action='store',help='[proxifier profile PPX file]')
    	parser.add_argument('-n',dest='threads',action='store',help='[number of threads]')
    	parser.add_argument('-t',dest='urlType',action='store',help='[type of website to test (https or http) ]')
    	parser.add_argument('-time', action='store_true', help='[check latency]')
    	parser.add_argument('-sort', action='store_true', help='[sort the results. to be used together with -time argument]')
    	parser.add_argument('-v', action='store_true', help='[verbose mode]')
    	options = parser.parse_args()

    	if len(sys.argv)==1:
        	parser.print_help()
        	sys.exit()
    	else:
		with open(options.ipFile) as f:
			proxyList = f.read().splitlines()
			proxyList=list(set(proxyList))
	
		if options.threads:
			tempList1 = chunk(proxyList, int(options.threads))
		else:
			tempList1 = chunk(proxyList, 35)

		totalCount=len(tempList1)
		count = 1 
		for proxyList in tempList1:
			jobs = [] 
			jobid=0
			print "- Set "+str(count)+" of "+str(len(tempList1))
			for proxyHost in proxyList:
				try:
					print "- Testing: "+proxyHost
					if options.urlType:
						urlType = options.urlType
						jobs.append((jobid,options.urlType,proxyHost))
					else:
						jobs.append((jobid,urlType,proxyHost))
						#jobs.append((jobid,urlType,proxyHost))
					jobid = jobid+1
				except TypeError:
					continue
		
			numProcesses = numThreads
			resultList = execute1(jobs,numProcesses)
			for result in resultList:
				if result[2]!=None:
					if "503" in result[2]:
						if options.v:
							print result[2]
					else:
						if "socks4" in str(result[2]):
							socks4List.append(result[2])
						elif "socks5" in str(result[2]):
							socks5List.append(result[2])
						elif "https" in str(result[2]):
							httpsList.append(result[2])
						else:
							httpList.append(result[2])
						print result[2]
			#statusCode=""
			count+=1


		print "\n------------------------------------------------------------------"
		proxyID=100
		proxyIDList=[]
		chainID=""

		if len(socks4List)>0:
			print "\nWorking Socks4 Proxies (Unsorted)"
			tempList=[]
			for x in socks4List:
				hostNo =  (x.split("\t"))[0]
				if options.time:
					results =  testSocks4(HostNo,urlType)
					if "503" not in results:
						#totalTime = timeit.timeit("testSocks4(hostNo,urlType)",number=1, setup="from __main__ import testSocks4, hostNo, urlType")					
						executionTime = (results.split("\t"))[3]

						if [hostNo,executionTime] not in tempList:
							print hostNo+"\t"+str(executionTime)+" seconds"
							tempList.append([hostNo,executionTime])

						proxyHost = (hostNo.split(":"))[0]
						proxyPort = (hostNo.split(":"))[1]
	
						textFormat+='\t<Proxy id="'+str(proxyID)+'" type="SOCKS4">\n'
      						textFormat+='\t\t<Address>'+proxyHost+'</Address>\n'
						textFormat+='\t\t<Port>'+proxyPort+'</Port>\n'
      						textFormat+='\t\t<Options>48</Options>\n'
    						textFormat+='\t</Proxy>\n'
						proxyIDList.append(str(proxyID))

				else:
					print hostNo

					proxyHost = (hostNo.split(":"))[0]
					proxyPort = (hostNo.split(":"))[1]

					textFormat+='\t<Proxy id="'+str(proxyID)+'" type="SOCKS4">\n'
      					textFormat+='\t\t<Address>'+proxyHost+'</Address>\n'
					textFormat+='\t\t<Port>'+proxyPort+'</Port>\n'
      					textFormat+='\t\t<Options>48</Options>\n'
    					textFormat+='\t</Proxy>\n'
					proxyIDList.append(str(proxyID))
				proxyID+=1
			if options.time:
				if len(tempList)>0:
					print "\nWorking Socks4 Proxies (Sorted)"
					tempList = sorted(tempList, key=operator.itemgetter(1))
					for x in tempList:
						print x[0]+"\t"+str(x[1])+" seconds"
			print "\n------------------------------------------------------------------"

		if len(socks5List)>0:
			print "\nWorking Socks5 Proxies (Unsorted)"
			tempList=[]
			for x in socks5List:
				hostNo =  (x.split("\t"))[0]
				if options.time:
					results = testSocks5(hostNo,urlType)
					if "503" not in results:
						executionTime = (results.split("\t"))[3]
		
						#totalTime = timeit.timeit("testSocks5(hostNo,urlType)",number=1, setup="from __main__ import testSocks5, hostNo,urlType")					

						if [hostNo,executionTime] not in tempList:
							print hostNo+"\t"+str(executionTime)+" seconds"
							tempList.append([hostNo,executionTime])

						proxyHost = (hostNo.split(":"))[0]
						proxyPort = (hostNo.split(":"))[1]
	
						textFormat+='\t<Proxy id="'+str(proxyID)+'" type="SOCKS5">\n'
      						textFormat+='\t\t<Address>'+proxyHost+'</Address>\n'
						textFormat+='\t\t<Port>'+proxyPort+'</Port>\n'
      						textFormat+='\t\t<Options>48</Options>\n'
    						textFormat+='\t</Proxy>\n'
						proxyIDList.append(str(proxyID))
				else:
					print hostNo

					proxyHost = (hostNo.split(":"))[0]
					proxyPort = (hostNo.split(":"))[1]

					textFormat+='\t<Proxy id="'+str(proxyID)+'" type="SOCKS5">\n'
      					textFormat+='\t\t<Address>'+proxyHost+'</Address>\n'
					textFormat+='\t\t<Port>'+proxyPort+'</Port>\n'
      					textFormat+='\t\t<Options>48</Options>\n'
    					textFormat+='\t</Proxy>\n'
					proxyIDList.append(str(proxyID))
				proxyID+=1
			if options.time and options.sort:
				if len(tempList)>0:
					print "\nWorking Socks5 Proxies (Sorted)"
					tempList = sorted(tempList, key=operator.itemgetter(1))
					for x in tempList:
						print x[0]+"\t"+str(x[1])+" seconds"

			print "\n------------------------------------------------------------------"

		if len(httpsList)>0:
			jobs = []
			jobid=0

			tempList=[]
			for x in httpsList:
				hostNo = (x.split("\t"))[0]			
				if options.time:
					jobs.append((jobid,options.urlType,hostNo))
					jobid = jobid+1
				
				else:
					if "503" not in getURL1(hostNo,"get",urlType):
						print hostNo

						proxyHost = (hostNo.split(":"))[0]
						proxyPort = (hostNo.split(":"))[1]

						if urlType=="https":
							textFormat+='\t<Proxy id="'+str(proxyID)+'" type="HTTPS">\n'
						if urlType=="http":
							textFormat+='\t<Proxy id="'+str(proxyID)+'" type="HTTP">\n'
      						textFormat+='\t\t<Address>'+proxyHost+'</Address>\n'
						textFormat+='\t\t<Port>'+proxyPort+'</Port>\n'
      						textFormat+='\t\t<Options>48</Options>\n'
    						textFormat+='\t</Proxy>\n'
						proxyIDList.append(str(proxyID))
						proxyID+=1
			print "\nWorking HTTPs Proxies (Unsorted)"
			tempList=[]
			numProcesses = numThreads
			resultList = execute2(jobs,numProcesses)
			for result in resultList:
				if "\t200" in result[2]:

					hostNo=result[1]
					proxyHost = (hostNo.split(":"))[0]
					proxyPort = (hostNo.split(":"))[1]

					executionTime = (result[2].split("\t"))[3]
					if [hostNo,executionTime] not in tempList:
						print hostNo+"\t"+str(executionTime)+" seconds"
						tempList.append([hostNo,(executionTime)])

					if urlType=="https":
						textFormat+='\t<Proxy id="'+str(proxyID)+'" type="HTTPS">\n'
					if urlType=="http":
						textFormat+='\t<Proxy id="'+str(proxyID)+'" type="HTTP">\n'
      					textFormat+='\t\t<Address>'+proxyHost+'</Address>\n'
					textFormat+='\t\t<Port>'+proxyPort+'</Port>\n'
      					textFormat+='\t\t<Options>48</Options>\n'
    					textFormat+='\t</Proxy>\n'
					proxyIDList.append(str(proxyID))
	
					proxyID+=1
			if options.time and options.sort:
				if len(tempList)>1:
					print "\nWorking HTTPs Proxies (Sorted)"
					tempList = sorted(tempList, key=operator.itemgetter(1))
					for x in tempList:
						print x[0]+"\t"+str(x[1])+" seconds"


			print "\n------------------------------------------------------------------"
		if len(httpList)>0:
			jobs = []
			jobid=0

			tempList=[]
			for x in httpList:
				hostNo = (x.split("\t"))[0]			
				if options.time:
					jobs.append((jobid,options.urlType,hostNo))
					jobid = jobid+1
				
				else:
					if "503" not in getURL1(hostNo,"get",urlType):
						print hostNo

						proxyHost = (hostNo.split(":"))[0]
						proxyPort = (hostNo.split(":"))[1]

						if urlType=="https":
							textFormat+='\t<Proxy id="'+str(proxyID)+'" type="HTTPS">\n'
						if urlType=="http":
							textFormat+='\t<Proxy id="'+str(proxyID)+'" type="HTTP">\n'
      						textFormat+='\t\t<Address>'+proxyHost+'</Address>\n'
						textFormat+='\t\t<Port>'+proxyPort+'</Port>\n'
      						textFormat+='\t\t<Options>48</Options>\n'
    						textFormat+='\t</Proxy>\n'
						proxyIDList.append(str(proxyID))
						proxyID+=1
			print "\nWorking HTTP Proxies (Unsorted)"
			tempList=[]
			numProcesses = numThreads
			resultList = execute2(jobs,numProcesses)
			for result in resultList:
				if "\t200" in result[2]:

					hostNo=result[1]
					proxyHost = (hostNo.split(":"))[0]
					proxyPort = (hostNo.split(":"))[1]

					executionTime = (result[2].split("\t"))[3]
					if [hostNo,executionTime] not in tempList:
						print hostNo+"\t"+str(executionTime)+" seconds"
						tempList.append([hostNo,(executionTime)])

					if urlType=="https":
						textFormat+='\t<Proxy id="'+str(proxyID)+'" type="HTTPS">\n'
					if urlType=="http":
						textFormat+='\t<Proxy id="'+str(proxyID)+'" type="HTTP">\n'
      					textFormat+='\t\t<Address>'+proxyHost+'</Address>\n'
					textFormat+='\t\t<Port>'+proxyPort+'</Port>\n'
      					textFormat+='\t\t<Options>48</Options>\n'
    					textFormat+='\t</Proxy>\n'
					proxyIDList.append(str(proxyID))
	
					proxyID+=1
			if options.time and options.sort:
				if len(tempList)>1:
					print "\nWorking HTTP Proxies (Sorted)"
					tempList = sorted(tempList, key=operator.itemgetter(1))
					for x in tempList:
						print x[0]+"\t"+str(x[1])+" seconds"


			print "\n------------------------------------------------------------------"

		textFormat += '</ProxyList>\n'
		textFormat += '<ChainList>\n'
   		textFormat += '\t<Chain id="'+str(proxyID)+'" type="load_balancing">\n'
		chainID = str(proxyID)
      		textFormat += '\t<Name>Chain1</Name>\n'
		for x in proxyIDList:
      			textFormat += '\t<Proxy enabled="true">'+x+'</Proxy>\n'
    		textFormat += '\t</Chain>\n'
		textFormat += '</ChainList>\n'
		textFormat += '<RuleList>\n'
		textFormat += '\t<Rule enabled="true">\n'
      		textFormat += '\t\t<Name>Localhost</Name>\n'
      		textFormat += '\t\t<Targets>localhost; 127.0.0.1; %ComputerName%</Targets>\n'
      		textFormat += '\t\t<Action type="Chain">'+chainID+'</Action>\n'
    		textFormat += '\t</Rule>\n'
    		textFormat += '\t<Rule enabled="true">\n'
      		textFormat += '\t\t<Name>Default</Name>\n'
      		textFormat += '\t\t<Action type="Chain">'+chainID+'</Action>\n'
    		textFormat += '\t</Rule>\n'
		textFormat += '</RuleList>\n'
		textFormat += '</ProxifierProfile>'
		if options.outFile:
			if len(httpList)>0 or len(httpsList)>0 or len(socks4List)>0 or len(socks5List)>0:
				f = open(options.outFile+".ppx", 'w')
				f.write(textFormat)
				f.close()
				print "\n[*] "+options.outFile+".ppx written."

