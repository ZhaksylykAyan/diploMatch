from rest_framework import serializers

from teams.models import Team
from .models import ThesisTopic

class ThesisTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesisTopic
        fields = '__all__'

    def validate(self, data):
        """ Ensure only 1 topic per student and max 10 for supervisors """
        user = self.context['request'].user
        if hasattr(user, 'student_profile'):
            if ThesisTopic.objects.filter(created_by_student=user.student_profile).exists():
                raise serializers.ValidationError("Students can create only one thesis topic.")
        elif hasattr(user, 'supervisor_profile'):
            if ThesisTopic.objects.filter(created_by_supervisor=user.supervisor_profile).count() >= 10:
                raise serializers.ValidationError("Supervisors can create up to 10 thesis topics.")
        return data

    def create(self, validated_data):
        """ Auto-create a team when a thesis topic is created """
        user = self.context['request'].user
        if hasattr(user, 'student_profile'):
            validated_data['created_by_student'] = user.student_profile
        elif hasattr(user, 'supervisor_profile'):
            validated_data['created_by_supervisor'] = user.supervisor_profile
        thesis_topic = super().create(validated_data)

        # Auto-create a team with the correct owner
        team_owner = user  # Automatically assign the user who created the topic as team owner
        Team.objects.create(
            thesis_topic=thesis_topic,
            owner=team_owner,
            status="open"
        )

        return thesis_topic