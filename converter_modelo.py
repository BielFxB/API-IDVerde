"""
Utilitário para conversão e otimização do modelo de Machine Learning do IDVerde.

Converte o modelo bruto 'modelo_svm.pkl' (112.6 MB) para 'modelo_svm.joblib' comprimido (~60.7 MB),
garantindo compatibilidade com o limite de 100MB por arquivo imposto pelo GitHub.
"""

import os
import sys
import time
import pickle
import joblib

PKL_PATH = "modelo_svm.pkl"
JOBLIB_PATH = "modelo_svm.joblib"


def otimizar_modelo():
    if not os.path.exists(PKL_PATH):
        if os.path.exists(JOBLIB_PATH):
            print(f"'{PKL_PATH}' não encontrado, mas '{JOBLIB_PATH}' já existe.")
            return
        print(f"Erro: Nenhum arquivo de modelo encontrado ({PKL_PATH} ou {JOBLIB_PATH}).")
        sys.exit(1)

    print(f"Lendo '{PKL_PATH}'...")
    inicio = time.time()
    with open(PKL_PATH, "rb") as f:
        modelo = pickle.load(f)
    print(f"Modelo carregado em {time.time() - inicio:.2f}s.")

    print(f"Salvando versão otimizada em '{JOBLIB_PATH}' (compressão nível 3)...")
    inicio_salvamento = time.time()
    joblib.dump(modelo, JOBLIB_PATH, compress=3)
    print(f"Salvo em {time.time() - inicio_salvamento:.2f}s.")

    tamanho_pkl = os.path.getsize(PKL_PATH) / (1024 * 1024)
    tamanho_joblib = os.path.getsize(JOBLIB_PATH) / (1024 * 1024)

    print("-" * 50)
    print(f"Tamanho original (PKL):    {tamanho_pkl:.2f} MB  (Aviso: >100MB excede limite do GitHub)")
    print(f"Tamanho comprimido (Joblib): {tamanho_joblib:.2f} MB  (Pronto para GitHub e Deploy)")
    print(f"Redução de tamanho:         {100 - (tamanho_joblib / tamanho_pkl * 100):.1f}%")
    print("-" * 50)


if __name__ == "__main__":
    otimizar_modelo()

