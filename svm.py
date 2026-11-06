from tkinter import Tk, filedialog
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# funções para criar o dataset
from leitor_dataset import ler_dataset, preparar_X

def selecionar_pasta():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return filedialog.askdirectory(title="Selecione a pasta do dataset")

def main():
    folder_path = selecionar_pasta()

    if not folder_path:
        import os
        if os.path.exists("Plantas"):
            folder_path = os.path.abspath("Plantas")
            print(f"Nenhuma pasta selecionada no diálogo. Usando pasta local: {folder_path}")
        else:
            print("Nenhuma pasta foi selecionada.")
            return

    infos, dataset, y = ler_dataset(folder_path, tamanho=200)
    X = preparar_X(dataset)

    print("Infos:", infos)
    print("Shape do dataset:", dataset.shape)
    print("Shape de X:", X.shape)
    print("Shape de y:", y.shape)

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    modelo = make_pipeline(
        StandardScaler(),
        SVC(kernel="rbf", C=1.0, gamma="scale", probability=True)
    )

    modelo.fit(X_treino, y_treino)
    y_pred = modelo.predict(X_teste)

    import pickle

    with open("modelo_svm.pkl", "wb") as f:
    	pickle.dump(modelo, f)

    print("Modelo salvo em modelo_svm.pkl")

    print("Acurácia:", accuracy_score(y_teste, y_pred))
    print(classification_report(y_teste, y_pred))

    ConfusionMatrixDisplay.from_predictions(y_teste, y_pred)
    plt.show()

    import json
    import time

    inicio = time.time()
    probabilidades = modelo.predict_proba(X_teste)
    classes = modelo.classes_

    probs_primeira = probabilidades[0]
    top3_indices = probs_primeira.argsort()[-3:][::-1]
    fim = time.time()

    def gerar_id(nome):
        return nome.lower().split(" (")[0].replace(" ", "_").replace("-", "_")

    resultado = {
        "image_id": "teste_0001",
        "topk": [
            {
                "id": gerar_id(classes[i]),
                "nome": classes[i],
                "score": round(float(probs_primeira[i]), 2)
            }
            for i in top3_indices
        ],
        "model_version": "svm-v1",
        "latency_ms": round((fim - inicio) * 1000)
    }

    with open("resultado.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print("\nJSON gerado:")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
