from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .modelStructure.dataDashboard import DataDashboard, Navigation
from visioServer.models import UserProfile

class DefaultView(APIView):
    permission_classes = (IsAuthenticated,)

class Data(DefaultView):

    def get(self, request):
        currentUser = request.user
        userGroup = request.user.groups.values_list('name', flat=True)
        currentProfile = UserProfile.objects.filter(user=currentUser)
        if userGroup:
            userIdGeo = currentProfile[0].idGeo if currentProfile else None
        else:
            return Response({"error":f"no profile defined for {currentUser.username} defined"})
        if 'action' in request.GET:
            action = request.GET["action"]
            if action == "navigation":
                dataNavigation = Navigation(userIdGeo, userGroup[0])
                return Response(dataNavigation.dataQuery)
            if action == "dashboard":
                dataDashBoard = DataDashboard()
                return Response(dataDashBoard.dataQuery)
            return Response({"error":f"action {action} unknown"})
        return Response({"error":f"no action defined"})
