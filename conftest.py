# -*- coding: utf-8 -*-
"""Configuracion global de pytest.

Acelera los tests con:
- MD5PasswordHasher (100x mas rapido que PBKDF2)
- Sin validadores de password
"""
import pytest


@pytest.fixture(autouse=True)
def use_fast_password_hasher(settings):
    settings.PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]


@pytest.fixture(autouse=True)
def disable_password_validation(settings):
    settings.AUTH_PASSWORD_VALIDATORS = []
