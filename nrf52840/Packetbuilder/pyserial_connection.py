import serial
import threading

DEBUG = True

port = 'COM10'
baud = 9600
timeout = 1
ser = serial.Serial(port, baudrate = baud, timeout = timeout) 

def handle_data(data):
	data_array = data.split(' ')
	method_name = data_array[0]
	data_array.pop(0)
	debug("method_name: " + method_name)

	possibles = globals().copy()
	possibles.update(locals())
	method = possibles.get(method_name)
	if not method:
		unknownCommand(method_name)
	else:
		method(data_array)

def debug(message):
	if DEBUG:
		print(message)

def read_from_port(ser):
		while True:
			end = False
			readbuffer = ""
			ser.write("input> ".encode())
			while not end:
				read = ser.read(1).decode()
				print(read)
				if bool(read):
					ascii_numer = ord(read[0]) 
					debug("ascii_numer: " + str(ascii_numer))
					if ascii_numer == 13:
						debug(readbuffer)
						ser.write("\r\n".encode())
						handle_data(readbuffer)
						end = True 
				
					if  not ((ascii_numer == 13) or (ascii_numer == 127)):
						readbuffer += read
						ser.write(read.encode())

					if ord(read[0]) == 127:
						print(readbuffer)
						print(len(readbuffer))
						if len(readbuffer) > 0:
							readbuffer = readbuffer[:-1]
							ser.write(read.encode())
						
			# # readline does not display content you entered immediatly
			# reading = ser.readline() #.decode
			# if reading.strip():
			# 	ser.write(reading + "\r\n")
			# 	handle_data(reading)
			# 	ser.write("\r\ninput> ")

def main():
	ser.write("\r\n \r\n Be a nice person and do not use Arrow Keys and Tab at this point \r\n".encode())
	thread = threading.Thread(target=read_from_port, args=(ser,))
	thread.start()

def unknownCommand(mathod_name):
	print("unknownCommand detected")
	ser.write(("output> '" + mathod_name + "' is no valid command  \r\n").encode())

# add further commands here

def healthcheck(args):
	# ToDo add further health checks
	print("pyserial is working")
	ser.write(("output> healthcheck successfull \r\n").encode())

def send(args):
	print("send command detected with args: " + str(args))
	ser.write(("output> sending with args: " + str(args) +  "\r\n").encode())

def receive(args):
	print("receive command detected with args: " + str(args))
	ser.write(("output> receiving with args: " + str(args) +  "\r\n").encode())

def configure(args):
	print("configure command detected with args: " + str(args))
	ser.write(("output> configuring device with args: " + str(args) +  "\r\n").encode())

main()