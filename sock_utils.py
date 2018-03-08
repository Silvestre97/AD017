# -*- coding: utf-8 -*-
import socket as s

def create_tcp_server_socket(address, port, queue_size):
	"""

	"""
	try:
		sock = s.socket(s.AF_INET, s.SOCK_STREAM)
		sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
		sock.bind((address, port))
		sock.listen(queue_size)
		return sock
	except s.error:
		print "Erro na criacao do socket!"

def create_tcp_client_socket(address, port):
	"""

	"""
	try:
		sock = s.socket(s.AF_INET, s.SOCK_STREAM)
		sock.connect((address, port))
		return sock
	except s.error:
		print "Erro na criacao do socket!"

def receive_all(socket, length):
	"""

	"""
	try:
		count = 0
		dados = ''
		while(count < length):
			dados += socket.recv(1024)
			count += 1024
		return dados
	except:
		print "Erro na rececao de dados"
