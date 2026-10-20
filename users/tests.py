from rest_framework.test import APITestCase

from .models import User


class InscriptionTests(APITestCase):

    def test_refuse_moins_de_15_ans(self):
        reponse = self.client.post('/api/users/', {
            'username': 'alice', 'password': 'Motdepasse-solide-42', 'age': 12,
        }, format='json')
        self.assertEqual(reponse.status_code, 400)

    def test_accepte_15_ans(self):
        reponse = self.client.post('/api/users/', {
            'username': 'emma', 'password': 'Motdepasse-solide-42', 'age': 15,
        }, format='json')
        self.assertEqual(reponse.status_code, 201)


class DeconnexionTests(APITestCase):

    def setUp(self):
        User.objects.create_user(username='erin', password='Motdepasse-solide-42', age=30)
        reponse = self.client.post('/api/token/', {
            'username': 'erin', 'password': 'Motdepasse-solide-42',
        }, format='json')
        self.refresh = reponse.data['refresh']

    def test_refresh_refuse_apres_deconnexion(self):
        reponse = self.client.post('/api/token/blacklist/', {'refresh': self.refresh}, format='json')
        self.assertEqual(reponse.status_code, 200)
        reponse = self.client.post('/api/token/refresh/', {'refresh': self.refresh}, format='json')
        self.assertEqual(reponse.status_code, 401)
