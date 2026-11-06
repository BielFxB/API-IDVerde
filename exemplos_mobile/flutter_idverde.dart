// ============================================================================
// Exemplo de Integração Flutter (Dart) com a API IDVerde
// Dependências no pubspec.yaml:
//   dependencies:
//     http: ^1.2.0
//     image_picker: ^1.0.7
// ============================================================================

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

/// Modelo de dados para a espécie classificada
class PredicaoEspecie {
  final String id;
  final String nome;
  final String nomePopular;
  final String nomeCientifico;
  final double score;
  final String porcentagem;
  final String familia;

  PredicaoEspecie({
    required this.id,
    required this.nome,
    required this.nomePopular,
    required this.nomeCientifico,
    required this.score,
    required this.porcentagem,
    required this.familia,
  });

  factory PredicaoEspecie.fromJson(Map<String, dynamic> json) {
    return PredicaoEspecie(
      id: json['id'] ?? '',
      nome: json['nome'] ?? '',
      nomePopular: json['nome_popular'] ?? json['nome'] ?? '',
      nomeCientifico: json['nome_cientifico'] ?? '',
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      porcentagem: json['porcentagem'] ?? '0%',
      familia: json['familia'] ?? '',
    );
  }
}

/// Resposta completa da API IDVerde
class RespostaIDVerde {
  final bool success;
  final String imageId;
  final List<PredicaoEspecie> topk;
  final PredicaoEspecie? melhorPredicao;
  final int latencyMs;

  RespostaIDVerde({
    required this.success,
    required this.imageId,
    required this.topk,
    this.melhorPredicao,
    required this.latencyMs,
  });

  factory RespostaIDVerde.fromJson(Map<String, dynamic> json) {
    final list = (json['topk'] as List? ?? [])
        .map((item) => PredicaoEspecie.fromJson(item))
        .toList();

    return RespostaIDVerde(
      success: json['success'] ?? false,
      imageId: json['image_id'] ?? '',
      topk: list,
      melhorPredicao: json['melhor_predicao'] != null
          ? PredicaoEspecie.fromJson(json['melhor_predicao'])
          : (list.isNotEmpty ? list.first : null),
      latencyMs: json['latency_ms'] ?? 0,
    );
  }
}

/// Serviço de comunicação HTTP com a API
class IDVerdeService {
  final String baseUrl;

  IDVerdeService({this.baseUrl = 'https://apiidverde.gamycoins.com.br'});

  /// Envia a foto capturada pela câmera/galeria para classificação
  Future<RespostaIDVerde> classificarPlanta(File arquivoImagem) async {
    final uri = Uri.parse('$baseUrl/predict');
    final request = http.MultipartRequest('POST', uri);

    // Adiciona a imagem no campo 'image'
    final multipartFile = await http.MultipartFile.fromPath(
      'image',
      arquivoImagem.path,
    );
    request.files.add(multipartFile);

    // Envia a requisição
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
      return RespostaIDVerde.fromJson(data);
    } else {
      final Map<String, dynamic> errorData = jsonDecode(utf8.decode(response.bodyBytes));
      throw Exception(errorData['error'] ?? 'Erro ${response.statusCode} na API');
    }
  }

  /// Verifica se a API está online e o modelo carregado
  Future<bool> verificarSaude() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['model_loaded'] == true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }
}

