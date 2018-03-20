#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações distribuídas - Projeto 1 - lock_client.py
Grupo: 017
Números de aluno: 50014, 50023, 50042
"""
# Zona para fazer imports
import pickle, struct, sys, net_client, sock_utils

# Programa principal
def verify(comandos, id):
	"""
	Verifica se os comandos estão correto e devolve uma lista final pronta a ser passada ao servidor.

	requires: Comandos é uma lista com os argumentos da linha de comandos. id é o id do cliente
	"""

	lista = []
	if comandos[0] in ["LOCK", "RELEASE"]:
		try:
			int(comandos[1])
		except:
			print "Argumentos Inválidos!"

		if commandos[0]=="LOCK":
			lista.append(10)
		else:
			lista.append(20)

		lista.append(id)
		lista.append(comandos[1])

	elif comandos[0] in ["TEST","STATS"]:
		try:
			int(comandos[1])
		except:
			pass

		if commandos[0]=="TEST":
			lista.append(30)
		else:
			lista.append(40)
		lista.append(comandos[1])

	elif comandos[0] == "STATS-Y":
		lista.append(50)

	elif comandos[0] == "STATS-N":
		lista.append(60)
	else:
		print "UNKNOWN COMMAND"

	return lista

def cliente():
	try:
		IP_Server = sys.argv[1]
		PORT = int(sys.argv[2])
		IP_Client = sys.argv[3]
	except:
		raise ValueError("Argumentos inválidos!")

	Cliente = net_client.server(IP_Server, PORT)

	while True:
		msg = raw_input("comando > ")
                if msg == "EXIT":
			exit()
		else:
			msg = msg.split(" ")
			lista = verify(msg, IP_Client)
			if lista != []:
                                
				msg_bytes = pickle.dumps(lista, -2)
				send_bytes =  struct.pack("!i",len(msg_bytes))
				

				Cliente.connect()
				
                                conn_sock.sendall(send_bytes)
                                conn_sock.sendall(msg_bytes)

                                resp_bytes = sock_utils.receive_all(Cliente, 4)
                                resp = sock_utils.receive_all(Cliente, int(struct.unpack("!i",resp_bytes)[0]))
                                resposta_final = pickle.loads(resp)


				Cliente.close()

				print 'Recebi: %s' % resposta:final
			else:
				print "UNKNOWN COMMAND"

if __name__ == "__main__":
	cliente()
