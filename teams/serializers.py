from rest_framework import serializers
from .models import Team
from profiles.models import StudentProfile, SupervisorProfile
from topics.models import ThesisTopic

class TeamSerializer(serializers.ModelSerializer):
    """ Serializer for Team model """
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=StudentProfile.objects.all())
    owner = serializers.PrimaryKeyRelatedField(queryset=SupervisorProfile.objects.all(), required=False)
    thesis_topic = serializers.PrimaryKeyRelatedField(queryset=ThesisTopic.objects.all())

    class Meta:
        model = Team
        fields = ['id', 'thesis_topic', 'owner', 'members', 'status', 'supervisor']

    def validate(self, data):
        """ Ensure a student can only apply to 1 team at a time """
        user = self.context['request'].user
        if hasattr(user, 'student_profile'):
            if user.student_profile.teams.filter(status="open").exists():
                raise serializers.ValidationError("You can only apply to 1 team at a time.")
        return data

    # def create(self, validated_data):
    #     """ Create a new team with the correct owner """
    #     user = self.context['request'].user
    #     if hasattr(user, 'student_profile'):
    #         validated_data['owner'] = user
    #     elif hasattr(user, 'supervisor_profile'):
    #         validated_data['owner'] = user
    #     return super().create(validated_data)
