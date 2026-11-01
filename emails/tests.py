from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, Mock


class EmailViewsTests(TestCase):

    def test_home_page(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)

    @patch('emails.views.send_welcome_emails.delay')
    def test_mail_sent(self, mock_delay):
        mock_task = Mock()
        mock_task.id = 'test-task-123'
        mock_delay.return_value = mock_task

        response = self.client.post(reverse('mail_sender'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test-task-123')
        mock_delay.assert_called_once()