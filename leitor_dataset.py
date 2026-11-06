import os
from PIL import Image
import numpy as np

EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def ler_dataset(folder_path, tamanho=200):
    """
    Lê imagens organizadas em subpastas por classe.

    Parâmetros:
        folder_path (str): Caminho para a pasta raiz com as subpastas das classes.
        tamanho (int): Largura e altura para redimensionar as imagens (padrão: 200).

    Retorna:
        infos (dict): Metadados sobre as classes e total de imagens.
        dataset (np.ndarray): Array de imagens com shape (N, tamanho, tamanho, 3).
        y (np.ndarray): Array de rótulos das classes com shape (N,).
    """
    imagens = []
    labels = []
    classes_count = {}

    subpastas = sorted([
        d for d in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, d))
    ])

    for classe in subpastas:
        caminho_classe = os.path.join(folder_path, classe)
        arquivos = sorted(os.listdir(caminho_classe))
        contador_classe = 0

        for arquivo in arquivos:
            ext = os.path.splitext(arquivo)[1].lower()
            if ext in EXTENSOES_VALIDAS:
                caminho_img = os.path.join(caminho_classe, arquivo)
                try:
                    with Image.open(caminho_img) as img:
                        img = img.convert("RGB")
                        img = img.resize((tamanho, tamanho))
                        imagens.append(np.array(img))
                        labels.append(classe)
                        contador_classe += 1
                except Exception as e:
                    print(f"Erro ao ler imagem {caminho_img}: {e}")

        classes_count[classe] = contador_classe

    dataset = np.array(imagens)
    y = np.array(labels)

    infos = {
        "classes": list(classes_count.keys()),
        "total_imagens": len(labels),
        "por_classe": classes_count
    }

    return infos, dataset, y


def preparar_X(dataset):
    """
    Achata as imagens em vetores 1D (features para o classificador).

    Parâmetros:
        dataset (np.ndarray): Array com shape (N, altura, largura, canais).

    Retorna:
        X (np.ndarray): Matriz 2D com shape (N, altura * largura * canais).
    """
    return dataset.reshape(len(dataset), -1).astype(np.float32)
