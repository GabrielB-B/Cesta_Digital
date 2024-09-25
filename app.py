from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configuração de conexão com MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/cadastro_familias'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelos do banco de dados
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Familia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    referencia = db.Column(db.String(255), nullable=True)
    internet = db.Column(db.Boolean, default=False)
    qtd_celulares = db.Column(db.Integer, default=0)
    auxilio_governo = db.Column(db.Boolean, default=False)
    estado_civil = db.Column(db.String(20), nullable=False)
    renda_familiar = db.Column(db.Float, nullable=False)

    # Verifica se a família está em situação de pobreza
    def is_pobreza(self):
        salario_minimo = 1412.00
        return self.renda_familiar < salario_minimo

# Rotas para o login e cadastro
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(nome=nome).first()
        if usuario and usuario.check_password(senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha incorretos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        usuario = Usuario(nome=nome)
        usuario.set_password(senha)
        db.session.add(usuario)
        db.session.commit()
        flash('Usuário registrado com sucesso.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Rota principal
@app.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    familias = Familia.query.all()
    return render_template('index.html', familias=familias)

# Rota para adicionar famílias
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_familia():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        cidade = request.form['cidade']
        estado = request.form['estado']
        cep = request.form['cep']
        telefone = request.form['telefone']
        referencia = request.form['referencia']
        internet = bool(request.form.get('internet'))
        qtd_celulares = request.form['qtd_celulares']
        auxilio_governo = bool(request.form.get('auxilio_governo'))
        estado_civil = request.form['estado_civil']
        renda_familiar = float(request.form['renda_familiar'])

        nova_familia = Familia(
            nome=nome, endereco=endereco, cidade=cidade, estado=estado, cep=cep,
            telefone=telefone, referencia=referencia, internet=internet,
            qtd_celulares=qtd_celulares, auxilio_governo=auxilio_governo,
            estado_civil=estado_civil, renda_familiar=renda_familiar
        )
        db.session.add(nova_familia)
        db.session.commit()
        flash('Família adicionada com sucesso!')
        return redirect(url_for('index'))

    return render_template('adicionar.html')

# Rota para ver o status de pobreza
@app.route('/familias')
def listar_familias():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    familias = Familia.query.all()
    return render_template('listar_familias.html', familias=familias)

if __name__ == '__main__':
    app.run(debug=True)
