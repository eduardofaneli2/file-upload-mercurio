import os
from flask import jsonify, request
from common.conexao import get_conexao
from common.usuario_logado import UsuarioLogado
from routes.session import check_authorization
from dao.register_dao import RegisterDAO
from model.solicitacao import Solicitacao
from model.usuario import Usuario
from common.envio_email import EnvioEmail

class Register(object):
    def __init__(self, request):
        self.request = request

    def register(self, app):
        try:
            email = self.request.json['email']
            password = self.request.json['senha']
            cnpj = self.request.json['cnpj']
            nome =self. request.json['nome']

            solicitacao = Solicitacao(0, email, cnpj, password, nome)

            conn = get_conexao()

            register = RegisterDAO(conn, solicitacao).verificarSolicitacao()

            if (register.get_id() != ''):
                raise Exception("Já existe uma solicitação para o email: '{}'".format(register.get_email()))

            register = RegisterDAO(conn, solicitacao).new()

            email = EnvioEmail(solicitacao.get_email(), app).enviar_confirmacao()

            conn.close()

        except Exception as ex:
            print(ex)
            return jsonify({'success': False, 'message': str(ex)}), 500
        else:
            return jsonify({'success': True, 'id_solicitacao': register.get_id()}), 200;


    def accept_register(self):
        try:
            conn = get_conexao()

            id = self.request.json['id']

            usuario = RegisterDAO(conn, None).buscarSolicitacao(id)

            if (usuario.get_nome == ''):
                raise Exception("Nenhuma solicitação encontrada para o ID: '{}'.".format(id))
            else:
                id_usuario = RegisterDAO(conn, None).aprovar_registro(usuario)
                RegisterDAO(conn, None).excluir_solicitacao(id)

            conn.close()

        except Exception as ex:
            return jsonify({'success': False, 'message': str(ex)}), 403
        else:
            return jsonify({'success': True, 'id_usuario': id_usuario}), 200;


    def __novo(self, solicitacao):
        return {'id': solicitacao[6], 'nome': solicitacao[0], 'email': solicitacao[1], 'empresa': solicitacao[4], 'cnpj': solicitacao[5]}


    @check_authorization
    def all_registers(self):
        try:
            conn = get_conexao()

            user = UsuarioLogado().identificar_usuario(self.request)

            solicitacoes = RegisterDAO(conn, None).listar_confirmados(user.get_empresa())

            lista = []

            for solicitacao in solicitacoes:
                lista.append(self.__novo(solicitacao))

            conn.close()

        except Exception as ex:
            return jsonify({'success': False, 'message': str(ex)}), 500
        else:
            return jsonify({'success': True, 'solicitacoes': lista}), 200;
