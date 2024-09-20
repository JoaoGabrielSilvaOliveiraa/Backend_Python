import cx_Oracle
import re

# Gustavo Lopes Santos da Silva RM: 556859
# Heloisa Alves de Mesquita RM: 59145
# João Gabriel Silva Oliveira RM: 555308

# ANOTAÇÃO IMPORTANTE: Foi usado a extensão Prettier para correção da formatação dos códigos!

# declaração global pra poder controlar o login
logado = False
id_do_usuario = None


# conexão do banco de dados
def get_connection():
    return cx_Oracle.connect(
        user="RM555308", password="211205", dsn="oracle.fiap.com.br:1521/ORCL"
    )


# Função para login (READ)
def login():
    global logado, id_do_usuario

    if logado:
        print("Você já está logado.")
        return True

    email = input("\nDigite o seu email: ")
    senha = input("Digite a sua senha: ")

    try:
        connection = get_connection()  # comando padrão pra pegar a conexão
        cursor = (
            connection.cursor()
        )  # o cursor é uma ferramenta predefinida nas APIs de acesso a banco de dados, portanto esse comando aqui é padronizado.

        cursor.execute(  # aqui o cursor ele acessa a função abaixo, que no caso seleciona do ID do usuario e através do ID ele acessa o email pra verificar se a coluna email na tabela usuario corresponde o valor que foi fornecido para o parametro email
            """
            SELECT id FROM Usuario WHERE email = :email AND senha = :senha
            """,  # filtrando pelo ID do usuario e verificando se o valor do email é correspondendo e a senha também
            email=email,
            senha=senha,
        )

        user = (
            cursor.fetchone()
        )  # se o email e a senha for encontrada no banco dados, ele armazena o ID no current_user_id
        if user:
            id_do_usuario = user[0]
            logado = True
            print("\nLogin realizado com sucesso!\n")
            return True
        else:
            print(
                "\nAs credenciais estão inválidas ou não foram encontradas. Por favor, verifique e tente novamente!\n"
            )
            return False
    except (
        cx_Oracle.DatabaseError
    ) as e:  # armazenei em uma variavel E (E de erro) para que eu possa acessar informações detalhadas sobre o erro que ocorreu
        print(f"Erro ao conectar-se ao banco: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def validar_email(email):
    # Regex para validar o formato do email
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(regex, email) is not None


# Função pra fazer o cadastro (CREATE)
def cadastro():
    while True:
        email = input("\nDigite o seu email:")

        if not validar_email(email):
            print("Email inválido. Por favor, digite um email válido.")
            continue

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                """SELECT email FROM Usuario WHERE email = :email""",
                email=email,
            )

            if cursor.fetchone():
                print("Este email já foi cadastrado, faça login!")
                return

            senha = input("Digite a sua senha:  ")
            confirmar_senha = input("Digite novamente a senha: ")

            if senha == confirmar_senha:
                nome = input("Insira seu nome: ")
                cursor.execute(
                    """INSERT INTO Usuario (email, senha, nome) VALUES (:email, :senha, :nome)""",
                    email=email,
                    senha=senha,
                    nome=nome,
                )
                connection.commit()
                print("\nO usuário foi cadastrado com sucesso.\n")
            else:
                print("\nAs senhas não são as mesmas. Tente novamente.\n")

            print("Retornando para o menu.\n")
            return
        except cx_Oracle.DatabaseError as e:
            print(f"Erro ao conectar-se ao banco: {e}")
        finally:
            cursor.close()
            connection.close()


# Função pra atualizar as credenciais
def atualizar_credenciais():
    global logado, id_do_usuario

    if not logado:
        print("\nVocê precisa estar logado para atualizar suas credenciais.\n")
        return

    novo_nome = input("Atualize seu nome: ")
    nova_senha = input("Atualize sua senha: ")
    confirmar_senha = input("Digite novamente sua nova senha para confirmação: ")

    if nova_senha != confirmar_senha:
        print("As senhas não são as mesmas. Tente novamente.")
        return

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE Usuario SET nome = :novo_nome, senha = :nova_senha WHERE id = :usuario_id """,
            novo_nome=novo_nome,
            nova_senha=nova_senha,
            usuario_id=id_do_usuario,
        )
        connection.commit()
        print("Usuário atualizado com sucesso!")
    except cx_Oracle.DatabaseError as e:
        print(f"Erro ao atualizar o banco de dados: {e}")
    finally:
        cursor.close()
        connection.close()


# Função para excluir usuário
def excluir_usuario():
    global logado, id_do_usuario

    if not logado:
        print("Você precisa estar logado para excluir a sua conta!")
        return

    confirmacao = (
        input("Tem certeza que deseja excluir sua conta? (sim/não): ").strip().lower()
    )
    if confirmacao != "sim":
        print("Exclusão cancelada.")
        return

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # excluir os registros na tabela localização que tem relação com o usuario
        cursor.execute(
            """
            DELETE FROM Localizacao WHERE fk_usuario_id = :usuario_id""",
            usuario_id=id_do_usuario,
        )
        connection.commit()

        # excluir os registros na tabela Automovel que tem relação com o usuario
        cursor.execute(
            """
            DELETE FROM Automovel WHERE fk_usuario_id = :usuario_id  """,
            usuario_id=id_do_usuario,
        )
        connection.commit()

        # e por fim, excluir o usuario.
        cursor.execute(
            """
            DELETE FROM Usuario WHERE id = :usuario_id """,
            usuario_id=id_do_usuario,
        )
        connection.commit()

        print("Conta apagada com sucesso!")
        logado = False  # aqui ele faz o logout da conta transformando o estado logado em falso!
    except cx_Oracle.DatabaseError as e:
        print(f"Erro ao tentar excluir um usuário do banco de dados: {e}")
    finally:
        cursor.close()
        connection.close()


# Uma função que obtem todos os usuarios
def lista_usuarios():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, email, nome FROM Usuario")

        usuarios = []
        for row in cursor.fetchall():
            usuario = {
                "id": row[0],
                "email": row[1],
                "nome": row[2],
            }
            usuarios.append(usuario)
        return usuarios

    except cx_Oracle.DatabaseError as e:
        print(f"Erro ao conectar-se ao banco: {e}")
        return []

    finally:
        cursor.close()
        connection.close()


# aqui não houve muitas alterações, função pra verificar os custos, só fez algumas alterações em base em algumas coisas aleatórias que eu pesquisei.
def verificar_custos():
    custos_servicos = {
        "Troca de óleo": 200,
        "Troca de pneu": 300,
        "Manutenção preventiva": 500,
    }

    # Exibe a lista de serviços
    print("\nEscolha o serviço para verificar o custo:")
    for i, servico in enumerate(custos_servicos.keys(), start=1):
        print(f"{i}. {servico}")

    try:
        # Recebe a escolha do usuário
        escolha = int(input("Escolha um serviço (1, 2 ou 3): "))

        # Verifica se a escolha é válida
        if 1 <= escolha <= len(custos_servicos):
            servico_escolhido = list(custos_servicos.keys())[escolha - 1]
            custo = custos_servicos[servico_escolhido]
            print(f"\nO custo do serviço '{servico_escolhido}' é R${custo}.\n")
        else:
            print("Escolha um serviço válido.")

    except ValueError:
        print("Entrada inválida. Por favor, escolha um número.")

    print("Voltando ao menu.\n")


# Função para exibir o menu principal
def menu_principal():
    print("Escolha uma opção: ")
    print("1 - Registro")
    print("2 - Login")
    print("3 - Sair")


def menu_logado():
    print("Escolha uma opção: ")
    print("1 - Atualizar Credenciais")
    print("2 - Excluir Conta")
    print("3 - Verificar Custos")
    print("4 - Lista de Usuários")
    print("5 - Sair")


# Função principal do menu
def executar_menu():
    global logado

    while True:
        if not logado:
            menu_principal()
            opcao = input("Escolha a opção: ")

            if opcao == "1":
                cadastro()
            elif opcao == "2":
                if login():
                    continue
            elif opcao == "3":
                print("Saindo do programa")
                break
            else:
                print("Opção não é válida. Escolha uma opção válida.")
        else:
            menu_logado()
            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                atualizar_credenciais()
            elif opcao == "2":
                excluir_usuario()
            elif opcao == "3":
                verificar_custos()
            elif opcao == "4":
                usuarios = lista_usuarios()
                print("\nLista de Usuários:")
                for usuario in usuarios:
                    print(
                        f"ID: {usuario['id']}, Email: {usuario['email']}, Nome: {usuario['nome']}"
                    )
            elif opcao == "5":
                print("Saindo do programa")
                break
            else:
                print("Opção inválida. Por favor, escolha uma opção válida.")


if __name__ == "__main__":
    try:
        executar_menu()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        print("Programa encerrado.")
