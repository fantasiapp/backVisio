let token = $("#mainMain input[name='csrfmiddlewaretoken']").val()
let etexColor = "rgb(241,100,39)"
let selectedAction = null
let selectedTableState = {"kpi":"Pdv", "table":"Current"}
let statusAgent = {}

// Navigation
$("#updateRef").on('click', function(event) {selectNav("updateRef")})
$("#upload").on('click', function(event) {selectNav("upload")})
$("#validation").on('click', function(event) {selectNav("validation")})
$("#param").on('click', function(event) {selectNav("param")})
$("img.boxClose").on('click', function(event) {closeBox()})

$("#updateBaseRef").on('click', function(event) {updateWithFile("referentiel")})
$("#updateRefCheck").on('click', function(event) {visualizeTable('Pdv', 'Current', true)})
$("#updateBaseVol").on('click', function(event) {updateWithFile("volume")})
$("#switchBase").on('click', function(event) {switchBase()})
$("#headerTable").on('click', function(event) {tableClose()})

$("#agentOK").on('click', function(event) {selectAgent()})

$('#AdOpenButton').on('click', function(event) {switchAdStatus()})

function initApplication () {
  selectNav("updateRef")
  formatMainBox()
  loadInit()
}

function selectNav(selection) {
  $("#articleMain").css({display:'block'})
  $('#tableArticle').css({display:'none'})
  $('#headerTable').css({display:'none'})
  $('#protect').css({display:'none'})
  $('div.box').css({display:'none'})
  selectedAction = selection
  let arraySelection = ["updateRef", "upload", "validation", "param"]
  for (let element of arraySelection) {
    if (element === selection) {
      $("#" + element).css({"background-color":etexColor, "color":"white"})
      $("#" + element + "Div").css({"display":"block"})
    } else {
      $("#" + element).css({"background-color":"white", "color":"black"})
      $("#" + element + "Div").css({"display":"none"})
    }
  }
}

function formatMainBox() {
  height = $("div.mainBox").height()
  width = (height *0.80).toString() + "px"
  marginLeft = ($("div.mainBox").width() - (height * 0.70) - $("div.boxTextButton").width()).toString() + "px"
  marginTop = (height *0.03).toString() + "px"
  $("div.mainBoxImage").css({"margin-left":marginLeft, "margin-top":marginTop ,"width": width, "height":width})
}

function loadInit() {
  loadInitRefEvent ()
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "get",
    data: {"action":"loadInit", "csrfmiddlewaretoken":token},
    success : function(response) {
      loadInitRef(response)
      switchAdStatusInterface(response)
    },
    error: function() {
      console.log("query loadInit error")
    }
  })
}

function displayWarning(title, content) {
  $("#protect").css("display", "block")
  $("#boxWarning").css("display", "block")
  $("#warningTitle").text(title)
  $("#warningContent").text(content)
}

function closeBox() {
  $("#wheel").css({display:'none'})
  $('div.boxClose').css("display", "block")
  $('#boxUploadClose').css("display", "block")
  $('#agentOK').removeClass("inhibit")
  $('#switchBase').removeClass("inhibit")
  $('#agentOK').attr("data", "activate")
  $("#protect").css("display", "none")
  $("div.box").css({display:"none"})
  $('#fileUploaded').text("")
}

// UpdateRef
function loadInitRefEvent () {
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
      uploadFile(response)
    },
    error: function(response) {
      console.log("httprequestUploadFile", response)
      $("#wheel").css({display:'none'})
    }
  })
}

function uploadFile(response) {
  closeBox()
  if (response["error"]) {
    displayWarning(response['title'], response['content'])
  } else if (response['warningAgent']) {
    displayWarnigAgent(response['warningAgent'])
  } else if (response["nature"] == "referentiel") {
    $("#updateRefMbSave p.title").text("Base de sauvegarde : " + response["version"])
    $("#updateRefMbSave p.date").text("Mis à jour le : " + response["date"])
    $("#updateRefMbSave p.file").text("Fichier xlsx : " + response["fileName"])
  } else {
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
  console.log("httprequestUploadFile", arrayAgent)
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

function selectAgent() {
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
        uploadFile(response)
      },
      error: function() {
        closeBox()
        console.log("query selectAgent error")
        $("#wheel").css({display:'none'})
      }
    })
  }
}

function loadInitRef (dictValue) {
  dictBox = dictValue["updateRef"]
  $("#updateRefMbSave p.title").text("Base de sauvegarde : " + dictBox["version"])
  $("#updateRefMbSave p.date").text("Mis à jour le : " + dictBox["date"])
  $("#updateRefMbSave p.file").text("Fichier xlsx : " + dictBox["fileName"])
  dictBox = dictValue["currentRef"]
  $("#updateSwitch p.title").text("Base en ligne : " + dictBox["version"])
  $("#updateSwitch p.date").text("Mis à jour le : " + dictBox["date"])
  $("#updateRSwitch p.file").text("Fichier xlsx : " + dictBox["fileName"])
  dictBox = dictValue["updateVol"]
  $("#updateVol p.title").text("Dernier mois : " + dictBox["month"])
  $("#updateVol p.date").text("Mis à jour le : " + dictBox["date"])
  $("#updateVol p.file").text("Fichier xlsx : " + dictBox["fileName"])
}

function updateWithFile(nature) {
  $("#boxUpload").attr("data", nature)
  $("#boxUpload").css({display:"block"})
  $("#protect").css({display:"block"})
}

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
      closeBox()
    },
    error : function(response) {
      console.log("error switchBase", response)
      closeBox()
    }
  })
}

function tableHeaderSaved() {
  if (selectTable("Saved")) {
    $("#tableMain").empty()
    visualizeTable('Pdv', 'Saved', false)
  }
}

function tableHeaderCurrent() {
  if (selectTable("Current")) {
    $("#tableMain").empty()
    visualizeTable('Pdv', 'Current', false)
  }
}

function tableHeaderBoth() {
  if (selectTable("Both")) {
    console.log("tableHeaderBoth")
  }
}

function selectKpiRef() {
  if (selectKpi("Ref")) {
    $("#tableMain").empty()
    visualizeTable('Pdv', 'Current', false)
  }
}

function selectKpiVol() {
  if (selectKpi("Vol")) {
    $("#tableMain").empty()
    visualizeTable('Sales', 'Current', false)
  }
}

function visualizeTable(tableName, kpiName, tableHeader) {
  $("#wheel").css({display:'block'})
  visualizeTableQuery(tableName+kpiName, scroll=true, tableHeader=tableHeader)
}

function selectTable (tableName) {
  if (selectedTableState["table"] != tableName) {
    $("#tableHeader" + tableName +" p").addClass("tableHeaderHighLight")
    $("#tableHeader" + selectedTableState["table"] +" p").removeClass("tableHeaderHighLight")
    selectedTableState["table"] = tableName
    return true
  }
  return false
}

function selectKpi (kpi) {
  if (selectedTableState["kpi"] != kpi) {
    $("#table" + kpi).addClass("tableTabHighLight")
    $("#table" + selectedTableState["kpi"]).removeClass("tableTabHighLight")
    selectedTableState["kpi"] = kpi
    return true
  }
  return false
}

function visualizeTableQuery(table, scroll=true, tableHeader=true) {
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : {"action":"visualize"+table, "csrfmiddlewaretoken":token},
    success : function(response) {
      columnsTitle = []
      $.each(response['titles'], function( _, value ) {
        columnsTitle.push({title: value})
      })
      loadTable (columnsTitle, response['values'], 'table' + table, scroll, tableHeader)
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
  if (tableHeader) {
    addTableHeader(tableId)
  }
  if (scroll) {
    $('#tableMain').append('<table id="'+tableId+'" class="display" style="width:100%">')
    $('#'+tableId).DataTable({"scrollX": scroll, data: values, columns: columnsTitle})
  } else {
    $('tableMain').append('<table id="'+tableId+'" class="display">')
    $('#'+tableId).DataTable({data: values, columns: columnsTitle})
  }
  translateTable()
}

function translateTable() {

}

function addTableHeader(tableId) {
  if (tableId == "tablePdvCurrent") {
    $('#tableHeader').append('<div id="tableHeadeRow1" class="tableHeader"></div>')
    $('#tableHeader').append('<div id="tableHeadeRow2" class="tableHeader"></div>')
    $('#tableHeadeRow1').css({"display":"flex", "flex-direction": "row"})
    $('#tableHeadeRow1').append("<div id='tableHeaderSaved'><p class='tableHeader'>La version sauvegardée</p></div>")
    $('#tableHeadeRow1').append('<div class="tableHeaderSep"></div>')
    $('#tableHeadeRow1').append("<div id='tableHeaderCurrent'><p class='tableHeader'>La version en ligne</p></div>")
    $('#tableHeadeRow1').append('<div class="tableHeaderSep"></div>')
    $('#tableHeadeRow1').append("<div id='tableHeaderBoth'><p class='tableHeader'>Comparer la version sauvegardée avec la version en ligne</p></div>")

    $('#tableHeadeRow2').append('<div id="tableTab">')
    $('#tableTab').append('<div id="tableRef" class="tableTab"><p>Référentiel</p></div>')
    $('#tableTab').append('<div id="tableVol"  class="tableTab"><p>Volumétrie</p></div>')

    $("#tableRef").addClass("tableTabHighLight")
    $("#tableHeaderCurrent p").addClass("tableHeaderHighLight")

    $("#tableHeaderSaved").on('click', function(event) {tableHeaderSaved()})
    $("#tableHeaderCurrent").on('click', function(event) {tableHeaderCurrent()})
    $("#tableHeaderBoth").on('click', function(event) {tableHeaderBoth()})
    $("#tableRef").on('click', function(event) {selectKpiRef()})
    $("#tableVol").on('click', function(event) {selectKpiVol()})
  }
}

function tableClose() {
  $.each({"#tableArticle":"none", "#headerTable":"none", "#articleMain":"block"}, function(id, value ) {
    $(id).css("display", value)
  })
  $.each(["#tableHeader", "#tableMain"], function(_, value ) {
    $(value).empty()
  })
}

// Parametrer
function switchAdStatusInterface (response) {
  if (response["isAdOpen"]) {
    $("#AdOpenBox p.file").text("Actuellement l'AD est ouverte")
    $("#AdOpenButton span").text("Fermer l'AD")
  } else {
    $("#AdOpenBox p.file").text("Actuellement l'AD est fermée")
    $("#AdOpenButton span").text("Ouvrir l'AD")
  }
}

function switchAdStatus() {
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "get",
    data: {"action":"switchAdStatus", "csrfmiddlewaretoken":token},
    success : function(response) {
      switchAdStatusInterface (response)
    }
  })
}


initApplication ()