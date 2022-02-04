from socket import socket, AF_INET, SOCK_STREAM, timeout, SOL_SOCKET, SO_REUSEADDR
import hashlib
import sys
import struct

def main(argv):
	# argument check
	if len(argv) < 2:
		print("**At least 2 arguments needed**")
		exit(1)
	
	srv_ip = argv[1]
	srv_port = int(argv[2])
	chsum_srv_ip = argv[3]
	chsum_srv_port = int(argv[4])
	file_id = argv[5]
	filename = argv[6]
	
	BUFFER_SIZE = 4096

	with open(filename, "w+") as f:
		server_addr = (srv_ip, srv_port)
		chsum_addr = (chsum_srv_ip, chsum_srv_port)
		packer = struct.Struct("64s")
		
		hasher = hashlib.md5()
		
		with socket(AF_INET, SOCK_STREAM) as server:
			server.bind(server_addr)
			server.listen(1)
			server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			
			client, client_addr = server.accept()
			print("Joined: ", client_addr)
			
			while True:
				data = client.recv(BUFFER_SIZE)
				
				if not data:
					server.close()
					break
				
				f.write(data.decode())
	
		f.seek(0)
		content = f.read()
	
	hasher.update(content.encode())
			
	print("**File received**")
	
	with socket(AF_INET, SOCK_STREAM) as client:
		client.connect(chsum_addr)
		
		data = "KI|" + file_id
		client.sendall(data.encode())
		
		unp_data = client.recv(64).decode()
		cmd = unp_data.split("|")

		
		if cmd[1] == hasher.hexdigest():
			print("CSUM OK")
		else:
			print("CSUM CORRUPTED")
			
		client.close()

if __name__ == "__main__":
	main(sys.argv)
