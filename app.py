"""
API REST do Projeto IDVerde (UFGD)
Classificação botânica de espécies vegetais utilizando Machine Learning (SVM).
Permite integração direta com aplicativos móveis (Flutter, React Native, Android/iOS nativo).
"""

import os
import io
import time
import uuid
import base64
import logging
from typing import Tuple, Optional

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from PIL import Image, UnidentifiedImageError
import numpy as np
import joblib
import pickle

from species_data import SPECIES_METADATA, obter_info_especie, normalizar_id

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger("IDVerdeAPI")

# Inicialização da aplicação Flask
app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem (essencial para mobile/web)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Limite máximo de 16MB por imagem
app.config["JSON_AS_ASCII"] = False

# Configurações do modelo
MODEL_VERSION = "svm-v1"
IMAGE_SIZE = 200
MODEL_CANDIDATES = ["modelo_svm.joblib", "modelo_svm.pkl"]

MODELO = None


def carregar_modelo():
    """Carrega o modelo treinado na inicialização do servidor."""
    global MODELO
    if MODELO is not None:
        return MODELO

    caminho_escolhido = None
    for caminho in MODEL_CANDIDATES:
        if os.path.exists(caminho):
            caminho_escolhido = caminho
            break

    if not caminho_escolhido:
        logger.error("Nenhum arquivo de modelo encontrado! Verifique se modelo_svm.joblib ou modelo_svm.pkl existe.")
        return None

    try:
        logger.info(f"Carregando modelo de '{caminho_escolhido}'...")
        inicio = time.time()
        if caminho_escolhido.endswith(".joblib"):
            MODELO = joblib.load(caminho_escolhido)
        else:
            with open(caminho_escolhido, "rb") as f:
                MODELO = pickle.load(f)
        tempo = time.time() - inicio
        logger.info(f"Modelo carregado com sucesso em {tempo:.2f}s! Classes: {MODELO.classes_}")
        return MODELO
    except Exception as e:
        logger.exception(f"Falha ao carregar o modelo de '{caminho_escolhido}': {e}")
        return None


# Carrega o modelo assim que o arquivo é importado
carregar_modelo()


def processar_imagem_bytes(imagem_bytes: bytes) -> np.ndarray:
    """
    Pré-processa a imagem recebida em bytes para o formato esperado pelo modelo:
    - Conversão para RGB
    - Redimensionamento para (200, 200)
    - Vetorização 1D (200 * 200 * 3 = 120.000 features float32)
    """
    with Image.open(io.BytesIO(imagem_bytes)) as img:
        img = img.convert("RGB")
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE))
        arr = np.array(img)
        # Formato (1, 120000) idêntico ao preparar_X() utilizado no treino
        X = arr.reshape(1, -1).astype(np.float32)
        return X


def extrair_bytes_requisicao() -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    Extrai os bytes da imagem da requisição HTTP, suportando:
    1. multipart/form-data: campo 'image', 'file' ou 'foto'
    2. application/json: campo 'image' ou 'image_base64' (com ou sem prefixo data:image/...)
    3. raw binary: Content-Type image/*
    """
    # 1. multipart/form-data
    if request.files:
        for campo in ["image", "file", "foto", "imagem"]:
            if campo in request.files:
                arquivo = request.files[campo]
                if arquivo.filename != "":
                    return arquivo.read(), arquivo.filename, None
        # Se veio algum arquivo com nome de campo diferente:
        primeiro_campo = next(iter(request.files))
        arquivo = request.files[primeiro_campo]
        if arquivo.filename != "":
            return arquivo.read(), arquivo.filename, None

    # 2. application/json (Base64)
    if request.is_json:
        dados = request.get_json(silent=True) or {}
        base64_str = (
            dados.get("image")
            or dados.get("image_base64")
            or dados.get("foto")
            or dados.get("imagem")
        )
        if base64_str:
            # Remove data URI header se presente (ex: 'data:image/jpeg;base64,...')
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]
            try:
                img_bytes = base64.b64decode(base64_str)
                return img_bytes, "base64_upload.jpg", None
            except Exception as e:
                return None, None, f"String base64 inválida: {str(e)}"

    # 3. Raw binary
    content_type = request.headers.get("Content-Type", "")
    if content_type.startswith("image/"):
        dados_raw = request.get_data()
        if dados_raw:
            return dados_raw, "raw_upload.jpg", None

    return None, None, (
        "Nenhuma imagem enviada. Envie um arquivo via multipart/form-data no campo 'image' "
        "ou um JSON com 'image' contendo a imagem em Base64."
    )


# ---------------------------------------------------------
# ROTAS DA API
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    """Página inicial com testador web interativo e documentação rápida."""
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API IDVerde - Reconhecimento de Espécies</title>
        <style>
            :root {
                --primary: #2e7d32;
                --primary-dark: #1b5e20;
                --bg: #f4f6f8;
                --card-bg: #ffffff;
                --text: #2c3e50;
                --border: #e0e0e0;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
            body { background: var(--bg); color: var(--text); padding: 20px; line-height: 1.6; }
            .container { max-width: 900px; margin: 0 auto; }
            header { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; padding: 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            header h1 { font-size: 1.8rem; margin-bottom: 8px; }
            header p { opacity: 0.9; font-size: 0.95rem; }
            .badge { display: inline-block; background: rgba(255,255,255,0.25); padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-top: 10px; }
            .card { background: var(--card-bg); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
            h2 { color: var(--primary-dark); font-size: 1.3rem; margin-bottom: 15px; border-bottom: 2px solid #e8f5e9; padding-bottom: 8px; }
            .dropzone { border: 2px dashed #81c784; border-radius: 8px; padding: 30px; text-align: center; cursor: pointer; transition: 0.2s; background: #f9fbf9; }
            .dropzone:hover { background: #e8f5e9; border-color: var(--primary); }
            .dropzone input { display: none; }
            .btn { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-top: 10px; }
            .btn:hover { background: var(--primary-dark); }
            #preview { max-width: 200px; max-height: 200px; border-radius: 8px; margin: 15px auto; display: none; object-fit: cover; }
            .result-bar { margin: 10px 0; }
            .bar-label { display: flex; justify-content: space-between; font-weight: 600; font-size: 0.9rem; margin-bottom: 4px; }
            .bar-bg { background: #e0e0e0; height: 16px; border-radius: 8px; overflow: hidden; }
            .bar-fill { background: var(--primary); height: 100%; width: 0%; transition: width 0.4s ease; }
            pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 0.85rem; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem; }
            th, td { padding: 10px; border-bottom: 1px solid var(--border); text-align: left; }
            th { background: #f8f9fa; }
            .code-tag { background: #e8f5e9; color: var(--primary-dark); padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.85rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🌿 API IDVerde - Reconhecimento Botânico</h1>
                <p>Módulo de Inteligência Artificial para classificação de espécies vegetais da UFGD.</p>
                <span class="badge">Versão: svm-v1</span>
                <span class="badge">Status: Operacional</span>
            </header>

            <div class="card">
                <h2>🧪 Testador Rápido (Upload de Imagem)</h2>
                <p style="margin-bottom: 15px; font-size: 0.9rem; color: #666;">
                    Envie uma foto de uma das 5 espécies (African Violet, Aloe Vera, Anthurium, Areca Palm, Asparagus Fern) para testar a classificação em tempo real:
                </p>
                <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" accept="image/*">
                    <p>📸 Clique ou arraste uma foto aqui</p>
                    <img id="preview" alt="Preview da imagem">
                </div>
                <div style="text-align: center;">
                    <button class="btn" id="uploadBtn" style="display:none;" onclick="enviarImagem()">Identificar Espécie</button>
                </div>
                <div id="loading" style="display:none; text-align:center; margin: 15px; font-weight:600; color:var(--primary);">
                    Analisando imagem com SVM...
                </div>
                <div id="results" style="margin-top: 20px; display:none;">
                    <h3>Classificações Mais Prováveis (Top 3):</h3>
                    <div id="bars"></div>
                    <div style="margin-top: 15px;">
                        <h4 style="margin-bottom: 6px; font-size: 0.9rem;">Resposta JSON enviada ao App Mobile:</h4>
                        <pre id="jsonOutput"></pre>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>📑 Endpoints Disponíveis para o App Mobile</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Método</th>
                            <th>Endpoint</th>
                            <th>Descrição</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="code-tag">POST</span></td>
                            <td><span class="code-tag">/predict</span> ou <span class="code-tag">/api/v1/predict</span></td>
                            <td>Classifica uma imagem enviada via <tt>multipart/form-data</tt> (campo <tt>image</tt>) ou JSON em Base64. Retorna top 3 predições com scores.</td>
                        </tr>
                        <tr>
                            <td><span class="code-tag">GET</span></td>
                            <td><span class="code-tag">/species</span> ou <span class="code-tag">/api/v1/species</span></td>
                            <td>Retorna o catálogo completo das espécies com nomes populares, científicos e guia de cuidados.</td>
                        </tr>
                        <tr>
                            <td><span class="code-tag">GET</span></td>
                            <td><span class="code-tag">/health</span> ou <span class="code-tag">/api/v1/health</span></td>
                            <td>Health check da API e status de carregamento do modelo.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            const fileInput = document.getElementById('fileInput');
            const preview = document.getElementById('preview');
            const uploadBtn = document.getElementById('uploadBtn');

            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(evt) {
                        preview.src = evt.target.result;
                        preview.style.display = 'block';
                        uploadBtn.style.display = 'inline-block';
                    }
                    reader.readAsDataURL(file);
                }
            });

            async function enviarImagem() {
                const file = fileInput.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('image', file);

                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';

                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('results').style.display = 'block';
                    document.getElementById('jsonOutput').textContent = JSON.stringify(data, null, 2);

                    const barsContainer = document.getElementById('bars');
                    barsContainer.innerHTML = '';

                    if (data.success && data.topk) {
                        data.topk.forEach((item, idx) => {
                            const pct = Math.round(item.score * 100);
                            const div = document.createElement('div');
                            div.className = 'result-bar';
                            div.innerHTML = `
                                <div class="bar-label">
                                    <span>${idx + 1}º ${item.nome_popular || item.nome} <i>(${item.nome_cientifico || ''})</i></span>
                                    <span>${pct}%</span>
                                </div>
                                <div class="bar-bg">
                                    <div class="bar-fill" style="width: ${pct}%"></div>
                                </div>
                            `;
                            barsContainer.appendChild(div);
                        });
                    }
                } catch (err) {
                    document.getElementById('loading').style.display = 'none';
                    alert('Erro ao comunicar com a API: ' + err.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/health", methods=["GET"])
@app.route("/api/v1/health", methods=["GET"])
def health():
    """Endpoint de checagem de saúde da API."""
    modelo = carregar_modelo()
    return jsonify({
        "status": "healthy" if modelo is not None else "degraded",
        "api_name": "IDVerde Plant Classification API",
        "model_version": MODEL_VERSION,
        "model_loaded": modelo is not None,
        "supported_classes": list(modelo.classes_) if modelo is not None else list(SPECIES_METADATA.keys())
    }), 200 if modelo is not None else 503


@app.route("/species", methods=["GET"])
@app.route("/api/v1/species", methods=["GET"])
def listar_especies():
    """Retorna o catálogo botânico das espécies cadastradas."""
    return jsonify({
        "total": len(SPECIES_METADATA),
        "species": list(SPECIES_METADATA.values())
    }), 200


@app.route("/predict", methods=["POST"])
@app.route("/api/v1/predict", methods=["POST"])
def predict():
    """
    Classifica a imagem enviada pelo aplicativo mobile.
    Recebe imagem via multipart/form-data (campo 'image') ou application/json (Base64).
    Retorna o Top-3 de espécies mais prováveis com pontuação e metadados.
    """
    inicio_req = time.time()
    modelo = carregar_modelo()

    if modelo is None:
        return jsonify({
            "success": False,
            "error": "O modelo de IA ainda não foi carregado ou não foi encontrado no servidor."
        }), 503

    # Extrai os bytes da imagem da requisição
    img_bytes, filename, erro = extrair_bytes_requisicao()
    if erro or not img_bytes:
        return jsonify({
            "success": False,
            "error": erro or "Imagem não encontrada na requisição."
        }), 400

    # Pré-processamento
    try:
        X = processar_imagem_bytes(img_bytes)
    except UnidentifiedImageError:
        return jsonify({
            "success": False,
            "error": "Arquivo enviado não é uma imagem válida suportada (JPG, PNG, WEBP, BMP)."
        }), 400
    except Exception as e:
        logger.exception("Erro durante o pré-processamento da imagem")
        return jsonify({
            "success": False,
            "error": f"Falha no processamento da imagem: {str(e)}"
        }), 400

    # Predição com o modelo SVM
    try:
        t0_inferencia = time.time()
        probabilidades = modelo.predict_proba(X)[0]
        tempo_inferencia = time.time() - t0_inferencia

        classes = modelo.classes_
        # Quantidade de resultados solicitados (default: 3)
        top_k_param = request.args.get("top_k", default=3, type=int)
        top_k = max(1, min(len(classes), top_k_param))

        # Índices ordenados de forma decrescente por probabilidade
        top_indices = probabilidades.argsort()[-top_k:][::-1]

        topk_resultado = []
        for idx in top_indices:
            nome_classe = classes[idx]
            score = float(probabilidades[idx])
            info = obter_info_especie(nome_classe)

            topk_resultado.append({
                "id": info["id"],
                "nome": nome_classe,
                "nome_popular": info.get("nome_popular", nome_classe),
                "nome_cientifico": info.get("nome_cientifico", ""),
                "score": round(score, 4),
                "porcentagem": f"{round(score * 100, 1)}%",
                "familia": info.get("familia", ""),
                "cuidados": info.get("cuidados", {})
            })

        tempo_total_ms = round((time.time() - inicio_req) * 1000)
        image_id = f"img_{uuid.uuid4().hex[:8]}"

        resultado = {
            "success": true_or_bool(True),
            "image_id": image_id,
            "topk": topk_resultado,
            "melhor_predicao": topk_resultado[0] if topk_resultado else None,
            "model_version": MODEL_VERSION,
            "latency_ms": tempo_total_ms,
            "inference_ms": round(tempo_inferencia * 1000)
        }

        logger.info(f"Classificação realizada com sucesso [{image_id}]: {topk_resultado[0]['nome']} ({topk_resultado[0]['porcentagem']}) em {tempo_total_ms}ms")
        return jsonify(resultado), 200

    except Exception as e:
        logger.exception("Erro durante a inferência do modelo")
        return jsonify({
            "success": False,
            "error": f"Erro interno ao realizar classificação: {str(e)}"
        }), 500


def true_or_bool(val: bool) -> bool:
    return val


# ---------------------------------------------------------
# TRATAMENTO DE ERROS HTTP
# ---------------------------------------------------------

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error": "A imagem enviada excede o limite máximo permitido de 16MB."
    }), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint não encontrado. Consulte GET / para documentação das rotas."
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": "Erro interno do servidor."
    }), 500


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"\n🌱 Servidor IDVerde API rodando em http://localhost:{porta}\n")
    app.run(host=host, port=porta, debug=False)

