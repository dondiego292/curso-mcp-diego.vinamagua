import re
from typing import Dict, List, Any


def validar_contrasena(password: str, min_longitud: int = 10) -> Dict[str, Any]:
    """
    Valida la seguridad de una contraseña evaluando los siguientes criterios:
    - No debe estar vacía.
    - Longitud mínima (por defecto: 10 caracteres).
    - Al menos una letra mayúscula.
    - Al menos una letra minúscula.
    - Al menos un número.
    - Al menos un carácter especial o símbolo.

    :param password: La contraseña a validar.
    :param min_longitud: Longitud mínima requerida (default: 10).
    :return: Un diccionario con el resultado de la validación y la lista de errores encontrados.
    """
    errores: List[str] = []

    # Validar si es nula o vacía
    if not password or not password.strip():
        return {
            "valida": False,
            "errores": ["La contraseña no puede estar vacía."]
        }

    # 1. Longitud mínima
    if len(password) < min_longitud:
        errores.append(f"Debe tener al menos {min_longitud} caracteres (tiene {len(password)}).")

    # 2. Al menos una letra mayúscula
    if not re.search(r"[A-Z]", password):
        errores.append("Debe contener al menos una letra mayúscula.")

    # 3. Al menos una letra minúscula
    if not re.search(r"[a-z]", password):
        errores.append("Debe contener al menos una letra minúscula.")

    # 4. Al menos un número
    if not re.search(r"[0-9]", password):
        errores.append("Debe contener al menos un número.")

    # 5. Al menos un carácter especial / símbolo
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]", password):
        errores.append("Debe contener al menos un carácter especial o símbolo (!@#$%^&*...).")

    return {
        "valida": len(errores) == 0,
        "errores": errores
    }


def es_contrasena_segura(password: str, min_longitud: int = 10) -> bool:
    """Devuelve True si la contraseña cumple todos los criterios de seguridad."""
    return validar_contrasena(password, min_longitud)["valida"]


def validar_email(email: str) -> Dict[str, Any]:
    """
    Valida el formato de una dirección de correo electrónico.
    - No debe estar vacío ni contener solo espacios.
    - No debe contener espacios intermedios.
    - Debe contener exactamente un '@'.
    - La parte local (usuario) debe ser válida.
    - El dominio debe contener al menos un punto y una extensión válida (mínimo 2 letras).

    :param email: Correo electrónico a validar.
    :return: Diccionario indicando si es válido y los errores detectados.
    """
    errores: List[str] = []

    if not email or not email.strip():
        return {
            "valido": False,
            "errores": ["El correo electrónico no puede estar vacío."]
        }

    email_limpio = email.strip()

    # Verificar si contiene espacios
    if " " in email_limpio:
        errores.append("El correo no debe contener espacios en blanco.")

    # Verificar presencia y cantidad de '@'
    if email_limpio.count("@") == 0:
        errores.append("Debe contener el símbolo '@'.")
    elif email_limpio.count("@") > 1:
        errores.append("No puede contener más de un símbolo '@'.")
    else:
        usuario, dominio = email_limpio.split("@", 1)

        # Validar parte local (usuario)
        if not usuario:
            errores.append("Falta el nombre de usuario antes del '@'.")
        elif not re.match(r"^[a-zA-Z0-9_.+-]+$", usuario):
            errores.append("El nombre de usuario contiene caracteres no permitidos.")

        # Validar dominio
        if not dominio:
            errores.append("Falta el dominio después del '@'.")
        elif "." not in dominio:
            errores.append("El dominio debe incluir una extensión (ejemplo: .com, .org).")
        else:
            # Validar formato general del dominio con regex
            patron_dominio = r"^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
            if not re.match(patron_dominio, dominio):
                errores.append("El formato del dominio no es válido (ejemplo: dominio.com).")

    return {
        "valido": len(errores) == 0,
        "errores": errores
    }


def es_email_valido(email: str) -> bool:
    """Devuelve True si el correo tiene un formato válido."""
    return validar_email(email)["valido"]


def es_usuario_admin(datos_usuario: Dict[str, Any]) -> bool:
    """
    Determina si un usuario tiene rol de administrador.
    Reconoce claves como 'rol', 'role', 'es_admin' o 'is_admin'.
    """
    rol = str(datos_usuario.get("rol") or datos_usuario.get("role") or "").strip().lower()
    return bool(
        datos_usuario.get("es_admin") is True
        or datos_usuario.get("is_admin") is True
        or rol in ["admin", "administrador", "administrator"]
    )


def validar_usuario(datos_usuario: Dict[str, Any], validar_contrasena_admin: bool = False) -> Dict[str, Any]:
    """
    Valida un usuario individual con sus campos de email y contraseña.
    - La validación de contraseña es opcional para administradores (es_admin=True o rol='admin').
      Si el administrador no define contraseña o define una sin restricciones, se considera válido.
    - Para usuarios regulares, la contraseña es obligatoria y se validan todos los criterios.

    :param datos_usuario: Diccionario con la información del usuario.
    :param validar_contrasena_admin: Si es True, fuerza la validación de contraseña incluso para admins.
    :return: Diccionario con el resultado de la validación consolidada.
    """
    nombre = datos_usuario.get("nombre") or datos_usuario.get("usuario") or "Usuario anónimo"
    email = datos_usuario.get("email") or datos_usuario.get("correo") or ""
    password = datos_usuario.get("password") or datos_usuario.get("contrasena") or ""
    es_admin = es_usuario_admin(datos_usuario)

    # Validar email (obligatorio para todos)
    resultado_email = validar_email(email)

    # Validar contraseña (opcional para administradores)
    if es_admin and not validar_contrasena_admin:
        resultado_pass = {
            "valida": True,
            "errores": [],
            "opcional": True,
            "detalle": "Validación de contraseña omitida (usuario administrador)"
        }
    else:
        resultado_pass = validar_contrasena(password)
        resultado_pass["opcional"] = False

    todos_errores = []
    if not resultado_email["valido"]:
        todos_errores.extend([f"[Email] {err}" for err in resultado_email["errores"]])
    if not resultado_pass["valida"]:
        todos_errores.extend([f"[Contraseña] {err}" for err in resultado_pass["errores"]])

    es_valido = resultado_email["valido"] and resultado_pass["valida"]

    return {
        "usuario": nombre,
        "email": email,
        "es_admin": es_admin,
        "valido": es_valido,
        "contrasena_opcional": resultado_pass.get("opcional", False),
        "errores_email": resultado_email["errores"],
        "errores_contrasena": resultado_pass["errores"],
        "todos_errores": todos_errores
    }


def validar_lista_usuarios(
    usuarios: List[Dict[str, Any]],
    detectar_emails_duplicados: bool = True,
    validar_contrasena_admin: bool = False
) -> Dict[str, Any]:
    """
    Valida una lista completa de usuarios, verificando:
    - Formato de email para cada usuario.
    - Seguridad de contraseña (opcional para administradores).
    - Detección opcional de correos duplicados en la lista.

    :param usuarios: Lista de diccionarios de usuarios.
    :param detectar_emails_duplicados: Si True, marca como error correos repetidos.
    :param validar_contrasena_admin: Si True, exige contraseña segura a administradores también.
    :return: Diccionario con los usuarios válidos, inválidos y estadísticas generales.
    """
    validos: List[Dict[str, Any]] = []
    invalidos: List[Dict[str, Any]] = []
    emails_vistos: Dict[str, List[str]] = {}

    for u in usuarios:
        res = validar_usuario(u, validar_contrasena_admin=validar_contrasena_admin)
        email_normalizado = res["email"].strip().lower()

        # Chequeo de correos duplicados
        if detectar_emails_duplicados and email_normalizado:
            if email_normalizado in emails_vistos:
                emails_vistos[email_normalizado].append(res["usuario"])
                res["valido"] = False
                res["todos_errores"].append(f"[Email] El correo '{res['email']}' está repetido en la lista.")
            else:
                emails_vistos[email_normalizado] = [res["usuario"]]

        if res["valido"]:
            validos.append(res)
        else:
            invalidos.append(res)

    return {
        "total": len(usuarios),
        "total_validos": len(validos),
        "total_invalidos": len(invalidos),
        "usuarios_validos": validos,
        "usuarios_invalidos": invalidos
    }


if __name__ == "__main__":
    print("=" * 68)
    print("     DEMOSTRACIÓN DE VALIDACIÓN CON CONTRASEÑA OPCIONAL PARA ADMINS ")
    print("=" * 68)

    lista_usuarios_ejemplo = [
        {
            "nombre": "Admin Supremo",
            "email": "admin@empresa.com",
            "rol": "admin",
            "password": ""  # Admin sin contraseña -> VÁLIDO (opcional)
        },
        {
            "nombre": "Supervisora Admin",
            "email": "supervisora@empresa.com",
            "es_admin": True,
            "password": "123"  # Admin con contraseña simple -> VÁLIDO (opcional)
        },
        {
            "nombre": "Ana García (Regular)",
            "email": "ana.garcia@empresa.com",
            "rol": "usuario",
            "password": "MiPasswordSeguro#2026"  # Regular con clave fuerte -> VÁLIDO
        },
        {
            "nombre": "Carlos López (Regular)",
            "email": "carlos@empresa.com",
            "rol": "usuario",
            "password": ""  # Regular sin contraseña -> INVÁLIDO (obligatoria)
        },
        {
            "nombre": "Beatriz Morales (Regular)",
            "email": "beatriz@empresa.com",
            "rol": "usuario",
            "password": "123"  # Regular con clave débil -> INVÁLIDO
        },
        {
            "nombre": "Admin Con Email Malo",
            "email": "admin_sin_arroba",
            "rol": "admin",
            "password": ""  # Admin pero con email inválido -> INVÁLIDO por email
        }
    ]

    reporte = validar_lista_usuarios(lista_usuarios_ejemplo)

    print(f"\nTotal de usuarios procesados: {reporte['total']}")
    print(f" Usuarios válidos: {reporte['total_validos']}")
    print(f"❌ Usuarios inválidos: {reporte['total_invalidos']}\n")

    print("--- USUARIOS VÁLIDOS ---")
    for u in reporte["usuarios_validos"]:
        admin_tag = "[ADMIN - Clave Opcional]" if u["es_admin"] else "[USUARIO]"
        print(f" {admin_tag} {u['usuario']} ({u['email']})")

    print("\n--- USUARIOS INVÁLIDOS ---")
    for u in reporte["usuarios_invalidos"]:
        admin_tag = "[ADMIN]" if u["es_admin"] else "[USUARIO]"
        print(f"❌ {admin_tag} {u['usuario']} ({u['email']}):")
        for err in u["todos_errores"]:
            print(f"   • {err}")

    print("\n" + "=" * 68)
