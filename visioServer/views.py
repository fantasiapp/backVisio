from django.db.models import indexes
from .models import *
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .dataStructure import buildTree, formatSales
import json
from django.db.models.fields.related import ForeignKey

class DefaultView(APIView):
    permission_classes = (IsAuthenticated,)
class Data(DefaultView):
    config = None
    # Il faut faire en sorte que ce tricks ne soit fait qu'en local et pas sur le server, on peut utilser qqchose du genre "if debug :"
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
        formatedPdvs, data['Pdv'] = self.__formatPdv([model_to_dict(object) for object in Pdv.objects.all()])
        regularModels = [eval(modelName) for modelName in self.config["regularModels"]]
        for model in regularModels:
            data.update({model.__name__.lower(): {object.id: object.name for object in model.objects.all()}})
        data['geoTree'] = buildTree('root', self.config["geoTreeStructure"], formatedPdvs)
        data['brandTree'] = buildTree('root', self.config["brandTreeStructure"], formatedPdvs)
        return Response(data)
    
    def __formatPdv(self, pdvs:list):
        formatedPdvs = {pdv['id']:[value for key, value in pdv.items() if key != 'id'] + [self.salesDict.get(str(pdv['id']), [])] for pdv in pdvs}
        fields = list(pdvs[0].keys())[1:]
        indexes = []
        for fieldName in fields:
            if type(Pdv._meta.get_field(fieldName)) is ForeignKey:
                indexes.append(fields.index(fieldName))
        fields += ['sales']
        dataPdv = {'fields' : fields, 'indexes': indexes}
        dataPdv.update(formatedPdvs)
        return formatedPdvs, dataPdv
