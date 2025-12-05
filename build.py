import os
import sys
import subprocess

exe_name = "ConsultaCuentasBancariasV1"
main_file = "main.py"

add_data = [
    "controllers;controllers",
    "services;services",
    "ui;ui",
]

add_data_args = []
for item in add_data:
    add_data_args.extend(["--add-data", item])

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--name", exe_name,
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--clean",
    *add_data_args,
    main_file
]

print("🚀 Ejecutando PyInstaller...")
print("🔧 Generando ejecutable...")

# 👉 Mostrar la consola para ver el error real
subprocess.run(cmd, check=True)

print(f"✅ COMPLETADO — Ejecutable generado en: dist/{exe_name}.exe")
