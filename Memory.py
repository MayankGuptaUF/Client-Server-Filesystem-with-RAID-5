'''
THIS IS A MEMORY MODULE ON THE SREVER WHICH ACTS LIKE MEMORY OF FILE SYSTEM. ALL THE OPERATIONS REGARDING THE FILE SYSTEM OPERATES IN 
THIS MODULE. THE MODULE HAS POINTER TO DISK AND HAS EXACT SAME LAYOUT AS UNIX TYPE FILE SYSTEM.
'''  
import config, DiskLayout
import hashlib

#POINTER TO DISK
sblock = DiskLayout.SuperBlock()			 


#BOOTS THE FILE SYSTEM
class Initialize():
	def __init__(self):
		#ALLOCATING BITMAP BLOCKS 0 AND 1 BLOCKS ARE RESERVED FOR BOOT BLOCK AND SUPERBLOCK
		sblock.BITMAP_BLOCKS_OFFSET, count = 2, 2 
		for i in range(0, sblock.TOTAL_NO_OF_BLOCKS / sblock.BLOCK_SIZE):  	
			sblock.ADDR_BITMAP_BLOCKS.append(DiskLayout.Bitmap_Block(sblock.BLOCK_SIZE))
			count += 1
		#ALLOCATING INODE BLOCKS
		sblock.INODE_BLOCKS_OFFSET = count
		for i in range(0, (sblock.MAX_NUM_INODES * sblock.INODE_SIZE) / sblock.BLOCK_SIZE):		#for Inode blocks
			sblock.ADDR_INODE_BLOCKS.append(DiskLayout.Inode_Block(sblock.INODES_PER_BLOCK))
			count  += 1
		#ALLOCATING DATA BLOCKS
		sblock.DATA_BLOCKS_OFFSET = count
		for i in range(sblock.DATA_BLOCKS_OFFSET, sblock.TOTAL_NO_OF_BLOCKS):
			sblock.ADDR_DATA_BLOCKS.append(DiskLayout.Data_Block(sblock.BLOCK_SIZE))
		#MAKING BLOCKS BEFORE DATA BLOCKS UNAVAILABLE FOR USE SINCE OCCUPIED BY SUPERBLOCK, BOOTBLOCK, BITMAP AND INODE TABLE
		for i in range(0, sblock.DATA_BLOCKS_OFFSET): 
			sblock.ADDR_BITMAP_BLOCKS[i / sblock.BLOCK_SIZE].block[i % sblock.BLOCK_SIZE] = -1


#OPERATIONS ON FILE SYSTEM
class Operations():

	running = True
	#GIVES ADDRESS OF INODE TABLE
	def addr_inode_table(self):				
		return sblock.ADDR_INODE_BLOCKS


	#RETURNS THE DATA OF THE BLOCK
	def get_data_block(self, block_number):	
		if block_number == 0: print("Memory: Reserved for Boot Block")
		elif block_number == 1: print("Memory: Reserved for Super Block")
		elif block_number >= sblock.BITMAP_BLOCKS_OFFSET and block_number < sblock.INODE_BLOCKS_OFFSET:
			return sblock.ADDR_BITMAP_BLOCKS[block_number - sblock.BITMAP_BLOCKS_OFFSET].block
		elif block_number >= sblock.INODE_BLOCKS_OFFSET and block_number < sblock.DATA_BLOCKS_OFFSET:
			return sblock.ADDR_INODE_BLOCKS[block_number - sblock.INODE_BLOCKS_OFFSET].block
		elif block_number >= sblock.DATA_BLOCKS_OFFSET and block_number < sblock.TOTAL_NO_OF_BLOCKS:
			# if (block_number == 44 ):
			# 	print(sblock.ADDR_DATA_BLOCKS[block_number - sblock.DATA_BLOCKS_OFFSET].block)
			# 	import pdb ; pdb.set_trace()
			return sblock.ADDR_DATA_BLOCKS[block_number - sblock.DATA_BLOCKS_OFFSET].block
		else: print("Memory: Block index out of range or Wrong input!")
		return -1


	#RETURNS THE BLOCK NUMBER OF AVAIALBLE DATA BLOCK  
	def get_valid_data_block(self):			
		for i in range(0, sblock.TOTAL_NO_OF_BLOCKS):
			if sblock.ADDR_BITMAP_BLOCKS[i / sblock.BLOCK_SIZE].block[i % sblock.BLOCK_SIZE] == 0:
				sblock.ADDR_BITMAP_BLOCKS[i / sblock.BLOCK_SIZE].block[i % sblock.BLOCK_SIZE] = 1
				return i
		print("Memory: No valid blocks available")
		return -1

	def block_numbers_required_to_write(self, total_blocks):
		block_numbers = []
		for i in range(0, sblock.TOTAL_NO_OF_BLOCKS):
			if sblock.ADDR_BITMAP_BLOCKS[i / sblock.BLOCK_SIZE].block[i % sblock.BLOCK_SIZE] == 0:
				sblock.ADDR_BITMAP_BLOCKS[i / sblock.BLOCK_SIZE].block[i % sblock.BLOCK_SIZE] = 1
				block_numbers.append(i)
				if(len(block_numbers) == total_blocks):
					return block_numbers


	def make_block_valid(self, block_number):
		if(sblock.ADDR_BITMAP_BLOCKS[block_number] != 1):
			sblock.ADDR_BITMAP_BLOCKS[block_number] = 1

	def corruptData(self):  
		for block_number in range(sblock.DATA_BLOCKS_OFFSET, sblock.TOTAL_NO_OF_BLOCKS):	
			sblock.ADDR_BITMAP_BLOCKS[block_number / sblock.BLOCK_SIZE].block[block_number % sblock.BLOCK_SIZE] = 0
			b = sblock.ADDR_DATA_BLOCKS[block_number - sblock.DATA_BLOCKS_OFFSET].block
			# import pdb ; pdb.set_trace()
			for i in range(0, sblock.BLOCK_SIZE + 16): b[i] = "\0"

	#REMOVES THE INVALID DATA BLOCK TO MAKE IT REUSABLE
	def free_data_block(self, block_number):  	
		sblock.ADDR_BITMAP_BLOCKS[block_number / sblock.BLOCK_SIZE].block[block_number % sblock.BLOCK_SIZE] = 0
		b = sblock.ADDR_DATA_BLOCKS[block_number - sblock.DATA_BLOCKS_OFFSET].block
		# import pdb ; pdb.set_trace()
		empty_block = "".ljust(sblock.BLOCK_SIZE, "\0")
		empty_block	= empty_block	+ hashlib.md5(empty_block).digest()
		empty_block	= list(empty_block)
		for i in range(0, sblock.BLOCK_SIZE + 16): b[i] = empty_block[i]
		        
        # b = b[:-16] + hashlib.md5(b[:-16]).digest()
        

	#WRITES TO THE DATA BLOCK
	def update_data_block(self, block_number, block_data):		
		b = sblock.ADDR_DATA_BLOCKS[block_number - sblock.DATA_BLOCKS_OFFSET].block
		for i in range(0, len(block_data)): b[i] = block_data[i]
		#print("Memory: Data Copy Completes")
	
	
	#UPDATES INODE TABLE WITH UPDATED INODE
	def update_inode_table(self, inode, inode_number):
		sblock.ADDR_INODE_BLOCKS[inode_number / sblock.INODES_PER_BLOCK].block[inode_number % sblock.INODES_PER_BLOCK] = inode

	
	#RETURNS THE INODE FROM INODE NUMBER
	def inode_number_to_inode(self, inode_number):
		return sblock.ADDR_INODE_BLOCKS[inode_number / sblock.INODES_PER_BLOCK].block[inode_number % sblock.INODES_PER_BLOCK]

	
	#SHOWS THE STATUS OF DISK LAYOUT IN MEMORY
	def status(self):
		counter = 1
		bitmap_string = ""
		bitmap_string += "\n----------BITMAP: ----------(Block Number : Valid Status)\n"
		block_number = 0
		for i in range(2, sblock.INODE_BLOCKS_OFFSET):
			bitmap_string += "Bitmap Block : " + str(i - 2) + "\n"
			b = sblock.ADDR_BITMAP_BLOCKS[i - sblock.BITMAP_BLOCKS_OFFSET].block
			for j in range(40, len(b)):
				if j == 60: break   #only to avoid useless data to print
				bitmap_string += "\t\t[" + str(block_number + j) + "  :  "  + str(b[j]) + "]  \n"
			block_number += len(b)
			if counter == 1: break
		bitmap_string += ".....showing just part(20) of 1st bitmap block!\n"

		inode_string = ""
		inode_string += "\n\n----------INODE Blocks: ----------(Inode Number : Inode(Address)\n"
		inode_number = 0
		for i in range(sblock.INODE_BLOCKS_OFFSET, sblock.DATA_BLOCKS_OFFSET):
			inode_string += "Inode Block : " + str(i - sblock.INODE_BLOCKS_OFFSET) + "\n"
			b = sblock.ADDR_INODE_BLOCKS[i - sblock.INODE_BLOCKS_OFFSET].block
			for j in range(0, len(b)):
				inode_string += "\t\t[" + str(inode_number + j) + "  :  "  + str(bool(b[j])) + "]  \n"
			inode_number += len(b)
		
		# data_string = ""
		# data_string += "\n\n----------DATA Blocks: ----------\n  "
		
		# counter = 0
		# for i in range(sblock.DATA_BLOCKS_OFFSET, sblock.TOTAL_NO_OF_BLOCKS):
		# 	if counter == 25: 
		# 		data_string += "......Showing just part(25) data blocks\n"
		# 		break
		# 	data_string += (str(i) + " : " + "".join(sblock.ADDR_DATA_BLOCKS[i - sblock.DATA_BLOCKS_OFFSET].block[:-16])) + "  "
		# 	counter += 1

		
		hier_string = ""
		hier_string += "\n\n----------HIERARCHY: ------------\n"
		for i in range(sblock.INODE_BLOCKS_OFFSET, sblock.DATA_BLOCKS_OFFSET):
			for j in range(0, sblock.INODES_PER_BLOCK):
				inode = sblock.ADDR_INODE_BLOCKS[i-sblock.INODE_BLOCKS_OFFSET].block[j]
				if inode and inode[0]:
					hier_string += "\nDIRECTORY: " + inode[1] + "\n"
					for x in inode[7]: hier_string += "".join(x[:config.MAX_FILE_NAME_SIZE]) + " || "
					hier_string += "\n"
		
		return [bitmap_string, inode_string, hier_string]

	def get_data_blocks_for_status(self):
		data_block = {}
		# data_string = ""
		# data_string += "\n\n----------DATA Blocks: ----------\n  "
		
		counter = 0
		for i in range(sblock.DATA_BLOCKS_OFFSET, sblock.TOTAL_NO_OF_BLOCKS):
			data_block[i] = "".join(sblock.ADDR_DATA_BLOCKS[i - sblock.DATA_BLOCKS_OFFSET].block[:-16])
			# data_string += (str(i) + " : " + "".join(sblock.ADDR_DATA_BLOCKS[i - sblock.DATA_BLOCKS_OFFSET].block[:-16])) + "  "
			# counter += 1
		return data_block