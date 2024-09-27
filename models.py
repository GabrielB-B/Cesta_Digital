# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
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

    # Relacionamento com os membros da família
    membros = db.relationship('Membro', backref='familia', lazy=True, cascade="all, delete-orphan")

    # Verifica se a família está em situação de pobreza
    def is_pobreza(self):
        salario_minimo = 1412.00
        renda_total = sum(membro.renda for membro in self.membros)
        num_membros = len(self.membros)
        if num_membros > 0:
            renda_per_capita = renda_total / num_membros
            return renda_per_capita < (salario_minimo / 2)
        return False

class Membro(db.Model):
    __tablename__ = 'membro'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    parentesco = db.Column(db.String(50), nullable=False)  # pai, mãe, filho, etc.
    renda = db.Column(db.Float, nullable=False)
    familia_id = db.Column(db.Integer, db.ForeignKey('familia.id'), nullable=False)
