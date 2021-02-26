'''
THIS MODULE ACTS LIKE FILE NAME LAYER AND PATH NAME LAYER (BOTH) ABOVE INODE LAYER.
IT RECIEVES INPUT AS PATH (WITHOUT INITIAL '/'). THE LAYER IMPLEMENTS LOOKUP TO FIND INODE NUMBER OF THE REQUIRED DIRECTORY.
PARENTS INODE NUMBER IS FIRST EXTRACTED BY LOOKUP AND THEN CHILD INODE NUMBER BY RESPECTED FUNCTION AND BOTH OF THEM ARE UPDATED
'''
import InodeNumberLayer

#HANDLE OF INODE NUMBER LAYER
interface = InodeNumberLayer.InodeNumberLayer()

class FileNameLayer():

	#PLEASE DO NOT MODIFY
	#RETURNS THE CHILD INODE NUMBER FROM THE PARENTS INODE NUMBER
	def CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(self, childname, inode_number_of_parent):
		inode = interface.INODE_NUMBER_TO_INODE(inode_number_of_parent)
		if not inode: 
			print("Error FileNameLayer: Lookup Failure!")
			return -1
		if inode.type == 0:
			print("Error FileNameLayer: Invalid Directory!")
			return -1
		if childname in inode.directory: return inode.directory[childname]
		print("Error FileNameLayer: Lookup Failure!")
		return -1

	#PLEASE DO NOT MODIFY
	#RETUNS THE PARENT INODE NUMBER FROM THE PATH GIVEN FOR A FILE/DIRECTORY 
	def LOOKUP(self, path, inode_number_cwd):   
		name_array = path.split('/')
		if len(name_array) == 1: return inode_number_cwd
		else:
			child_inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(name_array[0], inode_number_cwd)
			if child_inode_number == -1: return -1
			return self.LOOKUP("/".join(name_array[1:]), child_inode_number)

	#PLEASE DO NOT MODIFY
	#MAKES NEW ENTRY OF INODE
	def new_entry(self, path, inode_number_cwd, type):
		if path == '/': #SPECIAL CASE OF INITIALIZING FILE SYSTEM
			interface.new_inode_number(type, inode_number_cwd, "root")
			return True
		parent_inode_number = self.LOOKUP(path, inode_number_cwd)
		parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number) 
		childname = path.split('/')[-1]
		if not parent_inode: return -1
		if childname in parent_inode.directory:
			print("Error FileNameLayer: File already exists!")
			return -1
		child_inode_number = interface.new_inode_number(type, parent_inode_number, childname)  #make new child
		if child_inode_number != -1:
			parent_inode.directory[childname] = child_inode_number
			interface.update_inode_table(parent_inode, parent_inode_number)


	#IMPLEMENTS READ
	def read(self, path, inode_number_cwd, offset, length):
		'''WRITE YOUR CODE HERE'''
		parent_inode_number = self.LOOKUP(path, inode_number_cwd)
		parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number) 
		childname = path.split('/')[-1]
		if not parent_inode: return -1
		if childname not in parent_inode.directory:
			print("Error FileNameLayer: File does not exist!")
			return -1
		child_inode_number = parent_inode.directory[childname]
		return interface.read(child_inode_number, offset, length, parent_inode_number)
		
	
	#IMPLEMENTS WRITE
	def write(self, path, inode_number_cwd, offset, data):
		parent_inode_number = self.LOOKUP(path, inode_number_cwd)
		parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number) 
		childname = path.split('/')[-1]
		if not parent_inode: return -1
		if childname not in parent_inode.directory:
			print("Error FileNameLayer: File does not exist!")
			return -1
		child_inode_number = parent_inode.directory[childname]
		return interface.write(child_inode_number, offset, data, parent_inode_number)
		'''WRITE YOUR CODE HERE'''

	#HARDLINK
	def link(self, old_path, new_path, inode_number_cwd):
		'''WRITE YOUR CODE HERE'''
		old_inode_number = self.LOOKUP(old_path, inode_number_cwd)
		new_inode_number = self.LOOKUP(new_path, inode_number_cwd)
		old_inode = interface.INODE_NUMBER_TO_INODE(old_inode_number)
		#new_inode = interface.INODE_NUMBER_TO_INODE(new_inode_number)

		childname = old_path.split('/')[-1]
		if not old_inode: 
			return -1
		if childname not in old_inode.directory:
			print("Error FileNameLayer: File does not exist!")
			return -1
		new_name = new_path.split('/')[-1]
		child_inode_number = old_inode.directory[childname]		
		if child_inode_number != -1:
			return interface.link(child_inode_number, new_name ,new_inode_number )


	#REMOVES THE FILE/DIRECTORY
	def unlink(self, path, inode_number_cwd):
		if path == "": 
			print("Error FileNameLayer: Cannot delete root directory!")
			return -1
		parent_inode_number = self.LOOKUP(path, inode_number_cwd)
		parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number) 
		childname = path.split('/')[-1]
		if not parent_inode: return -1
		if childname not in parent_inode.directory:
			print("Error FileNameLayer: File does not exist!")
			return -1
		child_inode_number = parent_inode.directory[childname]		
		if (interface.unlink(child_inode_number, parent_inode_number, childname) == -1):
			return -1
		del parent_inode.directory[childname]
		interface.update_inode_table(parent_inode, parent_inode_number)
		return 0		
		'''WRITE YOUR CODE HERE'''


	#MOVE
	def mv(self, old_path, new_path, inode_number_cwd):
		'''WRITE YOUR CODE HERE'''
		old_inode_number = self.LOOKUP(old_path, inode_number_cwd)
		# import pdb ; pdb.set_trace()
		if(new_path  != ""):
			if(new_path[-1] != "/"):
				new_path = new_path + "/"
		new_inode_number = self.LOOKUP(new_path, inode_number_cwd)

		old_inode = interface.INODE_NUMBER_TO_INODE(old_inode_number)
		new_inode = interface.INODE_NUMBER_TO_INODE(new_inode_number)

		childname = old_path.split('/')[-1]
		if not old_inode: return -1
		if not new_inode: return -1
		if childname not in old_inode.directory:
			print("Error FileNameLayer: File does not exist!")
			return -1
		child_inode_number = old_inode.directory[childname]		

		if child_inode_number != -1:
			new_inode.directory[childname] = child_inode_number
			del old_inode.directory[childname]
			interface.update_inode_table(old_inode, old_inode_number)
			interface.update_inode_table(new_inode, new_inode_number)
			
		# 	self.link(old_path, new_path, inode_number_cwd)
		# 	self.unlink(old_path, inode_number_cwd)
		# print(new_path)
		# print(old_inode.directory)
		# print(new_inode.directory)



	