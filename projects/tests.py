from rest_framework.test import APITestCase

from users.models import User
from .models import Project, Contributor, Issue, Comment
from django.db import connection
from django.test.utils import CaptureQueriesContext

MDP = 'Motdepasse-solide-42'


class ScenarioTests(APITestCase):

    def setUp(self):
        self.carol = User.objects.create_user(username='carol', password=MDP, age=30)
        self.bob = User.objects.create_user(username='bob', password=MDP, age=30)
        self.dave = User.objects.create_user(username='dave', password=MDP, age=30)
        self.projet = Project.objects.create(
            title='SoftDesk', description='API', type='BACKEND', author=self.carol)
        Contributor.objects.create(user=self.carol, project=self.projet)
        Contributor.objects.create(user=self.bob, project=self.projet)
        self.issue = Issue.objects.create(
            title='Bug login', description='Erreur 500', priority='HIGH', tag='BUG',
            project=self.projet, author=self.carol)
        self.url_issues = f'/api/projects/{self.projet.id}/issues/'
        self.url_issue = f'{self.url_issues}{self.issue.id}/'
        self.url_comments = f'{self.url_issue}comments/'

    def nouvelle_issue(self, assigned_to=None):
        donnees = {'title': 'Bug', 'description': 'Détail', 'priority': 'LOW', 'tag': 'BUG'}
        if assigned_to:
            donnees['assigned_to'] = assigned_to
        return self.client.post(self.url_issues, donnees, format='json')

    def test_issue_assignee_a_un_contributeur(self):
        self.client.force_authenticate(user=self.carol)
        reponse = self.nouvelle_issue('bob')
        self.assertEqual(reponse.status_code, 201)
        self.assertEqual(reponse.data['status'], 'TODO')
        self.assertEqual(reponse.data['author'], 'carol')

    def test_assignation_pseudo_inconnu(self):
        self.client.force_authenticate(user=self.carol)
        self.assertEqual(self.nouvelle_issue('alice').status_code, 400)

    def test_assignation_non_contributeur(self):
        self.client.force_authenticate(user=self.carol)
        self.assertEqual(self.nouvelle_issue('dave').status_code, 400)

    def test_contributeur_cree_une_issue(self):
        self.client.force_authenticate(user=self.bob)
        self.assertEqual(self.nouvelle_issue().status_code, 201)

    def test_non_auteur_ne_modifie_pas_une_issue(self):
        self.client.force_authenticate(user=self.bob)
        reponse = self.client.patch(self.url_issue, {'status': 'FINISHED'}, format='json')
        self.assertEqual(reponse.status_code, 403)

    def test_contributeurs_commentent(self):
        for utilisateur in (self.carol, self.bob):
            self.client.force_authenticate(user=utilisateur)
            reponse = self.client.post(self.url_comments, {'description': 'Vu'}, format='json')
            self.assertEqual(reponse.status_code, 201)

    def test_non_contributeur_recoit_404(self):
        self.client.force_authenticate(user=self.dave)
        reponse = self.client.post(self.url_comments, {'description': 'Intrus'}, format='json')
        self.assertEqual(reponse.status_code, 404)

    def test_non_auteur_ne_modifie_pas_un_commentaire(self):
        commentaire = Comment.objects.create(description='Je regarde', issue=self.issue, author=self.carol)
        self.client.force_authenticate(user=self.bob)
        reponse = self.client.patch(f'{self.url_comments}{commentaire.id}/', {'description': 'Modifié'}, format='json')
        self.assertEqual(reponse.status_code, 403)

    def test_non_auteur_ne_supprime_pas_le_projet(self):
        self.client.force_authenticate(user=self.bob)
        reponse = self.client.delete(f'/api/projects/{self.projet.id}/')
        self.assertEqual(reponse.status_code, 403)

    def test_liste_paginee(self):
        self.client.force_authenticate(user=self.carol)
        reponse = self.client.get(self.url_issues)
        self.assertEqual(reponse.status_code, 200)
        self.assertIn('results', reponse.data)
        self.assertEqual(reponse.data['count'], 1)

    def compter_requetes(self):
        with CaptureQueriesContext(connection) as requetes:
            self.client.get(self.url_issues)
        return len(requetes)

    def test_nombre_de_requetes_constant(self):
        self.client.force_authenticate(user=self.carol)
        avant = self.compter_requetes()
        for numero in range(5):
            Issue.objects.create(
                title=f'Issue {numero}', description='Détail', priority='LOW', tag='BUG',
                project=self.projet, author=self.bob, assigned_to=self.carol)
        self.assertEqual(self.compter_requetes(), avant)
