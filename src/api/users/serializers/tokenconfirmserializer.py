from rest_framework import serializers


class TokenConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="Paste the token you got from the init endpoint here")