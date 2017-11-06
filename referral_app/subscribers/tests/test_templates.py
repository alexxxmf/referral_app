from bs4 import BeautifulSoup

from django.test import TestCase
from django.urls import reverse


class TestHomeTemplate(TestCase):
    """
    Test suite for the homepage templates
    """
    def test_home_template_title(self):
        response = self.client.get(reverse('home'), follow=True)
        self.assertNotEqual(response.content.find(b'<title>Home</title>'), -1)

    def test_home_template_form_rendered_properly(self):
        response = self.client.get(reverse('home'), follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')

        form_html_attr = soup.find(
            'form',
            attrs={
                "action": reverse('home'),
                "method": 'post',
                "role": 'form',
            })
        self.assertNotEqual(form_html_attr, None)
        email_input_attr = soup.find(
            'input',
            attrs={
                "maxlength": '100',
                "name": 'email',
                "type": 'email',
            })
        self.assertNotEqual(email_input_attr, None)
        submit_btn_attr = soup.find(
            'input',
            attrs={
                "type": 'submit',
                "value": 'Submit',
            })
        self.assertNotEqual(submit_btn_attr, None)


class TestConfirmationTemplate(TestCase):
    """
    Test suite for the confirmation templates
    """
    def test_confirmation_template_content_rendered_properly(self):
        response = self.client.get(reverse('confirmation_prompt'), follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_prompt = soup.find(
            'h1',
            attrs={
                "id": 'main_confirmation_prompt',
            }
        )
        self.assertNotEqual(main_prompt, None)
