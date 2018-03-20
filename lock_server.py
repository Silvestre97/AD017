#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Aplicações distribuídas - Projeto 1 - lock_server.py
Grupo: 017
Números de aluno: 50014, 50023, 50042
"""

# Zona para fazer importação

import datetime, signal, sys, pickle, struct, socket
from sock_utils import receive_all, create_tcp_server_socket
from multiprocessing import Semaphore

pool = ""       # variavel que guarda a instancia da class lock_pool
dicionario = "" # dicionario que guarda todas as instancias da class resource_lock

###############################################################################

class resource_lock:
    def __init__(self):
        """
        Define e inicializa as características de um LOCK num recurso.
        """
        self.status = "UNLOCKED"    # estado de iniciacao de um recurso do sistema
        self.count = 0              # numero de vezes que o recurso foi bloqueado
        self.time = -1              # tempo de concessao de bloqueio
        self.client_id = ""         # identificador do cliente que reservou o recurso


    def lock(self, client_id, time_limit):
        """
        Bloqueia o recurso se este não estiver bloqueado ou inativo, ou mantém o bloqueio
        se o recurso estiver bloqueado pelo cliente client_id. Neste caso renova
        o bloqueio do recurso até time_limit.
        Retorna True se bloqueou o recurso ou False caso contrário.
        """
        if (self.status == "UNLOCKED") or (self.status == "LOCKED" and self.client_id == client_id):
            self.status = "LOCKED"
            self.count += 1
            data = datetime.datetime.now()                              # variavel que guarda o tempo atual
            self.client_id = client_id
            self.time = data + datetime.timedelta(seconds = time_limit) # tempo limite de bloqueio do recurso
            return [11, True]
        else:
            return [11, False]


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
        retornando True nesse caso. Caso contrário retorna False.
        """
        if self.client_id == client_id:
            if pool.check() < pool.Y:       # verifica se ja atingiu os Y bloqueios
                self.status = "UNLOCKED"
                self.client_id = ""
                self.time = -1
            else:                           # disable se ja atingiu os Y bloqueios
                self.disable()
            return [21, True]
        else:
            return [21, False]

    def test(self):
        """
        Retorna o estado de bloqueio do recurso ou inativo, caso o recurso se
        encontre inativo.
        """
        statu = self.status
        lista = [31]
        if statu == "UNLOCKED":
            lista.append(True)
        elif statu == "LOCKED":
            lista.append(False)
        else:
            lista.append("Disabled")
        return lista

    def stat(self):
        """
        Retorna o número de vezes que este recurso já foi bloqueado em k.
        """
        contador = self.count
        return [41, contador]

    def disable(self):
        """
        Coloca o recurso inativo/indisponível incondicionalmente, alterando os
        valores associados à sua disponibilidade.
        """
        self.status = "DISABLED"
        self.client_id = ""
        self.time = -1


###############################################################################

class lock_pool:
    def __init__(self, N, K, Y, T):
        """
        Define um array com um conjunto de locks para N recursos. Os locks podem
        ser manipulados pelos métodos desta classe.
        Define K, o número máximo de bloqueios permitidos para cada recurso. Ao
        atingir K, o recurso fica indisponível/inativo.
        Define Y, o número máximo permitido de recursos bloqueados num dado
        momento. Ao atingir Y, não é possível realizar mais bloqueios até que um
        recurso seja libertado.Define T, o tempo máximo de concessão de bloqueio.
        """

        self.N = N  # numero de recursos que vão ser geridos
        self.K = K  # numero max de bloqueios para cada recurso
        self.Y = Y  # numero max de recursos bloqueados permitidos num dado momento
        self.T = T  # tempo max de bloqueio


    def clear_expired_locks(self):
        """
        Verifica se os recursos que estão bloqueados ainda estão dentro do tempo
        de concessão do bloqueio. Liberta os recursos caso o seu tempo de
        concessão tenha expirado.
        """
        for objecto in dicionario.values():
            if objecto.status == "LOCKED" and objecto.time < datetime.datetime.now():
                objecto.release(objecto.client_id) #Usar este release(objecto.client_id) ou o urelease()?

    def lock(self, resource_id, client_id, time_limit):
        """
        Tenta bloquear o recurso resource_id pelo cliente client_id, até ao
        instante time_limit.
        O bloqueio do recurso só é possível se o recurso estiver ativo, não
        bloqueado ou bloqueado para o próprio requerente, e Y ainda não foi
        excedido. É aconselhável implementar um método __try_lock__ para
        verificar estas condições.
        Retorna True em caso de sucesso e False caso contrário.
        """
        if dicionario[resource_id] > 0 and dicionario[resource_id] <= self.N:
            return dicionario[resource_id].lock(client_id, time_limit)
        else:
            return [11, None]

    def release(self, resource_id, client_id):
        """
        Liberta o bloqueio sobre o recurso resource_id pelo cliente client_id.
        True em caso de sucesso e False caso contrário.
        """
        if dicionario[resource_id] > 0 and dicionario[resource_id] <= self.N:
            return dicionario[resource_id].release(client_id)
        else:
            return [21, None]

    def test(self,resource_id):
        """
        Retorna True se o recurso resource_id estiver activo e False caso
        esteja bloqueado ou inativo.
        """
        if dicionario[resource_id] > 0 and dicionario[resource_id] <= self.N:
            return dicionario[resource_id].test()
        else:
            return [31, None]


    def stat(self,resource_id):
        """
        Retorna o número de vezes que o recurso resource_id já foi bloqueado, dos
        K bloqueios permitidos.
        """
        if dicionario[resource_id] > 0 and dicionario[resource_id] <= self.N:
            return [41, dicionario[resource_id].count]
        else:
            return [41, None]

    def stat_y(self):
        """
        Retorna o número de recursos bloqueados num dado momento do Y permitidos.
        """
        count = 0
        for objeto in dicionario.values():
            count += objeto.count

        return [51, count]

    def stat_n(self):
        """
        Retorna o número de recursos disponíneis em N.
        """
        counter = 0
        for objecto in dicionario.values():
            if objecto.test() == "UNLOCKED":
                counter += 1
        return [61, counter]

    def __repr__(self):
        """
        Representação da classe para a saída standard. A string devolvida por
        esta função é usada, por exemplo, se uma instância da classe for
        passada à função print.
        """
        # Acrescentar na output uma linha por cada recurso bloqueado, da forma:
        # recurso <número do recurso> bloqueado pelo cliente <id do cliente> até
        # <instante limite da concessão do bloqueio>
        #
        # Caso o recurso não esteja bloqueado a linha é simplesmente da forma:
        # recurso <número do recurso> desbloqueado
        # Caso o recurso não esteja inativo a linha é simplesmente da forma:
        # recurso <número do recurso> inativo

        output = ""
        for chave, objecto in dicionario.items():
            string = ""
            if objecto.test() == "LOCKED":
                string = "Recurso " + str(chave) + " bloqueado pelo cliente " + objecto.client_id + " até " + str(objecto.time)[:-7]
            elif objecto.test() == "UNLOCKED":
                string = "Recurso " + str(chave) + " desbloqueado"
            else:
                string = "Recurso " + str(chave) + " inativo"
            output += (string+"\n")
        return output

    def check_K(self):
        """
        Verifica se já atingiu os K bloqueios de cada recurso, dando disable aos recursos
        que já o tenham atingido.
        """
        for objeto in dicionario.values():
            if objeto.stat() >= self.K:
                objeto.disable()

    def check(self):
        """
        Verifica se já atingiu os Y bloqueios permitidos pelo servidor, retornando o total
        de bloqueios feitos no servidor.
        """
        count = 0
        for objeto in dicionario.values():
            count +=  objeto.count

        return count

###############################################################################

# código do programa principal

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
    Função usada para iniciar o programa, processando a linha de comandos, aceitando ligações de clientes,
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
        raise ValueError("Argumentos inválidos!")

    HOST = ''
    Servidor = create_tcp_server_socket(HOST, PORT, 1)  # Criaçao do listening socket do servidor
    semaforo = Semaphore(1)                             # Semaforo usado para garantir exclusao mutua
    keep = True                                         # variavel que mantem o servidor ligado
    while keep:
        try:
            (conn_sock, addr) = Servidor.accept()
        except s.error as err:
    		print "Erro na criacao do socket de conecao: ", err
    		exit()

        resp = ""

        pool.clear_expired_locks()
        pool.check_K()
        
        msg_nbytes = receive_all(Servidor, 4)
        msg_bytes = receive_all(Servidor, int(struct.unpack("!i",msg_nbytes)[0]))
        msg = pickle.loads(resp)
        
        if msg[0] == 10:
            resp = pool.lock(msg[-1], msg[1], T)
        elif msg[0] == 20:
            resp = pool.release(msg[-1],msg[1])
        elif msg[0] == 30:
            resp = pool.test(msg[1])
        elif msg[0] == 40:
            resp = pool.stat(msg[1])
        elif msg[0] == 50:
            resp = pool.stat_y()
        elif msg[0] == 60:
            resp = pool.stat_n()
        else:
            resp = "UNKNOWN COMMAND"

        msg_bytes = pickle.dumps(resp, -2)
        size_bytes = struct.pack("!i",len(msg_bytes))
        conn_sock.sendall(size_bytes)
        conn_sock.sendall(msg_bytes)
        conn_sock.close()

    sock.close()

if __name__ == "__main__":
    servidor()
