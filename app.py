# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Familia, Membro  # Importar do models.py
from config import Config  # Importar a configuração

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

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
        auxilio_governo = bool(request.form.get('auxilio_governo'))
        estado_civil = request.form['estado_civil']
        # renda_familiar será recalculada com base na renda dos membros

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
            auxilio_governo=auxilio_governo,
            estado_civil=estado_civil,
            renda_familiar=0.0
        )
        db.session.add(nova_familia)
        db.session.commit()

        # Adicionar membros da família
        nomes = request.form.getlist('nome_membro')
        parentescos = request.form.getlist('parentesco')
        rendas = request.form.getlist('renda')

        for nome_membro, parentesco, renda in zip(nomes, parentescos, rendas):
            if nome_membro and parentesco and renda:
                novo_membro = Membro(
                    nome=nome_membro,
                    parentesco=parentesco,
                    renda=float(renda),
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
        familia.auxilio_governo = bool(request.form.get('auxilio_governo'))
        familia.estado_civil = request.form['estado_civil']

        # Atualizar a renda_familiar com base na soma das rendas dos membros
        familia.renda_familiar = sum(membro.renda for membro in familia.membros)

        db.session.commit()
        flash('Família atualizada com sucesso!')
        return redirect(url_for('index'))
    return render_template('editar_familia.html', familia=familia)

# Rota para excluir membro
@app.route('/excluir_membro/<int:membro_id>', methods=['POST'])
def excluir_membro(membro_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    membro = Membro.query.get_or_404(membro_id)
    familia_id = membro.familia_id
    db.session.delete(membro)
    db.session.commit()

    # Atualizar a renda_familiar com base na soma das rendas dos membros
    familia = Familia.query.get(familia_id)
    familia.renda_familiar = sum(m.renda for m in familia.membros)
    db.session.commit()

    flash('Membro excluído com sucesso!')
    return redirect(url_for('editar_familia', familia_id=familia_id))

# Rota para editar membro
@app.route('/editar_membro/<int:membro_id>', methods=['GET', 'POST'])
def editar_membro(membro_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    membro = Membro.query.get_or_404(membro_id)
    if request.method == 'POST':
        membro.nome = request.form['nome_membro']
        membro.parentesco = request.form['parentesco']
        membro.renda = float(request.form['renda'])

        db.session.commit()

        # Atualizar a renda_familiar com base na soma das rendas dos membros
        familia = membro.familia
        familia.renda_familiar = sum(m.renda for m in familia.membros)
        db.session.commit()

        flash('Membro atualizado com sucesso!')
        return redirect(url_for('editar_familia', familia_id=membro.familia_id))
    return render_template('editar_membro.html', membro=membro)

if __name__ == '__main__':
    app.run(debug=True)
