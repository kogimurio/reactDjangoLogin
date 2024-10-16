from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:

            #check if the user exist
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError("User does not exist.")
            
            #authenticate the user with the provided password
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("This account is deactivated.")
            else:
                raise serializers.ValidationError("Incorrect Password.")
        else:
            raise serializers.ValidationError("Must include both username and password.")

        data['user'] = user
        return data

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, data):
        """
        Validate that the refresh token is provided.
        """
        refresh_token = data.get('refresh')

        if not refresh_token:
            raise serializers.ValidationError("Refresh token is required.")
        
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(min_length=8, write_only=True)


    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        #check if the two passwords match
        if data['password']!= data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return data
    
    def validate_email(self, data):
        #check if the email already exists in the database
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError("Email address already exists.")
        return data

    def create(self, validated_data):

        #remove password2 because its not used to create the user
        validated_data.pop('password2')
        
        #create the user with the valid data
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],       
        )
        return user
