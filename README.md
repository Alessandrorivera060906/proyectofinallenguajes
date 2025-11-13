# proyectofinallenguajes
Proyecto final de lenguajes formales y autómatas sección 01 Javier Alessandro Rivera Lemus 1241224
0) Abrir la programación
PowerShell
cd "RUTA\A\PROYECTO"
.\.venv\Scripts\Activate.ps1
python -m streamlit run chomsky_classifier_ai\ui_streamlit.py --server.port 8502
CMD
cd RUTA\A\PROYECTO
.\.venv\Scripts\activate.bat
python -m streamlit run chomsky_classifier_ai\ui_streamlit.py --server.port 8502
 
1) Pestaña: Gramática
Pega tus reglas en el cuadro de texto (usa ->, separa con | o ;, y e/ε para épsilon).
Clic en Clasificar para ver el tipo y la justificación.
Clic en Generar diagrama (PNG) para ver la vista previa y el botón Descargar PNG.
El archivo también queda en la carpeta output/.
 
2) Pestaña: Autómata
Pega el JSON del autómata (campos: type, states, alphabet, start, accepts, transitions).
Clic en Clasificar autómata para ver el resultado.
 
3) Pestaña: Regex → Gramática
Escribe la expresión regular.
Clic en Convertir.
Copia el resultado o usa Descargar gramatica.txt.
 
4) Pestaña: Reporte PDF
Pega las reglas.
Clic en Generar PDF.
Usa Descargar reporte.pdf.
También se guarda en output/.
 
5) Pestaña: Modo explicativo
Pega las reglas.
Clic en Analizar para ver los pasos (abre los expandibles).
 
6) Pestaña: Quiz
Elige el tipo (o deja Aleatoria).
Clic en Generar nueva.
Elige tu respuesta y clic en Verificar.
 
7) Pestaña: Comparar
Pega Gramática 1 y Gramática 2.
Ajusta la Profundidad n.
Clic en Comparar para ver el % de similitud y notas.
 
8) Descargas y salidas
Los PNG y PDF se guardan automáticamente en output/.
Si no ves el botón de descarga, desplázate un poco hacia abajo.
9) Cerrar / reiniciar
Para detener la app: vuelve a la terminal y presiona Ctrl + C.
Si el puerto está ocupado, ejecuta con otro: --server.port 8503.
