from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.secret_key = 'bulletin_senegal_2026_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bulletin.db'
db = SQLAlchemy(app)

# --- BASE DE DONNEES ---
class Eleve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(50), nullable=False)

class Bulletin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleve.id'), nullable=False)
    ia = db.Column(db.String(100)); ief = db.Column(db.String(100))
    etablissement = db.Column(db.String(200)); annee = db.Column(db.String(20))
    periode = db.Column(db.String(50)); classe = db.Column(db.String(50))
    moyenne = db.Column(db.Float); appreciation = db.Column(db.Text)
    data_json = db.Column(db.Text)

with app.app_context():
    db.create_all()

IA_LIST = ["IA DAKAR", "IA THIES", "IA KAOLACK", "IA SAINT-LOUIS", "IA ZIGUINCHOR", "IA TAMBACOUNDA", "IA DIOURBEL", "IA FATICK", "IA KOLDA", "IA MATAM", "IA LOUGA", "IA KEDOUGOU", "IA SEDHIOU"]
IEF_LIST = ["IEF DAKAR PLATEAU", "IEF DAKAR ALMADIES", "IEF MBOUR", "IEF THIES", "IEF KAOLACK", "IEF SAINT-LOUIS", "IEF ZIGUINCHOR", "IEF TAMBACOUNDA", "IEF DIOURBEL", "IEF FATICK", "IEF KOLDA", "IEF MATAM", "IEF LOUGA", "IEF KEDOUGOU", "IEF SEDHIOU"]
PERIODES = ["1er Trimestre", "2e Trimestre", "3e Trimestre", "1er Semestre", "2e Semestre"]
CLASSES = ["6e", "5e", "4e", "3e", "2nd S", "2nd L", "2nd G", "2nd T", "1ère S", "1ère L", "1ère G", "1ère T", "Terminale S", "Terminale L", "Terminale G", "Terminale T"]

MATIERES = { "6e": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC"], "5e": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC"], "4e": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC", "ESPAGNOL", "ITALIEN", "ARABE", "ALLEMAND"], "3e": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC", "ESPAGNOL", "ITALIEN", "ARABE", "ALLEMAND"], "2nd S": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"], "2nd L": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"], "1ère S": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"], "1ère L": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "ECONOMIE", "PC", "SVT", "EPS"], "Terminale S": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"], "Terminale L": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "ECONOMIE", "PC", "SVT", "EPS"], "2nd G": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "INFORMATIQUE", "EPS"], "1ère G": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "INFORMATIQUE", "EPS"], "Terminale G": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "MARKETING", "INFORMATIQUE", "EPS"], "2nd T": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "EPS"], "1ère T": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "EPS"], "Terminale T": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "TECHNOLOGIE", "EPS"] }

def get_appreciation_matiere(moy):
    if moy >= 18: return "Félicitations"
    elif moy >= 16: return "Excellent"
    elif moy >= 14: return "Très Bien"
    elif moy >= 12: return "Bien"
    elif moy >= 10: return "Assez Bien"
    else: return "Passable"

def get_appreciation_generale(moy, classe):
    if "2nd" in classe or "1ère" in classe or "Terminale" in classe:
        if moy >= 16: return f"Félicitations du Conseil de Classe. Excellent travail. Mention Très Bien."
        elif moy >= 14: return f"Tableau d'Honneur. Très bon travail. Mention Bien."
        elif moy >= 12: return f"Encouragements. Bon travail. Mention Assez Bien."
        elif moy >= 10: return f"Passable. L'élève est admis en classe supérieure."
        else: return f"Insuffisant. L'élève est redoublant."
    else:
        if moy >= 16: return "Félicitations du Conseil de Classe. Excellent travail."
        elif moy >= 14: return "Tableau d'Honneur. Très bon travail."
        elif moy >= 12: return "Encouragements. Bon travail."
        elif moy >= 10: return "Passable. Des efforts sont nécessaires."
        else: return "Insuffisant. Doit redoubler d'efforts."

LOGIN_HTML = """<!DOCTYPE html><html><head><title>Connexion Bulletin SN</title><style>body{font-family:Arial;background:#00853F;display:flex;justify-content:center;align-items:center;height:100vh}.box{background:white;padding:30px;border-radius:10px;width:350px;box-shadow:0 0 20px #000}h2{text-align:center;color:#00853F}input,select{width:100%;padding:10px;margin:8px 0;border:1px solid #ccc;border-radius:5px}button{background:#00853F;color:white;padding:12px;border:none;width:100%;border-radius:5px;font-size:16px;cursor:pointer}</style></head><body><div class="box"><h2>🇸🇳 BULLETIN SENEGAL 🇸🇳</h2><form method="POST" action="/inscription"><label>Téléphone:</label><input name="telephone" placeholder="77 123 45 67" required><label>Prénom:</label><input name="prenom" required><label>Nom:</label><input name="nom" required><label>Classe:</label><select name="classe">{% for c in classes %}<option>{{c}}</option>{% endfor %}</select><button>ENTRER</button></form></div></body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html><html><head><title>Dashboard</title><style>body{font-family:Arial;background:#eee;padding:20px}.container{max-width:1000px;margin:auto;background:white;padding:20px;border-radius:10px}.btn{background:#E31B23;color:white;padding:8px 15px;text-decoration:none;border-radius:5px;float:right}.btn-green{background:#00853F}.bulletin-card{border:1px solid #ccc;padding:10px;margin:10px 0;border-radius:5px}</style></head><body><div class="container"><a href="/deconnexion" class="btn">Déconnexion</a><h2>Bonjour {{eleve.prenom}} {{eleve.nom}}</h2><p>Classe: <b>{{eleve.classe}}</b></p><hr><h3>Mes Bulletins</h3>{% for b in bulletins %}<div class="bulletin-card"><b>{{b.periode}} - {{b.annee}}</b> | Moyenne: <b>{{b.moyenne}}/20</b><br>{{b.appreciation}}</div>{% else %}<p>Aucun bulletin pour le moment.</p>{% endfor %}<hr><h3>Nouveau Bulletin</h3><form method="POST" action="/saisie">...LE FORMULAIRE DE SAISIE ICI...</form></div></body></html>"""

@app.route("/", methods=["GET"])
def accueil():
    if 'eleve_id' in session: return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_HTML, classes=CLASSES)

@app.route("/inscription", methods=["POST"])
def inscription():
    tel = request.form.get("telephone")
    eleve = Eleve.query.filter_by(telephone=tel).first()
    if not eleve:
        eleve = Eleve(telephone=tel, nom=request.form.get("nom"), prenom=request.form.get("prenom"), classe=request.form.get("classe"))
        db.session.add(eleve); db.session.commit()
    session['eleve_id'] = eleve.id
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    eleve = Eleve.query.get(session['eleve_id'])
    bulletins = Bulletin.query.filter_by(eleve_id=eleve.id).all()
    return render_template_string(DASHBOARD_HTML, eleve=eleve, bulletins=bulletins)

@app.route("/saisie", methods=["POST"])
def saisie():
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    eleve = Eleve.query.get(session['eleve_id'])
    # ICI ON CALCULE COMME TON ANCIEN CODE ET ON SAUVEGARDE
    # Pour simplifier je te mets la logique complète si tu veux
    return redirect(url_for('dashboard'))

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for('accueil'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
