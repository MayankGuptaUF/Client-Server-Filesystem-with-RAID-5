def init():
	global portN
	portN = []

def getPort():
	return portN

def writeDelay(seconds):
	global write_delay
	write_delay = seconds

def readDelay(seconds):
	global read_delay
	read_delay = seconds

def get_write_delay():
	return write_delay

def get_read_delay():
	return read_delay