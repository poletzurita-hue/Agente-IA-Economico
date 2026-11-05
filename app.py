
import os
import json
import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from groq import Groq

from basic_memory import BasicMemory
from intermediate_tools import IntermediateTools

load_dotenv()

st.set_page_config(
    page_title="Agente IA Económico",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
section[data-testid="stSidebar"] {background: #f7f8fa;}
.chat-user {
    background: #f0f4fa; padding: 14px 18px;
    border-radius: 14px; margin: 10px 0;
}
.chat-agent {
    border: 1px solid #d5d9df; padding: 16px 18px;
    border-radius: 14px; margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("No encuentro GROQ_API_KEY. Revisa tu archivo .env.")
    st.stop()

client = Groq(api_key=api_key)
tools = IntermediateTools()

SYSTEM_PROMPT = """
Eres un agente económico que responde en español, de forma clara y concisa.
Ayudas a interpretar tipos de cambio, conversiones y comparaciones de monedas.
Utiliza las herramientas disponibles cuando necesites datos actuales.
No inventes datos. Explica las limitaciones de los resultados.
Las herramientas de clima y ubicación son complementarias.
No presentes datos ilustrativos como si fueran datos económicos reales.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_tipo_cambio_api",
            "description": "Consulta tipos de cambio de una moneda.",
            "parameters": {
                "type": "object",
                "properties": {
                    "moneda": {"type": "string"}
                },
                "required": ["moneda"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convertir_moneda_api",
            "description": "Convierte dinero entre dos monedas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cantidad": {"type": "number"},
                    "moneda_origen": {"type": "string"},
                    "moneda_destino": {"type": "string"}
                },
                "required": [
                    "cantidad", "moneda_origen", "moneda_destino"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "comparar_monedas_api",
            "description": "Compara monedas frente al quetzal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "monedas": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["monedas"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_lat_long",
            "description": "Busca las coordenadas de una ciudad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {"type": "string"}
                },
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_clima_api",
            "description": "Consulta el clima por coordenadas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat": {"type": "string"},
                    "long": {"type": "string"}
                },
                "required": ["lat", "long"]
            }
        }
    }
]

def ejecutar_herramienta(nombre, args):
    funciones = {
        "consultar_tipo_cambio_api": tools.consultar_tipo_cambio_api,
        "convertir_moneda_api": tools.convertir_moneda_api,
        "comparar_monedas_api": tools.comparar_monedas_api,
        "obtener_lat_long": tools.obtener_lat_long,
        "obtener_clima_api": tools.obtener_clima_api,
    }
    if nombre not in funciones:
        return {"error": "Herramienta desconocida"}
    try:
        return funciones[nombre](**args)
    except Exception as e:
        return {"error": str(e)}

def responder(historial, pregunta):
    mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]
    mensajes.extend(historial)
    mensajes.append({"role": "user", "content": pregunta})

    for _ in range(5):
        respuesta = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=mensajes,
            tools=TOOLS
        )
        msg = respuesta.choices[0].message

        if not msg.tool_calls:
            return msg.content or "No se recibió una respuesta."

        mensajes.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
        })

        for llamada in msg.tool_calls:
            nombre = llamada.function.name
            args = json.loads(llamada.function.arguments or "{}")
            resultado = ejecutar_herramienta(nombre, args)
            mensajes.append({
                "role": "tool",
                "tool_call_id": llamada.id,
                "content": json.dumps(resultado, ensure_ascii=False, default=str)
            })

    return "No pude completar la consulta. Intenta de nuevo."

if "historial" not in st.session_state:
    st.session_state.historial = []

if "memoria" not in st.session_state:
    st.session_state.memoria = BasicMemory(max_messages=10)

with st.sidebar:
    st.markdown("## 🤖 Agente IA")
    st.caption("Tu asistente económico de confianza")
    st.divider()

    st.markdown("### 💡 ¿Qué puedo hacer?")
    st.write(
        "Puedo ayudarte con tipos de cambio, conversiones de monedas, "
        "comparaciones y consultas económicas."
    )

    st.markdown("### 📊 Capacidades principales")
    st.markdown(
        "- Análisis de tipos de cambio\n"
        "- Interpretación de resultados\n"
        "- Comparación de monedas\n"
        "- Generación de gráficos"
    )

    st.markdown("### ⚙️ Herramientas incluidas")
    st.markdown(
        "- Consulta de tipos de cambio\n"
        "- Conversión de monedas\n"
        "- Comparación frente al quetzal\n"
        "- Ubicación y clima"
    )

    if st.button("🗑️ Nueva conversación"):
        st.session_state.historial = []
        st.session_state.memoria = BasicMemory(max_messages=10)
        st.rerun()

st.title("💬 Conversación con el Agente IA")
st.caption("Consulta información y solicita análisis económico.")

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

pregunta = st.chat_input("Escribe tu pregunta o solicitud...")

if pregunta:
    st.session_state.historial.append(
        {"role": "user", "content": pregunta}
    )

    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Analizando tu consulta..."):
            try:
                historial_modelo = st.session_state.memoria.messages()
                texto = responder(historial_modelo, pregunta)
                st.markdown(texto)

                # Gráfica solo cuando el agente devuelve datos estructurados.
                if isinstance(texto, str) and "GRAFICA_JSON:" in texto:
                    st.caption(
                        "Para crear una gráfica, solicita categorías y "
                        "valores numéricos claramente identificados."
                    )

            except Exception as e:
                texto = (
                    "No pude completar la consulta. "
                    "Verifica tu conexión y la configuración de Groq."
                )
                st.error(texto)
                st.caption(str(e))

    st.session_state.memoria.add("user", pregunta)
    st.session_state.memoria.add("assistant", texto)
    st.session_state.historial.append(
        {"role": "assistant", "content": texto}
    )
