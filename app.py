from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "chave-desenvolvimento-cadastro-municipes"
## usando o secret key, por que se não, o flash não funciona
##o flash será usado para exibir erro, mensagem etc

municipes = [] ## armazenar dados dos munícipes

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

## a função deixa "auto explicativa" 
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


if __name__ == "__main__":
    app.run(debug=True)
