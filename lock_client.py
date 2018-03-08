#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações distribuídas - Projeto 1 - lock_client.py
Grupo: 017
Números de aluno: 50014, 50023, 50042
"""
# Zona para fazer imports
import pickle, struct, sys, net_client

# Programa principal

def cliente(IP_Server, PORT, IP_Client):
    Keep = True
    try:
        Cliente = net_client.server(IP_Server, PORT)
    except:
        print "Erro a criar a socket."

    while Keep:
        msg = raw_input("comando > ")
        if msg == "exit":
            Keep = False
        else:
            msg += " " + IP_Client
            msg = msg.split(" ")
            msg_bytes = pickle.dumps(msg, -2)

            send_bytes =  struct.pack("!i",len(msg_bytes))
            try:
                Cliente.connect()
                resposta1 = Cliente.send_receive(send_bytes)
                if resposta1 == "ACK":
                    resposta2 = Cliente.send_receive(msg_bytes)
                    Cliente.close()
                    print 'Recebi: %s' % resposta1
                    print 'Recebi: %s' % resposta2

            except:
                Cliente.close()
                print "Erro na ligaçao ao servidor."

    print "Desliguei a conecao com o servidor!"




if __name__ == "__main__":
	try:
		IP_Server = sys.argv[1]
		PORT = int(sys.argv[2])
		IP_Client = sys.argv[3]
	except:
		raise ValueError("Argumentos inválidos!")

	cliente(IP_Server, PORT, IP_Client)
