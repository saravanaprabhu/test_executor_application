from rest_framework import serializers
from .models import Request, Test, Template,   Requester


class RequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requester
        fields = ('id', 'username')

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ('id', 'template_name')

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('test_env_id', 'system_status')

class RequestSerializer(serializers.ModelSerializer):
    username = RequesterSerializer()
    template = TemplateSerializer()
    test_details = TestSerializer()
    class Meta:
        model = Request
        fields = ('req_id', 'username','template','test_details','created','test_status')