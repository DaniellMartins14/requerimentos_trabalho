from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "chave-desenvolvimento-cadastro-municipes"
## usando o secret key, por que se não, o flash não funciona
##o flash será usado para exibir erro, mensagem etc

municipes = [] ## armazenar dados, sem banco de dados os dados reiniciam ao reiniciar o flask
processos = []
inscricoes = []

## verifica se o usuario existe - para não ter um processo do "scoobdoo 123"
def municipe_existe(nome):
    """Verifica se o nome informado corresponde a um munícipe já cadastrado."""
    nome_normalizado = " ".join((nome or "").split()).casefold()

    return any(
        " ".join(municipe["nome"].split()).casefold() == nome_normalizado
        for municipe in municipes
    )


## validação de cpf -- peguei o código no github. Daniel.
## funciona por meio do calculo dos número e verifica resultados esperados
def validar_cpf(cpf):
    """Valida CPF usando os dois dígitos verificadores."""
    numeros = "".join(filter(str.isdigit, cpf or ""))
    if len(numeros) != 11 or numeros == numeros[0] * 11:
        return False

    soma = sum(int(numeros[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    if int(numeros[9]) != digito1:
        return False

    soma = sum(int(numeros[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    return int(numeros[10]) == digito2

## formata o cpf no padrão 000.000.000-00 
def formatar_cpf(cpf):
    numeros = "".join(filter(str.isdigit, cpf or ""))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return cpf


## define index - automaticamente GET
@app.route("/")
def index():
    return render_template("index.html", total_municipes=len(municipes))

## agora aqui vamos fazer o cadastro dos munícipes
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro(): ## se preencher o formulario, pega os dados pelo 'post'
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        endereco = request.form.get("endereco", "").strip()
        cep = request.form.get("cep", "").strip()
        numero = request.form.get("numero", "").strip() or "S/N"
        cidade = request.form.get("cidade", "").strip()
        estado = request.form.get("estado", "").strip()
        complemento = request.form.get("complemento", "").strip()
        email = request.form.get("email", "").strip()
        cpf = request.form.get("cpf", "").strip()
        data_nascimento = request.form.get("data_nascimento", "").strip()
        nivel_acesso = request.form.get("nivel_acesso", "").strip()
        preferencial = request.form.get("preferencial", "Não")
        cadastro_cras = request.form.get("cadastro_cras", "Não")

        erros = [] ## armazena o valor erro
        if not nome: erros.append("Informe o nome.")
        if not telefone: erros.append("Informe o telefone.")
        if not endereco: erros.append("Informe o endereço.")
        if not cep: erros.append("Informe o CEP.")
        if not cidade: erros.append("Informe a cidade.")
        if not estado: erros.append("Informe o estado.")
        if not email: erros.append("Informe o e-mail.")
        if not cpf: erros.append("Informe o CPF.")
        elif not validar_cpf(cpf): erros.append("CPF inválido. Confira os números digitados.")
        if not data_nascimento: erros.append("Informe a data de nascimento.")
        if nivel_acesso not in ["municipe", "servidor", "administrador"]:
            erros.append("Selecione um nível de acesso válido.")

        if nivel_acesso != "municipe":
            preferencial = "Não"
            cadastro_cras = "Não"

        if erros:
            for erro in erros:
                flash(erro, "danger")
            dados = request.form.to_dict()
            return render_template("cadastro.html", dados=dados, nivel_acesso=nivel_acesso)

        municipes.append({
            "id": len(municipes) + 1,
            "nome": nome,
            "telefone": telefone,
            "endereco": endereco,
            "cep": cep,
            "numero": numero,
            "cidade": cidade,
            "estado": estado,
            "complemento": complemento,
            "email": email,
            "cpf": formatar_cpf(cpf),
            "data_nascimento": data_nascimento,
            "nivel_acesso": nivel_acesso,
            "preferencial": preferencial,
            "cadastro_cras": cadastro_cras,
        })
        flash("Munícipe cadastrado com sucesso!", "success")
        return redirect(url_for("listagem"))

    return render_template("cadastro.html", dados={}, nivel_acesso="")




@app.route("/listagem") ## define a rota de listagem, e manda os munícipes 
def listagem():
    return render_template("listagem.html", municipes=municipes)



## formulario simples
@app.route("/cadastro_processo", methods=["GET", "POST"])
def cadastro_processo():
    if request.method == "POST":
        municipe = request.form.get("municipe", "").strip()
        pedido = request.form.get("pedido", "").strip()
        erros = []

        if not municipe:
            erros.append("Informe o nome do munícipe.")
        elif not municipe_existe(municipe):
            erros.append("Munícipe não encontrado. Crie um cadastro antes.")

        if not pedido:
            erros.append("Informe o pedido.")

        if erros:
            for erro in erros:
                flash(erro, "danger")

            return render_template(
                "cadastro_processo.html",
                dados=request.form.to_dict()
            )

        processos.append({
            "id": len(processos) + 1,
            "municipe": municipe,
            "pedido": pedido
        })

        flash("Processo simples cadastrado com sucesso!", "success")

        return redirect(url_for("listagem_processo"))

    return render_template("cadastro_processo.html", dados={})


## lista os processos
@app.route("/listagem_processo")
def listagem_processo():
    return render_template(
        "listagem_processo.html",
        processos=processos
    )



## formulario de inscrição municipal (dados simulados - documentos requeridos variam de acordo com knae numa situação real)
@app.route("/cadastro_inscricao", methods=["GET", "POST"])
def cadastro_inscricao():
    if request.method == "POST":
        municipe = request.form.get("municipe", "").strip()
        cnpj = request.form.get("cnpj", "").strip()
        codigo_atividade = request.form.get("codigo_atividade", "").strip()
        erros = []

        if not municipe:
            erros.append("Informe o nome do munícipe.")
        elif not municipe_existe(municipe):
            erros.append("Munícipe não encontrado. Crie um cadastro antes.")

        if not cnpj:
            erros.append("Informe o CNPJ da empresa.")

        if not codigo_atividade:
            erros.append("Informe o código de atividade.")

        if erros:
            for erro in erros:
                flash(erro, "danger")

            return render_template(
                "cadastro_inscricao.html",
                dados=request.form.to_dict()
            )

        inscricoes.append({
            "id": len(inscricoes) + 1,
            "municipe": municipe,
            "cnpj": cnpj,
            "codigo_atividade": codigo_atividade
        })

        flash("Inscrição municipal cadastrada com sucesso!", "success")

        return redirect(url_for("listagem_inscricao"))

    return render_template("cadastro_inscricao.html", dados={})

## inscrições

@app.route("/listagem_inscricao")
def listagem_inscricao():
    return render_template(
        "listagem_inscricao.html",
        inscricoes=inscricoes
    )

## ultimo ponto do arquivo
if __name__ == "__main__":
    app.run(debug=True)
