import sys
sys.path.append('..')
from visioServer.models import ParamVisio, Sales

class AdminParam:

  def __init__(self):
    pass

  def openAd(self):
    isAdOpen = ParamVisio.dictValues()["isAdOpen"]
    before = "Ouverte" if isAdOpen else "Fermée"
    ParamVisio.setValue("isAdOpen", False if isAdOpen else True)
    if ParamVisio.getValue("isAdOpen"):
      print("clean date")
      for sale in Sales.objects.filter(date__isnull=False):
        sale.date = None
        sale.save()
    after = "Fermée" if isAdOpen else "Ouverte"
    return {"message":f"L'AD était {before}, elle est maintenant {after}"}