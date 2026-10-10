# accounts/tests.py
from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from .models import User


class UserModelTests(TestCase):
    """Tests del modelo User personalizado."""

    def test_crear_usuario_normal(self):
        user = User.objects.create_user(
            username="testuser",
            password="Compleja123!",
            email="test@example.com",
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("Compleja123!"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_crear_superusuario(self):
        admin = User.objects.create_superuser(
            username="admin_test",
            password="Compleja123!",
            email="admin@example.com",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_usuario_str(self):
        user = User.objects.create_user(username="juan", password="x12345678")
        self.assertEqual(str(user), "juan")

    def test_campos_personalizados(self):
        user = User.objects.create_user(
            username="maria",
            password="x12345678",
            idioma_nativo="Espanol",
            zona_horaria="UTC-5",
        )
        self.assertEqual(user.idioma_nativo, "Espanol")
        self.assertEqual(user.zona_horaria, "UTC-5")


class RegistroViewTests(TestCase):
    """Tests de la vista de registro."""

    def setUp(self):
        translation.activate("es")

    def tearDown(self):
        translation.deactivate()

    def test_get_registro_devuelve_200(self):
        response = self.client.get(reverse("accounts:registro"))
        self.assertEqual(response.status_code, 200)

    def test_post_registro_crea_usuario_y_redirige(self):
        response = self.client.post(reverse("accounts:registro"), {
            "username": "nuevo_user",
            "email": "nuevo@test.com",
            "password1": "Compleja123!",
            "password2": "Compleja123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nuevo_user").exists())

    def test_post_registro_password_no_coincide(self):
        response = self.client.post(reverse("accounts:registro"), {
            "username": "otro_user",
            "email": "otro@test.com",
            "password1": "Compleja123!",
            "password2": "OtraDiferente456!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="otro_user").exists())

    def test_post_registro_username_duplicado(self):
        User.objects.create_user(username="existente", password="Compleja123!")
        response = self.client.post(reverse("accounts:registro"), {
            "username": "existente",
            "email": "nuevo@test.com",
            "password1": "Compleja123!",
            "password2": "Compleja123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="existente").count(), 1)


class LoginViewTests(TestCase):
    """Tests de login/logout."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="logintest",
            password="Compleja123!",
        )

    def test_login_correcto(self):
        response = self.client.post("/es/accounts/login/", {
            "username": "logintest",
            "password": "Compleja123!",
        })
        self.assertEqual(response.status_code, 302)

    def test_login_password_incorrecto(self):
        response = self.client.post("/es/accounts/login/", {
            "username": "logintest",
            "password": "wrong_password",
        })
        self.assertEqual(response.status_code, 200)