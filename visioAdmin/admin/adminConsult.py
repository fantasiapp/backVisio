import openpyxl
from openpyxl.styles import Font
from django.utils import timezone
import os
import json
from pathlib import Path
from django.http import HttpResponse
from wsgiref.util import FileWrapper

import os.path
from os import path

class AdminConsult:
  pathSave = os.getenv('PATH_FILE_SEND')
  dictFileName =  json.loads(os.getenv('DICO_FILE_SEND'))
  extention = "xlsx"

  def __init__(self, adminUpdate, adminParam):
    self.adminUpdate = adminUpdate
    self.adminParam = adminParam
    self.dataDashboard = adminUpdate.dataDashboard

  def buildExcelFile(self, nature):
    data = self.__findData(nature)
    return self.__createExcelFile(data, nature)
    

  def __findData(self, nature):
    if nature == "currentBase":
      dataRef = self.adminUpdate.visualizeTable("Ref", "Current")
      dataVol = self.adminUpdate.visualizeTable("Vol", "Current")
      return {"Référentiel de la base courante":dataRef, "Volume de la base courante":dataVol}
    if nature == "connection":
      dataConnection = self.adminParam.paramAccountInit()
      dataConnection["titles"] = list(dataConnection["titles"].keys())
      dataConnection["values"] = list(dataConnection["values"].values())
      print(dataConnection)
      return {"Rapport des connexions":dataConnection}


  def __createExcelFile(self, data, nature):
    file, flagStart = openpyxl.Workbook(), True
    for sheetName, data in data.items():
      if flagStart:
        sheet = file.active
        sheet.title = sheetName
        flagStart = False
      else:
        sheet = file.create_sheet(sheetName)
      self.__createTitle(sheet, data["titles"])
      self.__createLine(sheet, data["values"])
    return self.__saveExcelFile(file, nature)

  def __createTitle(self, sheet, titles):
    color = openpyxl.styles.colors.Color(rgb='0B64A0')
    fill = openpyxl.styles.fills.PatternFill(patternType='solid', fgColor=color)
    fontColor = Font(color="FFFFFF", bold=True)
    nbRow, nbCol = 1, 1
    for title in titles:
      cell = sheet.cell(row=nbRow, column=nbCol)
      cell.value = title
      nbCol += 1
      cell.fill = fill
      cell.font = fontColor

  def __createLine(self, sheet, values):
    nbRow = 2
    for line in values:
      nbCol = 1
      for value in line:
        cell = sheet.cell(row=nbRow, column=nbCol)
        cell.value = value
        nbCol += 1
      nbRow += 1


  def __saveExcelFile(self, file, nature):
    now = timezone.now()
    name = f"{self.dictFileName[nature]}_{now.strftime('%d_%m_%y_%Hh%Mmn_%Ss')}.{self.extention}"
    fileName = f"{Path.cwd()}/{self.pathSave}{name}"
    file.save(fileName)
    # content = FileWrapper(fileName)
    with open(fileName, 'rb') as file:
      response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
      response['Content-Length'] = os.path.getsize(fileName)
      response['Content-Disposition'] = 'inline; filename=%s' % name
      print("__saveExcelFile", isinstance(response, dict))
      return response

    # return fileName

