from django.test import TestCase

from survey.models import SurveyUser
from survey.submodels.provider import Provider, PAYOUT_USER_BITCOIN


class UserTestCase(TestCase):

    user = None
    provider = None
    user_ref_id = None

    USER_ID = 'testman'
    PROVIDER = 'test'

    BITCOIN_ADDRESS = '123'
    BAD_BITCOIN_ADDRESS = 'uyqwteytqwueyq'
    GOOD_BITCOIN_ADDRESS = '1Eymp19t8KT8dzWy9NW1QJGGB18sdYWq9s'

    REF_ID = 'test:testman'
    BAD_REF_ID = 'qwe1asd23zxczxc'
    GOOD_REF_ID = 'qwe1qwe2'

    def setUp(self):
        self.provider, provider_created = Provider.objects.get_or_create(name=self.PROVIDER, payout_method=PAYOUT_USER_BITCOIN)
        self.user, user_created = SurveyUser.get_or_create_user(
            provider=self.provider, provider_user_id=self.USER_ID, ip='1.1.1.1'
        )
        if user_created:
            self.user_ref_id = self.user.ref_id
        self.user.bitcoin_address = self.BITCOIN_ADDRESS

    def test_user_update_bad(self):
        user = self.user
        data = {
            'bitcoin_address': self.BAD_BITCOIN_ADDRESS,
            'ref_id': self.BAD_REF_ID
        }

        self.assertEqual(user.bitcoin_address, self.BITCOIN_ADDRESS)
        self.assertEqual(user.ref_id, self.user_ref_id)

        with self.assertRaises(Exception) as cm:
            self.user.update_data(data)
        the_exception = cm.exception
        message,code = the_exception.args
        self.assertEqual(code, 412)
        self.assertEqual(user.bitcoin_address, self.BITCOIN_ADDRESS)
        self.assertEqual(user.ref_id, self.user_ref_id)

    def test_user_update_good(self):
        user = self.user
        data = {
            'bitcoin_address': self.GOOD_BITCOIN_ADDRESS,
            'ref_id': self.GOOD_REF_ID
        }
        self.assertEqual(user.bitcoin_address, self.BITCOIN_ADDRESS)
        self.assertEqual(user.ref_id, self.user_ref_id)
        self.user.update_data(data)
        self.assertEqual(user.bitcoin_address, self.GOOD_BITCOIN_ADDRESS)
        self.assertEqual(user.ref_id, self.GOOD_REF_ID)

    def tearDown(self):
        self.user.delete()

