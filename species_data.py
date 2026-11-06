"""
Metadados e informações botânicas das espécies catalogadas no IDVerde.
Classes suportadas pelo modelo SVM treinado.
"""

SPECIES_METADATA = {
    "African Violet": {
        "id": "african_violet",
        "nome": "African Violet",
        "nome_popular": "Violeta-africana",
        "nome_cientifico": "Saintpaulia ionantha",
        "familia": "Gesneriaceae",
        "origem": "Tanzânia e leste da África",
        "descricao": "Planta herbácea perene de pequeno porte com folhas aveludadas em formato de coração e flores vistosas nas cores roxa, violeta, rosa e branca.",
        "cuidados": {
            "luz": "Luz indireta brilhante (evitar sol direto)",
            "rega": "Moderada; regar pelo prato inferior sem molhar as folhas",
            "temperatura": "18°C a 24°C"
        }
    },
    "Aloe Vera": {
        "id": "aloe_vera",
        "nome": "Aloe Vera",
        "nome_popular": "Babosa",
        "nome_cientifico": "Aloe barbadensis miller",
        "familia": "Asphodelaceae",
        "origem": "Península Arábica e regiões tropicais áridas",
        "descricao": "Planta suculenta com folhas espessas, carnosas e serrilhadas que armazenam um gel amplamente utilizado para fins cosméticos e medicinais.",
        "cuidados": {
            "luz": "Sol pleno ou meia-sombra abundante",
            "rega": "Espaçada; esperar o substrato secar completamente",
            "temperatura": "15°C a 30°C"
        }
    },
    "Anthurium": {
        "id": "anthurium",
        "nome": "Anthurium",
        "nome_popular": "Antúrio",
        "nome_cientifico": "Anthurium andreanum",
        "familia": "Araceae",
        "origem": "América Central e do Sul (Colômbia e Equador)",
        "descricao": "Planta tropical ornamental com folhas verde-escuras brilhantes e espatas coloridas cerosas (comumente vermelhas, rosas ou brancas) com espádice central.",
        "cuidados": {
            "luz": "Meia-sombra ou luz difusa brilhante",
            "rega": "Regular para manter o solo úmido sem encharcar",
            "temperatura": "20°C a 28°C"
        }
    },
    "Areca Palm": {
        "id": "areca_palm",
        "nome": "Areca Palm",
        "nome_popular": "Palmeira-areca / Areca-bambu",
        "nome_cientifico": "Dypsis lutescens",
        "familia": "Arecaceae",
        "origem": "Madagascar",
        "descricao": "Palmeira cespitosa com múltiplos troncos amarelados e frondes longas e arqueadas, muito utilizada em paisagismo e decoração de interiores.",
        "cuidados": {
            "luz": "Luz indireta abundante a sol brando matinal",
            "rega": "Frequente nos meses quentes, reduzindo no inverno",
            "temperatura": "18°C a 26°C"
        }
    },
    "Asparagus Fern": {
        "id": "asparagus_fern",
        "nome": "Asparagus Fern",
        "nome_popular": "Aspargo-samambaia / Melindre",
        "nome_cientifico": "Asparagus setaceus",
        "familia": "Asparagaceae",
        "origem": "Sul e leste da África",
        "descricao": "Planta trepadeira ou pendente com cladódios muito finos e ramificados que lembram a textura de uma plumagem verde delicada.",
        "cuidados": {
            "luz": "Meia-sombra ou luz filtrada",
            "rega": "Constante mantendo o solo levemente úmido",
            "temperatura": "15°C a 25°C"
        }
    }
}


def normalizar_id(nome: str) -> str:
    """Converte o nome da classe em um ID seguro em snake_case."""
    return nome.lower().split(" (")[0].replace(" ", "_").replace("-", "_")


def obter_info_especie(nome_classe: str) -> dict:
    """Retorna os metadados da espécie a partir do nome retornado pelo modelo."""
    if nome_classe in SPECIES_METADATA:
        return SPECIES_METADATA[nome_classe]
    return {
        "id": normalizar_id(nome_classe),
        "nome": nome_classe,
        "nome_popular": nome_classe,
        "nome_cientifico": "Desconhecido",
        "familia": "Desconhecida",
        "descricao": "Informações não catalogadas.",
        "cuidados": {}
    }

