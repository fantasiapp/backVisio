from django.http.response import JsonResponse
# from django.shortcuts import render
from django.contrib import auth
from .models import *
#import django.apps
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .dataStructure import formatPdv, buildStructure, diceSales
import time

class DefaultView(APIView):
    permission_classes = (IsAuthenticated,)
class Data(DefaultView):
    salesDict = diceSales(Ventes.objects.all())

    def get(self, request):
        data = {}
        data['Pdv'] = formatPdv([model_to_dict(object) for object in Pdv.objects.all()], self.salesDict)
        # A terme il faudra faire quelque chose de plus générique avec django.apps.apps.get_models() pour récup les models
        # Ou alors on peut juste stocker cette liste dans une config
        for model in [Drv, Agent, AgentFinitions, Dep, Bassin, Ville, SegmentMarketing, SegmentCommercial, Enseigne, Ensemble, SousEnsemble, Site, Produit, Industrie]:
            data.update({model.__name__: {object.id: object.name for object in model.objects.all()}})
        geoStructure = [2,3,4,5] # Correspond à Drv, Agent, Département, Bassin
        brandStructure = [11, 12, 13] # Correspond à Enseigne, Ensemble, Sous-Ensemble
        data['geoTree'] = buildStructure('root', geoStructure, data['Pdv'])
        data['brandTree'] = buildStructure('root', brandStructure, data['Pdv'])
        return Response(data)
