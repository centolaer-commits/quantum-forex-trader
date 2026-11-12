@echo off
title Publicar Quantum Forex Trader no GitHub
chcp 65001 > nul
echo ========================================================
echo   PUBLICAR QUANTUM FOREX TRADER NO GITHUB
echo ========================================================
echo.
echo Certifique-se de que ja criou o repositorio vazio em:
echo https://github.com/new com o nome: quantum-forex-trader
echo.
pause
echo.
echo Enviando branch main para o GitHub...
"C:\Users\enric\AppData\Local\Programs\Git\cmd\git.exe" push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ========================================================
    echo   SUCESSO! Repositorio publicado no GitHub:
    echo   https://github.com/centolaer-commits/quantum-forex-trader
    echo ========================================================
) else (
    echo Houve um erro ao enviar. Verifique se o repositorio foi criado no GitHub.
)
echo.
pause
