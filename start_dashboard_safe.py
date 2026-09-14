# -*- coding: utf-8 -*-
"""Script de inicio seguro y monitoreado del dashboard.

Blindaje contra caidas de Streamlit con:
- Limpieza de procesos zombie
- Verificacion de puerto
- Reinicio automatico
- Logging de monitoreo
"""

import subprocess
import time
import sys
import os
import socket
import psutil
from pathlib import Path

def limpiar_puerto_8501():
    """Limpia cualquier proceso usando el puerto 8501."""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == 8501:
                try:
                    proc = psutil.Process(conn.pid)
                    print(f"Matando proceso zombie en puerto 8501: PID {conn.pid}")
                    proc.terminate()
                    time.sleep(1)
                except psutil.NoSuchProcess:
                    pass
    except Exception as e:
        print(f"Advertencia limpiando puerto: {e}")

def verificar_puerto_libre(puerto=8501):
    """Verifica que el puerto esté libre."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', puerto))
    sock.close()
    return result != 0

def iniciar_streamlit_seguro():
    """Inicia Streamlit con configuración segura."""
    print("=" * 60)
    print("INICIANDO DASHBOARD VIGÍA RH - MODO SEGURO")
    print("=" * 60)
    
    # Limpiar puerto
    print("Limpiando puerto 8501...")
    limpiar_puerto_8501()
    
    # Esperar a que puerto esté libre
    max_intentos = 10
    for i in range(max_intentos):
        if verificar_puerto_libre():
            print("Puerto 8501 libre [OK]")
            break
        print(f"Esperando liberación de puerto... ({i+1}/{max_intentos})")
        time.sleep(1)
    else:
        print("ERROR: No se pudo liberar el puerto 8501")
        return False
    
    # Configuración segura de Streamlit
    # Desactivar auto-reload para evitar inestabilidad durante desarrollo
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "dashboard/app.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--logger.level", "warning",  # Reducir verbosity
    ]
    
    print("Iniciando Streamlit con configuración segura...")
    print(f"Comando: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        # Iniciar proceso
        proceso = subprocess.Popen(cmd, cwd=Path(__file__).parent)
        
        print(f"Streamlit iniciado con PID: {proceso.pid}")
        print("Dashboard disponible en: http://localhost:8501")
        print("Presiona Ctrl+C para detener (monitoreo activo)")
        print("=" * 60)
        
        # Monitoreo activo
        while True:
            time.sleep(5)
            
            # Verificar que el proceso siga vivo
            if proceso.poll() is not None:
                print("[WARNING] Streamlit se detuvo inesperadamente")
                print("Código de salida:", proceso.poll())
                print("Reiniciando en 3 segundos...")
                time.sleep(3)
                return iniciar_streamlit_seguro()  # Reinicio automático
            
            # Verificar que el puerto siga respondiendo
            if not verificar_puerto_libre():
                print("[OK] Puerto 8501 respondiendo correctamente")
            else:
                print("[WARNING] Puerto 8501 no responde, posible caída")
                print("Reiniciando en 3 segundos...")
                proceso.terminate()
                time.sleep(3)
                return iniciar_streamlit_seguro()
                
    except KeyboardInterrupt:
        print("\nDeteniendo Streamlit...")
        proceso.terminate()
        proceso.wait(timeout=5)
        print("Streamlit detenido correctamente")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import psutil
    except ImportError:
        print("Instalando psutil para monitoreo de procesos...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
    
    # Iniciar con monitoreo
    exit_code = 0
    max_reinicios = 5
    intento = 0
    
    while intento < max_reinicios:
        if iniciar_streamlit_seguro():
            break
        intento += 1
        if intento < max_reinicios:
            print(f"Reinicio {intento}/{max_reinicios} en 5 segundos...")
            time.sleep(5)
    
    if intento >= max_reinicios:
        print("ERROR: Máximo número de reinicios alcanzado")
        exit_code = 1
    
    sys.exit(exit_code)
