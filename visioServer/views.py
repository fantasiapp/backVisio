from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .modelStructure.dataDashboard import DataDashboard, Navigation

class DefaultView(APIView):
    permission_classes = (IsAuthenticated,)

class Data(DefaultView):
    dataDashBoard = DataDashboard()

    def get(self, request):
        if 'action' in request.GET:
            print("ici", request.GET["action"])
            if request.GET["action"] == "navigation":
                dataNavigation = Navigation()
                return Response(dataNavigation.dataQuery)
        return Response(self.dataDashBoard.dataQuery)
