# Proyecto Alessandro

## Descripción
El proyecto Alessandro es un asistente virtual que utiliza tecnologías de procesamiento de lenguaje natural y reconocimiento de voz para proporcionar información sobre figuras públicas. El asistente puede realizar las siguientes funciones:

- Convertir voz a texto mediante Azure Speech SDK.
- Analizar el contenido del texto para evaluar su seguridad utilizando Azure Content Moderator.
- Realizar resúmenes extractivos del texto utilizando Azure Text Analytics.
- Reconocer entidades en el texto, especialmente personas, utilizando Azure Text Analytics.
- Consultar la API de Knowledge Graph de Google para obtener información adicional sobre figuras públicas.

## Requisitos
- Python 3.x
- Paquetes especificados en `requirements.txt`
- Claves y credenciales de API para Azure y Google Cloud Platform.

## Configuración del Entorno
1. Instalar dependencias: `pip install -r requirements.txt`
2. Configurar variables de entorno:
   - `SPEECH_KEY`: Clave de suscripción de Azure Speech.
   - `SPEECH_REGION`: Región de Azure para Speech.
   - `LANGUAGE_KEY`: Clave de suscripción de Azure Text Analytics.
   - `LANGUAGE_ENDPOINT`: Endpoint de Azure Text Analytics.
   - `CONTENT_SAFETY_KEY`: Clave de suscripción de Azure Content Moderator.
   - `CONTENT_SAFETY_ENDPOINT`: Endpoint de Azure Content Moderator.
   - `API_GOOGLE_KEY`: Clave de API de Google.

## Uso
1. Ejecutar `alessandro2.py`.
2. Hablar al micrófono cuando se indique.
3. El asistente proporcionará información sobre figuras públicas y evaluará la seguridad del contenido.

