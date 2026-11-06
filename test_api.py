"""
Suite de testes automatizados para a API do IDVerde.
Testa todos os endpoints (/health, /species, /predict) com multipart/form-data e base64.
"""

import io
import base64
import unittest
from PIL import Image
from app import app


class TestIDVerdeAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def gerar_imagem_teste_bytes(self, color=(100, 180, 80)):
        """Cria uma imagem de teste sintética em memória."""
        img = Image.new("RGB", (200, 200), color=color)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return buf

    def test_health_endpoint(self):
        """Verifica se o endpoint /health responde 200 e confirma o modelo carregado."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])
        self.assertEqual(len(data["supported_classes"]), 5)

    def test_species_endpoint(self):
        """Verifica se o catálogo de espécies retorna as 5 classes com metadados."""
        response = self.client.get("/species")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["total"], 5)
        ids = [item["id"] for item in data["species"]]
        self.assertIn("african_violet", ids)
        self.assertIn("aloe_vera", ids)
        self.assertIn("anthurium", ids)
        self.assertIn("areca_palm", ids)
        self.assertIn("asparagus_fern", ids)

    def test_predict_multipart_real_image(self):
        """Testa o endpoint /predict com uma imagem real do dataset."""
        with open("Plantas/African Violet/1.jpg", "rb") as f:
            img_bytes = io.BytesIO(f.read())

        response = self.client.post(
            "/predict",
            data={"image": (img_bytes, "african_violet.jpg")},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("topk", data)
        self.assertEqual(len(data["topk"]), 3)
        self.assertEqual(data["topk"][0]["nome"], "African Violet")
        self.assertGreater(data["topk"][0]["score"], 0.5)

    def test_predict_base64(self):
        """Testa o endpoint /predict com imagem codificada em Base64."""
        with open("Plantas/Aloe Vera/1.jpg", "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        response = self.client.post(
            "/predict",
            json={"image": f"data:image/jpeg;base64,{b64}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("topk", data)
        self.assertEqual(len(data["topk"]), 3)

    def test_predict_sem_imagem(self):
        """Testa validação de requisição sem arquivo de imagem."""
        response = self.client.post("/predict", data={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])

    def test_predict_arquivo_invalido(self):
        """Testa envio de arquivo corrompido ou texto como imagem."""
        fake_file = io.BytesIO(b"isto nao e uma imagem")
        response = self.client.post(
            "/predict",
            data={"image": (fake_file, "fake.jpg")},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])


if __name__ == "__main__":
    unittest.main()

