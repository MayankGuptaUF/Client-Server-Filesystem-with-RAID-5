
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import time, Memory, pickle , InodeOps, config, DiskLayout, sys

global portNumber

filesystem = Memory.Operations()



def configure():
	configuration = [config.TOTAL_NO_OF_BLOCKS, config.BLOCK_SIZE, config.MAX_NUM_INODES, config.INODE_SIZE, config.MAX_FILE_NAME_SIZE]
	retVal        = pickle.dumps((configuration))
	return retVal

def Initialize():
	retVal = Memory.Initialize()
	retVal = pickle.dumps((retVal))
	return retVal

def get_data_blocks_for_status():
	return pickle.dumps(filesystem.get_data_blocks_for_status())

def addr_inode_table():
	retVal = filesystem.addr_inode_table()
	retVal = pickle.dumps((retVal))
	return retVal

def get_data_block(block_number):
	retVal  = filesystem.get_data_block(block_number)
	retVal  = pickle.dumps((retVal))
	return retVal

def get_valid_data_block():	
	retVal = filesystem.get_valid_data_block()
	retVal = pickle.dumps((retVal))
	return retVal

def free_data_block(block_number):  
	retVal  = filesystem.free_data_block(block_number)
	retVal  = pickle.dumps((retVal))
	return retVal

def free_data_block_id(block_number):  
	# passVal = pickle.loads(block_number)
	retVal  = filesystem.free_data_block(block_number)
	retVal  = pickle.dumps((retVal))
	return retVal

def update_data_block(block_number, block_data):	
	retVal 	 = filesystem.update_data_block(block_number, pickle.loads(block_data))
	retVal   = pickle.dumps((retVal))
	return retVal

def update_inode_table(inode, inode_number):
	retVal 	 = filesystem.update_inode_table(pickle.loads(inode), inode_number)
	retVal   = pickle.dumps((retVal))
	return retVal

def inode_number_to_inode(inode_number):
	retVal  = filesystem.inode_number_to_inode(inode_number)
	print(retVal)
	retVal  = pickle.dumps((retVal))
	return retVal

def status():
	retVal = filesystem.status()
	retVal = pickle.dumps((retVal))
	return retVal

def corruptData():
	retVal = 'Data Corrupted in server ' + str(portNumber)
	retVal = pickle.dumps((retVal))
	filesystem.corruptData()
	return retVal

def is_running():
	return pickle.dumps(filesystem.running)

def make_valid_block(block_number):
	return pickle.dumps(filesystem.make_valid_block(pickle.loads(block_number)))

def block_numbers_required_to_write(total_blocks):
	return pickle.dumps(filesystem.block_numbers_required_to_write(pickle.loads(total_blocks)))

portNumber = int(sys.argv[1])
#portNumber = 8000
server = SimpleXMLRPCServer(("localhost",portNumber), allow_none = True)
print ("Listening on port " + str(portNumber) +   "...")

server.register_function(corruptData, 			"corruptData")
server.register_function(configure, 		   	"configure")
server.register_function(Initialize, 		   	"Initialize")
server.register_function(addr_inode_table, 	   	"addr_inode_table")
server.register_function(get_data_block, 	   	"get_data_block")
server.register_function(get_valid_data_block, 	"get_valid_data_block")
server.register_function(free_data_block, 		"free_data_block")
server.register_function(free_data_block_id, 		"free_data_block_id")
server.register_function(update_data_block, 	"update_data_block")
server.register_function(update_inode_table, 	"update_inode_table")
server.register_function(inode_number_to_inode, "inode_number_to_inode")
server.register_function(status, 				"status")
server.register_function(is_running, 			"is_running")
server.register_function(make_valid_block,		"make_valid_block")
server.register_function(get_data_blocks_for_status, "get_data_blocks_for_status")
server.register_function(block_numbers_required_to_write, "block_numbers_required_to_write")
server.serve_forever()
