# -*- coding: utf-8 -*-
"""
Servicio de autenticación y seguridad.
Encapsula la lógica de verificación de usuarios y credenciales.
"""
from typing import Optional
from ..domain.models import User


class AuthService:
    """Servicio de negocio para autenticación de usuarios."""

    def __init__(self, valid_username: str, valid_password: str):
        self._valid_username = valid_username
        self._valid_password = valid_password

    def authenticate(self, username: Optional[str], password: Optional[str]) -> Optional[User]:
        """Verifica las credenciales y retorna la entidad User si es válido."""
        if not username or not password:
            return None

        if username.strip() == self._valid_username and password == self._valid_password:
            return User(username=username.strip(), is_authenticated=True)

        return None
