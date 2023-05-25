import csv
import sqlite3

def read_csv(name):
    with open(name, newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=';')
        return list(reader)


def crete_data_base():
    # Abrir uma conexão com o banco de dados (ou criar um novo)
    conexao = sqlite3.connect('dados_notas.db')

    # Criar tabela "notas" se não existir
    conexao.execute('''CREATE TABLE IF NOT EXISTS notas (
                        numero TEXT PRIMARY KEY,
                        fornecedor TEXT,
                        sede TEXT,
                        emissao TEXT,
                        vencimento TEXT,
                        especie TEXT
                    )''')

    # Criar tabela "products" se não existir
    conexao.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY,
                        numero TEXT,
                        produto TEXT,
                        valor TEXT,
                        contrato TEXT,
                        cc TEXT,
                        movimento TEXT,
                        FOREIGN KEY (numero) REFERENCES notas (numero)
                    )''')

    # Ler o arquivo CSV
    conexao.execute("DELETE FROM notas")
    conexao.execute("DELETE FROM products")
    dados_csv = read_csv('test.csv')

    # Iterar sobre os dados do arquivo CSV
    for row in dados_csv:
        numero = row['numero'].replace("-", "")
        fornecedor = row['fornecedor'].replace(".", "").replace( "-", "").replace("/", "")
        sede = row['sede']
        emissao = row['emissão']
        especie = row["especie"]
        valor = row['valor'].strip().replace("R$","").replace(".","").replace(",", ".")
        contrato = row['contrato']
        cc = row['cc']
        produto = row["produto"]
        movimento = row["movimento"]


        # Verificar se o número da nota já existe na tabela "notas"
        cursor = conexao.execute("SELECT numero FROM notas WHERE numero = ?", (numero,))
        nota_existente = cursor.fetchone()

        if nota_existente is None:
            # Inserir os dados da linha na tabela "notas"
            conexao.execute("INSERT INTO notas (numero, fornecedor, sede, emissao, especie) VALUES (?, ?, ?, ?, ?)",
                            (numero, fornecedor, sede, emissao, especie))

        # Inserir os dados da linha na tabela "products"
        conexao.execute("INSERT INTO products (numero, produto, valor, contrato, cc, movimento) VALUES (?, ?, ?, ?, ?, ?)",
                        (numero, produto, valor, contrato, cc, movimento))

    # Confirmar as alterações e fechar a conexão com o banco de dados
    conexao.commit()
    conexao.close()