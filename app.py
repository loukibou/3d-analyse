from flask import Flask, request, jsonify
import cadquery as cq
import tempfile, os, requests
import boto3

# ← Modifie ici uniquement si tu changes de région/endpoint Wasabi
S3_ENDPOINT   = "https://s3.ca-central-1.wasabisys.com"
S3_REGION     = "ca-central-1"
S3_BUCKET     = "bardou-prod"       # ← Ton bucket Wasabi
S3_KEY_PREFIX = "cleaned/"

# Lecture des clés dans les variables d'env. Railway
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
    try:
        data = request.get_json()
        url  = data.get("url")
        if not url:
            return jsonify({"error": "URL manquante"}), 400

        # 1) Télécharger le STEP
        resp = requests.get(url)
        resp.raise_for_status()
        tmp_in = tempfile.NamedTemporaryFile(suffix=".step", delete=False)
        tmp_in.write(resp.content)
        tmp_in.flush()

        # 2) Import & extraction des solides
        assembly    = cq.importers.importStep(tmp_in.name)
        solids      = assembly.solids().vals()
        nombre_de_pieces = len(solids)

        # 3) Bounding box globale
        bb = assembly.val().BoundingBox()
        boite_englobante_x = bb.xlen
        boite_englobante_y = bb.ylen
        boite_englobante_z = bb.zlen

        # 4) Volumes et surfaces pièce‐par‐pièce
        volumes  = [s.Volume() for s in solids]
        surfaces = [s.Area()   for s in solids]

        # Totaux
        volume_total  = sum(volumes)
        surface_total = sum(surfaces)

        # 5) Répartition par matériau
        materials = {}
        for s in solids:
            # Exemple d'extraction de nom de matériau ; à adapter selon ton STEP
            mat = getattr(s, 'material', None) or 'Inconnu'
            if mat not in materials:
                materials[mat] = { 'volume': 0.0, 'surface': 0.0 }
            materials[mat]['volume']  += s.Volume()
            materials[mat]['surface'] += s.Area()
        repartition = []
        for mat, vals in materials.items():
            repartition.append({
                'nom': mat,
                'volume': vals['volume'],
                'surface': vals['surface'],
                'pourc_volume': 100 * vals['volume']  / (volume_total or 1),
                'pourc_surface':100 * vals['surface'] / (surface_total or 1)
            })

        # 6) Réexport STEP anonymisé et upload
        tmp_out = tempfile.NamedTemporaryFile(suffix=".step", delete=False)
        cq.exporters.export(assembly, tmp_out.name)
        key = S3_KEY_PREFIX + os.path.basename(tmp_out.name)
        s3.upload_file(tmp_out.name, S3_BUCKET, key, ExtraArgs={"ACL": "public-read"})
        url_nettoye = f"{S3_ENDPOINT}/{S3_BUCKET}/{key}"

        # 7) Réponse JSON en clefs françaises (snake_case)
        return jsonify({
            'nombre_de_pieces':     nombre_de_pieces,
            'boite_englobante_x':   boite_englobante_x,
            'boite_englobante_y':   boite_englobante_y,
            'boite_englobante_z':   boite_englobante_z,
            'volumes':              volumes,
            'surfaces':             surfaces,
            'volume_total':         volume_total,
            'surface_total':        surface_total,
            'repartition_materiaux':repartition,
            'url_fichier_nettoye':  url_nettoye
        })

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)



