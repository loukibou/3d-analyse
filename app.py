from flask import Flask, request, jsonify
import tempfile, os, requests, boto3, traceback

# OCP / XCAF pour récupérer labels STEP
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.BRepGProp import brepgprop_VolumeProperties, brepgprop_SurfaceProperties
from OCP.GProp import GProp_GProps

app = Flask(__name__)

# ← Paramètres Wasabi
S3_ENDPOINT   = "https://s3.ca-central-1.wasabisys.com"
S3_REGION     = "ca-central-1"
S3_BUCKET     = "bardou-prod"
S3_KEY_PREFIX = "cleaned/"

# client S3
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=S3_REGION,
    aws_access_key_id=os.getenv("WASABI_KEY"),
    aws_secret_access_key=os.getenv("WASABI_SECRET")
)

def parse_step_with_labels(path):
    """Retourne une liste de dict {name, volume, surface, bbox} pour chaque pièce du STEP."""
    # 1) Crée le document XDE
    app_xde = XCAFApp_Application.GetApplication().GetObject()
    doc     = TDocStd_Document()
    app_xde.NewDocument("MDTV-Standard", doc)
    shape_tool = XCAFDoc_DocumentTool(doc.Main())

    # 2) Lecture STEPCAF (labels + géométrie)
    reader = STEPCAFControl_Reader()
    reader.ReadFile(path)
    reader.Transfer(doc)

    # 3) Parcours des FreeShapes (chaque sous-ensemble/pièce)
    result = []
    free_shapes = shape_tool.GetFreeShapes()
    for idx in range(1, free_shapes.Extent()+1):
        lbl   = free_shapes.Value(idx)
        name  = shape_tool.GetLabel(lbl).GetText()  # Nom du label
        shape = shape_tool.GetShape(lbl)

        # Volume
        gv = GProp_GProps(); brepgprop_VolumeProperties(shape, gv)
        vol = gv.Mass()
        # Surface
        gs = GProp_GProps(); brepgprop_SurfaceProperties(shape, gs)
        surf = gs.Mass()

        # Bounding box via GProp ou CadQuery si tu préfères
        # (ici on skip bbox par simplicité)

        result.append({
            "name":    name,
            "volume":  vol,
            "surface": surf,
        })
    return result

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        url  = data.get("url")
        if not url:
            return jsonify({"error": "URL manquante"}), 400

        # DL STEP
        resp = requests.get(url); resp.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(suffix=".step", delete=False)
        tmp.write(resp.content); tmp.flush()

        # Extraction pièce par pièce
        pieces = parse_step_with_labels(tmp.name)

        # Upload anonymisé
        key = S3_KEY_PREFIX + os.path.basename(tmp.name)
        s3.upload_file(tmp.name, S3_BUCKET, key, ExtraArgs={"ACL": "public-read"})
        cleaned_url = f"{S3_ENDPOINT}/{S3_BUCKET}/{key}"

        return jsonify({
            "assembly": {
                "piece_count": len(pieces)
            },
            "pieces":       pieces,
            "cleaned_file_url": cleaned_url
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run("0.0.0.0", port=port)


