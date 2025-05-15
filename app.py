from flask import Flask, request, jsonify
import tempfile, os, requests, boto3, traceback

# FreeCAD headless
import FreeCAD
import ImportGui  # permet d'importer le STEP en mémoire

app = Flask(__name__)

# ← Modifiez si besoin
S3_ENDPOINT   = "https://s3.ca-central-1.wasabisys.com"
S3_REGION     = "ca-central-1"
S3_BUCKET     = "bardou-prod"
S3_KEY_PREFIX = "cleaned/"

# Init client Wasabi (S3‑compatible)
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=S3_REGION,
    aws_access_key_id=os.getenv("WASABI_KEY"),
    aws_secret_access_key=os.getenv("WASABI_SECRET"),
)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        url  = data.get("url")
        if not url:
            return jsonify({"error": "URL manquante"}), 400

        # 1) Télécharger le STEP
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        suffix = os.path.splitext(url)[1] or ".step"
        tmp_in = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp_in.write(resp.content)
        tmp_in.flush()

        # 2) Créer un document FreeCAD headless et y importer le STEP
        doc = FreeCAD.newDocument("TmpDoc")
        ImportGui.insert(tmp_in.name, doc.Name)

        # 3) Parcourir chaque objet (pièce)
        pieces = []
        for obj in doc.Objects:
            # Nom (objet FreeCAD a un attribut Name ou Label)
            nom = getattr(obj, "Label", obj.Name)

            # Forme
            shp = obj.Shape

            # Volume & surface
            vol  = shp.Volume
            surf = shp.Area

            # Matériau (si défini dans obj.Material ou dans obj.ViewObject)
            mat = None
            if hasattr(obj, "Material") and obj.Material:
                mat = obj.Material
            else:
                # fallback : on cherche un champ ViewObject.Material
                mat = getattr(obj.ViewObject, "Material", None)
            mat = mat or "Inconnu"

            pieces.append({
                "nom":      nom,
                "materiau": mat,
                "volume":   vol,
                "surface":  surf
            })

        # 4) Totaux et répartition matériaux
        n_pieces    = len(pieces)
        vol_total   = sum(p["volume"]  for p in pieces)
        surf_total  = sum(p["surface"] for p in pieces)

        repart = {}
        for p in pieces:
            m = p["materiau"]
            repart.setdefault(m, {"volume": 0.0, "surface": 0.0})
            repart[m]["volume"]  += p["volume"]
            repart[m]["surface"] += p["surface"]

        repartition = [
            {
                "materiau":       m,
                "volume":         vals["volume"],
                "surface":        vals["surface"],
                "pourc_volume":   100 * vals["volume"]  / (vol_total  or 1),
                "pourc_surface":  100 * vals["surface"] / (surf_total or 1),
            }
            for m, vals in repart.items()
        ]

        # 5) “Anonymiser” / renvoyer le même STEP sur Wasabi
        tmp_out = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        with open(tmp_in.name, "rb") as src, open(tmp_out.name, "wb") as dst:
            dst.write(src.read())
        key = S3_KEY_PREFIX + os.path.basename(tmp_out.name)
        s3.upload_file(tmp_out.name, S3_BUCKET, key, ExtraArgs={"ACL": "public-read"})
        url_clean = f"{S3_ENDPOINT}/{S3_BUCKET}/{key}"

        # 6) Réponse finale
        return jsonify({
            "nombre_de_pieces":       n_pieces,
            "volume_total":           vol_total,
            "surface_total":          surf_total,
            "repartition_materiaux":  repartition,
            "liste_pieces":           pieces,
            "url_fichier_nettoye":    url_clean
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

