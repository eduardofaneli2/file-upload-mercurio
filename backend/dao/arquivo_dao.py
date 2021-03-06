from common.conexao import get_conexao
from model.empresa import Empresa
from model.usuario import Usuario
from model.arquivo import Arquivo
from dao.categoria_dao import CategoriaDao

class ArquivoDao(object):
    def __init__(self, conn, usuario):
        self.usuario = usuario
        self.conn = conn

    def __get_sql(self):
        sql = "SELECT id, descricao, categoria_id, chave, usuario_id, data_criacao, hash, status, tipo, empresa_id, arquivo, hash, tamanho "
        sql += " FROM ged.arquivos "

        return sql


    def obter(self, id):
        sql = self.__get_sql()
        sql += " where id = {} and usuario_id = {} and empresa_id = {}"
        sql = sql.format(id, self.usuario.get_id(), self.usuario.get_empresa().get_id())
        cursor = self.conn.cursor()
        cursor.execute(sql)

        rs = cursor.fetchone()

        arquivo = self.__novo(rs)

        cursor.close()

        return arquivo


    def __novo(self, rs):
        keys = rs[3].split(";")
        if keys[-1] == '':
            keys = keys[:-1]

        categoria = CategoriaDao(self.conn, self.usuario).obter_pelo_id(rs[2])

        return Arquivo(rs[1], categoria, keys, rs[8], rs[5], self.usuario, rs[10], rs[12], rs[0])


    def listar(self):
        sql = self.__get_sql()
        sql += " where usuario_id = {} and empresa_id = {}"
        sql = sql.format(self.usuario.get_id(), self.usuario.get_empresa().get_id())

        cursor = self.conn.cursor()
        cursor.execute(sql)

        lista = []

        ds = cursor.fetchall()

        for rs in ds:
            lista.append(self.__novo(rs))

        cursor.close()

        return lista

    def listar(self, pagina, quantidade):

        inicio = (pagina - 1) * quantidade
        fim = quantidade * pagina

        sql = self.__get_sql()
        sql += " where usuario_id = {} and empresa_id = {} "
        sql += " limit {} offset {}"
        sql = sql.format(self.usuario.get_id(), self.usuario.get_empresa().get_id(), fim, inicio)

        cursor = self.conn.cursor()
        cursor.execute(sql)

        lista = []

        ds = cursor.fetchall()

        for rs in ds:
            lista.append(self.__novo(rs))

        cursor.close()

        return lista



    def pesquisar(self, texto):
        sql = self.__get_sql()
        sql += " where usuario_id = {} and empresa_id = {} and lower(descricao||chave||arquivo) like '%{}%'"
        sql = sql.format(self.usuario.get_id(), self.usuario.get_empresa().get_id(), texto.lower())

        cursor = self.conn.cursor()
        cursor.execute(sql)

        lista = []

        ds = cursor.fetchall()

        for rs in ds:
            lista.append(self.__novo(rs))

        cursor.close()

        return lista


    def adicionar(self, arquivo):
        keys = ''
        for key in arquivo.get_keys():
            keys += '{};'.format(key)

        sql = "INSERT INTO ged.arquivos "
        sql += " (id, descricao, categoria_id, chave, usuario_id, data_criacao, hash, tipo, empresa_id, arquivo, tamanho) "
        sql += "VALUES "
        sql += " (nextval('ged.seq_arquivo'), '{}', {}, '{}', {}, current_timestamp, '{}', '{}', {}, '{}', {}) returning id "
        sql = sql.format(arquivo.get_descricao(),
                          arquivo.get_categoria().get_id(),
                          keys,
                          arquivo.get_usuario_postou().get_id(),
                          arquivo.get_hash(),
                          arquivo.get_tipo().upper(),
                          arquivo.get_usuario_postou().get_empresa().get_id(),
                          arquivo.get_arquivo(),
                          arquivo.get_tamanho())

        print(sql)

        cursor = self.conn.cursor()
        cursor.execute(sql)

        rs = cursor.fetchone()

        id = rs[0]

        self.conn.commit()

        cursor.close()

        return id
