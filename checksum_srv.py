from socket import socket, AF_INET, SOCK_STREAM, timeout, SOL_SOCKET, SO_REUSEADDR
from select import select
import sys
import struct
import time

def main(argv):
	# argument check
	if len(argv) < 2:
		print("**At least 2 arguments needed**")
		exit(1)

	srv_ip = argv[1]
	srv_port = int(argv[2])
	
	server_addr = (srv_ip, srv_port)
	last_check = 0
	checksums = {"checksums":[]}

	with socket(AF_INET, SOCK_STREAM) as server:
		server.bind(server_addr)
		server.listen(1)
		server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		
		sockets = [ server ]
		
		while True:
			r, w, e = select(sockets, [], [], 1)
			
			if not (r or w or e):
				continue
			
			for s in r:
				if s is server:
					# client joins
					client, client_addr = s.accept()
					sockets.append(client)
					print("Client joined", client_addr)
				else:
					data = s.recv(64)
					# if 0 byte then the client left
					if not data:
						sockets.remove(s)
						s.close()
						print("Client left")
					else:
						# update validity and remove not valid checksums
						if last_check == 0:
							last_check = int(time.time())
						
						elapsed_time = last_check - int(time.time())
						last_check = int(time.time())
						for cs in checksums["checksums"]:
							print(cs)
							if cs["validity"] - elapsed_time <= 0:
								checksums.remove(cs)
							else:
								cs["validity"] -= elapsed_time
					
						# processing the received data
						data = data.decode()
						
						print("recv: ", data)
						
						cmd = data.split("|")
						print(cmd)
						resp = ""
						
						if cmd[0] == "BE":
							checksums["checksums"].append({
								"file_id" : int(cmd[1]),
								"validity" : int(cmd[2]),
								"size" : int(cmd[3]),
								"checksum" : cmd[4]
							})
							resp = "OK"
						elif cmd[0] == "KI":
							resp = "0|"
							for cs in checksums["checksums"]:
								if cs["file_id"] == int(cmd[1]):
									resp = str(cs["size"]) + "|" + str(cs["checksum"])
									break
						
						s.sendall(resp.encode())

if __name__ == "__main__":
	main(sys.argv)
