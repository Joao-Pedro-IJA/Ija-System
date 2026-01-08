from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

# -------------------------------------------------------------
# USUÁRIO
# -------------------------------------------------------------
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)

    nome_uvis = db.Column(db.String(100), nullable=False, index=True)
    regiao = db.Column(db.String(50), index=True)
    codigo_setor = db.Column(db.String(10))

    login = db.Column(db.String(50), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(200), nullable=False)

    # tipos esperados: "admin", "uvis", "operario", "visualizador", "piloto"
    tipo_usuario = db.Column(db.String(20), default='uvis', index=True)

    # ✅ NOVO: vínculo opcional com a tabela Pilotos (para usuários do tipo "piloto")
    piloto_id = db.Column(
        db.Integer,
        db.ForeignKey("pilotos.id"),
        nullable=True,
        index=True
    )
    piloto = db.relationship("Pilotos", lazy="joined")

    solicitacoes = db.relationship(
        "Solicitacao",
        back_populates="usuario",
        lazy="select"
    )

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


# -------------------------------------------------------------
# SOLICITAÇÃO DE VOO
# -------------------------------------------------------------
class Solicitacao(db.Model):
    __tablename__ = 'solicitacoes'

    id = db.Column(db.Integer, primary_key=True)

    # ----------------------
    # Dados Básicos e Data
    # ----------------------
    data_agendamento = db.Column(db.Date, nullable=False, index=True)
    hora_agendamento = db.Column(db.Time, nullable=False)

    foco = db.Column(db.String(50), nullable=False, index=True)

    # ----------------------
    # Detalhes Operacionais
    # ----------------------
    tipo_visita = db.Column(db.String(50), index=True)
    altura_voo = db.Column(db.String(20), index=True)

    criadouro = db.Column(db.Boolean, default=False)
    apoio_cet = db.Column(db.Boolean, default=False)

    observacao = db.Column(db.Text)

    # ----------------------
    # Endereço
    # ----------------------
    cep = db.Column(db.String(9), nullable=False)
    logradouro = db.Column(db.String(150), nullable=False)
    bairro = db.Column(db.String(100), nullable=False, index=True)
    cidade = db.Column(db.String(100), nullable=False, index=True)
    uf = db.Column(db.String(2), nullable=False, index=True)

    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))

    # Geolocalização
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))

    # Anexos
    anexo_path = db.Column(db.String(255))
    anexo_nome = db.Column(db.String(255))

    # ----------------------
    # Controle Admin
    # ----------------------
    protocolo = db.Column(db.String(50), index=True)
    justificativa = db.Column(db.String(255))

    data_criacao = db.Column(
        db.DateTime,
        default=datetime.now,
        index=True
    )

    status = db.Column(
        db.String(30),
        default="EM ANÁLISE",
        index=True
    )

    # quem criou (usuário logado)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )
    usuario = db.relationship(
        "Usuario",
        back_populates="solicitacoes"
    )

    # ✅ NOVO: piloto responsável pela solicitação (para dashboard do piloto)
    piloto_id = db.Column(
        db.Integer,
        db.ForeignKey("pilotos.id"),
        nullable=True,
        index=True
    )
    piloto = db.relationship(
        "Pilotos",
        back_populates="solicitacoes"
    )

    # 🔥 ÍNDICES COMPOSTOS (MUITO IMPORTANTES PARA RELATÓRIOS)
    __table_args__ = (
        db.Index(
            "ix_solicitacao_data_status",
            "data_criacao",
            "status"
        ),
        db.Index(
            "ix_solicitacao_usuario_data",
            "usuario_id",
            "data_criacao"
        ),
        # ✅ NOVO: otimiza listagem do dashboard do piloto
        db.Index(
            "ix_solicitacao_piloto_data",
            "piloto_id",
            "data_criacao"
        ),
    )


# -------------------------------------------------------------
# NOTIFICAÇÕES
# -------------------------------------------------------------
class Notificacao(db.Model):
    __tablename__ = "notificacoes"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )

    titulo = db.Column(db.String(140), nullable=False)
    mensagem = db.Column(db.Text)
    link = db.Column(db.String(255))

    criada_em = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False,
        index=True
    )

    lida_em = db.Column(db.DateTime, index=True)
    apagada_em = db.Column(db.DateTime, index=True)


# -------------------------------------------------------------
# CLIENTES
# -------------------------------------------------------------
class Clientes(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True, index=True)

    nome_cliente = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    documento = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    contato = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100), index=True)
    endereco = db.Column(db.String(255))


# -------------------------------------------------------------
# PILOTOS
# -------------------------------------------------------------
class Pilotos(db.Model):
    __tablename__ = "pilotos"

    id = db.Column(db.Integer, primary_key=True, index=True)

    nome_piloto = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )
    regiao = db.Column(db.String(20))
    telefone = db.Column(db.String(20))

    # ✅ NOVO: relacionamento reverso para ver solicitações atribuídas ao piloto
    solicitacoes = db.relationship(
        "Solicitacao",
        back_populates="piloto",
        lazy="select"
    )
