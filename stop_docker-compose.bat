@echo off
setlocal

echo.
echo [======================= Parando los contenedores =========================]
echo.

docker-compose -f docker-compose.local.yml down

echo.
echo [========================= Contenedores Parados ===========================]
echo.
endlocal