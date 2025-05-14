from flask import Flask, request, jsonify
import cadquery as cq
import tempfile, os, requests
import boto3

# ← Modifie ici uniquement si tu changes de région/endpoint Wasabi
S3_ENDPOINT   = "https://s3.ca-central-1.wasabisys.com"
S3_REGION     = "ca-central-1"
S3_BUCKET     = "bardou-prod"       # ← Ton bucket Wasabi
S3_KEY_PREFIX = "cleaned/"

# Les clés WASABI_KEY et WASABI_SECRET seront lues depuis
# les variables d'environnement de Railway.
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=S3_REGION,
    aws_access_key_id=os.getenv("WASABI_KEY"),
    aws_secret_access_key=os.getenv("WASABI_SECRET")
)

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    url  = data.get("url")
    if not url:
        return jsonify({"error": "URL manquante"}), 400

    # 1) Téléchargement du fichier STEP
    resp = requests.get(url)
    tmp_in = tempfile.NamedTemporaryFile(suffix=".step", delete=False)
    tmp_in.write(resp.content)
    tmp_in.flush()

    # 2) Analyse avec CadQuery
    assembly = cq.importers.importStep(tmp_in.name)
    solids   = assembly.solids().vals()
    piece_count = len(solids)
    bb = assembly.val().BoundingBox()
    dims = {"x": bb.xlen, "y": bb.ylen, "z": bb.zlen}
    volumes  = [s.Volume() for s in solids]
    surfaces = [s.Area()   for s in solids]

    # 3) Réexport pour anonymisation et upload
    tmp_out = tempfile.NamedTemporaryFile(suffix=".step", delete=False)
    cq.exporters.export(assembly, tmp_out.name)
    key = S3_KEY_PREFIX + os.path.basename(tmp_out.name)
    s3.upload_file(tmp_out.name, S3_BUCKET, key, ExtraArgs={"ACL": "public-read"})
    cleaned_url = f"{S3_ENDPOINT}/{S3_BUCKET}/{key}"

    # 4) Retour JSON
    return jsonify({
        "piece_count": piece_count,
        "bounding_box": dims,
        "volumes": volumes,
        "surfaces": surfaces,
        "cleaned_file_url": cleaned_url
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
