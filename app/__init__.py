from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from whitenoise import WhiteNoise
from flask_talisman import Talisman

# Carrega as variáveis do arquivo .env (local) ou do painel do Render (produção)
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # --- CONFIGURAÇÕES DINÂMICAS ---
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/')
    
    # 1. Pega a Secret Key do ambiente ou usa uma padrão se não existir
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-padrao-desenvolvimento')

    # 2. Configuração Inteligente do Banco de Dados
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Correção: Render usa 'postgres://', mas SQLAlchemy exige 'postgresql://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Se estiver no seu PC e não houver DATABASE_URL, usa SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sgsv.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicialização das extensões
    db.init_app(app)
    migrate.init_app(app, db)

    if not app.debug:
        Talisman(app, content_security_policy=None)
    else:
        # No seu PC (modo debug), ele não força HTTPS para facilitar os testes
        Talisman(app, content_security_policy=None, force_https=False)

    # Configuração do LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'bp.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.query.get(int(user_id))

    # Context Processor para Dark Mode e Usuário Global
    @app.context_processor
    def inject_global_vars():
        tema = request.cookies.get('theme', 'light')
        from flask_login import current_user
        return dict(
            tema_escolhido=tema,
            current_user=current_user
        )

    # --- TRATAMENTO DE ERROS ---
    @app.errorhandler(404)
    def erro_404(e):
        return render_template("erro.html", codigo=404, titulo="Página não encontrada", 
                               mensagem="A página que você tentou acessar não existe."), 404

    @app.errorhandler(500)
    def erro_500(e):
        return render_template("erro.html", codigo=500, titulo="Erro interno do servidor", 
                               mensagem="Ocorreu um erro inesperado."), 500

    @app.errorhandler(Exception)
    def erro_generico(e):
        return render_template("erro.html", codigo="Erro", titulo="Ocorreu um erro", 
                               mensagem=str(e)), 500

    # Registrar rotas e modelos
    from app.routes import bp
    app.register_blueprint(bp)
    
    from app import models  

    return app