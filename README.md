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

Para integrar o aplicativo mobile com a API, utilize a URL oficial em produção:

```
https://apiidverde.gamycoins.com.br
```

> **Nota:** Como a API está rodando com HTTPS público via Cloudflare, ela funciona diretamente em qualquer dispositivo (Android, iOS ou emuladores), sem necessidade de configurações de rede local ou liberação de tráfego HTTP sem segurança (`cleartextTraffic`).

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

*(Arquivo pronto disponível em [`exemplos_mobile/react_native_idverde.js`](exemplos_mobile/react_native_idverde.js)).*

---

### Exemplo via cURL

Testando a classificação pelo terminal:
```bash
curl -X POST https://apiidverde.gamycoins.com.br/predict \
  -F "image=@Plantas/African Violet/1.jpg"
```

---

## 🖥️ Hospedagem no seu Servidor Local (Linux + PM2 + Cloudflare Tunnel)

Se você possui um servidor local (Linux, PM2 e Cloudflare Tunnel) como o ambiente do seu laboratório/máquina (`frdata@frdata:~`), esta é a melhor opção: custo zero, sem hibernação de plano gratuito e sob seu controle total.

### 📊 Análise de Recursos no seu Servidor
- **CPU:** Intel Core i5-2400 (4 núcleos / 4 threads) — A inferência do modelo SVM leva de 50ms a 150ms em uma única thread. O impacto de CPU é inferior a 1% em uso médio.
- **Memória RAM:** 8 GB — A API consome aproximadamente **180 MB a 250 MB de RAM** com o modelo carregado em memória. Não haverá nenhuma interferência com seus outros serviços (Next.js nas portas 3000-3002 e FastAPI nas portas 8000-8001).
- **Porta Escolhida:** Como as portas `3000`, `3001`, `3002`, `8000` e `8001` já estão em uso, configuramos a API por padrão para a **porta `5000`** (ou `8002`, configurável via variável de ambiente `PORT`).

---

### 🛠️ Passo a Passo no Terminal do Servidor (`frdata@frdata:~`)

#### 1. Clonar o projeto no servidor
```bash
cd ~
git clone https://github.com/SEU_USUARIO/API-IA-IDVerde.git
cd API-IA-IDVerde
```

#### 2. Criar e ativar o ambiente virtual Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Iniciar com o PM2 (Arquivo `ecosystem.config.js` já incluso!)
O projeto já inclui o arquivo `ecosystem.config.js` pré-configurado com Gunicorn, limite de memória e autorestart:
```bash
pm2 start ecosystem.config.js
pm2 save
```

Para verificar o status e logs:
```bash
pm2 status
pm2 logs idverde-api
```

#### 4. Testar localmente no servidor
```bash
curl http://127.0.0.1:5000/health
```

---

### 🌐 Expondo com o Cloudflare Tunnel (`cloudflared`)

Como seu servidor já utiliza o Cloudflare Tunnel, você não precisa abrir nenhuma porta no roteador.

#### Opção A: Pelo Painel Web do Cloudflare (Zero Trust Dashboard)
1. Acesse o **[Cloudflare One / Zero Trust](https://one.dash.cloudflare.com/)** > **Networks** > **Tunnels**.
2. Clique no seu Túnel ativo e vá na aba **Public Hostname**.
3. Clique em **Add a public hostname**:
   - **Subdomain:** `idverde` (ou `plantas-api`, `api-idverde`)
   - **Domain:** escolha seu domínio cadastrado (ex: `seudominio.com`)
   - **Type:** `HTTP`
   - **URL:** `localhost:5000` (ou `127.0.0.1:5000`)
4. Salve. Em poucos segundos você terá a URL pública segura com SSL ativo:
   `https://idverde.seudominio.com`

#### Opção B: Pelo arquivo de configuração CLI (`~/.cloudflared/config.yml`)
Se o seu túnel for configurado por arquivo local, adicione a rota de ingress:
```yaml
ingress:
  - hostname: idverde.seudominio.com
    service: http://localhost:5000
  # Demais serviços existentes continuam abaixo...
  - service: http_status:404
```
Reinicie o túnel:
```bash
sudo systemctl restart cloudflared
```

---

## ☁️ Guia de Hospedagem Alternativa na Nuvem (Render / Deploy Gratuito)

O repositório já vem preparado com `Dockerfile`, `Procfile` e `render.yaml`. O serviço gratuito mais simples e recomendado é o **Render**:

### Passo a Passo no Render:
1. Acesse **[render.com](https://render.com/)** e crie uma conta gratuita (você pode fazer login com sua conta do GitHub).
2. Clique no botão **"New +"** no topo e selecione **"Web Service"**.
3. Escolha **"Build and deploy from a Git repository"** e selecione o repositório `API-IA-IDVerde` da sua conta do GitHub.
4. Preencha os campos básicos:
   - **Name:** `idverde-api` (ou outro nome desejado)
   - **Region:** Ohio (US East) ou Oregon
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
   - **Instance Type:** `Free`
5. Clique em **"Deploy Web Service"**.
6. Em cerca de 2 a 3 minutos, sua API estará online com certificado SSL automático (HTTPS):
   `https://idverde-api.onrender.com`
7. Forneça este link para a equipe mobile colocar como `baseUrl`!

> **Dica:** O plano gratuito do Render hiberna após 15 minutos sem requisições. Na primeira requisição do dia ele pode levar ~30 a 50 segundos para "acordar".

---

## 🚀 Como Subir o Projeto no GitHub

Abra o terminal dentro da pasta do projeto e execute os comandos:

```bash
# 1. Inicializar o repositório git local
git init

# 2. Adicionar todos os arquivos (o .gitignore evitará arquivos pesados)
git add .

# 3. Criar o commit inicial
git commit -m "feat: API REST IDVerde para classificacao de plantas mobile"

# 4. Criar branch principal
git branch -M main

# 5. Vincular ao seu repositório no GitHub (crie antes o repositório vazio no github.com)
git remote add origin https://github.com/SEU_USUARIO/API-IA-IDVerde.git

# 6. Enviar para o GitHub
git push -u origin main
```

---

## 🧪 Testes Automatizados

O projeto inclui testes de integração automatizados cobrindo todos os endpoints, envio de imagem em `multipart/form-data`, envio em `Base64` e tratamento de erros:

```bash
python test_api.py
```

Resultado esperado:
```
Ran 6 tests in 0.85s
OK
```

---

## 📄 Licença e Créditos

Este projeto é desenvolvido no âmbito acadêmico na **Universidade Federal da Grande Dourados (UFGD)**, fomentado pela **FUNAEPE**.

