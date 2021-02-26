# SKELETON CODE FOR SERVER STUB HW4
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import time, Memory, pickle , InodeOps, config, DiskLayout


filesystem = Memory.Operations()

# FUNCTION DEFINITIONS 

# example provided for initialize
def Initialize():
	retVal = Memory.Initialize()
	retVal = pickle.dumps(retVal)
	return retVal


''' WRITE CODE HERE FOR REST OF FUNCTIONS'''

#REQUEST TO FETCH THE INODE FROM INODE NUMBER FROM SERVER
def inode_number_to_inode(inode_number):
    return pickle.dumps(filesystem.inode_number_to_inode(inode_number))


#REQUEST THE DATA FROM THE SERVER
def get_data_block(block_number):
    return pickle.dumps(''.join(filesystem.get_data_block(block_number)))


#REQUESTS THE VALID BLOCK NUMBER FROM THE SERVER 
def get_valid_data_block():
    return pickle.dumps(( filesystem.get_valid_data_block() ))


#REQUEST TO MAKE BLOCKS RESUABLE AGAIN FROM SERVER
def free_data_block(block_number):
    filesystem.free_data_block((block_number))


#REQUEST TO WRITE DATA ON THE THE SERVER
def update_data_block(block_number, block_data):
    filesystem.update_data_block(block_number, block_data)


#REQUEST TO UPDATE THE UPDATED INODE IN THE INODE TABLE FROM SERVER
def update_inode_table(inode, inode_number):
    filesystem.update_inode_table(pickle.loads(inode), inode_number)


#REQUEST FOR THE STATUS OF FILE SYSTEM FROM SERVER
def status():
    return pickle.dumps(filesystem.status())


server = SimpleXMLRPCServer(("",8000), allow_none = True)
print ("Listening on port 8000...")

# REGISTER FUNCTIONS

#example provided for initialize
server.register_function(Initialize, 		   	"Initialize")

''' WRITE CODE HERE FOR REST OF REGISTER CALLS '''
server.register_function(inode_number_to_inode, 		   	"inode_number_to_inode")
server.register_function(get_data_block, 		   	"get_data_block")
server.register_function(get_valid_data_block, 		   	"get_valid_data_block")
server.register_function(free_data_block, 		   	"free_data_block")
server.register_function(update_data_block, 		   	"update_data_block")
server.register_function(update_inode_table, 		   	"update_inode_table")
server.register_function(status, 		   	"status")

# run the server
server.serve_forever()














