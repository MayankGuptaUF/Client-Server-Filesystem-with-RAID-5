import portNumber
import sys

portNumber.init()

def updatePort(port):
	portNumber.portN.append(port)

if(len(sys.argv) < 4):
	print("usage python UI.py <number of servers> <programable write delay> <programable read delay>")
	exit()
PortNumber = 8000
delay = int(sys.argv[2])

portNumber.writeDelay(delay)
portNumber.readDelay(int(sys.argv[3]))

servers = int(sys.argv[1])
for i in range(servers):
	updatePort(PortNumber + i)

import FileSystem as F1

# print("starting testing")
F1.Initialize_My_FileSystem()
my_object1 = F1.FileSystemOperations()
## UNIT TESTS START
# string_ = ""
# string_1 = ""
# for i in range(300):
# 	string_ += str(i)
# for i in range(770):
# 	string_1 += str(1)
# print(string_)
# print(string_1)
# my_object1.mkdir("/A")
# my_object1.create("/A/1.txt")
# my_object1.write("/A/1.txt", string_, 0)
# my_object1.status()
# my_object1.write("/A/1.txt", string_1, 0)
# my_object1.write("/A/1.txt", "helloWorld", 126)
# my_object1.write("/A/1.txt", "helloWorld", 769)
# my_object1.mv("/A/1.txt", "/")
# my_object1.create("/A/1.txt")
# my_object1.write("/A/1.txt", "this_is_the_new_file", 0)
# # my_object1.create("/1.txt")
# my_object1.write("/1.txt", "byeee", 769)
# my_object1.write("/1.txt", "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111", 772)
# my_object1.write("/1.txt", string_, 900)
# my_object1.read("/1.txt", 1400, 38)
##UNIT TEST END
print("Running input terminal....")
print("a.	mkdir <directory to be created>\nExample: mkdir /A")
print("b.	create <file to be created>\nExample: create /A/new_file.txt")
print("c.	write <file to be written to> <data to be written> <offset>")
print("Example: write /A/new_file.txt \"hello World!\" 0")
print("d.	read <file to be read> <offset>\nExample: read /A/new_file.txt 5")
print("e.	rm <file to be removed>\nExample: rm /A/new_file.txt")
print("f.	mv <file to be moved> <new location>\nExample: mv /A/new_file.txt / \nThis command actually moves to file new_file.txt from directory \"/A\" to root directory \"/\" with the same name.")
print("g.	status")
print("h.	exit\n\n")
while(1):
	try:
		command = str(raw_input("$ "))
		tokens = (command.split())
		if (tokens[0] == "mkdir"):
			print("generating directory" + tokens[1])
			my_object1.mkdir(tokens[1])
		elif(tokens[0] == "create"):
			my_object1.create(tokens[1])
		elif(tokens[0] == "write"):
			# print(int(tokens[3]))
			string_to_write = command.split("\"")[1]
			my_object1.write(tokens[1], string_to_write, int(tokens[-1]))
		elif(tokens[0] == "status"):
			my_object1.status()
		elif(tokens[0] == "read"):
			my_object1.read(tokens[1], int(tokens[2]), int(tokens[3]))
		elif(tokens[0] == "rm"):
			my_object1.rm(tokens[1])
		elif(tokens[0] == "mv"):
			my_object1.mv(tokens[1],tokens[2])
		elif(tokens[0] == "exit"):
			break
		else:
			print("command not identified")
	except Exception as err :
			print("Invalid input.")

