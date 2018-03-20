# -*- coding: utf-8 -*-
"""
Aplicações distribuídas - Projeto 1 - net_client.py
Grupo: 017
Números de aluno: 50014, 50023, 50042
"""

# zona para fazer importação

from sock_utils import create_tcp_client_socket, receive_all

# definição da classe server

class server:
    """
    Classe para abstrair uma ligação a um servidor TCP. Implementa métodos
    para estabelecer a ligação, para envio de um comando e receção da resposta,
    e para terminar a ligação
    """

    def __init__(self, address, port):
        """
        Inicializa a classe com parâmetros para funcionamento futuro.
        """
        self.address = address
        self.port = int(port)
        self.socket = ""

    def connect(self):
        """
        Estabelece a ligação ao servidor especificado na inicialização do
        objeto.
        """
        sock = create_tcp_client_socket(self.address, self.port)
        self.socket = sock

    def send_receive(self, data):
        """
        Envia os dados contidos em data para a socket da ligação, e retorna a
        resposta recebida pela mesma socket.
        """
        try:
            
            self.socket.sendall(data)
            msg = receive_all(self.socket, 1024)

            return msg
        except:
            print "erro no send receive"
            self.close()

    def close(self):
        """
        Termina a ligação ao servidor.
        """
        try:
            self.socket.close()
            self.socket = ""
        except:
            print "Erro ao terminar ligaçao ao servidor!"
