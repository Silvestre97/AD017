
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplica��es distribu�das - Projeto 1 - lock_server.py
Grupo: 017
N�meros de aluno: 50014, 50023, 50042
"""

# Zona para fazer importa��o

import datetime, signal, sys, pickle, struct, socket
from sock_utils import receive_all, create_tcp_server_socket
from multiprocessing import Semaphore

pool = ""       # variavel que guarda a instancia da class lock_pool
dicionario = "" # dicionario que guarda todas as instancias da class resource_lock

###############################################################################

class resource_lock:
    def __init__(self):
        """
        Define e inicializa as caracter�sticas de um LOCK num recurso.
        """
        self.status = "UNLOCKED"    # estado de iniciacao de um recurso do sistema
        self.count = 0              # numero de vezes que o recurso foi bloqueado
        self.time = -1              # tempo de concessao de bloqueio
        self.client_id = ""         # identificador do cliente que reservou o recurso


    def lock(self, client_id, time_limit):
        """
        Bloqueia o recurso se este n�o estiver bloqueado ou inativo, ou mant�m o bloqueio
        se o recurso estiver bloqueado pelo cliente client_id. Neste caso renova
        o bloqueio do recurso at� time_limit.
        Retorna True se bloqueou o recurso ou False caso contr�rio.
        """
        if (self.status == "UNLOCKED") or (self.status == "LOCKED" and self.client_id == client_id):
            self.status = "LOCKED"
            self.count += 1
            data = datetime.datetime.now()                              # variavel que guarda o tempo atual
            self.client_id = client_id
            self.time = data + datetime.timedelta(seconds = time_limit) # tempo limite de bloqueio do recurso
            return True
        else:
            return False


    def urelease(self):
        """
        Liberta o recurso incondicionalmente, alterando os valores associados
        ao bloqueio.
        """
        self.status = "UNLOCKED"
        self.client_id = ""
        self.time = -1

    def release(self, client_id):
        """
        Liberta o recurso se este foi bloqueado pelo cliente client_id,
        retornando True nesse caso. Caso contr�rio retorna False.
        """
        if self.client_id == client_id:
            if pool.check() < pool.Y:       # verifica se ja atingiu os Y bloqueios
                self.status = "UNLOCKED"
                self.client_id = ""
                self.time = -1
            else:                           # disable se ja atingiu os Y bloqueios
                self.disable()
            return True
        else:
            return False

    def test(self):
        """
        Retorna o estado de bloqueio do recurso ou inativo, caso o recurso se
        encontre inativo.
        """
        statu = self.status
        return statu

    def stat(self):
        """
        Retorna o n�mero de vezes que este recurso j� foi bloqueado em k.
        """
        contador = self.count
        return contador

    def disable(self):
        """
        Coloca o recurso inativo/indispon�vel incondicionalmente, alterando os
        valores associados � sua disponibilidade.
        """
        self.status = "DISABLED"
        self.client_id = ""
        self.time = -1


###############################################################################

class lock_pool:
    def __init__(self, N, K, Y, T):
        """
        Define um array com um conjunto de locks para N recursos. Os locks podem
        ser manipulados pelos m�todos desta classe.
        Define K, o n�mero m�ximo de bloqueios permitidos para cada recurso. Ao
        atingir K, o recurso fica indispon�vel/inativo.
        Define Y, o n�mero m�ximo permitido de recursos bloqueados num dado
        momento. Ao atingir Y, n�o � poss�vel realizar mais bloqueios at� que um
        recurso seja libertado.Define T, o tempo m�ximo de concess�o de bloqueio.
        """

        self.N = N  # numero de recursos que v�o ser geridos
        self.K = K  # numero max de bloqueios para cada recurso
        self.Y = Y  # numero max de recursos bloqueados permitidos num dado momento
        self.T = T  # tempo max de bloqueio


    def clear_expired_locks(self):
        """
        Verifica se os recursos que est�o bloqueados ainda est�o dentro do tempo
        de concess�o do bloqueio. Liberta os recursos caso o seu tempo de
        concess�o tenha expirado.
        """
        for objecto in dicionario.values():
            if objecto.status == "LOCKED" and objecto.time < datetime.datetime.now():
                objecto.release(objecto.client_id) #Usar este release(objecto.client_id) ou o urelease()?

    def lock(self, resource_id, client_id, time_limit):
        """
        Tenta bloquear o recurso resource_id pelo cliente client_id, at� ao
        instante time_limit.
        O bloqueio do recurso s� � poss�vel se o recurso estiver ativo, n�o
        bloqueado ou bloqueado para o pr�prio requerente, e Y ainda n�o foi
        excedido. � aconselh�vel implementar um m�todo __try_lock__ para
        verificar estas condi��es.
        Retorna True em caso de sucesso e False caso contr�rio.
        """
        if dicionario[resource_id].lock(client_id, time_limit):
            return True
        else:
            return False

    def release(self, resource_id, client_id):
        """
        Liberta o bloqueio sobre o recurso resource_id pelo cliente client_id.
        True em caso de sucesso e False caso contr�rio.
        """
        objecto = dicionario[resource_id]
        if objecto.test() == "LOCKED":
            if objecto.release(client_id):
                return True
            else:
                return False
        else:
            return False

    def test(self,resource_id):
        """
        Retorna True se o recurso resource_id estiver activo e False caso
        esteja bloqueado ou inativo.
        """
        if dicionario[resource_id].test() == "UNLOCKED":
            return True
        else:
            return False


    def stat(self,resource_id):
        """
        Retorna o n�mero de vezes que o recurso resource_id j� foi bloqueado, dos
        K bloqueios permitidos.
        """
        return dicionario[resource_id].count

    def stat_y(self):
        """
        Retorna o n�mero de recursos bloqueados num dado momento do Y permitidos.
        """
        count = 0
        for objeto in dicionario.values():
            count += objeto.count

        return count

    def stat_n(self):
        """
        Retorna o n�mero de recursos dispon�neis em N.
        """
        counter = 0
        for objecto in dicionario.values():
            if objecto.test() == "UNLOCKED":
                counter += 1
        return counter

    def __repr__(self):
        """
        Representa��o da classe para a sa�da standard. A string devolvida por
        esta fun��o � usada, por exemplo, se uma inst�ncia da classe for
        passada � fun��o print.
        """
        # Acrescentar na output uma linha por cada recurso bloqueado, da forma:
        # recurso <n�mero do recurso> bloqueado pelo cliente <id do cliente> at�
        # <instante limite da concess�o do bloqueio>
        #
        # Caso o recurso n�o esteja bloqueado a linha � simplesmente da forma:
        # recurso <n�mero do recurso> desbloqueado
        # Caso o recurso n�o esteja inativo a linha � simplesmente da forma:
        # recurso <n�mero do recurso> inativo

        output = ""
        for chave, objecto in dicionario.items():
            string = ""
            if objecto.test() == "LOCKED":
                string = "Recurso " + str(chave) + " bloqueado pelo cliente " + objecto.client_id + " at� " + str(objecto.time)[:-7]
            elif objecto.test() == "UNLOCKED":
                string = "Recurso " + str(chave) + " desbloqueado"
            else:
                string = "Recurso " + str(chave) + " inativo"
            output += (string+"\n")
        return output

    def check_K(self):
        """
        Verifica se j� atingiu os K bloqueios de cada recurso, dando disable aos recursos
        que j� o tenham atingido.
        """
        for objeto in dicionario.values():
            if objeto.stat() >= self.K:
                objeto.disable()

    def check(self):
        """
        Verifica se j� atingiu os Y bloqueios permitidos pelo servidor, retornando o total
        de bloqueios feitos no servidor.
        """
        count = 0
        for objeto in dicionario.values():
            count +=  objeto.count

        return count

###############################################################################

# c�digo do programa principal

def dictionary_create(instance):
    """
    Cria um dicionario em que os seus valores sao instancias da class resource_lock.
    Retorna um dicionario.
    """
    d = {}
    for x in range(1, instance.N + 1):
        d[x] = resource_lock()
    return d

def servidor():
    """
    Fun��o usada para iniciar o programa, processando a linha de comandos, aceitando liga��es de clientes,
    processando o pedido, gerindo os recursos definidos e enviando a devida resposta ao pedido.
    """
    # python lock_server.py <PORT> <n recursos> <maximo de bloqueios k> <maximo de bloqueios y> <tempo limite de ligacao(segundos)
    try:
        PORT = int(sys.argv[1])
        N = int(sys.argv[2])
        K = int(sys.argv[3])
        Y = int(sys.argv[4])
        T = int(sys.argv[5])
        global pool
        pool = lock_pool(N, K, Y, T)
        global  dicionario
        dicionario = dictionary_create(pool)
    except:
        raise ValueError("Argumentos inv�lidos!")

    HOST = ''
    Servidor = create_tcp_server_socket(HOST, PORT, 1)  # Cria�ao do listening socket do servidor
    semaforo = Semaphore(1)                             # Semaforo usado para garantir exclusao mutua
    keep = True                                         # variavel que mantem o servidor ligado
    while keep:
        try:
            (conn_sock, addr) = Servidor.accept()
        except:
            print 'Erro na cria��o do servidor!'
            conn_sock.close()

        semaforo.acquire()
        resp = "ACK"
        print "Ligado ao cliente: %s" % addr[0] + " na porta: " + str(PORT)

        size_bytes = conn_sock.recv(4)
        size = struct.unpack("!i",size_bytes)[0]
        conn_sock.sendall(resp)

        pool.clear_expired_locks()
        pool.check_K()
        
        msg_bytes = receive_all(conn_sock, size)        # Recebe a mensagem
        msg = pickle.loads(msg_bytes)
        
        if msg[0] == "LOCK" or msg[0]=="RELEASE":   # Verifica se o comando � LOCK ou RELEASE
            if pool.stat_y() < pool.Y:              # Verifica se h� recursos disponiveis
                if len(msg) == 3:                   # Verifica se o comando est� bem
                    try:
                        if int(msg[1]) <= pool.N:   # Verifica se � um recurso v�lido
                            if msg[0] == "LOCK":    # E processa ent�o o comando
                                if pool.lock(int(msg[1]),msg[2],T):
                                    resp = "OK"
                                else:
                                    resp = "NOK"
                            else:
                                if pool.release(int(msg[1]),msg[2]):
                                    resp = "OK"
                                else:
                                    resp = "NOK"
                        else:
                            resp = "UNKNOWN RESOURCE"
                                
                    except:
                        resp = "Argumentos Inv�lidos"
                else:
                    resp = "Argumentos Inv�lidos"
            else:
                resp = "Recursos do servidor ESGOTADOS! Por favor volte mais tarde."
                        
        elif msg[0] == "TEST" or msg[0] == "STATS":    # Verifica se o comando � TEST ou STATS
            if len(msg) == 3:                           # Verifica se o comando est� bem
                try:
                    if int(msg[1]) <= pool.N:           # Verifica se � um recurso v�lido
                        if msg[0] == "TEST":            # E processa ent�o o comando
                            resp = dicionario[int(msg[1])].test()
                        else:
                            resp = "� possivel bloquear o recurso n�mero" + str(msg[1]) + " mais " + str(pool.K - pool.stat(int(msg[1]))) + " vezes."
                    elif:
                        resp = "UNKNOWN RESOURCE"
                except:
                    resp = "Argumentos Inv�lidos"
            else:
                resp = "Argumentos Inv�lidos"
                
        elif msg[0] == "STATS-Y" or msg[0] == "STATS-N":    # Verifica se o comando � STATS-Y ou STATS-N
            if len(msg) == 2:                               # Verifica se o comando est� bem
                if pool.stat_y() < pool.Y:                  # Verifica se h� recursos disponiveis
                    if msg[0] == "STATS-Y":
                        resp = str(pool.stat_y())           
                    else:
                        resp = str(pool.stat_n())
                else:                                       # Se n�o houver
                    resp = "Recursos do servidor ESGOTADOS!"
            else:
                resp = "Argumentos Inv�lidos"

        else:       # Caso nao reconhe�a o commando
            resp = "UNKNOWN COMMAND"
            

        print pool
        conn_sock.sendall(resp)
        semaforo.release()
        conn_sock.close()

    sock.close()

if __name__ == "__main__":
    servidor()
