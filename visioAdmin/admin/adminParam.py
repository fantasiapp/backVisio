from visioServer.models import ParamVisio, Sales, Pdv
from visioServer.modelStructure.dataDashboard import DataDashboard, Sales

class AdminParam:

  def __init__(self, dataDashboard):
    self.dataDashboard = dataDashboard

  def openAd(self):
    isAdOpen = ParamVisio.dictValues()["isAdOpen"]
    before = "Ouverte" if isAdOpen else "Fermée"
    ParamVisio.setValue("isAdOpen", False if isAdOpen else True)
    if ParamVisio.getValue("isAdOpen"):
      for sale in Sales.objects.filter(date__isnull=False):
        sale.date = None
        sale.save()
      pdvs = getattr(self.dataDashboard, "__pdvs")
      indexSales = Pdv.listFields().index("sales")
      indexDate = Sales.listFields().index("date")
      listSales = [pdv[indexSales] for pdv in pdvs.values()]
      for sales in listSales:
        for sale in sales:
          sale[indexDate] = None
    after = "Fermée" if isAdOpen else "Ouverte"
    return {"message":f"L'AD était {before}, elle est maintenant {after}"}

  def visualizePdv(self):
    print("AdminParam, visualize pdv")
    return {"message":"AdminParam, visualize pdv"}