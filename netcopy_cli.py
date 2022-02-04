from socket import socket, AF_INET, SOCK_STREAM, timeout, SOL_SOCKET, SO_REUSEADDR
import hashlib
import sys
import struct

def main(argv):
	srv_ip = argv[1]
	srv_port = int(argv[2])
	chsum_srv_ip = argv[3]
	chsum_srv_port = int(argv[4])
	file_id = argv[5]
	filename = argv[6]

	BUFFER_SIZE = 4096
	hasher = hashlib.md5()
	srv_addr = (srv_ip, srv_port)
	chsum_srv_addr = (chsum_srv_ip, chsum_srv_port)
	
	with open(filename, "r") as f:
		content = f.read()
		hasher.update(content.encode())

		f.seek(0)
		
		with socket(AF_INET, SOCK_STREAM) as client:
			client.connect(srv_addr)
			
			while True:
				data = f.read(BUFFER_SIZE)
				if not data:
					break
					
				client.sendall(data.encode())
			client.close()
		
	print("**File sent**")
		
	with socket(AF_INET, SOCK_STREAM) as client:
		client.connect(chsum_srv_addr)
		
		data = "BE|" + file_id + "|60|" + str(len(hasher.hexdigest())) + "|" + hasher.hexdigest()
		print(data)
		
		client.sendall(data.encode())
		
		client.close()

if __name__ == "__main__":
	main(sys.argv)
