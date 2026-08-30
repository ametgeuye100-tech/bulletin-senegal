from flask import Flask, render_template_string, request

app = Flask(__name__)

IA_LIST = ["IA DAKAR", "IA THIES", "IA KAOLACK", "IA SAINT-LOUIS", "IA ZIGUINCHOR", "IA TAMBACOUNDA", "IA DIOURBEL", "IA FATICK", "IA KOLDA", "IA MATAM", "IA LOUGA", "IA KEDOUGOU", "IA SEDHIOU"]
IEF_LIST = ["IEF DAKAR PLATEAU", "IEF DAKAR ALMADIES", "IEF MBOUR", "IEF THIES", "IEF KAOLACK", "IEF SAINT-LOUIS", "IEF ZIGUINCHOR", "IEF TAMBACOUNDA", "IEF DIOURBEL", "IEF FATICK", "IEF KOLDA", "IEF MATAM", "IEF LOUGA", "IEF KEDOUGOU", "IEF SEDHIOU"]
PERIODES = ["1er Trimestre", "2e Trimestre", "3e Trimestre", "1er Semestre", "2e Semestre"]
CLASSES = ["6e", "5e", "4e", "3e", "2nd S", "2nd L", "2nd G", "2nd T", "1ère S", "1ère L", "1ère G", "1ère T", "Terminale S", "Terminale L", "Terminale G", "Terminale T"]

MATIERES = {
    "6e": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC"],
    "5e": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC"],
    "4e": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC", "ESPAGNOL", "ITALIEN", "ARABE", "ALLEMAND"],
    "3e": ["FRANÇAIS", "MATHS", "PC", "SVT", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "EPS", "EC", "ESPAGNOL", "ITALIEN", "ARABE", "ALLEMAND"],
    "2nd S": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"],
    "2nd L": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"],
    "1ère S": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"],
    "1ère L": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "ECONOMIE", "PC", "SVT", "EPS"],
    "Terminale S": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "PC", "SVT", "EPS"],
    "Terminale L": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "ARABE", "ALLEMAND", "ITALIEN", "MATHS", "ECONOMIE", "PC", "SVT", "EPS"],
    "2nd G": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "INFORMATIQUE", "EPS"],
    "1ère G": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "INFORMATIQUE", "EPS"],
    "Terminale G": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "COMPTABILITE", "ECONOMIE", "DROIT", "ORGANISATION", "MARKETING", "INFORMATIQUE", "EPS"],
    "2nd T": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "EPS"],
    "1ère T": ["FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "EPS"],
    "Terminale T": ["PHILOSOPHIE", "FRANÇAIS", "HISTOIRE/GEOGRAPHIE", "ANGLAIS", "ESPAGNOL", "MATHS", "PHYSIQUE", "CONSTRUCTION", "MECANIQUE", "ELECTRICITE", "DESSIN TECH", "TECHNOLOGIE", "EPS"],
}

def get_appreciation_matiere(moy):
    if moy >= 18: return "Félicitations"
    elif moy >= 16: return "Excellent"
    elif moy >= 14: return "Très Bien"
    elif moy >= 12: return "Bien"
    elif moy >= 10: return "Assez Bien"
    else: return "Passable"

def get_appreciation_generale(moy):
    if moy >= 16: return "Félicitations du Conseil de Classe. Excellent travail et très bonne compréhension."
    elif moy >= 14: return "Tableau d'Honneur. Très bon travail et bonne compréhension."
    elif moy >= 12: return "Encouragements. Bon travail. Bonne compréhension."
    elif moy >= 10: return "Passable. Des efforts de compréhension sont nécessaires."
    else: return "Insuffisant. Doit travailler sa compréhension."

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Bulletin Officiel Sénégal</title>
    <style>
        body { font-family: 'Times New Roman', serif; background: #eee; padding: 10px; }
.bulletin { width: 21cm; min-height: 29.7cm; background: white; margin: auto; padding: 15px; border: 3px solid black; }
.drapeau { display: flex; height: 30px; }
.drapeau div { width: 33.33%; }
.vert { background: #00853F; }
.jaune { background: #FDEF42; }
.rouge { background: #E31B23; }
.header { display: flex; justify-content: space-between; font-size: 12px; margin-top: 5px; }
.titre { text-align: center; font-weight: bold; font-size: 18px; text-decoration: underline; margin: 10px 0; }
.info-eleve { width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 10px; border: 1px solid black; }
.info-eleve td { padding: 4px; border: 1px solid black; }
        table.notes { width: 100%; border-collapse: collapse; font-size: 10px; border: 1px solid black; }
        table.notes th, table.notes td { border: 1px solid black; padding: 3px; text-align: center; }
        table.notes th { background: #f0f0f0; font-weight: bold; }
.total { font-weight: bold; background: #D9EAD3; }
.signature { display: flex; justify-content: space-between; margin-top: 25px; font-size: 12px; }
.tampon { border: 3px dashed red; border-radius: 50%; padding: 15px; color: red; font-weight: bold; width: 100px; height: 100px; text-align:center; line-height: 20px; }
.btn { background: #00853F; color: white; padding: 12px; border: none; width: 100%; font-size: 16px; cursor: pointer; border-radius: 5px; }
.form-box { background:white; padding:15px; max-width:1000px; margin:auto; border-radius:10px; box-shadow: 0 0 10px #ccc; }
      select, input { padding: 6px; margin: 3px; border-radius: 4px; border: 1px solid #ccc; }
      input[readonly] { background: #ddd; }
        @media print {.btn,.form-box { display: none; } body { background: white; }.bulletin { border: 2px solid black; } }
    </style>
</head>
<body>

{% if not bulletin %}
<div class="form-box">
<form method="POST">
    <h2 style="text-align:center; color:#00853F;">🇸🇳 SAISIE BULLETIN OFFICIEL SENEGAL 🇸🇳</h2>
    <label><b>IA:</b></label><select name="ia">{% for ia in ia_list %}<option>{{ ia }}</option>{% endfor %}</select>
    <label><b>IEF:</b></label><select name="ief">{% for ief in ief_list %}<option>{{ ief }}</option>{% endfor %}</select><br>
    <label><b>Établissement:</b></label><input name="etablissement" value="LYCEE D'EXCELLENCE">
    <label><b>Année:</b></label><input name="annee" value="2025-2026">
    <label><b>Période:</b></label><select name="periode">{% for p in periodes %}<option>{{ p }}</option>{% endfor %}</select><hr>

    <label><b>Prénom:</b></label><input name="prenom" value="PRENOM">
    <label><b>Nom:</b></label><input name="nom" value="NOM"><br>
    <label><b>Né(e) le:</b></label><input name="naissance" value="01/01/2008">
    <label><b>à:</b></label><input name="lieu" value="DAKAR"><br>
    <label><b>Classe:</b></label><select name="classe" id="classe" onchange="updateMatieres()">{% for c in classes %}<option>{{ c }}</option>{% endfor %}</select>
    <label><b>Matricule:</b></label><input name="matricule" value="N/A" readonly>
    <label><b>Effectif:</b></label><input name="nb_eleves" value="N/A" readonly style="background:#ddd;">
    <label><b>Rang Classe:</b></label><input name="rang" value="N/A" readonly style="background:#ddd;"><br><hr>

    <table border="1" style="width:100%; font-size:11px;">
        <tr><th>N°</th><th>DISCIPLINES</th><th>1er Devoir</th><th>2e Devoir</th><th>Comp</th><th>Coeff</th><th>Appréciation</th></tr>
        {% for i in range(20) %}
        <tr>
            <td>{{ i+1 }}</td>
            <td><select name="matiere{{i}}" class="matiere-select" style="width:200px"></select></td>
            <td><input name="devoir1_{{i}}" type="number" step="0.01" style="width:60px"></td>
            <td><input name="devoir2_{{i}}" type="number" step="0.01" style="width:60px"></td>
            <td><input name="comp{{i}}" type="number" step="0.01" style="width:60px"></td>
            <td><input name="coeff{{i}}" type="number" value="1" style="width:50px"></td>
            <td><input name="app_mat{{i}}" value="Auto" readonly style="width:120px; background:#ddd;"></td>
        </tr>
        {% endfor %}
    </table>
    <button class="btn">GENERER LE BULLETIN</button>
</form>
</div>
<script>
    let matieres = {{ matieres_json | safe }};
    function updateMatieres() {
        let classe = document.getElementById("classe").value;
        let filiere = classe;
        let selects = document.querySelectorAll('.matiere-select');
        selects.forEach(select => {
            select.innerHTML = '<option value="">-- Choisir --</option>';
            if(matieres[filiere]){
                matieres[filiere].forEach(m => {
                    let opt = document.createElement('option');
                    opt.value = m; opt.text = m;
                    select.appendChild(opt);
                });
            }
        });
    }
    updateMatieres();
</script>
{% endif %}

{% if bulletin %}
<div class="bulletin">
    <div class="drapeau"><div class="vert"></div><div class="jaune"></div><div class="rouge"></div></div>
    <div class="header">
        <div><b>{{ ia }}</b><br><b>{{ ief }}</b><br><b>{{ etablissement }}</b></div>
        <div style="text-align:right;"><b>Année Scolaire:</b> {{ annee }}<br><b>{{ periode }}</b></div>
    </div>
    <div class="titre">BULLETIN DE NOTES</div>

    <table class="info-eleve">
        <tr><td><b>Prénoms:</b> {{ prenom }}</td><td><b>Nom:</b> {{ nom }}</td><td><b>Classe:</b> {{ classe }}</td></tr>
        <tr><td><b>Né(e) le:</b> {{ naissance }}</td><td><b>à:</b> {{ lieu }}</td><td><b>Matricule:</b> {{ matricule }}</td></tr>
        <tr><td><b>Effectif:</b> N/A</td><td><b>Rang:</b> N/A</td><td></td></tr>
    </table>

    <table class="notes">
        <tr><th>N°</th><th>DISCIPLINES</th><th>D1</th><th>D2</th><th>Comp</th><th>Moy/20</th><th>Coef</th><th>Total Pts</th><th>Appréciation</th></tr>
        {% for i, m in enumerate(matieres_calculees) %}
        <tr>
            <td>{{ i+1 }}</td><td style="text-align:left">{{ m.nom }}</td><td>{{ m.d1 }}</td><td>{{ m.d2 }}</td><td>{{ m.comp }}</td><td>{{ m.moy }}</td>
            <td>{{ m.coef }}</td><td>{{ m.total }}</td><td><b>{{ m.app_mat }}</b></td>
        </tr>
        {% endfor %}
        <tr class="total">
            <td colspan="6">TOTAUX</td>
            <td>{{ total_coeff }}</td>
            <td>{{ total_points }} / {{ total_possible }}</td>
            <td></td>
        </tr>
        <tr class="total">
            <td colspan="5">MOYENNE GENERALE</td>
            <td>{{ moyenne }}/20</td>
            <td colspan="2">Rang: N/A</td>
            <td>Abs: 0 / Ret: 0</td>
        </tr>
    </table>

    <div style="margin-top:10px; font-size:12px; border:1px solid black; padding:5px;">
        <b>Appréciation du Conseil de Classe:</b> {{ appreciation }}
    </div>

    <div class="signature">
        <div style="width:45%;"><b>Observations:</b><br><br><br>_________________________</div>
        <div style="width:45%; text-align:center;"><b>Le Chef d'Etablissement</b><br><br><div class="tampon">CACHET<br>OFFICIEL</div></div>
    </div>
    <button onclick="window.print()" class="btn">IMPRIMER LE BULLETIN 🖨️</button>
</div>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ia = request.form.get("ia"); ief = request.form.get("ief"); etablissement = request.form.get("etablissement")
        annee = request.form.get("annee"); periode = request.form.get("periode")
        nom = request.form.get("nom"); prenom = request.form.get("prenom")
        naissance = request.form.get("naissance"); lieu = request.form.get("lieu")
        classe = request.form.get("classe"); matricule = request.form.get("matricule")

        matieres_calculees = []
        total_points = 0; total_coeff = 0

        for i in range(20):
            matiere = request.form.get(f"matiere{i}")
            d1 = request.form.get(f"devoir1_{i}")
            d2 = request.form.get(f"devoir2_{i}")
            comp = request.form.get(f"comp{i}")
            coeff = request.form.get(f"coeff{i}")
            if matiere and coeff:
                coeff = float(coeff) if coeff else 1
                d1 = float(d1) if d1 else 0
                d2 = float(d2) if d2 else 0
                comp = float(comp) if comp else 0
                moy = round((d1 + d2 + comp*2)/4, 2)
                total = round(moy * coeff, 2)
                total_points += total; total_coeff += coeff

                app_mat = get_appreciation_matiere(moy)

                matieres_calculees.append({"nom":matiere, "d1":d1, "d2":d2, "comp":comp, "moy":moy, "coef":coeff, "total":total, "app_mat":app_mat})

        moyenne = round(total_points/total_coeff, 2) if total_coeff > 0 else 0
        total_possible = round(total_coeff * 20, 2)
        appreciation = get_appreciation_generale(moyenne)

        return render_template_string(HTML, bulletin=True, ia=ia, ief=ief, etablissement=etablissement, annee=annee, periode=periode,
                                      nom=nom, prenom=prenom, naissance=naissance, lieu=lieu, classe=classe,
                                      matricule=matricule, appreciation=appreciation,
                                      matieres_calculees=matieres_calculees, total_coeff=total_coeff,
                                      total_points=round(total_points,2), total_possible=total_possible, moyenne=moyenne,
                                      classes=CLASSES, ia_list=IA_LIST, ief_list=IEF_LIST, periodes=PERIODES, matieres_json=MATIERES, enumerate=enumerate)

    return render_template_string(HTML, bulletin=False, classes=CLASSES, ia_list=IA_LIST, ief_list=IEF_LIST,
                                  periodes=PERIODES, matieres_json=MATIERES)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
