#!/usr/bin/env bash
# Salir inmediatamente si un comando falla
set -o errexit

echo "--- Iniciando script de compilación personalizado ---"

# 1. Instalar dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt

echo "--- Dependencias de Python instaladas ---"

# 2. Definir el directorio de caché persistente
STORAGE_DIR=/opt/render/project/.render
CHROME_DIR=$STORAGE_DIR/chrome

# 3. Lógica de caché: Solo descargar si no existe
if [ ! -d "$CHROME_DIR" ]; then
  echo "... Descargando Google Chrome (no encontrado en caché)..."
  mkdir -p $CHROME_DIR
  cd $CHROME_DIR
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  
  echo "... Extrayendo binarios de Chrome (usando dpkg -x)..."
  # Esta es la clave: dpkg -x extrae, NO requiere root [cite: 109, 111]
  dpkg -x ./google-chrome-stable_current_amd64.deb $CHROME_DIR
  
  # Limpiar el .deb
  rm ./google-chrome-stable_current_amd64.deb
  
  cd $HOME/project/src
  echo "... Google Chrome descargado y extraído. ---"
else
  echo "... Usando Google Chrome desde la caché de compilación ---"
fi

# 4. Opcional: Imprimir la versión para depurar
echo "Versión de Chrome en caché:"
$CHROME_DIR/opt/google/chrome/google-chrome --version

echo "--- Script de compilación personalizado finalizado ---"