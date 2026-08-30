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
    sexe = db.Column(db.String(10), default="MASCULIN")

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
    if moy >= 18: return "FELICITATIONS"
    elif moy >= 16: return "EXCELLENT"
    elif moy >= 14: return "TRES BIEN"
    elif moy >= 12: return "BIEN"
    elif moy >= 10: return "ASSEZ BIEN"
    else: return "PASSABLE"

def get_decision_conseil(moy, classe):
    # MENTIONS SPÉCIALES POUR 2NDE 1ERE TERMINALE
    if "2ND" in classe or "1ERE" in classe or "TERMINALE" in classe:
        if moy >= 16: return "Félicitations"
        elif moy >= 14: return "Tableau d'honneur"
        elif moy >= 12: return "Encouragements"
        elif moy >= 10: return "Passable"
        else: return "Doit redoubler d'effort"
    else: # Collège
        if moy >= 16: return "Félicitations"
        elif moy >= 14: return "Tableau d'honneur"
        elif moy >= 12: return "Encouragements"
        elif moy >= 10: return "Passable"
        else: return "Insuffisant"

LOGIN_HTML = """<!DOCTYPE html><html><head><title>CONNEXION BULLETIN SN</title><style>body{font-family:Arial;background:#00853F;display:flex;justify-content:center;align-items:center;height:100vh}input{text-transform:uppercase}.box{background:white;padding:30px;border-radius:10px;width:350px} h2{text-align:center;color:#00853F} input,select{width:100%;padding:10px;margin:8px 0;border:1px solid #ccc;border-radius:5px} button{background:#00853F;color:white;padding:12px;border:none;width:100%;border-radius:5px;font-size:16px;cursor:pointer}</style></head><body><div class="box"><h2>🇸🇳 BULLETIN SENEGAL 🇸🇳</h2><form method="POST" action="/inscription"><label>TELEPHONE:</label><input name="telephone" required><label>PRENOM:</label><input name="prenom" required><label>NOM:</label><input name="nom" required><label>DATE DE NAISSANCE:</label><input name="date_naissance" type="date" required><label>CLASSE:</label><select name="classe">{% for c in classes %}<option>{{c}}</option>{% endfor %}</select><button>ENTRER</button></form></div></body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html><html><head><title>DASHBOARD</title><style>
body{font-family:Arial;background:#eee;padding:10px}input,select{text-transform:uppercase}.container{max-width:1100px;margin:auto;background:white;padding:15px;border-radius:10px}
.btn{background:#E31B23;color:white;padding:8px 15px;text-decoration:none;border-radius:5px;float:right}.btn-green{background:#00853F;border:none;color:white;padding:12px;width:100%;font-size:16px;cursor:pointer}
table{width:100%;border-collapse:collapse;font-size:10px}td,th{border:1px solid #000;padding:2px;text-align:center}
input{width:45px}select{width:140px}
</style><script>
let matieres = {{matieres_json|safe}};
function updateMatieres(){let classe=document.getElementById("classe").value;let selects=document.querySelectorAll('.matiere-select');
selects.forEach(s=>{s.innerHTML='<option>--CHOISIR--</option>';if(matieres[classe]){matieres[classe].forEach(m=>{let o=document.createElement('option');o.value=m;o.text=m;s.appendChild(o);})}})}

function calculer(i){let d1=parseFloat(document.getElementsByName('devoir1_'+i)[0].value)||0;
let comp=parseFloat(document.getElementsByName('comp'+i)[0].value)||0;
let moy=((d1+d1+comp*2)/4).toFixed(2); // 2 DEVOIRS + 2 COMP
document.getElementsByName('moy_calc'+i)[0].value=moy;
}
</script></head><body><div class="container">
<a href="/deconnexion" class="btn">DECONNEXION</a><h2>BONJOUR {{eleve.prenom}} {{eleve.nom}}</h2>
<p>CLASSE: <b>{{eleve.classe}}</b> | NE LE: <b>{{eleve.date_naissance}}</b></p><hr><h3>NOUVEAU BULLETIN</h3>
<form method="POST" action="/saisie">
<label>IA:</label><select name="ia">{% for ia in ia_list %}<option>{{ ia }}</option>{% endfor %}</select>
<label>IEF:</label><select name="ief">{% for ief in ief_list %}<option>{{ ief }}</option>{% endfor %}</select>
<label>ETABLISSEMENT:</label><input name="etablissement" value="LYCEE MBACKE">
<label>ANNEE:</label><input name="annee" value="2025-2026">
<label>PERIODE:</label><select name="periode">{% for p in periodes %}<option>{{ p }}</option>{% endfor %}</select>
<input type="hidden" id="classe" name="classe" value="{{eleve.classe}}">
<hr>
<table><tr><th>N°</th><th style="width:140px">DISCIPLINES</th><th>DEVOIRS</th><th>COMPOS</th><th>COEF</th><th>MOY</th></tr>
{% for i in range(20) %}
<tr>
<td>{{ i+1 }}</td>
<td><select name="matiere{{i}}" class="matiere-select" style="width:140px"></select></td>
<td><input name="devoir1_{{i}}" type="number" step="0.01" max="20" onkeyup="calculer({{i}})"></td>
<td><input name="comp{{i}}" type="number" step="0.01" max="20" onkeyup="calculer({{i}})"></td>
<td><input name="coeff{{i}}" type="number" value="1"></td>
<td><input name="moy_calc{{i}}" readonly style="background:#ddd;width:45px"></td>
</tr>
{% endfor %}
</table><br><button class="btn-green">ENREGISTRER LE BULLETIN</button></form>
<script>updateMatieres();</script></div></body></html>"""

BULLETIN_OFFICIEL_HTML = """<!DOCTYPE html><html><head><title>BULLETIN {{bulletin.periode}}</title><style>
body{font-family:'Arial';padding:10px;background:#fff;font-size:9px;text-transform:uppercase}.cadre{border:1px solid #000;padding:8px}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px}
.drapeau{height:40px}.titre{text-align:center;font-weight:bold}
.titre h3{margin:0;font-size:12px}.titre h4{margin:0;font-size:10px}

.info-top{display:grid;grid-template-columns:1fr 1fr;gap:10px;border:1px solid #000;padding:5px;margin:5px 0}
.info-box{border:1px solid #000;padding:4px;font-size:8px}
.info-box div{margin:2px 0}

table{width:100%;border-collapse:collapse;margin-top:5px;font-size:8px}
th{background:#D3D3D3;border:1px solid #000;padding:3px;text-align:center;font-weight:bold}
td{border:1px solid #000;padding:2px;text-align:center}
td.left{text-align:left;padding-left:3px}

.totaux{font-weight:bold;background:#D3D3D3}

.blocs-bas{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
.bloc{border:1px solid #000;padding:4px;font-size:8px}
.bloc table{margin:0;font-size:8px}
.bloc.titre-bloc{background:#D3D3D3;font-weight:bold;text-align:center;padding:2px}

.decision table td{border:1px solid #000;padding:2px;text-align:left}
.decision.x{font-weight:bold;font-size:12px;text-align:center}

.signatures{display:flex;justify-content:space-between;margin-top:15px}
.qr{display:flex;justify-content:space-between;margin-top:10px}
.nb{font-size:7px;text-align:center;margin-top:5px;border-top:1px solid #000;padding-top:3px}
@media print{.no-print{display:none}} </style></head><body><div class="cadre">

<div class="header">
<img src="https://flagcdn.com/w320/sn.png" class="drapeau">
<div class="titre">
<h3>République du Sénégal</h3>
<h4>Ministère de l'Education nationale</h4>
<h3>{{bulletin.etablissement}}</h3>
<h4>ANNEE SCOLAIRE: {{bulletin.annee}}</h4>
</div>
<img src="https://upload.wikimedia.org/wikipedia/commons/8/89/Education_logo.png" class="drapeau">
</div>

<div class="info-top">
<div class="info-box">
<div><b>Tel:</b> {{eleve.telephone}}</div>
<div><b>Email:</b> </div>
<div><b>Niveau:</b> {{niveau}}</div>
<div><b>Série:</b> {{serie}}</div>
<div><b>Effectif:</b> 60</div>
<div><b>Moyenne classe:</b> 9.30</div>
</div>
<div class="info-box">
<div><b>IEN:</b> BAYGNFC</div>
<div><b>SEXE:</b> {{eleve.sexe}}</div>
<div><b>Classe:</b> {{bulletin.classe}}</div>
<div><b>Classe doublée:</b> NEANT</div>
<div><b>Prénom(s):</b> {{eleve.prenom}}</div>
<div><b>Nom:</b> {{eleve.nom}}</div>
<div><b>Né(e) le:</b> {{eleve.date_naissance}} à TOUBA</div>
</div>
</div>

<div style="background:#D3D3D3;text-align:center;font-weight:bold;padding:4px;margin:5px 0">
BULLETIN DU {{bulletin.periode}}
</div>

<table>
<tr>
<th>Disciplines</th><th>Devoirs</th><th>Compos</th><th>Moy</th><th>Coeff</th><th>MoyxCoeff</th><th>Rang</th><th>Appréciations</th>
</tr>
{% for i, m in enumerate(matieres) %}
<tr>
<td class="left">{{m.nom}}</td>
<td>{{m.d1}}</td><td>{{m.comp}}</td><td>{{m.moy}}</td><td>{{m.coef}}</td><td>{{m.total}}</td><td>{{i+1}}ex</td><td>{{m.app}}</td>
</tr>
{% endfor %}
<tr class="totaux">
<td class="left">Totaux</td><td></td><td></td><td></td><td>{{somme_coeff}}</td><td>{{somme_points}}</td><td></td><td></td>
</tr>
</table>

<div style="margin:5px 0"><b>Moyenne: {{bulletin.moyenne}}</b> | <b>Rang: 11</b> | <b>Retards: 0 heure(s) 0 minute(s)</b> | <b>Absences: 2 dont 0 justifiée(s)</b></div>

<div class="blocs-bas">
<div class="bloc decision">
<div class="titre-bloc">Décision</div>
<table>
<tr><td>Travail excellent</td><td class="x">{% if bulletin.moyenne >= 16 %}X{% endif %}</td></tr>
<tr><td>Satisfaisant doit continuer</td><td class="x">{% if 14 <= bulletin.moyenne < 16 %}X{% endif %}</td></tr>
<tr><td>Peut mieux faire</td><td class="x">{% if 12 <= bulletin.moyenne < 14 %}X{% endif %}</td></tr>
<tr><td>Insuffisant</td><td class="x">{% if 10 <= bulletin.moyenne < 12 %}X{% endif %}</td></tr>
<tr><td>Risque de redoubler</td><td class="x">{% if bulletin.moyenne < 10 %}X{% endif %}</td></tr>
<tr><td>Risque exclusion</td><td></td></tr>
<tr><td>Blâme</td><td></td></tr>
</table>
</div>
<div class="bloc">
<div class="titre-bloc">Observations du conseil des professeurs</div>
<div style="height:60px">{{bulletin.appreciation}}</div>
</div>
</div>

<div class="signatures">
<div></div>
<div>Le Chef d'établissement</div>
</div>

<div class="qr">
<img src="https://api.qrserver.com/v1/create-qr-code/?size=70x70&data={{eleve.id}}" />
<img src="https://api.qrserver.com/v1/create-qr-code/?size=70x70&data=bulletin{{bulletin.id}}" />
</div>

<div class="nb">
N.B.: Ce bulletin n'est délivré qu'une seule fois. Toute demande de duplicata pourrait faire l'objet d'une contrepartie financière.<br>
Ce bulletin est édité le {{date_jour}} à {{heure}}
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

@app.route("/saisie", methods=["POST"])
def saisie():
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    eleve = Eleve.query.get(session['eleve_id'])
    periode = request.form.get("periode")

    matieres_calculees = []; total_points = 0; total_coeff = 0
    for i in range(20):
        matiere = request.form.get(f"matiere{i}")
        if matiere and matiere!= "--CHOISIR--":
            d1=float(request.form.get(f"devoir1_{i}") or 0); d2=d1
            comp=float(request.form.get(f"comp{i}") or 0); coeff=float(request.form.get(f"coeff{i}") or 1)
            if d1>0 or comp>0:
                moy=round((d1+d2+comp*2)/4,2) # FORMULE 2 DEVOIRS + 2 COMP
                total=round(moy*coeff,2)
                total_points+=total; total_coeff+=coeff
                app_mat=get_appreciation_matiere(moy)
                matieres_calculees.append({"nom":matiere.upper(),"d1":d1,"comp":comp,"moy":moy,"coef":coeff,"total":total,"app":app_mat})

    moyenne=round(total_points/total_coeff,2) if total_coeff>0 else 0
    appreciation=get_decision_conseil(moyenne, eleve.classe)

    new_bulletin=Bulletin(eleve_id=eleve.id, ia=request.form.get("ia"), ief=request.form.get("ief"),
        etablissement=request.form.get("etablissement").upper(), annee=request.form.get("annee"),
        periode=periode, classe=eleve.classe, moyenne=moyenne,
        appreciation=appreciation, data_json=json.dumps(matieres_calculees))
    db.session.add(new_bulletin); db.session.commit()
    return redirect(url_for('dashboard'))

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

    niveau = "SECONDE" if "2ND" in bulletin.classe else "PREMIERE" if "1ERE" in bulletin.classe else "TERMINALE" if "TERMINALE" in bulletin.classe else "COLLEGE"
    serie = "S" if "S" in bulletin.classe else "L" if "L" in bulletin.classe else "G" if "G" in bulletin.classe else "T" if "T" in bulletin.classe else ""

    return render_template_string(BULLETIN_OFFICIEL_HTML, bulletin=bulletin, eleve=eleve, matieres=matieres, date_jour=date.today().strftime("%d-%m-%Y"), heure=datetime.now().strftime("%H:%M:%S"), somme_points=somme_points, somme_coeff=somme_coeff, niveau=niveau, serie=serie, enumerate=enumerate)

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for('accueil'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
