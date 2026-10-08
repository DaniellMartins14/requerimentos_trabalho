import re
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave-desenvolvimento-cadastro-municipes"
## usando o secret key, por que se não, o flash não funciona
##o flash será usado para exibir erro, mensagem etc

municipes = [] ## armazenar dados, sem banco de dados os dados reiniciam ao reiniciar o flask
processos = []
inscricoes = []

## para conferir o formato do e-mail 
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TAMANHO_MINIMO_SENHA = 6


def email_valido(email):
    """Confere o formato básico do e-mail: texto@dominio.ext, sem espaços."""
    return bool(EMAIL_REGEX.match(email or ""))


def buscar_municipe_por_email(email):
    """Procura o cadastro pelo e-mail, ignorando maiúsculas/minúsculas e espaços."""
    email_normalizado = (email or "").strip().casefold()
    for municipe in municipes:
        if municipe["email"].strip().casefold() == email_normalizado:
            return municipe
    return None


def destino_seguro(destino):
    """Só aceita voltar para caminhos internos do próprio site (evita redirecionar para site de fora)."""
    if destino and destino.startswith("/") and not destino.startswith(("//", "/\\")):
        return destino
    return None


## decorator: colocar abaixo do @app.route para exigir login na página
def login_required(rota):
    @wraps(rota)
    def verificar_login(*args, **kwargs):
        if "municipe_id" not in session:
            flash("Faça login para acessar esta página.", "warning")
            return redirect(url_for("login", next=request.path))
        return rota(*args, **kwargs)
    return verificar_login


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
@login_required
def index():
    return render_template("index.html", total_municipes=len(municipes))


## tela de login: confere e-mail e senha do cadastro de munícipe
@app.route("/login", methods=["GET", "POST"])
def login():
    if "municipe_id" in session: ## já está logada, não precisa ver o login de novo
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "") ## senha não leva strip()
        proximo = request.form.get("next", "")
        erros = []

        if not email:
            erros.append("Informe o e-mail.")
        elif not email_valido(email):
            erros.append("E-mail inválido. Use o formato nome@email.com.")

        if not senha:
            erros.append("Informe a senha.")

        ## só consulta o cadastro se os campos estiverem preenchidos corretamente
        if not erros:
            municipe = buscar_municipe_por_email(email)
            ## mesma mensagem para e-mail inexistente e senha errada: não revela quais e-mails existem
            if not municipe or not check_password_hash(municipe["senha_hash"], senha):
                erros.append("E-mail ou senha incorretos.")

        if erros:
            for erro in erros:
                flash(erro, "danger")
            return render_template("login.html", dados={"email": email}, proximo=proximo)

        session.clear() ## começa uma sessão limpa a cada login
        session["municipe_id"] = municipe["id"]
        session["municipe_nome"] = municipe["nome"]
        flash(f"Bem-vindo(a), {municipe['nome']}!", "success")
        return redirect(destino_seguro(proximo) or url_for("index"))

    return render_template("login.html", dados={}, proximo=request.args.get("next", ""))


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))


## agora aqui vamos fazer o cadastro dos munícipes
## o cadastro fica público de propósito: é por ele que a pessoa cria o acesso para conseguir fazer login
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
        senha = request.form.get("senha", "") ## senha não leva strip(): espaços podem fazer parte dela
        confirmar_senha = request.form.get("confirmar_senha", "")

        erros = [] ## armazena o valor erro
        if not nome: erros.append("Informe o nome.")
        if not telefone: erros.append("Informe o telefone.")
        if not endereco: erros.append("Informe o endereço.")
        if not cep: erros.append("Informe o CEP.")
        if not cidade: erros.append("Informe a cidade.")
        if not estado: erros.append("Informe o estado.")
        if not email: erros.append("Informe o e-mail.")
        elif not email_valido(email): erros.append("E-mail inválido. Use o formato nome@email.com.")
        elif buscar_municipe_por_email(email): erros.append("Já existe um cadastro com este e-mail.") ## o e-mail é o login, então não pode repetir
        if not cpf: erros.append("Informe o CPF.")
        elif not validar_cpf(cpf): erros.append("CPF inválido. Confira os números digitados.")
        if not data_nascimento: erros.append("Informe a data de nascimento.")
        if nivel_acesso not in ["municipe", "servidor", "administrador"]:
            erros.append("Selecione um nível de acesso válido.")

        if not senha: erros.append("Informe a senha.")
        elif len(senha) < TAMANHO_MINIMO_SENHA: erros.append(f"A senha deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.")
        elif senha != confirmar_senha: erros.append("As senhas não conferem.")

        if nivel_acesso != "municipe":
            preferencial = "Não"
            cadastro_cras = "Não"

        if erros:
            for erro in erros:
                flash(erro, "danger")
            dados = request.form.to_dict()
            dados.pop("senha", None) ## nunca devolve a senha para a tela
            dados.pop("confirmar_senha", None)
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
            "senha_hash": generate_password_hash(senha), ## guarda só o hash, nunca a senha em texto
        })
        flash("Munícipe cadastrado com sucesso!", "success")
        if "municipe_id" in session: ## quem já está logada volta para a listagem
            return redirect(url_for("listagem"))
        flash("Agora faça login para acessar o sistema.", "info")
        return redirect(url_for("login"))

    return render_template("cadastro.html", dados={}, nivel_acesso="")




@app.route("/listagem") ## define a rota de listagem, e manda os munícipes
@login_required
def listagem():
    return render_template("listagem.html", municipes=municipes)



## formulario simples
@app.route("/cadastro_processo", methods=["GET", "POST"])
@login_required
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
@login_required
def listagem_processo():
    return render_template(
        "listagem_processo.html",
        processos=processos
    )



## formulario de inscrição municipal (dados simulados - documentos requeridos variam de acordo com knae numa situação real)
@app.route("/cadastro_inscricao", methods=["GET", "POST"])
@login_required
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
@login_required
def listagem_inscricao():
    return render_template(
        "listagem_inscricao.html",
        inscricoes=inscricoes
    )

## ultimo ponto do arquivo
if __name__ == "__main__":
    app.run(debug=True)
