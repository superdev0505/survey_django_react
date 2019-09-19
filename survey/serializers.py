from datetime import timedelta

from rest_framework import serializers
from rest_framework.serializers import *
from social_django.models import UserSocialAuth

from survey.models import SurveyUser, IPHistory, UserFlags, UserHistory, UserFeedback, UserBanHistory
from survey.submodels.fingerprint import UserFingerprint, Fingerprint
from survey.submodels.metrics import Metric
from survey.submodels.provider import Provider
from survey.submodels.survey import Choice, Question, Survey, QuestionAnswer
from survey.submodels.tag import Tag
from survey.submodels.transaction import Transaction, ProviderTransaction, UserTransaction


class UserSerializer(ModelSerializer):
    class Meta:
        model = SurveyUser
        fields = ('username', 'is_staff', 'is_superuser', 'is_anonymous')


class UserAdminSerializer(ModelSerializer):
    class Meta:
        model = SurveyUser
        fields = ('id', 'ref_id', 'provider', 'first_name', 'last_name')


class IPHistorySerializer(ModelSerializer):
    class Meta:
        model = IPHistory
        fields = ('ip', 'date',)


class UserHistorySerializer(ModelSerializer):
    class Meta:
        model = UserHistory
        fields = ('changes', 'date',)


class UserFlagsSerializer(ModelSerializer):
    class Meta:
        model = UserFlags
        fields = ('key', 'date',)


class ProviderSerializer(ModelSerializer):
    class Meta:
        model = Provider
        fields = ('name','id')


class UserFeedbackSerializer(ModelSerializer):
    user=UserAdminSerializer(read_only=True)

    class Meta:
        model = UserFeedback
        fields = ('date', 'type', 'text', 'user', 'fingerprint')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'text',)


class ChoiceSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Choice
        fields = ('id', 'question', 'text', 'tags')


class ProviderTransactionSerializer(ModelSerializer):
    class Meta:
        model = ProviderTransaction
        fields = ('to_account', 'amount', 'status', 'date_created', 'date_sent', 'payout_id', 'payout_status', 'payout_currency', 'payout_user_hash')


class UserTransactionSerializer(ModelSerializer):
    class Meta:
        model = UserTransaction
        fields = ('to_account', 'amount', 'status', 'date_created', 'date_sent', 'payout_id', 'payout_status', 'payout_currency', 'payout_user_hash')


class QuestionSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    choice_set = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'thumbnail', 'text', 'answer_type', 'tags', 'choice_set', 'enabled')


class SurveySerializer(ModelSerializer):
    current_question = QuestionSerializer(read_only=True)
    usertransaction_set = UserTransactionSerializer(many=True, read_only=True)
    providertransaction_set = ProviderTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'created', 'solved', 'current_question', 'status', 'usertransaction_set', 'providertransaction_set')


class SurveyRateSerializer(ModelSerializer):
    class Meta:
        model = Survey
        fields = ('status',)


class QuestionAnswerSerializer(ModelSerializer):
    choice = ChoiceSerializer(many=True, read_only=True)
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = QuestionAnswer
        fields = ('question', 'choice', 'created')


class SurveyProgressSerializer(ModelSerializer):
    class Meta:
        model = Survey
        fields = ('id', 'created', 'solved', 'questionanswer_set')


class SocialAuthSerializer(ModelSerializer):
    class Meta:
        model = UserSocialAuth
        fields = ('provider', 'uid',)


class UserBanHistorySerializer(ModelSerializer):
    class Meta:
        model = UserBanHistory
        fields = ('user', 'date', 'timeout', 'suspend_till', 'reason')


class FingerprintSerizlizer(ModelSerializer):
    class Meta:
        model = Fingerprint
        fields = ('userAgent', 'language', 'colorDepth', 'deviceMemory', 'hardwareConcurrency', 'screenResolution', 'availableScreenResolution', 'timezoneOffset', 'timezone', 'sessionStorage', 'localStorage', 'indexedDb', 'addBehavior', 'openDatabase', 'cpuClass', 'platform', 'plugins', 'webglVendorAndRenderer', 'adBlock', 'hasLiedLanguages', 'hasLiedResolution', 'hasLiedOs', 'hasLiedBrowser', 'touchSupport', 'fonts', 'audio')


class UserFingerprintSerizlizer(ModelSerializer):
    fingerprint = FingerprintSerizlizer(read_only=True)
    class Meta:
        model = UserFingerprint
        fields = ('date', 'fingerprint')


class UserListSerializer(ModelSerializer):
    ip_history = IPHistorySerializer(many=True, read_only=True)
    user_flags = serializers.SerializerMethodField('get_last_flags')
    provider = ProviderSerializer(read_only=True)
    current_survey = SurveyProgressSerializer(read_only=True)
    last_survey = SurveyProgressSerializer(read_only=True)
    user_ban_history = UserBanHistorySerializer(many=True, read_only=True)
    survey_count = serializers.IntegerField( read_only=True)
    fingerprint = UserFingerprintSerizlizer(many=True, read_only=True)

    class Meta:
        model = SurveyUser
        fields = ('id', 'ref_id', 'is_suspended', 'user_ban_history', 'date_joined', 'provider', 'provider_user_id', 'username', 'ip_history', 'user_flags', 'fingerprint', 'is_active', 'current_survey', 'last_survey', 'survey_count')

    def get_last_flags(self, user):
        qs = UserFlags.objects.filter(user=user, date__gte=timezone.now() - timedelta(days=2))
        serializer = UserFlagsSerializer(instance=qs, many=True, read_only=True)
        return serializer.data


class MetricSerializer(ModelSerializer):
    class Meta:
        model = Metric
        fields = ('date', 'survey', 'questions', 'survey_success', 'survey_unsuccess', 'transaction', 'users_registered')