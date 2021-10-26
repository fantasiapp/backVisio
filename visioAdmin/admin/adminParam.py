import sys
sys.path.append('..')
from visioServer.models import ParamVisio, Sales

class AdminParam:
  params = ParamVisio.dictValues()

  def __init__(self):
    pass

  def openAd(self):
    isAdOpen = self.params["isAdOpen"]
    before = "Ouverte" if isAdOpen else "Fermée"
    ParamVisio.setValue("isAdOpen", False if isAdOpen else True)
    if not self.params["isAdOpen"]:
      print("clean date")
      for sale in Sales.objects.all():
        sale.date = None
        sale.save()
    after = "Fermée" if isAdOpen else "Ouverte"
    return {"message":f"L'AD était {before}, elle est maintenant {after}"}