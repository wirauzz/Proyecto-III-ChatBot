from dotenv import load_dotenv
import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    ExtractiveSummaryAction
    ) 
import azure.cognitiveservices.speech as speechsdk
import time
import json
import pandas as pd
import requests


######################SPEECHE TO TEXT##############
load_dotenv("environments.txt")
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))

def from_mic(speech_config):
    # https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=stt
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="es-BO")

    print("Speak into your microphone.\n")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        #print("Recognized: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

speech_result = from_mic(speech_config)
print("--USER: " + speech_result + "\n")



##########################Get sumary and Entity######################################
key = os.environ.get('LANGUAGE_KEY')
endpoint = os.environ.get('LANGUAGE_ENDPOINT')
# Autenticarse
def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=ta_credential)
    return text_analytics_client
client = authenticate_client()
def sample_extractive_summarization(client, documents):
    document = documents
    poller = client.begin_analyze_actions(
        document,
        actions=[
            ExtractiveSummaryAction(max_sentence_count=1)
        ],
    )
    document_results = poller.result()
    for result in document_results:
        extract_summary_result = result[0]  # first document, first result
        if extract_summary_result.is_error:
            print("Error: '{}' - Mensaje: '{}'".format(
                extract_summary_result.code, extract_summary_result.message
            ))
        else:
            #print("Resumen: \n{}".format(
            #   " ".join([sentence.text for sentence in extract_summary_result.sentences]))
            #)
            return " ".join([sentence.text for sentence in extract_summary_result.sentences])

def entity_recognition_example(client, documents):
    try:
        result = client.recognize_entities(documents = documents)[0]
        return result.entities
    
    except Exception as err:
        print("Encountered exception. {}".format(err))     

##########################Implement content SAfe ############################# 
def analyze_text(text_input: str):
    # Analizar el texto
    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Crear un cliente de Content Safety
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    # Construir la solicitud
    request = AnalyzeTextOptions(text=text_input)

    try:
        # Analizar el texto
        response = client.analyze_text(request)
        results = {
            "Hate severity": response.hate_result.severity if response.hate_result else 0,
            "SelfHarm severity": response.self_harm_result.severity if response.self_harm_result else 0,
            "Sexual severity": response.sexual_result.severity if response.sexual_result else 0,
            "Violence severity": response.violence_result.severity if response.violence_result else 0,
        }
        return results
    except HttpResponseError as e:
        print("Error al analizar el texto.")
        if e.error:
            print(f"Código de error: {e.error.code}")
            print(f"Mensaje de error: {e.error.message}")
            raise
        raise

severidad_resultados = analyze_text(speech_result)

if severidad_resultados is not None:

    umbral_ofensivo = 1
    if any(severidad > umbral_ofensivo for severidad in severidad_resultados.values()):
       
        message_not_safe = "Lo siento, no puedo ayudarte porque he detectado contenido ofensivo en tu pregunta"
        description = message_not_safe
    else:
        key = os.environ.get('LANGUAGE_KEY')
        endpoint = os.environ.get('LANGUAGE_ENDPOINT')
        
        document = [speech_result];
        sumary = sample_extractive_summarization(client,document)
        document = [sumary]
        entities = entity_recognition_example(client,document)
        data_list = []
        for entity in entities:
            data_list.append([entity.text, entity.category, entity.confidence_score])
            
        columns = ['Name','Category','Confidence Score']
        df = pd.DataFrame(data_list, columns=columns)
        no_person ="Lo siento, soy un asistente únicamente orientado a darte información sobrefiguras públicas."
        entity = df[df['Category'] == 'Person'].iloc[0].Name if not df[df['Category'] == 'Person'].empty else None
        ##########################Asking google for entity#################
        # Clave de API de Google
        api_key = os.environ.get('API_GOOGLE_KEY')

        # Query para obtener información sobre Evo Morales
        query = entity

        # URL base de la API de Knowledge Graph
        url = "https://kgsearch.googleapis.com/v1/entities:search"

        # Parámetros de la consulta
        params = {
            "query": query,
            "key": api_key,
            "limit": 1,  # Puedes ajustar el límite según tus necesidades
            "languages": "es"
        }

        # Realizar la solicitud a la API de google
        if entity is not None:
            response = requests.get(url, params=params)
            data = response.json()
            
            # Procesar la respuesta
            if "itemListElement" in data and len(data["itemListElement"]) > 0:
                result = data["itemListElement"][0]["result"]
                if "detailedDescription" in result and "articleBody" in result["detailedDescription"]:
                    description = result["detailedDescription"]["articleBody"]
                else:
                    description = f"Lo siento, no puedo ayudarte porque no tengo información sobre {entity}"
            else:
                description = f"Lo siento, no puedo ayudarte porque no tengo información sobre {entity}"
        else:
            description = no_person  
           
else:
    description = "Ha ocurrido algun error, por favor intenta nuevamente mas tarde"

 ############################Info to Audio#########################

print("-ALESSANDRO: " +description + "\n")
message = description


speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_config.speech_synthesis_voice_name='es-BO-MarceloNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

speech_synthesis_result = speech_synthesizer.speak_text_async(message).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Alessandro out")
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
