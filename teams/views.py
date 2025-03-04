from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Team
from .serializers import TeamSerializer
from django.core.exceptions import ValidationError

class TeamCreateView(generics.CreateAPIView):
    """ Allows students and supervisors to create a team manually (not needed, as teams are auto-created). """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

class TeamListView(generics.ListAPIView):
    """ Lists all teams. """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]

class TeamDetailView(generics.RetrieveAPIView):
    """ Retrieves a single team. """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]

class ApplyToSupervisorView(APIView):
    """ Allows a team to apply to a supervisor if it meets skill requirements. """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)

            if team.status != "open":
                return Response({"error": "Team is not open for applications."}, status=status.HTTP_400_BAD_REQUEST)

            if not team.has_required_skills():
                return Response({"error": "Team does not meet the required skills."}, status=status.HTTP_400_BAD_REQUEST)

            team.status = "pending"
            team.save()
            return Response({"message": "Application sent to supervisor."}, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

class ApproveTeamView(APIView):
    """ Allows a supervisor to approve a team, making them the new owner. """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)

            if not hasattr(request.user, 'supervisor_profile'):
                return Response({"error": "Only supervisors can approve teams."}, status=status.HTTP_403_FORBIDDEN)

            if request.user.supervisor_profile.teams.count() >= 10:
                return Response({"error": "Supervisors can only manage up to 10 teams."}, status=status.HTTP_400_BAD_REQUEST)

            team.approve_team(request.user.supervisor_profile)
            return Response({"message": "Team approved successfully."}, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

class RejectTeamView(APIView):
    """ Allows a supervisor to reject a team. """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)

            if not hasattr(request.user, 'supervisor_profile'):
                return Response({"error": "Only supervisors can reject teams."}, status=status.HTTP_403_FORBIDDEN)

            team.reject_team()
            return Response({"message": "Team rejected successfully."}, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
