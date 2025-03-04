from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import StudentProfile, SupervisorProfile, DeanOfficeProfile, Skill
from .serializers import StudentProfileSerializer, SupervisorProfileSerializer, DeanOfficeProfileSerializer, SkillSerializer

User = get_user_model()

class SkillListView(generics.ListCreateAPIView):
    """ API to get and create skills """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class ProfileCompletionView(generics.UpdateAPIView):
    """ API to complete user profile (Student, Supervisor, Dean's Office) """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        if user.role == 'student':
            return StudentProfileSerializer
        elif user.role == 'supervisor':
            return SupervisorProfileSerializer
        elif user.role == 'dean_office':
            return DeanOfficeProfileSerializer

    def get_object(self):
        """ Return the appropriate profile based on user role """
        user = self.request.user
        if user.role == 'student':
            return user.student_profile
        elif user.role == 'supervisor':
            return user.supervisor_profile
        elif user.role == 'dean_office':
            return user.dean_office_profile

    def perform_update(self, serializer):
        """ Mark profile as completed after update """
        serializer.save()
        self.request.user.is_profile_completed = True
        self.request.user.save()