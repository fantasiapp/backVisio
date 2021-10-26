import sys
sys.path.append('..')
from visioServer.models import ParamVisio, Sales

class AdminParam:
  params = ParamVisio.dictValues()

  def __init__(self):
    pass

  def openAd(self):
    isAdOpen = self.params["isAdOpen"]
    before = "Ouvert" if isAdOpen else "Fermé"
    ParamVisio.setValue("isAdOpen", False if isAdOpen else True)
    if self.params["isAdOpen"]:
      for sale in Sales.objects.all():
        sale.date = None
        sale.save()
    after = "Fermé" if isAdOpen else "Ouvert"
    return {"message":f"L'AD était {before}, elle est maintenant {after}"}