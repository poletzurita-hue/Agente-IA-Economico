#######################
# Agente Basico De IA #
# Agente              #
#######################

# Importacion para el ambiente
from dotenv import load_dotenv

# Importacion para el LLM
from groq import Groq

# Importacion para el manejo de sistema
import os

# Importacion para el uso de formato JSON
import json

# Importacion para el manejo de fechas y zonas horarias
from datetime import datetime
from zoneinfo import ZoneInfo

# Importacion para el manejo memoria y herramientas
from basic_memory import BasicMemory
from intermediate_tools import IntermediateTools


# Cargar variables de entorno
load_dotenv()

# Inicializar el cliente de Groq con la clave de API
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Captura la hora actual en la zona horaria de Guatemala
now = datetime.now(ZoneInfo("America/Guatemala"))

# Inicializar herramientas y memoria
MEMORY_MAX_MESSAGES = 10
memory = BasicMemory(max_messages=MEMORY_MAX_MESSAGES)


SYSTEM_PROMPT = f"""
Eres un agente económico que habla en español y responde de manera clara y concisa.

Tu objetivo es apoyar al usuario en consultas económicas relacionadas con tipos de cambio,
conversiones de moneda y comparación de monedas utilizando información actualizada.

También puedes utilizar información de ubicación y clima cuando sea útil para la consulta.

Debes utilizar las herramientas disponibles cuando la consulta requiera información actual.
No inventes datos y proporciona la información obtenida por las herramientas de forma clara.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_tipo_cambio_api",
            "description": (
                "Llama a esta funcion para consultar el tipo de cambio de una moneda "
                "respecto al quetzal de Guatemala. "
                "Se debe enviar como argumento el codigo de la moneda que se desea consultar."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "moneda": {
                        "type": "string",
                        "description": "Codigo de la moneda que se desea consultar, por ejemplo USD"
                    }
                },
                "required": ["moneda"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convertir_moneda_api",
            "description": (
                "Convierte una cantidad de una moneda a otra "
                "utilizando el tipo de cambio actual."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cantidad": {
                        "type": "number",
                        "description": "Cantidad de dinero que se desea convertir"
                    },
                    "moneda_origen": {
                        "type": "string",
                        "description": "Codigo de la moneda de origen, por ejemplo USD"
                    },
                    "moneda_destino": {
                        "type": "string",
                        "description": "Codigo de la moneda de destino, por ejemplo GTQ"
                    }
                },
                "required": [
                    "cantidad",
                    "moneda_origen",
                    "moneda_destino"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "comparar_monedas_api",
            "description": (
                "Consulta y compara el tipo de cambio de varias monedas "
                "respecto al quetzal de Guatemala. "
                "Se debe enviar una lista de códigos de monedas."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "monedas": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": (
                            "Lista de códigos de monedas que se desean comparar, "
                            "por ejemplo USD, EUR y MXN"
                        )
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
            "description": (
                "Obtiene la latitud y longitud de una ciudad."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "Nombre de la ciudad"
                    }
                },
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_clima_api",
            "description": (
                "Obtiene el clima actual utilizando la latitud y longitud "
                "de una ubicación."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "string",
                        "description": "Latitud de la ubicación"
                    },
                    "long": {
                        "type": "string",
                        "description": "Longitud de la ubicación"
                    }
                },
                "required": ["lat", "long"]
            }
        }
    }
]


print("Agente Basico De IA")


def process_response(client: Groq, memory_messages: list[dict], user_text: str):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory_messages)
    messages.append({"role": "user", "content": user_text})

    while True:

        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOLS
        )

        msg = resp.choices[0].message

        # Si no hay llamados a herramientas, entonces ya regresamos la respuesta
        if not getattr(msg, "tool_calls", None):
            return msg.content or ""

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
        })

        for tool_call in msg.tool_calls:

            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")

            if name == "consultar_tipo_cambio_api":

                tools = IntermediateTools()

                result = tools.consultar_tipo_cambio_api(
                    moneda=args["moneda"]
                )

            elif name == "convertir_moneda_api":

                tools = IntermediateTools()

                result = tools.convertir_moneda_api(
                    cantidad=args["cantidad"],
                    moneda_origen=args["moneda_origen"],
                    moneda_destino=args["moneda_destino"]
                )

            elif name == "comparar_monedas_api":

                tools = IntermediateTools()

                result = tools.comparar_monedas_api(
                    monedas=args["monedas"]
                )

            elif name == "obtener_lat_long":

                tools = IntermediateTools()

                result = tools.obtener_lat_long(
                    ciudad=args["ciudad"]
                )

            elif name == "obtener_clima_api":

                tools = IntermediateTools()

                result = tools.obtener_clima_api(
                    lat=args["lat"],
                    long=args["long"]
                )

            else:

                print(
                    f"Se intentó llamar a una herramienta desconocida {name}"
                )

                result = {
                    "error": f"Herramienta desconocida: {name}"
                }

            # Agregar a los mensajes el resultado del llamado de la herramienta
            # Esto lo recibirá el modelo al continuar la iteración
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False
                )
            })


while True:

    user_text = input("Tú: ").strip()

    if not user_text:
        continue

    if user_text.lower() in ("exit", "salir"):
        print("Hasta luego!")
        break

    assistant_text = process_response(
        client,
        memory.messages(),
        user_text
    )

    print(f"Agente: {assistant_text}")

    # Actualizar la memoria
    memory.add("user", user_text)
    memory.add("assistant", assistant_text)