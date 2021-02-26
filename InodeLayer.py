import datetime, config, BlockLayer, InodeOps, MemoryInterface
import time
import math
import portNumber
servers = len(portNumber.getPort())
MemoryInterface.Initialize_My_FileSystem()
#HANDLE OF BLOCK LAYER
interface = BlockLayer.BlockLayer()
RAID_BLOCK_SIZE = config.BLOCK_SIZE*(servers-1)
class InodeLayer():

    #PLEASE DO NOT MODIFY THIS
    #RETURNS ACTUAL BLOCK NUMBER FROM RESPECTIVE MAPPING  
    def INDEX_TO_BLOCK_NUMBER(self, inode, index):
        if index == len(inode.blk_numbers): return -1
        return inode.blk_numbers[index]


    #PLEASE DO NOT MODIFY THIS
    #RETURNS BLOCK DATA FROM INODE and OFFSET
    def INODE_TO_BLOCK(self, inode, offset, length_req):
        index = offset / RAID_BLOCK_SIZE
        block_number = self.INDEX_TO_BLOCK_NUMBER(inode, index)
        if block_number == -1: return ''
        else: return interface.BLOCK_NUMBER_TO_DATA_BLOCK(block_number, offset%RAID_BLOCK_SIZE, length_req+offset%RAID_BLOCK_SIZE)


    #PLEASE DO NOT MODIFY THIS
    #MAKES NEW INODE OBJECT
    def new_inode(self, type):
        return InodeOps.Table_Inode(type)


    #PLEASE DO NOT MODIFY THIS
    #FLUSHES ALL THE BLOCKS OF INODES FROM GIVEN INDEX OF MAPPING ARRAY  
    def free_data_block(self, inode, index, server = -1):
        # import pdb ; pdb.set_trace()
        if(server == -1):
            for i in range(index, len(inode.blk_numbers)):
                for server_id in range(servers):
                    parity_server = inode.blk_numbers[i]%servers 
                    interface.free_data_block(inode.blk_numbers[i], server_id)
                inode.blk_numbers[i] = -1
            return 
        else:               
            for i in range(index, len(inode.blk_numbers)):
                parity_server = inode.blk_numbers[i]%servers 
                if(server_id != parity_server):
                    interface.free_data_block(inode.blk_numbers[i], server)
                inode.blk_numbers[i] = -1
            return

    def serverToAccess(self, offset, data_length, file_blocks):
        total_length = offset + data_length
        starting_server_blocks = (offset%RAID_BLOCK_SIZE) / config.BLOCK_SIZE
        ending_server_blocks = int(math.ceil((float(total_length) % RAID_BLOCK_SIZE)/config.BLOCK_SIZE))
        data_blocks = {}
        parity_blocks = {}
        for i in file_blocks:
            parity = i%servers
            parity_blocks[parity] = 1
            server_indexes = range(servers)
            del server_indexes[parity]
            if i == file_blocks[0]:
                del server_indexes[:starting_server_blocks]
            if i == file_blocks[-1]:
                del server_indexes[ending_server_blocks:]
            for j in server_indexes:
                data_blocks[j] = 1
        return [data_blocks, parity_blocks]

    def printWhereToWrite(self, inode, offset, data):
        to_write = len(data)
        total_length = offset + to_write
        total_blocks_req = int(math.ceil(float(total_length) / RAID_BLOCK_SIZE))
        file_blocks = []
        
        for i in inode.blk_numbers:
            if(i != -1):
                file_blocks.append(i)
            if(total_blocks_req) == len(file_blocks): #chk this
                break
        if total_blocks_req > len(file_blocks):
            new_block_req = []
            num_of_new_blocks_req = total_blocks_req - len(file_blocks)
            for i in range(num_of_new_blocks_req):
                new_block_req.append(MemoryInterface.get_valid_data_block())
            for i in new_block_req:
                interface.free_data_block(i, -1)
            file_blocks = file_blocks + new_block_req
            not_used_blocks = offset/RAID_BLOCK_SIZE
            del file_blocks[:not_used_blocks]

            data_blocks = {}
            parity_blocks = {}

            [data_blocks, parity_blocks] = self.serverToAccess(offset, len(data), file_blocks)

            print("Data is going to be written in server : "),
            for server_number in data_blocks.keys():       
                print(str(portNumber.getPort()[server_number]) + " "),
            print("")
            print("Parity is going to be written in server : "),
            for server_number in parity_blocks.keys():       
                print(str(portNumber.getPort()[server_number]) + " "),
            print("")           
        else:
            not_used_blocks = offset/RAID_BLOCK_SIZE
            del file_blocks[:not_used_blocks]
            starting_server_blocks = (offset%RAID_BLOCK_SIZE) / config.BLOCK_SIZE
            ending_server_blocks = int(math.ceil((float(total_length) % RAID_BLOCK_SIZE)/config.BLOCK_SIZE))
            data_blocks = {}
            parity_blocks = {}
            for i in file_blocks:
                parity = i%servers
                parity_blocks[parity] = 1
                server_indexes = range(servers)
                del server_indexes[parity]
                if i == file_blocks[0]:
                    del server_indexes[:starting_server_blocks]
                if i == file_blocks[-1]:
                    del server_indexes[ending_server_blocks:]
                for j in server_indexes:
                    data_blocks[j] = 1
            print("Data is going to be written in server : "),
            for server_number in data_blocks.keys():       
                print(str(portNumber.getPort()[server_number]) + " "),
            print("")
            print("Parity is going to be written in server : "),
            for server_number in parity_blocks.keys():       
                print(str(portNumber.getPort()[server_number]) + " "),
            print("")    

    #IMPLEMENTS WRITE FUNCTIONALITY
    def write(self, inode, offset, data):

        '''WRITE YOUR CODE HERE '''
        if(inode.type != 0):
            print("error:wrong type")
            return -1
        if(offset > inode.size):
            print("error: offset greater than file size")
            return -1
        
        self.printWhereToWrite(inode, offset, data)
        time.sleep(portNumber.get_write_delay())
        block_size = RAID_BLOCK_SIZE
        index = offset/block_size
        position_to_change = offset%block_size
        slice_number = (offset/config.BLOCK_SIZE)%(servers-1)
        length_req = math.ceil(float(offset%config.BLOCK_SIZE + len(data))/config.BLOCK_SIZE)*config.BLOCK_SIZE
        previous_data = self.INODE_TO_BLOCK(inode, (offset/config.BLOCK_SIZE)*config.BLOCK_SIZE, int(length_req))
        parity_server = inode.blk_numbers[index]%servers
        to_write_server = slice_number
        if parity_server == slice_number:
            to_write_server = (to_write_server + 1 )%servers
        block_to_change = inode.blk_numbers[index]
        if(block_to_change == -1):
            block_to_change = MemoryInterface.get_valid_data_block()
        inode.blk_numbers[index] = -1
        total_length = len(previous_data) + len(data)
        MemoryInterface.update_data_block(block_to_change,previous_data[0:position_to_change%config.BLOCK_SIZE] + data[:block_size - slice_number*config.BLOCK_SIZE - position_to_change%config.BLOCK_SIZE], slice_number)
        if(len(inode.blk_numbers) <= index):
            inode.blk_numbers.append(block_to_change)
        else:
            inode.blk_numbers[index] = block_to_change
        new_size = block_size*(index) + slice_number*config.BLOCK_SIZE +len(previous_data[0:position_to_change%config.BLOCK_SIZE] + data[:block_size - position_to_change%config.BLOCK_SIZE])
        if(inode.size/RAID_BLOCK_SIZE == new_size/RAID_BLOCK_SIZE):
            inode.size = new_size
        elif(inode.size < index*RAID_BLOCK_SIZE + RAID_BLOCK_SIZE):
            inode.size = index*RAID_BLOCK_SIZE + RAID_BLOCK_SIZE
        for i in range(block_size - position_to_change , len(data), block_size):
            new_entry = (data[i:i+block_size])
            to_write_server = 0
            parity_server = inode.blk_numbers[index + 1]%servers
            if(to_write_server == parity_server):
                to_write_server = (to_write_server + 1)%servers
            block_to_change = inode.blk_numbers[index + 1]
            if block_to_change == -1:
                block_to_change = MemoryInterface.get_valid_data_block()
            MemoryInterface.update_data_block(block_to_change, new_entry, 0)
            parity_server = inode.blk_numbers[index+1]%servers
            if(len(inode.blk_numbers) > index+1 ):
                inode.blk_numbers[index+1] = block_to_change
            else:
                inode.blk_numbers.append(block_to_change)
            index = index+1
            new_size = (index)*RAID_BLOCK_SIZE + len(new_entry)
            if(inode.size/config.BLOCK_SIZE == new_size/config.BLOCK_SIZE):
                inode.size = new_size
            else:
                inode.size = inode.size + len(new_entry)
        inode.time_accessed = str(datetime.datetime.now())[:19]
        inode.time_modified = str(datetime.datetime.now())[:19]
        return 0

    #IMPLEMENTS THE READ FUNCTION 
    def read(self, inode, offset, length): 
        '''WRITE   YOUR CODE HERE '''
        if(inode.type != 0):
            print("error:wrong type")
            return -1

        index = offset/RAID_BLOCK_SIZE
        cursor = offset%RAID_BLOCK_SIZE
        data = ''
        list_of_blocks_to_iterate = inode.blk_numbers
        number_of_blocks_to_read = math.ceil(float(offset + length)/RAID_BLOCK_SIZE)
        offset_length_to_read = ((offset + length)%RAID_BLOCK_SIZE)
        del list_of_blocks_to_iterate[int(number_of_blocks_to_read):]
        number_of_blocks_to_read = math.ceil(float(offset + length)/RAID_BLOCK_SIZE) - ((offset)/RAID_BLOCK_SIZE)
        length_to_get = 0
        iteration = 1
        length_temp = 0

        [data_blocks, parity_blocks] = self.serverToAccess(offset, length, list_of_blocks_to_iterate[index:])

        print("Data is going to be read from server : "),
        for server_number in data_blocks.keys():       
            print(str(portNumber.getPort()[server_number]) + " "),
        print("")

        time.sleep(portNumber.get_read_delay())

        for i in list_of_blocks_to_iterate:
            if(index == length_temp):
                if int(number_of_blocks_to_read) == 1:
                    length_to_get = offset_length_to_read
                else:
                    length_to_get = RAID_BLOCK_SIZE
                    number_of_blocks_to_read = number_of_blocks_to_read - 1
                if(i != -1) and iteration != 1:
                    data = data + str(interface.BLOCK_NUMBER_TO_DATA_BLOCK(i, 0, length_to_get))
                if iteration == 1:
                    iteration = iteration + 1
                    data = str(interface.BLOCK_NUMBER_TO_DATA_BLOCK(i, offset%RAID_BLOCK_SIZE, length_to_get))  
            else:
                length_temp = length_temp + 1
        inode.time_accessed = str(datetime.datetime.now())[:19]
        return [inode, data]

    def copy(self, inode):
        #create new inode
        if(inode.type != 0):
            print("error:wrong type")
            return -1
        new_node = self.new_inode(inode.type)
        length = inode.size
        data = self.read(inode,0,length)
        ret = self.write(new_node,0,data[1])
        if (ret ==-1):
            return -1
        return new_node

    def status(self):
        print(MemoryInterface.status())
