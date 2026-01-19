from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reciclaje.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave_secreta'

db = SQLAlchemy(app)


preguntas = [
    {
        'pregunta': '¿Cuál es el objetivo principal del reciclaje PET?',
        'respuestas': [
            'Tirar la basura más rápido',
            'Reducir, reutilizar y reciclar los residuos',
            'Usar más plásticos',
            'Quemar la basura'
        ],
        'respuesta_correcta': 'Reducir, reutilizar y reciclar los residuos'
    },
    {
        'pregunta': '¿En qué contenedor se debe depositar el plástico?',
        'respuestas': ['Rojo', 'Verde', 'Azul', 'Amarillo'],
        'respuesta_correcta': 'Amarillo'
    },
    {
        'pregunta': '¿Qué acción ayuda más al reciclaje?',
        'respuestas': [
            'Mezclar toda la basura',
            'Tirar residuos en la calle',
            'Separar los residuos por tipo',
            'Usar más bolsas de plástico'
        ],
        'respuesta_correcta': 'Separar los residuos por tipo'
    },
    {
        'pregunta': '¿Quiénes deben participar en el PET de reciclaje?',
        'respuestas': [
            'Solo los alumnos',
            'Solo los maestros',
            'Toda la comunidad escolar',
            'Solo los directivos'
        ],
        'respuesta_correcta': 'Toda la comunidad escolar'
    },
    {
        'pregunta': '¿Qué material se recicla en el PET?',
        'respuestas': ['Vidrio', 'Papel', 'Plástico', 'Metal'],
        'respuesta_correcta': 'Plástico'
    }
]

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/encuesta', methods=['GET', 'POST'])
def encuesta():
    if request.method == 'POST':
        puntaje = 0
        for i, pregunta in enumerate(preguntas):
            respuesta = request.form.get(f'pregunta{i}')
            if respuesta == pregunta['respuesta_correcta']:
                puntaje += 20
        return render_template('resultado.html', puntaje=puntaje)

    return render_template('encuesta.html', preguntas=preguntas)


@app.route("/beneficios")
def beneficios():
    return render_template("beneficios.html")

@app.route("/como_reciclar")
def como_reciclar():
    return render_template("como_reciclar.html")

@app.route("/concepto_del_pet")
def concepto_del_pet():
    return render_template("concepto_del_pet.html")

@app.route("/importancia")
def importancia():
    return render_template("importancia.html")

@app.route("/objetivos")
def objetivos():
    return render_template("objetivos.html")

@app.route("/comentario", methods=["GET", "POST"])
@login_required
def comentario():
    if request.method == "POST":
        texto = request.form["texto"]

        nuevo = Comentario(texto=texto, usuario_id=current_user.id)
        db.session.add(nuevo)
        db.session.commit()

        return redirect(url_for("comentario"))

    comentarios = Comentario.query.all()
    return render_template("comentario.html", comentarios=comentarios)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('comentarios', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = None

    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        existente = Usuario.query.filter_by(usuario=usuario).first()
        if existente:
            mensaje = "El usuario ya existe, intenta otro."
            return render_template("registro.html", mensaje=mensaje)

        try:
            nuevo = Usuario(usuario=usuario)
            nuevo.set_password(password)
            db.session.add(nuevo)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            mensaje = "Error al registrar al usuario."
            return render_template("registro.html", mensaje=mensaje)

    return render_template("registro.html", mensaje=mensaje)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        user = Usuario.query.filter_by(usuario=usuario).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))  
        else:
            return render_template('login.html', mensaje="Usuario o contraseña incorrectos")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# CREAR BD
with app.app_context():
    db.create_all()





