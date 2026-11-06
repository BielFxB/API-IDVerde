# 🌿 IDVerde - API de Reconhecimento de Espécies Vegetais por IA

API REST desenvolvida em Python (Flask) para classificação automatizada de espécies vegetais a partir de fotos tiradas por usuários, permitindo a comunicação em tempo real com o aplicativo mobile do projeto **IDVerde**.

---

## 📖 Sobre o Projeto

O **IDVerde** é uma iniciativa que aproxima o conhecimento botânico e a conservação da biodiversidade da comunidade externa (escolas públicas de Dourados, moradores locais e comunidade universitária).

O módulo de Machine Learning processa fotografias enviadas pelo aplicativo mobile e identifica as espécies com seus respectivos índices de probabilidade e guias de cuidados.

---

## 🧠 Arquitetura de Inteligência Artificial

- **Pipeline:** `StandardScaler` + `Support Vector Machine (SVM)` com kernel RBF (`C=1.0`, `gamma='scale'`, `probability=True`).
- **Pré-processamento:** Imagens normalizadas para resolução de $200 \times 200$ pixels em 3 canais (RGB), gerando vetores com **120.000 features**.
- **Desempenho avaliado:**
  - K-Nearest Neighbors (KNN): 47% de acurácia
  - Random Forest: 67% de acurácia
  - **SVM (Modelo Escolhido): 73% de acurácia**
- **Tempo médio de inferência:** ~60 a 150 ms por imagem.

---

## 🌸 Espécies Catalogadas

O modelo atual foi treinado e valida 5 espécies botânicas:

| ID | Nome em Inglês | Nome Popular (PT-BR) | Nome Científico | Família |
| :--- | :--- | :--- | :--- | :--- |
| `african_violet` | African Violet | Violeta-africana | *Saintpaulia ionantha* | Gesneriaceae |
| `aloe_vera` | Aloe Vera | Babosa | *Aloe barbadensis miller* | Asphodelaceae |
| `anthurium` | Anthurium | Antúrio | *Anthurium andreanum* | Araceae |
| `areca_palm` | Areca Palm | Palmeira-areca / Areca-bambu | *Dypsis lutescens* | Arecaceae |
| `asparagus_fern` | Asparagus Fern | Aspargo-samambaia / Melindre | *Asparagus setaceus* | Asparagaceae |

---

## 📑 Documentação dos Endpoints

### 1. `GET /health` (ou `/api/v1/health`)
Verifica se o servidor está ativo e se o modelo de IA foi carregado na memória.

**Resposta de Exemplo (HTTP 200):**
```json
{
  "api_name": "IDVerde Plant Classification API",
  "model_loaded": true,
  "model_version": "svm-v1",
  "status": "healthy",
  "supported_classes": [
    "African Violet",
    "Aloe Vera",
    "Anthurium",
    "Areca Palm",
    "Asparagus Fern"
  ]
}
```

---

### 2. `GET /species` (ou `/api/v1/species`)
Retorna os detalhes botânicos completos e instruções de cultivo das espécies suportadas.

**Resposta de Exemplo (HTTP 200):**
```json
{
  "total": 5,
  "species": [
    {
      "id": "african_violet",
      "nome": "African Violet",
      "nome_popular": "Violeta-africana",
      "nome_cientifico": "Saintpaulia ionantha",
      "familia": "Gesneriaceae",
      "origem": "Tanzânia e leste da África",
      "descricao": "Planta herbácea perene de pequeno porte...",
      "cuidados": {
        "luz": "Luz indireta brilhante (evitar sol direto)",
        "rega": "Moderada; regar pelo prato inferior sem molhar as folhas",
        "temperatura": "18°C a 24°C"
      }
    }
  ]
}
```

---

### 3. `POST /predict` (ou `/api/v1/predict`)
Classifica a foto de uma planta enviada pelo app mobile.

#### Opção A: Via `multipart/form-data` (Recomendado para Mobile)
- **Header:** `Content-Type: multipart/form-data`
- **Campo:** `image` (arquivo de imagem JPG, PNG, WEBP)

#### Opção B: Via `application/json` (Base64)
- **Header:** `Content-Type: application/json`
- **Body:**
  ```json
  {
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
  ```

#### Resposta de Sucesso (HTTP 200):
```json
{
  "success": true,
  "image_id": "img_a1b2c3d4",
  "topk": [
    {
      "id": "african_violet",
      "nome": "African Violet",
      "nome_popular": "Violeta-africana",
      "nome_cientifico": "Saintpaulia ionantha",
      "score": 0.7782,
      "porcentagem": "77.8%",
      "familia": "Gesneriaceae",
      "cuidados": {
        "luz": "Luz indireta brilhante (evitar sol direto)",
        "rega": "Moderada; regar pelo prato inferior sem molhar as folhas",
        "temperatura": "18°C a 24°C"
      }
    },
    {
      "id": "aloe_vera",
      "nome": "Aloe Vera",
      "nome_popular": "Babosa",
      "nome_cientifico": "Aloe barbadensis miller",
      "score": 0.0755,
      "porcentagem": "7.6%",
      "familia": "Asphodelaceae",
      "cuidados": { ... }
    },
    {
      "id": "anthurium",
      "nome": "Anthurium",
      "nome_popular": "Antúrio",
      "nome_cientifico": "Anthurium andreanum",
      "score": 0.0724,
      "porcentagem": "7.2%",
      "familia": "Araceae",
      "cuidados": { ... }
    }
  ],
  "melhor_predicao": {
    "id": "african_violet",
    "nome": "African Violet",
    "nome_popular": "Violeta-africana",
    "nome_cientifico": "Saintpaulia ionantha",
    "score": 0.7782,
    "porcentagem": "77.8%",
    "familia": "Gesneriaceae"
  },
  "model_version": "svm-v1",
  "latency_ms": 118,
  "inference_ms": 52
}
```

---

## 📲 Tutorial de Conexão da API

### Endereço da API (Base URL)

Para integrar o aplicativo mobile com a API, utilize a URL:

```
https://apiidverde.gamycoins.com.br
```

---

### Exemplo em Flutter (Dart)

Adicione as dependências no `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.2.0
  image_picker: ^1.0.7
```

Arquivo de serviço para o app (`idverde_service.dart`):
```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class IDVerdeService {
  static const String baseUrl = 'https://apiidverde.gamycoins.com.br';

  static Future<Map<String, dynamic>> identificarPlanta(File imageFile) async {
    final uri = Uri.parse('$baseUrl/predict');
    final request = http.MultipartRequest('POST', uri);

    // Anexa a imagem no campo 'image'
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      // Decodifica com UTF-8 para preservar acentuação dos nomes populares
      return jsonDecode(utf8.decode(response.bodyBytes));
    } else {
      final error = jsonDecode(utf8.decode(response.bodyBytes));
      throw Exception(error['error'] ?? 'Erro ao classificar planta');
    }
  }
}
```

Como chamar na tela do Flutter:
```dart
try {
  final resultado = await IDVerdeService.identificarPlanta(minhaFoto);
  final melhor = resultado['melhor_predicao'];
  print('Espécie detectada: ${melhor['nome_popular']} (${melhor['porcentagem']})');
} catch (e) {
  print('Erro: $e');
}
```

*(O código completo com classes de modelo tipadas está disponível em [`exemplos_mobile/flutter_idverde.dart`](exemplos_mobile/flutter_idverde.dart)).*

---

### Exemplo em React Native

```javascript
const BASE_URL = 'https://apiidverde.gamycoins.com.br';

export async function identificarPlanta(imageUri) {
  const formData = new FormData();
  
  formData.append('image', {
    uri: imageUri,
    name: 'planta.jpg',
    type: 'image/jpeg',
  });

  const response = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    body: formData,
    headers: {
      'Accept': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Erro na requisição');
  }
  return data;
}
```


