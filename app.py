from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date

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

def get_appreciation_generale(moy, classe):
    if "2ND" in classe or "1ERE" in classe or "TERMINALE" in classe:
        if moy >= 18: return "EXCELLENT. FELICITATIONS DU CONSEIL DE CLASSE."
        elif moy >= 16: return "TRES BIEN. TABLEAU D'HONNEUR."
        elif moy >= 14: return "BIEN. ENCOURAGEMENTS."
        elif moy >= 12: return "ASSEZ BIEN."
        elif moy >= 10: return "PASSABLE."
        else: return "INSUFFISANT. REDOUBLANT."
    else:
        if moy >= 16: return "FELICITATIONS DU CONSEIL DE CLASSE. EXCELLENT TRAVAIL."
        elif moy >= 14: return "TABLEAU D'HONNEUR. TRES BON TRAVAIL."
        elif moy >= 12: return "ENCOURAGEMENTS. BON TRAVAIL."
        elif moy >= 10: return "PASSABLE. DES EFFORTS SONT NECESSAIRES."
        else: return "INSUFFISANT. DOIT REDOUBLER D'EFFORTS."

LOGIN_HTML = """<!DOCTYPE html><html><head><title>CONNEXION BULLETIN SN</title><style>body{font-family:Arial;background:#00853F;display:flex;justify-content:center;align-items:center;height:100vh}.box{background:white;padding:30px;border-radius:10px;width:350px;box-shadow:0 0 20px #000} h2{text-align:center;color:#00853F} input,select{width:100%;padding:10px;margin:8px 0;border:1px solid #ccc;border-radius:5px} button{background:#00853F;color:white;padding:12px;border:none;width:100%;border-radius:5px;font-size:16px;cursor:pointer}</style></head><body><div class="box"><h2>🇸🇳 BULLETIN SENEGAL 🇸🇳</h2><form method="POST" action="/inscription"><label>TELEPHONE:</label><input name="telephone" placeholder="77 123 45 67" required><label>PRENOM:</label><input name="prenom" required><label>NOM:</label><input name="nom" required><label>CLASSE:</label><select name="classe">{% for c in classes %}<option>{{c}}</option>{% endfor %}</select><button>ENTRER</button></form></div></body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html><html><head><title>DASHBOARD</title><style>
body{font-family:Arial;background:#eee;padding:10px}.container{max-width:1000px;margin:auto;background:white;padding:15px;border-radius:10px}
.btn{background:#E31B23;color:white;padding:8px 15px;text-decoration:none;border-radius:5px;float:right}.btn-green{background:#00853F;border:none;color:white;padding:12px;width:100%;font-size:16px;cursor:pointer}
.btn-blue{background:#007BFF;color:white;padding:5px 10px;text-decoration:none;border-radius:5px;font-size:12px}
.bulletin-box{border:2px solid #00853F;padding:15px;margin:15px 0;border-radius:10px;background:#f9f9f9}
table{width:100%;border-collapse:collapse;font-size:11px}td,th{border:1px solid #000;padding:3px;text-align:center}
input{width:50px}select{width:150px}
</style><script>
let matieres = {{matieres_json|safe}};
function updateMatieres(){let classe=document.getElementById("classe").value;let selects=document.querySelectorAll('.matiere-select');
selects.forEach(s=>{s.innerHTML='<option>--CHOISIR--</option>';if(matieres[classe]){matieres[classe].forEach(m=>{let o=document.createElement('option');o.value=m;o.text=m;s.appendChild(o);})}})}

function calculer(i){let d1=parseFloat(document.getElementsByName('devoir1_'+i)[0].value)||0;
let d2=parseFloat(document.getElementsByName('devoir2_'+i)[0].value)||0;
let d3=parseFloat(document.getElementsByName('devoir3_'+i)[0].value)||0;
let comp=parseFloat(document.getElementsByName('comp'+i)[0].value)||0;
let moy=((d1+d2+d3+comp*2)/5).toFixed(2);
let app=''; if(moy>=18)app='FELICITATIONS';else if(moy>=16)app='EXCELLENT';else if(moy>=14)app='TRES BIEN';
else if(moy>=12)app='BIEN';else if(moy>=10)app='ASSEZ BIEN';else app='PASSABLE';
document.getElementsByName('app_mat'+i)[0].value=app;
}
</script></head><body><div class="container">
<a href="/deconnexion" class="btn">DECONNEXION</a><h2>BONJOUR {{eleve.prenom}} {{eleve.nom}}</h2>
<p>CLASSE: <b>{{eleve.classe}}</b></p><hr><h3>MES BULLETINS</h3>
{% for b in bulletins %}
<div class="bulletin-box">
<b>{{b.periode}} - {{b.annee}}</b> <br>
<b>IA:</b> {{b.ia}} | <b>IEF:</b> {{b.ief}} | <b>ETABLISSEMENT:</b> {{b.etablissement}} <br>
<b>MOYENNE GENERALE:</b> <span style="font-size:18px;color:#E31B23">{{b.moyenne}}/20</span> <br>
<b>APPRECIATION:</b> {{b.appreciation}} <br><br>
<a href="/bulletin/{{b.id}}" class="btn-blue">📄 VOIR LE BULLETIN OFFICIEL</a>
</div>
{% else %}<p>AUCUN BULLETIN POUR LE MOMENT.</p>{% endfor %}<hr>

<h3>NOUVEAU BULLETIN</h3>
<form method="POST" action="/saisie">
<label>IA:</label><select name="ia">{% for ia in ia_list %}<option>{{ ia }}</option>{% endfor %}</select>
<label>IEF:</label><select name="ief">{% for ief in ief_list %}<option>{{ ief }}</option>{% endfor %}</select>
<label>ETABLISSEMENT:</label><input name="etablissement" value="LYCEE D'EXCELLENCE">
<label>ANNEE:</label><input name="annee" value="2025-2026">
<label>PERIODE:</label><select name="periode">{% for p in periodes %}<option>{{ p }}</option>{% endfor %}</select>
<input type="hidden" id="classe" name="classe" value="{{eleve.classe}}">
<hr>
<table><tr><th>N°</th><th style="width:160px">DISCIPLINES</th><th>D1</th><th>D2</th><th>D3</th><th>COMP</th><th>COEF</th><th style="width:110px">APPRECIATION</th></tr>
{% for i in range(20) %}
<tr>
<td>{{ i+1 }}</td>
<td><select name="matiere{{i}}" class="matiere-select" style="width:160px"></select></td>
<td><input name="devoir1_{{i}}" type="number" step="0.01" max="20" onkeyup="calculer({{i}})"></td>
<td><input name="devoir2_{{i}}" type="number" step="0.01" max="20" onkeyup="calculer({{i}})"></td>
<td><input name="devoir3_{{i}}" type="number" step="0.01" max="20" onkeyup="calculer({{i}})"></td>
<td><input name="comp{{i}}" type="number" step="0.01" max="20" onkeyup="calculer({{i}})"></td>
<td><input name="coeff{{i}}" type="number" value="1"></td>
<td><input name="app_mat{{i}}" readonly style="background:#ddd;width:110px"></td>
</tr>
{% endfor %}
</table><br><button class="btn-green">ENREGISTRER LE BULLETIN</button></form>
<script>updateMatieres();</script>
</div></body></html>"""

BULLETIN_OFFICIEL_HTML = """<!DOCTYPE html><html><head><title>BULLETIN {{bulletin.periode}}</title><style>
body{font-family:'Times New Roman';padding:20px;background:#fff;font-size:12px;text-transform:uppercase}.cadre{border:4px double #00853F;padding:15px}
.header{text-align:center;margin-bottom:10px}.drapeau-img{height:60px;margin-bottom:5px}.titre{color:#00853F;font-weight:bold;text-transform:uppercase}
.info{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:15px 0;border-bottom:2px solid #000;padding-bottom:10px;font-weight:bold}
table{width:100%;border-collapse:collapse;margin-top:10px}th{background:#00853F;color:white;text-transform:uppercase}td,th{border:1px solid #000;padding:6px;text-align:center;text-transform:uppercase}
.total-box{display:flex;justify-content:space-between;margin-top:15px;padding:10px;border:2px solid #E31B23;background:#FFF0F0;text-transform:uppercase}
.moyenne{font-size:22px;font-weight:bold;color:#E31B23}
.mention{font-size:18px;font-weight:bold;padding:5px 10px;border-radius:5px}
.passable{background:#FFD700}.ab{background:#90EE90}.bien{background:#87CEEB}.tb{background:#FFA500;color:white}.excellent{background:#E31B23;color:white}
.footer{margin-top:30px;display:flex;justify-content:space-between;text-transform:uppercase}
.signature{border-top:1px solid #000;padding-top:5px;width:200px;text-align:center;font-weight:bold}
@media print{.no-print{display:none}} </style></head><body><div class="cadre">
<div class="header">
<img src="https://flagcdn.com/w320/sn.png" class="drapeau-img">
<h2 class="titre">REPUBLIQUE DU SENEGAL</h2>
<h3 class="titre">MINISTERE DE L'EDUCATION NATIONALE</h3>
<h4>BULLETIN DE NOTES</h4>
</div>

<div class="info">
<div><b>ELEVE:</b> {{eleve.prenom}} {{eleve.nom}}</div><div><b>CLASSE:</b> {{bulletin.classe}}</div>
<div><b>IA:</b> {{bulletin.ia}}</div><div><b>IEF:</b> {{bulletin.ief}}</div>
<div><b>ETABLISSEMENT:</b> {{bulletin.etablissement}}</div><div><b>ANNEE SCOLAIRE:</b> {{bulletin.annee}}</div>
<div><b>PERIODE:</b> {{bulletin.periode}}</div><div><b>RANG:</b> N/A</div>
</div>

<table><tr><th>DISCIPLINES</th><th>MOY/20</th><th>COEF</th><th>TOTAL</th><th>APPRECIATION</th></tr>
{% for m in matieres %}
<tr><td style="text-align:left">{{m.nom}}</td><td>{{m.moy}}</td><td>{{m.coef}}</td><td>{{m.total}}</td><td>{{m.app}}</td></tr>
{% endfor %}</table>

<div class="total-box">
<div>
<b>APPRECIATION GENERALE:</b><br> {{bulletin.appreciation}} <br><br>
<b>MENTION:</b> <span class="mention {{mention_class}}">{{mention_text}}</span>
</div>
<div style="text-align:right">
<b>NOTE SUR:</b> {{somme_points}} / {{note_sur}} <br>
<b>SOMME DES COEFF:</b> {{somme_coeff}} <br>
<b>MOYENNE GENERALE:</b><br>
<span class="moyenne">{{bulletin.moyenne}}/20</span>
</div>
</div>

<div class="footer">
<div class="signature">FAIT A DAKAR, LE {{date_jour}} ET DISPONIBLE<br>LE TITULAIRE</div>
<div class="signature">LE PROVISEUR<br><br><br>CACHET</div>
</div>
</div><button class="no-print" onclick="window.print()" style="padding:10px 20px;background:#00853F;color:white;border:none;border-radius:5px;margin-top:10px">🖨️ IMPRIMER / ENREGISTRER EN PDF</button></body></html>"""

@app.route("/", methods=["GET"])
def accueil():
    if 'eleve_id' in session: return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_HTML, classes=CLASSES)

@app.route("/inscription", methods=["POST"])
def inscription():
    tel = request.form.get("telephone")
    eleve = Eleve.query.filter_by(telephone=tel).first()
    if not eleve:
        eleve = Eleve(telephone=tel, nom=request.form.get("nom").upper(), prenom=request.form.get("prenom").upper(), classe=request.form.get("classe"))
        db.session.add(eleve); db.session.commit()
    session['eleve_id'] = eleve.id
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    eleve = Eleve.query.get(session['eleve_id'])
    bulletins = Bulletin.query.filter_by(eleve_id=eleve.id).all()
    return render_template_string(DASHBOARD_HTML, eleve=eleve, bulletins=bulletins, classes=CLASSES, ia_list=IA_LIST, ief_list=IEF_LIST, periodes=PERIODES, matieres_json=MATIERES)

@app.route("/saisie", methods=["POST"])
def saisie():
    if 'eleve_id' not in session: return redirect(url_for('accueil'))
    eleve = Eleve.query.get(session['eleve_id'])

    matieres_calculees = []; total_points = 0; total_coeff = 0
    for i in range(20):
        matiere = request.form.get(f"matiere{i}")
        if matiere and matiere!= "--CHOISIR--":
            d1=float(request.form.get(f"devoir1_{i}") or 0); d2=float(request.form.get(f"devoir2_{i}") or 0)
            d3=float(request.form.get(f"devoir3_{i}") or 0); comp=float(request.form.get(f"comp{i}") or 0); coeff=float(request.form.get(f"coeff{i}") or 1)
            if d1>0 or d2>0 or d3>0 or comp>0:
                moy=round((d1+d2+d3+comp*2)/5,2); total=round(moy*coeff,2)
                total_points+=total; total_coeff+=coeff
                matieres_calculees.append({"nom":matiere,"moy":moy,"coef":coeff,"total":total})

    moyenne=round(total_points/total_coeff,2) if total_coeff>0 else 0
    appreciation=get_appreciation_generale(moyenne, eleve.classe)

    new_bulletin=Bulletin(eleve_id=eleve.id, ia=request.form.get("ia"), ief=request.form.get("ief"),
        etablissement=request.form.get("etablissement").upper(), annee=request.form.get("annee"),
        periode=request.form.get("periode"), classe=eleve.classe, moyenne=moyenne,
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
        m['app'] = get_appreciation_matiere(m['moy'])
        somme_points += m['total']; somme_coeff += m['coef']
    somme_points = round(somme_points, 2); somme_coeff = round(somme_coeff, 2)
    note_sur = round(somme_coeff * 20, 2)

    moy = bulletin.moyenne
    if moy >= 18: mention_text="EXCELLENT"; mention_class="excellent"
    elif moy >= 16: mention_text="TRES BIEN"; mention_class="tb"
    elif moy >= 14: mention_text="BIEN"; mention_class="bien"
    elif moy >= 12: mention_text="ASSEZ BIEN"; mention_class="ab"
    elif moy >= 10: mention_text="PASSABLE"; mention_class="passable"
    else: mention_text="INSUFFISANT"; mention_class=""

    return render_template_string(BULLETIN_OFFICIEL_HTML, bulletin=bulletin, eleve=eleve, matieres=matieres, date_jour=date.today().strftime("%d/%m/%Y"), somme_points=somme_points, somme_coeff=somme_coeff, note_sur=note_sur, mention_text=mention_text, mention_class=mention_class)

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for('accueil'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
