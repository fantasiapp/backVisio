from .models import *
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .dataStructure import buildTree, formatSales
import json

class DefaultView(APIView):
    permission_classes = (IsAuthenticated,)
class Data(DefaultView):
    config = None
    with open('visioServer/config.json', 'r') as cfgFile:
        config = json.load(cfgFile)
    salesDict = None
    try:
        with open('visioServer/salesDict.json', 'r') as jsonFile:
            salesDict = json.load(jsonFile)
    except:
        salesDict = formatSales(Ventes.objects.all())
        with open('visioServer/salesDict.json', 'w') as jsonFile:
            json.dump(salesDict, jsonFile)

    def get(self, request):
        data = {}
        data['Pdv'] = self.__formatPdv([model_to_dict(object) for object in Pdv.objects.all()])
        regularModels = [eval(modelName) for modelName in self.config["regularModels"]]
        for model in regularModels:
            data.update({model.__name__: {object.id: object.name for object in model.objects.all()}})
        data['geoTree'] = buildTree('root', self.config["geoTreeStructure"], data['Pdv'])
        data['brandTree'] = buildTree('root', self.config["brandTreeStructure"], data['Pdv'])
        return Response(data)
    
    def __formatPdv(self, pdvs:list):
        return {pdv['id']:[value for key, value in pdv.items() if key != 'id'] + [self.salesDict.get(str(pdv['id']), [])] for pdv in pdvs}
