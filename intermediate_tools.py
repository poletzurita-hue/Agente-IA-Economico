#######################
# Agente Basico De IA #
# Herramientas        #
#######################

# Importacion para el manejo de sistema
import os
import requests


class IntermediateTools:

    def __init__(self):
        pass

    # Herramienta para consultar el tipo de cambio
    def consultar_tipo_cambio_api(self, moneda: str):
        print(f"Herramienta consultar_tipo_cambio_api llamada con moneda: {moneda}")

        if not moneda:
            return "Error: Se requiere el código de la moneda para obtener el tipo de cambio."

        # URL del servicio para obtener el tipo de cambio según la moneda
        url = f"https://open.er-api.com/v6/latest/{moneda.upper()}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Error al obtener_tipo_cambio_api: {moneda}. Error: {e}")
            return f"ERROR: No se pudo obtener el tipo de cambio para la moneda: {moneda}"

    # Herramienta para convertir monedas
    def convertir_moneda_api(
        self,
        cantidad,
        moneda_origen,
        moneda_destino
    ):
        print(
            f"Herramienta convertir_moneda_api llamada: "
            f"{cantidad} {moneda_origen} a {moneda_destino}"
        )

        if not cantidad:
            return "Error: Se requiere una cantidad para realizar la conversión."

        if not moneda_origen or not moneda_destino:
            return "Error: Se requieren las monedas de origen y destino."

        url = f"https://open.er-api.com/v6/latest/{moneda_origen.upper()}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            tasa = data["rates"][moneda_destino.upper()]
            resultado = cantidad * tasa

            return {
                "cantidad": cantidad,
                "moneda_origen": moneda_origen.upper(),
                "moneda_destino": moneda_destino.upper(),
                "tasa": tasa,
                "resultado": resultado
            }

        except Exception as e:
            print(f"Error al convertir moneda: {e}")
            return "ERROR: No se pudo realizar la conversión."

    # Herramienta para comparar monedas
    def comparar_monedas_api(self, monedas):
        print(
            f"Herramienta comparar_monedas_api llamada con monedas: {monedas}"
        )

        if not monedas:
            return "Error: Se requiere una lista de monedas para comparar."

        resultados = {}

        for moneda in monedas:
            moneda = moneda.upper()

            try:
                url = f"https://open.er-api.com/v6/latest/{moneda}"
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                data = response.json()

                resultados[moneda] = {
                    "nombre": data.get("base_code", moneda),
                    "tasa_a_GTQ": data["rates"].get("GTQ")
                }

            except Exception as e:
                resultados[moneda] = {
                    "error": f"No se pudo consultar la moneda. {e}"
                }

        return resultados

    # Herramienta para obtener latitud y longitud de una ciudad
    def obtener_lat_long(self, ciudad: str):
        print(
            f"Herramienta obtener_lat_long llamada con ciudad: {ciudad}"
        )

        url = (
            f"https://geocoding-api.open-meteo.com/v1/search"
            f"?name={ciudad}&count=1&language=es&format=json"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "results" in data and data["results"]:
                return {
                    "lat": data["results"][0]["latitude"],
                    "long": data["results"][0]["longitude"],
                    "nombre": data["results"][0].get("name", ciudad),
                    "pais": data["results"][0].get("country", "")
                }

            return "ERROR: No se encontró la ciudad."

        except Exception as e:
            print(f"Error al obtener_lat_long: {e}")
            return "ERROR: No se pudo obtener la ubicación."

    # Herramienta para obtener el clima actual
    def obtener_clima_api(self, lat: str, long: str):
        print(
            f"Herramienta obtener_clima_api llamada con lat: {lat}, long: {long}"
        )

        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={long}&current_weather=true"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"Error al obtener_clima_api: {e}")
            return "ERROR: No se pudo obtener el clima."