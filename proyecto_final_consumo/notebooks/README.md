# Entrenamiento SARIMA en Colab

Usa el notebook oficial de la guía para entrenar el modelo con la serie de temperatura de InfluxDB.

1. Configura en Colab los secretos INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG e INFLUX_BUCKET.
2. Indica MEASUREMENT=sensores y FIELD=temperatura; cámbialos si tu base usa otros nombres.
3. Ejecuta el notebook completo y descarga el archivo sarima_config.json.
4. Guárdalo en proyecto_final_consumo/models/sarima_config.json.
5. Sube también la copia ejecutada del notebook a esta carpeta.

El token no debe guardarse en el notebook, en GitHub ni en el video de entrega.
