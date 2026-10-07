from flask import Flask, render_template, methods
app = Flask(__name__)

@app.route('/')
def pagina_inicial():
   
    return render_template('index.html')
 

## ultima coisa do arquivo
if __name__ == '__main__':
    app.run(debug=True)