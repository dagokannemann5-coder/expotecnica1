"""Genera el hash de la clave de administrador.
Uso:  python generar_hash.py
Copiá la línea que imprime en tu .env como ADMIN_PASSWORD_HASH='...'
"""
from getpass import getpass
from werkzeug.security import generate_password_hash
 
clave = getpass("Nueva clave de administrador: ")
print("\nPegá esto en tu .env (con las comillas simples):\n")
print(f"ADMIN_PASSWORD_HASH='{generate_password_hash(clave)}'")