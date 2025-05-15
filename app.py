# app.py - Service d'analyse STEP
from flask import Flask, request, jsonify
import tempfile, os, requests, boto3, traceback
from urllib.parse import urlparse, unquote

# pythonOCC imports utilisant le namespace OCC.Core
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.BRepGProp import brepgprop_VolumeProperties, brepgprop_SurfaceProperties
from OCC.Core.GProp import GProp_GProps

app = Flask(__name__)

# Paramètres Wasabi
S3_ENDPOINT   = "https://s3.ca-central-1.wasabisys.com"
S3_REGION     = "ca-central-1"
S3_BUCKET     = "bardou-prod"
S3_KEY_PREFIX = "cleaned/"

# Initialisation du client S3
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=S3_REGION,
    aws_access_key_id=os.getenv("WASABI_KEY"),
    aws_secret_access_key=os.getenv("WASABI_SECRET")
)

def parse_step_caf(path):
    """Lit un STEP avec labels et extrait nom, volume, surface, matériau."""
    # On retire .GetObject() — GetApplication() renvoie déjà l’instance
    app_xde = XCAFApp_Application.GetApplication()
    doc     = TDocStd_Document()
    app_xde.NewDocument("MDTV-Standard", doc)
    tool = XCAFDoc_DocumentTool(doc.Main())

    reader = STEPCAFControl_Reader()
    reader.ReadFile(path)
    reader.Transfer(doc)

    pieces = []
    free = tool.GetFreeShapes()
    for i in range(1, free.Extent() + 1):
        lbl   = free.Value(i)
        name  = tool.GetLabel(lbl).GetText() or f"Pièce_{i}"
        shape = tool.GetShape(lbl)

        # Propriétés géométriques
        vp = GProp_GProps()
        brepgprop_VolumeProperties(shape, vp)
        vol = vp.Mass()

        sp = GProp_GProps()
        brepgprop_SurfaceProperties(shape, sp)
        surf = sp.Mass()

        # Matériau (par défaut inconnu)
        materiau = "Inconnu"
        if hasattr(tool, "GetMaterial"):
            try:
                materiau = tool.GetMaterial(lbl)
            except:
                pass

        pieces.append({
            "nom":      name,
            "materiau": materiau,
            "volume":   vol,
            "surface":  surf
        })
    return pieces

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        url  = data.get("url")
        if not url:
            return jsonify({"error": "URL manquante"}), 400

        # 1) Télécharger le STEP
        resp = requests.get(url)
        resp.raise_for_status()

        # 2) Extraire l’extension proprement (sans query string)
        parsed = urlparse(url)
        path   = unquote(parsed.path)
        ext    = os.path.splitext(path)[1].lower() or ".step"
        if ext not in {".step", ".stp", ".stp2", ".stepz"}:
            ext = ".step"

        # 3) Sauvegarder en fichier temporaire
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.content)
        tmp.flush()

        # 4) Parser et extraire les pièces
        pieces = parse_step_caf(tmp.name)
        nombre_de_pieces = len(pieces)

        # 5) Calcul des totaux
        volume_total  = sum(p["volume"]  for p in pieces)
        surface_total = sum(p["surface"] for p in pieces)

        # 6) Répartition par matériau
        repart = {}
        for p in pieces:
            mat = p["materiau"]
            repart.setdefault(mat, {"volume": 0.0, "surface": 0.0})
            repart[mat]["volume"]  += p["volume"]
            repart[mat]["surface"] += p["surface"]
        repartition = []
        for mat, vals in repart.items():
            repartition.append({
                "nom":           mat,
                "volume":        vals["volume"],
                "surface":       vals["surface"],
                "pourc_volume":  100 * vals["volume"]  / (volume_total or 1),
                "pourc_surface": 100 * vals["surface"] / (surface_total or 1)
            })

        # 7) Copier & uploader l’original anonymisé
        tmp_out = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        with open(tmp.name, "rb") as src, open(tmp_out.name, "wb") as dst:
            dst.write(src.read())
        key = S3_KEY_PREFIX + os.path.basename(tmp_out.name)
        s3.upload_file(tmp_out.name, S3_BUCKET, key, ExtraArgs={"ACL": "public-read"})
        url_nettoye = f"{S3_ENDPOINT}/{S3_BUCKET}/{key}"

        # 8) Retour JSON
        return jsonify({
            "nombre_de_pieces":      nombre_de_pieces,
            "volume_total":          volume_total,
            "surface_total":         surface_total,
            "repartition_materiaux": repartition,
            "liste_pieces":          pieces,
            "url_fichier_nettoye":   url_nettoye
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

