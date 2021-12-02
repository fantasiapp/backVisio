let selectedTableState = {"kpi":"Ref", "table":"Current"}
// Initialisation

function loadInitRefEvent () {
  $("#updateBaseRef").on('click', function(event) {updateWithFile("Ref")})
  $("#updateRefCheck").on('click', function(event) {tableHeaderSelect('Ref', 'Saved', true)})
  $("#updateBaseVol").on('click', function(event) {updateWithFile("Vol")})
  $("#switchBase").on('click', function(event) {switchBase()})
  $("#headerTable").on('click', function(event) {tableClose()})
  $("#agentOK").on('click', function(event) {fillUpDataBaseWithAgent()})

  $.each(['dragenter', 'dragover', 'dragleave', 'drop'], function(index, eventName) {
    $("#boxUploadDnd").on(eventName, function(event) {
      event.preventDefault()
      event.stopPropagation()
    })
  })
  
  $.each(['dragenter', 'dragover'], function(index, eventName) {
    $("#boxUploadDnd").on(eventName, function(event) {
      $("#boxUploadDnd").addClass('highlightBoxUpload')
    })
  })
  
  $.each(['dragleave', 'drop'], function(index, eventName) {
    $("#boxUploadDnd").on(eventName, function(event) {
      $("#boxUploadDnd").removeClass('highlightBoxUpload')
    })
  })

  $("#boxUploadDnd").on('drop', function(event){
    let files = event.originalEvent.dataTransfer.files
    let message = "Fichier en cours de sauvegarde: "
    $('#boxUploadClose').css("display", "none")
    console.log("boxUploadDnd ", message)
    $.each(files, function(index, file) {
      message += file.name + " "
      let formData = new FormData()
      formData.append('file', file)
      formData.append("uploadFile", $("#boxUpload").attr("data"))
      formData.append("csrfmiddlewaretoken", token)
      httprequestUploadFile(formData)
    })
   $('#fileUploaded').text(message)
  })
}

function loadInitRef (dictValue) {
  dictBox = dictValue["updateRef"]
  console.log("updateRef", dictBox["version"])
  $("#updateRefMbSave p.title").text("Base de sauvegarde : " + dictBox["version"])
  $("#updateRefMbSave p.date").text("Mis à jour le : " + dictBox["date"])
  $("#updateRefMbSave p.file").text("Fichier xlsx : " + dictBox["fileName"])
  dictBox = dictValue["currentRef"]
  $("#updateSwitch p.title").text("Base en ligne : " + dictBox["version"])
  $("#updateSwitch p.date").text("Mis à jour le : " + dictBox["date"])
  $("#updateSwitch p.file").text("Fichier xlsx : " + dictBox["fileName"])
  dictBox = dictValue["updateVol"]
  $("#updateVol p.title").text("Dernier mois : " + dictBox["month"])
  $("#updateVol p.date").text("Mis à jour le : " + dictBox["date"])
  $("#updateVol p.file").text("Fichier xlsx : " + dictBox["fileName"])
}

function tableClose() {
  $.each({"#tableArticle":"none", "#headerTable":"none", "#articleMain":"block"}, function(id, value ) {
    $(id).css("display", value)
  })
  $.each(["#tableHeader", "#tableMain"], function(_, value ) {
    $(value).empty()
  })
}

//upload files
function httprequestUploadFile(formData) {
  $("#wheel").css({display:'block'})
  $("div.boxClose").css("display", "none")
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "post",
    data: formData,
    contentType : false,
    processData : false,
    success : function(response) {
      uploadFileResponse(response)
    },
    error: function(response) {
      console.log("httprequestUploadFile", response)
      $("#wheel").css({display:'none'})
    }
  })
}

function updateWithFile(nature) {
  $("#boxUpload").attr("data", nature)
  $("#boxUpload").css({display:"block"})
  $("#protect").css({display:"block"})
}

function selectStatusAgent(newName) {
  if (statusAgent[newName]["status"]) {
    statusAgent[newName]["status"] = false
    newName_ = newName.replace(" ", "_")
    $('#agent_'+newName_+' img.agentImg').attr('src', "/static/visioAdmin/images/CheckBoxOff.png")
  } else {
    statusAgent[newName]["status"] = true
    newName_ = newName.replace(" ", "_")
    $('#agent_'+newName_+' img.agentImg').attr('src', "/static/visioAdmin/images/CheckBoxOn.png")
  }
}

function fillUpDataBaseWithAgent() {
  if ($('#agentOK').attr("data") == "activate") {
    $('#agentOK').addClass("inhibit")
    $('#agentOK').attr("data", "inhibit")
    $("#wheel").css({display:'block'})
    $("div.boxClose").css("display", "none")
    data =  {"action":"selectAgent", "csrfmiddlewaretoken":token}
    $.each(statusAgent, function (newName, arrayAgent) {
      if (arrayAgent["status"]) {
        data[newName] = "replace"
      } else {
        data[newName] = "noReplace"
      }
    })
    $.ajax({
      url : "/visioAdmin/principale/",
      type: "get",
      data: data,
      success : function(response) {
        uploadFileResponse(response)
      },
      error: function() {
        closeBox()
        console.log("query selectAgent error")
        $("#wheel").css({display:'none'})
      }
    })
  }
}

function uploadFileResponse(response) {
  closeBox()
  console.log("uploadFileResponse", response)
  if ('error' in response) {
    displayWarning(response['title'], response['content'])
  } else if ('warningAgent' in response) {
    displayWarnigAgent(response['warningAgent'])
  } else if (response["nature"] == "Ref") {
    console.log("nature", response["nature"])
    $("#updateRefMbSave p.title").text("Base de sauvegarde : " + response["version"])
    $("#updateRefMbSave p.date").text("Mis à jour le : " + response["date"])
    $("#updateRefMbSave p.file").text("Fichier xlsx : " + response["fileName"])
  } else {
    console.log("nature", response["nature"])
    $("#updateVol p.title").text("Dernier mois : " + response["month"])
    $("#updateVol p.date").text("Mis à jour le : " + response["date"])
    $("#updateVol p.file").text("Fichier xlsx : " + response["fileName"])
  }
}

function displayWarnigAgent(arrayAgent) {
  closeBox()
  $("#protect").css("display", "block")
  $("#boxWarningAgent").css("display", "block")
  $('#agentContent').empty()
  statusAgent = {}
  $.each(arrayAgent, function( _, value) {
    statusAgent[value['newName']] ={"status":true, "oldName":value['oldName']}
    newName = value['newName'].replace(" ", "_")
    line = $('<div class="agentLine" id="agent_'+newName+'"></div>')
    text = $('<span class="agentContent">')
    text.text("L'agent "+value['newName']+" remplace l'agent "+value['oldName'])
    line.append(text)
    checkbox = $('<img class="agentImg" src="/static/visioAdmin/images/CheckBoxOn.png">')
    line.append(checkbox)
    checkbox.on('click', function(event) {selectStatusAgent(value['newName'])})
    $('#agentContent').append(line)
  })
}
// Switch Base
function switchBase() {
  $("#wheel").css({display:'block'})
  $('#switchBase').addClass("inhibit")
  $('#protect').css('display', "block")
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : {"action":"switchBase", "csrfmiddlewaretoken":token},
    success : function(response) {
      console.log("success switchBase", response)
      loadInitRef(response)
      closeBox()
    },
    error : function(response) {
      console.log("error switchBase", response)
      closeBox()
    }
  })
}

// Visualize Tables

//select table
function tableHeaderSelect(kpi, table, tableHeader=false) {
  console.log("tableHeaderSelect", kpi, table)
  if (tableHeader) {
    selectedTableState["table"] = "Current"
  }
  if (selectTableKpi(table, "table") || selectTableKpi(kpi, "kpi")) {
    $("#tableMain").empty()
    $("#wheel").css("display", 'block')
    visualizeTableQuery(scroll=true, tableHeader=tableHeader)
  }
}

function selectTableKpi (value, field) {
  console.log("selectTableKpi start", value, field)
  if (selectedTableState[field] != value && value) {
    $("#tableHeader" + value +" p").addClass("tableHeaderHighLight")
    $("#tableHeader" + selectedTableState[field] +" p").removeClass("tableHeaderHighLight")
    selectedTableState[field] = value
    console.log("selectTableKpi", field, value, selectedTableState)
    console.log("return", true)
    return true
  }
  console.log("return", false)
  return false
}

function visualizeTableQuery(scroll=true, tableHeader=true) {
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : {"action":"visualizeTable", "kpi":selectedTableState["kpi"], "table":selectedTableState["table"], "csrfmiddlewaretoken":token},
    success : function(response) {
      columnsTitle = []
      $.each(response['titles'], function( _, value ) {
        columnsTitle.push({title: value})
      })
      loadTable (columnsTitle, response['values'], 'table' + selectedTableState["kpi"] + selectedTableState["table"], scroll, tableHeader)
      $("#wheel").css({display:'none'})
    },
    error : function(response) {
      console.log("error visualizeTableQuery", response)
      $("#wheel").css({display:'none'})
    }
  })
}

function loadTable (columnsTitle, values, tableId, scroll, tableHeader) {
  $("#articleMain").css({display:'none'})
  $('#tableArticle').css({display:'block'})
  $('#headerTable').css({display:'block'})
  console.log("tableHeader", tableHeader)
  if (tableHeader) {
    addTableHeader()
  }
  langage = {
    lengthMenu: "Affichage _MENU_ enregistrements par page",
    zeroRecords: "Pas d'enregistrement correspondant à la recherche",
    emptyTable: "Pas de donnée disponible",
    info: "Numéros de page : de _PAGE_ à _PAGES_",
    infoEmpty: "Pas d'enregistrement disponible",
    infoFiltered: "(filtrés sur un nombre total de _MAX_ enregistrements)",
    search: "Barre de recherche:",
    processing: "Calculs en cours de traitement",
    loadingRecords: "Chargement ...",
    thousands: " ",
    decimal: ",",
    paginate: {
      first: "Premier",
      last:  "Dernier",
      next:  "Suivant",
      previous: "Précédent"
    },
  }
  console.log("tableId", tableId)
  if (scroll) {
    $('#tableMain').append('<table id="'+tableId+'" class="display" style="width:100%">')
    $('#'+tableId).DataTable({
      scrollX:scroll,
      data: values,
      columns: columnsTitle,
      language: langage,
  })
  } else {
    $('tableMain').append('<table id="'+tableId+'" class="display">')
    $('#'+tableId).DataTable({
      data: values,
      columns: columnsTitle,
      language: langage,
    })
  }
}

function addTableHeader() {
  $('#tableHeader').append('<div id="tableHeadeRow1" class="tableHeader"></div>')
  $('#tableHeader').append('<div id="tableHeadeRow2" class="tableHeader"></div>')
  $('#tableHeadeRow1').css({"display":"flex", "flex-direction": "row"})
  $('#tableHeadeRow1').append("<div id='tableHeaderSaved'><p class='tableHeader'>La version sauvegardée</p></div>")
  $('#tableHeadeRow1').append('<div class="tableHeaderSep"></div>')
  $('#tableHeadeRow1').append("<div id='tableHeaderCurrent'><p class='tableHeader'>La version en ligne</p></div>")
  $('#tableHeadeRow1').append('<div class="tableHeaderSep"></div>')
  $('#tableHeadeRow1').append("<div id='tableHeaderBoth'><p class='tableHeader'>Comparer la version sauvegardée avec la version en ligne</p></div>")

  $('#tableHeadeRow2').append('<div id="tableTab">')
  $('#tableTab').append('<div id="tableHeaderRef" class="tableTab"><p class="tableHeader">Référentiel</p></div>')
  $('#tableTab').append('<div id="tableHeaderVol"  class="tableTab"><p class="tableHeader">Volumétrie</p></div>')

  $("#tableHeaderRef p").addClass("tableHeaderHighLight")
  $("#tableHeaderSaved p").addClass("tableHeaderHighLight")

  $("#tableHeaderSaved").on('click', function(event) {tableHeaderSelect(false, "Saved")})
  $("#tableHeaderCurrent").on('click', function(event) {tableHeaderSelect(false, "Current")})
  $("#tableHeaderBoth").on('click', function(event) {tableHeaderSelect(false, "Both")})
  $("#tableHeaderRef").on('click', function(event) {tableHeaderSelect("Ref", false)})
  $("#tableHeaderVol").on('click', function(event) {tableHeaderSelect("Vol", false)})
}