from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Familia, Membro  # Importar do models.py
from config import Config  # Importar a configuração

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

# Define o valor da linha de pobreza
SALARIO_MINIMO = 1412.00  # Valor atual do salário mínimo

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
        qtd_celulares = int(request.form['qtd_celulares'])
        auxilio_governo = bool(request.form.get('auxilio_governo'))

        # Criação da nova família
        nova_familia = Familia(
            nome=nome,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            cep=cep,
            telefone=telefone,
            referencia=referencia,
            internet=internet,
            qtd_celulares=qtd_celulares,
            auxilio_governo=auxilio_governo,
            renda_familiar=0.0  # Será recalculada
        )
        db.session.add(nova_familia)
        db.session.commit()

        # Adicionar membros da família
        nomes = request.form.getlist('nome_membro')
        parentescos = request.form.getlist('parentesco')
        rendas = request.form.getlist('renda')
        estados_civis = request.form.getlist('estado_civil')
        idades = request.form.getlist('idade')
        sexos = request.form.getlist('sexo')
        carteiras = request.form.getlist('carteira_assinada')
        deficiencias = request.form.getlist('deficiencia_fisica')

        # Adiciona cada membro
        for i in range(len(nomes)):
            if nomes[i]:  # Verifica se o nome do membro não está vazio
                novo_membro = Membro(
                    nome=nomes[i],
                    parentesco=parentescos[i],
                    renda=float(rendas[i]) if i < len(rendas) and rendas[i] else 0.0,
                    estado_civil=estados_civis[i],
                    idade=int(idades[i]) if i < len(idades) and idades[i] else None,
                    sexo=sexos[i],
                    carteira_assinada=bool(carteiras[i]) if i < len(carteiras) and carteiras[i] else False,
                    deficiencia_fisica=bool(deficiencias[i]) if i < len(deficiencias) and deficiencias[i] else False,
                    familia_id=nova_familia.id
                )
                db.session.add(novo_membro)

        db.session.commit()

        # Atualizar a renda_familiar com base na soma das rendas dos membros
        nova_familia.renda_familiar = sum(membro.renda for membro in nova_familia.membros)
        db.session.commit()

        flash('Família e membros adicionados com sucesso!')
        return redirect(url_for('index'))

    return render_template('adicionar.html')

# Rota para ver o status de pobreza
@app.route('/familias')
def listar_familias():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    familias = Familia.query.all()
    return render_template('listar_familias.html', familias=familias)

# Rota para excluir família
@app.route('/excluir_familia/<int:familia_id>', methods=['POST'])
def excluir_familia(familia_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    familia = Familia.query.get_or_404(familia_id)
    db.session.delete(familia)
    db.session.commit()
    flash('Família excluída com sucesso!')
    return redirect(url_for('index'))

# Rota para editar família
@app.route('/editar_familia/<int:familia_id>', methods=['GET', 'POST'])
def editar_familia(familia_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    familia = Familia.query.get_or_404(familia_id)
    if request.method == 'POST':
        familia.nome = request.form['nome']
        familia.endereco = request.form['endereco']
        familia.cidade = request.form['cidade']
        familia.estado = request.form['estado']
        familia.cep = request.form['cep']
        familia.telefone = request.form['telefone']
        familia.referencia = request.form['referencia']
        familia.internet = bool(request.form.get('internet'))
        familia.qtd_celulares = int(request.form['qtd_celulares'])
        familia.auxilio_governo = bool(request.form.get('auxilio_governo'))

        # Atualiza a renda familiar
        familia.renda_familiar = sum(membro.renda for membro in familia.membros)
        db.session.commit()

        flash('Família editada com sucesso!')
        return redirect(url_for('index'))
    
    return render_template('editar_familia.html', familia=familia)

if __name__ == '__main__':
    app.run(debug=True)