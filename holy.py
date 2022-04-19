from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
from jogos import Jogo
from dao import UsuarioDao
from flask_mysqldb import MySQL
from dao import JogoDao
import os


app = Flask(__name__)
app.secret_key = 'o mais quente de todos os tempos'

app.config['MYSQL_HOST'] = "0.0.0.0"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Root@2001'
app.config['MYSQL_DB'] = "holy"
app.config['MYSQL_PORT'] = 3306
app.config['UPLOAD_PATH'] = os.path.dirname(os.path.abspath(__file__)) + '/uploads'

db = MySQL(app)
jogo_dao = JogoDao(db)
user_dao = UsuarioDao(db)


@app.route('/login')
def login():
    next = request.args.get('next')
    if next != None:
        return render_template('login.html', next=next)
    return render_template('login.html', next=url_for('index'))


@app.route('/logout')
def logout():
    session['acesso'] = None
    flash('Usuário deslogado!')
    return redirect(url_for('index'))


@app.route('/auth', methods=['POST', ])
def auth():
    acess = user_dao.buscar_por_id(request.form['usuario'])
    if acess:
        if acess.senha == request.form['senha']:
            session['acesso'] = acess.id
            flash('Bem vindo de volta ' + session['acesso'])
            next_page = request.form['next']
            return redirect(next_page)

    else:
        flash('Usuário ou senha inválidos.')
        return redirect(url_for('login'))


@app.route('/criar', methods=['POST', ])
def criar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console, id=None)
    save = jogo_dao.salvar(jogo)

    path = app.config['UPLOAD_PATH']
    arquivo = request.files['arch']
    arquivo.save(f'/{path}/capa{save.id}.jpg')
    return redirect(url_for('index'))


@app.route('/add')
def add():
    if 'acesso' not in session or session['acesso'] == None:
        flash('Por gentileza, efetue o login para cadastrar um novo jogo.')
        return redirect(url_for('login', next=url_for('add')))
    else:
        return render_template('add.html', titulo='Adicionar Jogo')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'acesso' not in session or session['acesso'] == None:
        flash('Por gentileza, efetue o login para editar um jogo.')
        return redirect(url_for('login'))
    jogo = jogo_dao.busca_por_id(id)
    return render_template('edit.html', titulo='Alterar Jogo', jogo=jogo, capa=f'capa{jogo.id}.jpg')


@app.route('/alter', methods=['POST', ])
def alter():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console, id=request.form['id'])
    jogo_dao.salvar(jogo)
    return redirect(url_for('index'))


@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)


@app.route('/delete/<int:id>')
def delete(id):
    if 'acesso' not in session or session['acesso'] == None:
        flash('Por gentileza, efetue o login para apagar um jogo.')
        return redirect(url_for('login'))
    jogo_dao.deletar(id)
    flash("Jogo apagado!")
    return redirect(url_for('index'))


@app.route('/')
def index():
    lista = jogo_dao.listar()
    return render_template('lista.html', titulo='HolyGames', jogos=lista)


app.run(debug=True)