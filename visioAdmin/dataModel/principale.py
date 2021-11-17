from visioServer.models import DataAdmin, ParamVisio
from django.utils import timezone

dictMonth = {1:"Janvier", 2:"Février", 3:"Mars", 4:"Avril", 5:"Mai", 6:"Juin", 7:"Juillet", 8:"Août", 9:"Septembre", 10:"Octobre", 11:"Novembre", 12:"Décembre"}

def loadInit():
  dictInit = {}
  dictInit["updateRef"] = DataAdmin.getSavedParam(False)
  dictInit["currentRef"] = DataAdmin.getSavedParam(True)
  dictInit["updateVol"] = DataAdmin.getSavedParam("vol")
  dictInit["isAdOpen"] = ParamVisio.getValue("isAdOpen")
  return dictInit

def handleUploadedFile(fileContent, fileNature):
  dir = "Référentiel/" if fileNature == "referentiel" else "Volume/"
  path = "visioAdmin/dataFile/FromEtex/" + dir + fileContent._get_name()
  with open(path, 'wb+') as destination:
    for chunk in fileContent.chunks():
      destination.write(chunk)
  dataAdmin = DataAdmin.getLastSavedObject()
  if fileNature == "referentiel":
    dataAdmin.fileNameRef = fileContent._get_name()
    dataAdmin.dateRef = timezone.now()
    dataAdmin.save()
    return {"status":"OK", "nature":fileNature, "fileName":dataAdmin.fileNameRef, "date":dataAdmin.dateRef.strftime("%Y-%m-%d %H:%M:%S"), "version":dataAdmin.getVersion}
  dataAdmin.fileNameVol = fileContent._get_name()
  dataAdmin.dateVol = timezone.now()
  dataAdmin.save()
  return {"status":"OK", "nature":fileNature, "fileName":dataAdmin.fileNameVol, "date":dataAdmin.dateVol.strftime("%Y-%m-%d %H:%M:%S"), "month":dictMonth[dataAdmin.dateVol.month - 1]}