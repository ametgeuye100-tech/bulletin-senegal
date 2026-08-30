from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = 'bulletin_senegal_2026_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bulletin.db'
db = SQLAlchemy(app)

class Eleve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(50), nullable=False)
    date_naissance = db.Column(db.String(20), nullable=False)

class Bulletin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eleve_id = db.Column(db.Integer, db.ForeignKey('eleve.id'), nullable=False)
    ia = db.Column(db.String(100)); ief = db.Column(db.String(100))
    etablissement = db.Column(db.String(200)); annee = db.Column(db.String(20))
    periode = db.Column(db.String(50)); classe = db.Column(db.String(50))
    moyenne = db.Column(db.Float); appreciation = db.Column(db.Text)
    data_json = db.Column(db.Text)
    date_creation = db.Column(db.String(20))

with app.app_context():
    db.create_all()

IA_LIST = ["IA DAKAR", "IA THIES", "IA KAOLACK", "IA SAINT-LOUIS", "IA ZIGUINCHOR", "IA TAMBACOUNDA", "IA DIOURBEL", "IA FATICK", "IA KOLDA", "IA MATAM", "IA LOUGA", "IA KEDOUGOU", "IA SEDHIOU"]
IEF_LIST = ["IEF DAKAR PLATEAU", "IEF DAKAR ALMADIES", "IEF MBOUR", "IEF THIES", "IEF KAOLACK", "IEF SAINT-LOUIS", "IEF ZIGUINCHOR", "IEF TAMBACOUNDA", "IEF DIOURBEL", "IEF FATICK", "IEF KOLDA", "IEF MATAM", "IEF LOUGA", "IEF KEDOUGOU", "IEF SEDHIOU"]
PERIODES = ["1ER TRIMESTRE", "2E TRIMESTRE", "3E TRIMESTRE", "1ER SEMESTRE", "2E SEMESTRE"]
CLASSES = ["6E", "5E", "4E", "3E", "2ND S", "2ND L", "2ND G", "2ND T", "1ERE S", "1ERE L", "1ERE G", "1ERE T", "TERMINALE S", "TERMINALE L", "TERMINALE G", "TERMINALE T"]

MATIERES = {
    "6E": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC", "DESSIN"],
    "5E": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC", "DESSIN"],
    "4E": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC", "ESPAGNOL", "ITALIEN", "ARABE", "ALLEMAND", "DESSIN", "ART"],
    "3E": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC", "ESPAGNOL", "ITALIEN", "ARABE", "ALLEMAND", "DESSIN", "ART"],
    "2ND S": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"],
    "2ND L": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"],
    "1ERE S": ["PHILOSOPHIE","FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"],
    "1ERE L": ["PHILOSOPHIE","FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "ECONOMIE", "PC", "SVT", "EPS"],
    "TERMINALE S": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"],
    "TERMINALE L": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "ECONOMIE", "PC", "SVT", "EPS"],
    "2ND G": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "INFORMATIQUE", "EPS"],
    "1ERE G": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "INFORMATIQUE", "EPS"],
    "TERMINALE G": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "MARKETING", "INFORMATIQUE", "EPS"],
    "2ND T": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "EPS"],
    "1ERE T": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "EPS"],
    "TERMINALE T": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "TECHNOLOGIE", "EPS"]
}

def get_appreciation_matiere(moy):
    if moy >= 18: return "Félicitations"
    elif moy >= 16: return "Excellent"
    elif moy >= 14: return "Très Bien"
    elif moy >= 12: return "Bien"
    elif moy >= 10: return "Assez Bien"
    else: return "Passable"

def get_mention_generale(moy):
    if moy >= 16: return "EXCELLENT"
    elif moy >= 14: return "TRES BIEN"
    elif moy >= 12: return "BIEN"
    elif moy >= 10: return "ASSEZ BIEN"
    else: return "PASSABLE"

def get_decision_conseil(moy, classe):
    if moy >= 10: return "ADMIS(E) EN CLASSE SUPERIEURE"
    else: return "DOIT REDOUBLER D'EFFORTS"

LOGIN_HTML = """<!DOCTYPE html><html><head><title>CONNEXION BULLETIN SN</title><style>body{font-family:Arial;background:#00853F;display:flex;justify-content:center;align-items:center;height:100vh}input{text-transform:uppercase}.box{background:white;padding:30px;border-radius:10px;width:350px} h2{text-align:center;color:#00853F} input,select{width:100%;padding:10px;margin:8px 0;border:1px solid #ccc;border-radius:5px} button{background:#00853F;color:white;padding:12px;border:none;width:100%;border-radius:5px;font-size:16px;cursor:pointer}</style></head><body><div class="box"><h2>🇸🇳 BULLETIN SENEGAL 🇸🇳</h2><form method="POST" action="/inscription"><label>TELEPHONE:</label><input name="telephone" required><label>PRENOM:</label><input name="prenom" required><label>NOM:</label><input name="nom" required><label>DATE DE NAISSANCE:</label><input name="date_naissance" type="date" required><label>CLASSE:</label><select name="classe">{% for c in classes %}<option>{{c}}</option>{% endfor %}</select><button>ENTRER</button></form></div></body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html><html><head><title>DASHBOARD</title><style>
body{font-family:Arial;background:#eee;padding:10px}input,select{text-transform:uppercase}.container{max-width:1000px;margin:auto;background:white;padding:15px;border-radius:10px}
.btn{background:#E31B23;color:white;padding:8px 15px;text-decoration:none;border-radius:5px;float:right;margin-left:5px}
.btn-green{background:#00853F;border:none;color:white;padding:12px;width:100%;font-size:16px;cursor:pointer}
.btn-blue{background:#007BFF;color:white;padding:5px 10px;text-decoration:none;border-radius:5px}
table{width:100%;border-collapse:collapse;font-size:10px}td,th{border:1px solid #000;padding:2px;text-align:center}
input{width:60px}select{width:180px}
</style><script>
let matieres = {{matieres_json|safe}};
function updateMatieres(){let classe=document.getElementById("classe").value;let selects=document.querySelectorAll('.matiere-select');
selects.forEach(s=>{s.innerHTML='<option>--CHOISIR--</option>';if(matieres[classe]){matieres[classe].forEach(m=>{let o=document.createElement('option');o.value=m;o.text=m;s.appendChild(o);})}})}

function calculer(i){let moy=parseFloat(document.getElementsByName('moy'+i)[0].value)||0;
let coeff=parseFloat(document.getElementsByName('coeff'+i)[0].value)||1;
let total=(moy*coeff).toFixed(2);
document.getElementsByName('total_calc'+i)[0].value=total;
}
</script></head><body><div class="container">
<a href="/deconnexion" class="btn">DECONNEXION</a><a href="/mes_bulletins" class="btn" style="background:#007BFF">📦 MES BULLETINS</a>
<h2>BONJOUR {{eleve.prenom}} {{eleve.nom}}</h2>
<p>CLASSE: <b>{{eleve.classe}}</b></p><hr><h3>SAISIE BULLETIN</h3>
<form method="POST" action="/saisie">
<label>IA:</label><select name="ia">{% for ia in ia_list %}<option>{{ ia }}</option>{% endfor %}</select>
<label>IEF:</label><select name="ief">{% for ief in ief_list %}<option>{{ ief }}</option>{% endfor %}</select>
<label>ETABLISSEMENT:</label><input name="etablissement" value="LYCEE D'EXCELLENCE">
<label>ANNEE:</label><input name="annee" value="2025-2026">
<label>PERIODE:</label><select name="periode">{% for p in periodes %}<option>{{ p }}</option>{% endfor %}</select>
<input type="hidden" id="classe" name="classe" value="{{eleve.classe}}">
<hr>
<table><tr><th>N°</th><th style="width:200px">DISCIPLINES</th><th>MOY/20</th><th>COEF</th><th>TOTAL</th></tr>
{% for i in range(20) %}
<tr>
<td>{{ i+1 }}</td>
<td><select name="matiere{{i}}" class="matiere-select" style="width:180px"></select></td>
<td><input name="moy{{i}}" type="number" step="0.01" max="20" onkeyup="calculer({{i}})"></td>
<td><input name="coeff{{i}}" type="number" step="0.1" value="1" onkeyup="calculer({{i}})"></td>
<td><input name="total_calc{{i}}" readonly style="background:#ddd;width:60px"></td>
</tr>
{% endfor %}
</table><br><button class="btn-green">ENREGISTRER LE BULLETIN</button></form>
<script>updateMatieres();</script></div></body></html>"""

BOITE_BULLETINS_HTML = """<!DOCTYPE html><html><head><title>MES BULLETINS</title><style>
body{font-family:Arial;background:#eee;padding:10px}.container{max-width:900px;margin:auto;background:white;padding:15px;border-radius:10px}
.btn{background:#E31B23;color:white;padding:8px 15px;text-decoration:none;border-radius:5px;float:right}
.btn-blue{background:#007BFF;color:white;padding:5px 10px;text-decoration:none;border-radius:5px}
table{width:100%;border-collapse:collapse;margin-top:10px}th{background:#00853F;color:white}td,th{border:1px solid #ccc;padding:8px;text-align:center}
</style></head><body><div class="container">
<a href="/dashboard" class="btn">RETOUR</a><h2>📦 MES BULLETINS - {{eleve.prenom}} {{eleve.nom}}</h2>
<table><tr><th>PERIODE</th><th>CLASSE</th><th>ANNEE</th><th>MOYENNE</th><th>ACTION</th></tr>
{% for b in bulletins %}
<tr>
<td>{{b.periode}}</td><td>{{b.classe}}</td><td>{{b.annee}}</td><td><b>{{b.moyenne}}/20</b></td>
<td><a href="/bulletin/{{b.id}}" class="btn-blue">VOIR PDF</a></td>
</tr>
{% endfor %}
</table>
{% if bulletins|length == 0 %}<p style="text-align:center;margin-top:20px">Aucun bulletin enregistré</p>{% endif %}
</div></body></html>"""

BULLETIN_OFFICIEL_HTML = """<!DOCTYPE html><html><head><title>BULLETIN {{bulletin.periode}}</title><style>
body{font-family:'Times New Roman';padding:20px;background:#fff;font-size:11px}.cadre{border:2px solid #000;padding:15px}
.header{text-align:center;margin-bottom:15px}
.titre1{font-size:14px;font-weight:bold}.titre2{font-size:16px;font-weight:bold}
.info{display:flex;justify-content:space-between;margin:15px 0}
.info div{line-height:1.6}

table{width:100%;border-collapse:collapse;margin-top:10px;font-size:10px}
th{background:#f0f0f0;border:1px solid #000;padding:6px;text-align:center;font-weight:bold}
td{border:1px solid #000;padding:5px;text-align:center}
td.left{text-align:left;padding-left:8px}

.resume{display:flex;justify-content:space-around;margin:15px 0;padding:10px;border:2px solid #000;background:#f9f9f9;font-weight:bold}
.resume div{text-align:center}
.moyenne{font-size:16px;color:#E31B23}

.appreciation{border:1px solid #000;padding:10px;margin-top:15px;min-height:50px}
.footer{margin-top:20px;text-align:right}
@media print{.no-print{display:none}} </style></head><body><div class="cadre">

<div class="header">
<div class="titre1">SN</div>
<div class="titre2">REPUBLIQUE DU SENEGAL</div>
<div class="titre1">MINISTERE DE L'EDUCATION NATIONALE</div>
<div class="titre1">BULLETIN DE NOTES</div>
</div>

<div class="info">
<div>
<b>Elève:</b> {{eleve.prenom}} {{eleve.nom}}<br>
<b>IA:</b> {{bulletin.ia}}<br>
<b>Etablissement:</b> {{bulletin.etablissement}}<br>
<b>Période:</b> {{bulletin.periode}}
</div>
<div>
<b>Classe:</b> {{bulletin.classe}}<br>
<b>IEF:</b> {{bulletin.ief}}<br>
<b>Année:</b> {{bulletin.annee}}<br>
<b>Moyenne:</b> {{bulletin.moyenne}}/20
</div>
</div>

<div class="resume">
<div>SOMME DES COEFFICIENTS<br>{{somme_coeff}}</div>
<div>SOMME DES NOTES<br>{{somme_points}} PTS</div>
<div>MOYENNE GENERALE<br><span class="moyenne">{{bulletin.moyenne}}/20</span></div>
<div>MENTION<br>{{mention_text}}</div>
</div>

<table>
<tr>
<th>DISCIPLINES</th><th>MOY/20</th><th>COEF</th><th>TOTAL</th><th>APPRECIATION</th>
</tr>
{% for i, m in enumerate(matieres) %}
<tr>
<td class="left">{{m.nom}}</td>
<td>{{m.moy}}</td><td>{{m.coef}}</td><td>{{m.total}}</td><td>{{m.app}}</td>
</tr>
{% endfor %}
</table>

<div class="appreciation">
<b>APPRECIATION GENERALE:</b> {{bulletin.appreciation}}
</div>

<div class="footer">
FAIT A DAKAR, LE {{date_jour}}<br><br>
LE CHEF D'ETABLISSEMENT
</div>

</div><button class="no-print" onclick="window.print()" style="padding:8px 15px;background:#00853F;color:white;border:none;border-radius:5px;margin-top:8px">🖨️ IMPRIMER PDF</button></body></html>"""

@app.route("/", methods=["GET"])
def accueil():
    if 'eleve_id' in session: return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_HTML, classes=CLASSES)

@app.route("/inscription", methods=["POST"])
def inscription():
    tel = request.form.get("telephone")
    eleve = Eleve.query.filter_by(telephone=tel).first()
    if not eleve:
        eleve = Eleve(telephone=tel, nom=request.form.get("nom").upper(), prenom=request.form.get("prenom").upper(), classe=request.form.get("classe"), date_naissance=request.form.get("date_naissance"))
        db.session.add(eleve); db.session.commit()
    session['eleve_id'] = eleve.id
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    eleve = Eleve.query.get(session['eleve_id'])
    return render_template_string(DASHBOARD_HTML, eleve=eleve, classes=CLASSES, ia_list=IA_LIST, ief_list=IEF_LIST, periodes=PERIODES, matieres_json=MATIERES)

@app.route("/mes_bulletins")
def mes_bulletins():
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    eleve = Eleve.query.get(session['eleve_id'])
    bulletins = Bulletin.query.filter_by(eleve_id=eleve.id).all()
    return render_template_string(BOITE_BULLETINS_HTML, eleve=eleve, bulletins=bulletins)

@app.route("/saisie", methods=["POST"])
def saisie():
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    eleve = Eleve.query.get(session['eleve_id'])
    periode = request.form.get("periode")

    matieres_calculees = []; total_points = 0; total_coeff = 0
    for i in range(20):
        matiere = request.form.get(f"matiere{i}")
        if matiere and matiere!= "--CHOISIR--":
            moy=float(request.form.get(f"moy{i}") or 0)
            coeff=float(request.form.get(f"coeff{i}") or 1)
            if moy>0:
                total=round(moy*coeff,2)
                total_points+=total; total_coeff+=coeff
                app_mat=get_appreciation_matiere(moy)
                matieres_calculees.append({"nom":matiere.upper(),"moy":moy,"coef":coeff,"total":total,"app":app_mat})

    moyenne=round(total_points/total_coeff,2) if total_coeff>0 else 0
    appreciation=get_decision_conseil(moyenne, eleve.classe)

    new_bulletin=Bulletin(eleve_id=eleve.id, ia=request.form.get("ia"), ief=request.form.get("ief"),
        etablissement=request.form.get("etablissement").upper(), annee=request.form.get("annee"),
        periode=periode, classe=eleve.classe, moyenne=moyenne,
        appreciation=appreciation, data_json=json.dumps(matieres_calculees),
        date_creation=datetime.now().strftime("%d/%m/%Y %H:%M"))
    db.session.add(new_bulletin); db.session.commit()
    return redirect(url_for('mes_bulletins'))

@app.route("/bulletin/<int:id>")
def voir_bulletin(id):
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    bulletin = Bulletin.query.get(id)
    eleve = Eleve.query.get(bulletin.eleve_id)
    matieres = json.loads(bulletin.data_json)
    somme_points = 0; somme_coeff = 0
    for m in matieres:
        somme_points += m['total']; somme_coeff += m['coef']
    somme_points = round(somme_points, 2); somme_coeff = round(somme_coeff, 2)
    mention_text = get_mention_generale(bulletin.moyenne)

    return render_template_string(BULLETIN_OFFICIEL_HTML, bulletin=bulletin, eleve=eleve, matieres=matieres, date_jour=date.today().strftime("%d/%m/%Y"), somme_points=somme_points, somme_coeff=somme_coeff, mention_text=mention_text, enumerate=enumerate)

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for('accueil'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
