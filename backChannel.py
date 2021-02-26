import xmlrpclib, config, pickle, os, sys, subprocess, time

#Back Channel
proxy = []
#create servers
# number of servers
num_servers   	= sys.argv[1]
num_servers   	= int(num_servers)
print(num_servers)
portNum 		= 8000

for i in range(num_servers) :
	# append to the list of client proxies
	print('running server #' + str(portNum+i))
	proxy.append(xmlrpclib.ServerProxy("http://localhost:" + str(portNum + i) + "/", allow_none = True))
	os.system('gnome-terminal -e \"python server.py ' + str(portNum + i) + '\"')
	time.sleep(1)

while True:
	serverNum = int(raw_input("Select Server to Corrupt..."))
	print(proxy)
	
	print(serverNum)
	retVal =  proxy[serverNum].corruptData()
		
	print(pickle.loads(retVal))

