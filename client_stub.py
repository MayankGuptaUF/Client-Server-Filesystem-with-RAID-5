# SKELETON CODE FOR CLIENT STUB HW4
import xmlrpclib, config, pickle
import portNumber
import math
import hashlib
import time

servers = len(portNumber.getPort())
SINGLE_SERVER_SIZE = config.BLOCK_SIZE
print(portNumber.getPort()) 
parity_index = 0
class client_stub():

	def __init__(self):
		self.proxy = []
		for i in range(servers):
			self.proxy.append(xmlrpclib.ServerProxy("http://localhost:"+ str(portNumber.getPort()[i]) + "/"))


	# DEFINE FUNCTIONS HERE

	# example provided for initialize
	def Initialize(self):
		try :
			for i in range(servers):
				self.proxy[i].Initialize()
		except Exception as err :
			print("Init Error In Network. System exiting")
			quit()

	''' WRITE CODE HERE '''
	def is_running(self, server_index):
		try:
			value = pickle.loads(self.proxy[server_index].is_running())
		except:
			return False
		return value

	def inode_number_to_inode(self,inode_number):
		try:
			try:
				return pickle.loads(self.proxy[0].inode_number_to_inode(inode_number))
			except: 
				return pickle.loads(self.proxy[1].inode_number_to_inode(inode_number))
		except Exception as err :
			print("Error In Network. System exiting")
			quit()
	def get_value_from_parity(self, block_number, corrupted_server):
		try: 
			server_indexes = range(servers)
			parity_server = block_number%servers
			del server_indexes[parity_server]
			if corrupted_server	in server_indexes:
				server_indexes.remove(corrupted_server)
			parity = "".ljust(SINGLE_SERVER_SIZE	 + 16, "\0")
			if(parity_server != corrupted_server):
				parity = "".join(pickle.loads(self.proxy[parity_server].get_data_block(block_number)))

			for i in server_indexes:	
				parity = self.xor_strings(parity,"".join(pickle.loads(self.proxy[i].get_data_block(block_number))))
			return list(parity)
		except Exception as err :
			print("gvfp Error In Network. System exiting")
			quit()	
	def get_data_block(self,block_number, offset, length):
		try:
			data = []
			server_indexes = range(servers)
			starting_index = math.floor((float(offset))/SINGLE_SERVER_SIZE)
			indexes_to_check = math.ceil((float(length))/SINGLE_SERVER_SIZE)
			parity_server = block_number%servers
			del server_indexes[parity_server]
			del server_indexes[:int(starting_index)]
			del server_indexes[int(indexes_to_check) - int(starting_index) :]
			for i in server_indexes:
				retVal=[]
				retVal = self.get_value_from_server(block_number, i)
				if(retVal == -1):
					return []
				data += retVal[:-16]
			return data[offset%SINGLE_SERVER_SIZE:length-offset + offset%SINGLE_SERVER_SIZE]
		except Exception as err :
			print("gdb Error In Network. System exiting")
			quit()

	def get_valid_data_block(self):
		try:
			try:
				retVal = pickle.loads( self.proxy[0].get_valid_data_block() )
				for i in range(servers):
					if(i != 0):
						valid_block = pickle.loads( self.proxy[i].get_valid_data_block() )
				return retVal
			except:
				valid_block = 0
				for i in range(servers):
					if(i != 0):
						valid_block = pickle.loads( self.proxy[i].get_valid_data_block() )
				return valid_block

		except Exception as err :
			print("gvdb Error In Network. System exiting")
			quit()
	def free_data_block(self,block_number, server = -1):
		try:			
			if(server != -1):
				self.proxy[server].free_data_block(block_number)
			else :
				for i in range(servers):
					self.proxy[i].free_data_block(block_number)
		except Exception as err :
			print("fdb FDB Error In Network. System exiting")
			quit()

	def xor_strings(self, string1, string2):
		return ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(string1,string2))

	def check_checksum(self, string):
		data = string[:-16]
		checksum = hashlib.md5(data).digest()

		if(checksum == string[-16:]):
			return True
		else:
			return False

	def get_value_from_server(self, block_number, server_number):
		try:
			if(self.is_running(server_number)):
				value = pickle.loads(self.proxy[server_number].get_data_block(block_number))
				if(self.check_checksum("".join(value))):
					return value
				else:
					print(str(portNumber.getPort()[server_number]) + " is corrupted. Getting value from other servers using parity")
					return (self.get_value_from_parity(block_number, server_number))
			else:
				print(str(portNumber.getPort()[server_number]) + " is corrupted. Getting value from other servers using parity")
				return (self.get_value_from_parity(block_number, server_number))
		except:
			print("Lost connection with server with port " + str(portNumber.getPort()[server_number]) + ". Getting value from other servers using parity ")
			return (self.get_value_from_parity(block_number, server_number))


	def send_data_block_to_server(self, block_number, data_block, server_number):
		try:
			self.proxy[server_number].update_data_block(block_number, data_block )	
		except:
			print("server " + str(server_number) + " is not available to write data. Continuing with remaining servers.")

	def update_data_block(self,block_number, block_data, slice_number = 0):
		try:
			block_size = SINGLE_SERVER_SIZE
			parity_server = block_number%servers
			server_indexes = range(servers)
			del server_indexes[parity_server]
			if(slice_number != 0 ):
				for i in range(slice_number):
					del server_indexes[0]
			data = []
			number_of_servers_to_be_updated = int(math.ceil(float(len(block_data))/block_size))
			for i in range(0, len(block_data), block_size):
				block_data_portion = block_data[i:i+block_size]
				if(len(block_data[i:i+block_size]) == SINGLE_SERVER_SIZE):
					block_data_portion = block_data[i:i+block_size] + hashlib.md5(block_data[i:i+block_size]).digest()
				data.append(block_data_portion)
			update_parity = False
			if self.is_running(parity_server):
				print("looking for parity")
				parity = self.get_value_from_server(block_number, parity_server)
				if(self.check_checksum("".join(parity))):
					update_parity = True
			del server_indexes[number_of_servers_to_be_updated :]
			data_index = 0
			for i in (server_indexes):
				previous_data = self.get_value_from_server(block_number, i)
				if(len(data[data_index]) != SINGLE_SERVER_SIZE + 16 ):
					data[data_index] = "".join(list(data[data_index]) + (previous_data[len(data[data_index]):-16]))
					data[data_index] = data[data_index] + hashlib.md5(data[data_index]).digest()
				if(update_parity):
					previous_data = "".join(previous_data)
					parity = self.xor_strings("".join(parity), previous_data)
					parity = self.xor_strings(parity, data[data_index])

				if self.is_running(i):
					data_to_send = pickle.dumps(data[data_index])
					print("writing data to server " + str(portNumber.getPort()[i]))
					self.send_data_block_to_server(block_number, data_to_send, i)
				data_index =data_index + 1
			if update_parity:
				data_to_send = pickle.dumps(parity[:-16] + hashlib.md5(parity[:-16]).digest())
				print("waiting to write parity on server " + str(portNumber.getPort()[parity_server]))
				time.sleep(portNumber.get_write_delay())
				self.send_data_block_to_server(block_number, data_to_send, parity_server)
		except Exception as err :
			print("udb Error In Network. System exiting")
			quit()

	def update_inode_table(self, inode, inode_number):
	
		try:
			for i in range(servers):
				try:
					self.proxy[i].update_inode_table(pickle.dumps(inode), inode_number)
				except:
					print("server " + str(i) + " is not availbale for updating the inode table.")
		except Exception as err :
			print("uit Error In Network. System exiting")
			quit()
#REQUEST TO UPDATE THE UPDATED INODE IN THE INODE TABLE FROM SERVER

#REQUEST FOR THE STATUS OF FILE SYSTEM FROM SERVER
	def status(self):
		# try:
		# print(9)
		retVal = ""
		try:
			retVal = pickle.loads(self.proxy[0].status())
		except:
			retVal = pickle.loads(self.proxy[1].status())
		block_data_from_servers = []

		final_status = {}
		corrupted_server = -1
		for i in range(servers):
			entry = {}
			if(self.is_running(i)):
				entry = pickle.loads(self.proxy[i].get_data_blocks_for_status())
				check_key = 0
				if (self.check_checksum("".join(self.get_value_from_server(entry.keys()[-1], i))) == False):
					print("server " + str(portNumber.getPort()[i]) + "'s data is corrupted.")
					corrupted_server = i
			else:
				corrupted_server = i
			block_data_from_servers.append(entry)
		reference_server = 0
		if(corrupted_server == 0):
			reference_server = 1
		for k in block_data_from_servers[reference_server].keys():
			data_of_one_block = []
			for i in range(servers):
				if(i != corrupted_server):
					data_of_one_block.append(block_data_from_servers[i][k])
				else:
					data_of_one_block.append('')
			final_status[k] = tuple(data_of_one_block)
		counter = 0
		if(corrupted_server != -1):
			print("Recovering data of server " + str(portNumber.getPort()[corrupted_server]))
			final_status = self.recover_data_for_status(corrupted_server, final_status)
		print(retVal[0])
		print(retVal[1])
		print(retVal[2])		
		counter = 0
		for k in final_status.keys():
			counter = counter+1
			data = list(final_status[k])
			data_string = ""

			for i in range(len(data)):
				data_string += data[i]
			del data[k%servers]
			print(str(k) + ": "+str("".join(data)) + " ")
			if(counter == 10):
				break

		print("Printing first 10 blocks only!")
	def recover_data_for_status(self, corrupted_server, block_data_from_servers):
		for k in block_data_from_servers.keys():
			data = list(block_data_from_servers[k])
			recovered_data = ''.ljust(SINGLE_SERVER_SIZE, "\0")
			for i in range(len(data)):
				if(i != corrupted_server):
					recovered_data = self.xor_strings(recovered_data, data[i])
			data[corrupted_server] = recovered_data
			block_data_from_servers[k] = tuple(data)
		return block_data_from_servers 

