/**
 * Exemplo de Integração React Native (Expo ou Bare React Native) com a API IDVerde
 * Utilizando FormData e fetch nativo
 */

const BASE_URL = 'https://apiidverde.gamycoins.com.br';

/**
 * Envia uma foto selecionada com expo-image-picker ou react-native-image-picker
 * @param {string} imageUri - URI local do arquivo (ex: 'file:///data/user/0/.../cache/photo.jpg')
 */
export async function classificarPlanta(imageUri) {
  const formData = new FormData();

  const filename = imageUri.split('/').pop() || 'planta.jpg';
  const match = /\.(\w+)$/.exec(filename);
  const type = match ? `image/${match[1]}` : 'image/jpeg';

  formData.append('image', {
    uri: imageUri,
    name: filename,
    type: type,
  });

  try {
    const response = await fetch(`${BASE_URL}/predict`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
        // Não defina Content-Type manualmente para que o boundary do FormData seja gerado automaticamente
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `Erro HTTP ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error('Falha ao classificar planta no IDVerde:', error);
    throw error;
  }
}

/**
 * Consulta a lista e guia botânico das 5 espécies
 */
export async function obterEspecies() {
  const response = await fetch(`${BASE_URL}/species`);
  return await response.json();
}

