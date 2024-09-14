@echo off
setlocal

echo.
echo [======================= Construyendo las Imagenes ========================]
echo.
docker-compose -f docker-compose.local.yml build 

echo.
echo [========================== Creando los Contenedores ======================]
echo.
docker-compose -f docker-compose.local.yml up -d

echo.
echo [========================== Creando Migraciones ===========================]
echo.
docker-compose -f docker-compose.local.yml run --rm django python manage.py makemigrations

echo.
echo [======================= Ejecuctando Migraciones ==========================]
echo.
docker-compose -f docker-compose.local.yml run --rm django python manage.py migrate

echo.
echo [========================= Contenedores Corriendo =========================]
echo.
endlocal

