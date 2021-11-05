let token = $("#mainMain input[name='csrfmiddlewaretoken']").val()
let etexColor = "rgb(241,100,39)"
let selectedAction = null

// Navigation
$("#updateRef").on('click', function(event) {selectNav("updateRef")})
$("#upload").on('click', function(event) {selectNav("upload")})
$("#validation").on('click', function(event) {selectNav("validation")})
$("#param").on('click', function(event) {selectNav("param")})
$("#boxUploadClose").on('click', function(event) {closeBoxUpload()})

$("#updateBaseRef").on('click', function(event) {updateWithFile("referentiel")})
$("#updateRefCheck").on('click', function(event) {visualizeTablePdv()})
$("#updateBaseVol").on('click', function(event) {updateWithFile("volume")})

function initApplication () {
  selectNav("updateRef")
  formatMainBox()
  loadInit()
}

function fillUpInterface (dictValue) {
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
  console.log(dictBox)
}

function selectNav(selection) {
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
  width = (height *0.94).toString() + "px"
  marginLeft = ($("div.mainBox").width() - height - $("div.boxTextButton").width()).toString() + "px"
  marginTop = (height *0.03).toString() + "px"
  $("div.mainBoxImage").css({"margin-left":marginLeft, "margin-top":marginTop ,"width": width, "height":width})
}

function loadInit() {
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "get",
    data: {"action":"loadInit", "csrfmiddlewaretoken":token},
    success : function(response) {
      fillUpInterface(response)
    },
    error: function() {
      console.log("query loadInit error")
    }
  })
}

// UpdateRef
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
  $.each(files, function(index, file) {
    let formData = new FormData()
    formData.append('file', file)
    formData.append("uploadFile", $("#boxUpload").attr("data"))
    formData.append("csrfmiddlewaretoken", token)
    $.ajax({
      url : "/visioAdmin/principale/",
      type: "post",
      data: formData,
      contentType : false,
      processData : false,
      success : function(response) {
        console.log(response)
        $("#boxUpload").css("display", "none")
        if (response["nature"] == "referentiel") {
          $("#updateRefMbSave p.title").text("Base de sauvegarde : " + response["version"])
          $("#updateRefMbSave p.date").text("Mis à jour le : " + response["date"])
          $("#updateRefMbSave p.file").text("Fichier xlsx : " + response["fileName"])
        } else {
          $("#updateVol p.title").text("Dernier mois : " + response["month"])
          $("#updateVol p.date").text("Mis à jour le : " + response["date"])
          $("#updateVol p.file").text("Fichier xlsx : " + response["fileName"])
        }
      },
      error: function(response) {
        // console.log("query error")
      }
    })
  })
})

function updateWithFile(nature) {
  console.log("updateWithFile", nature)
  $("#boxUpload").attr("data", nature)
  $("#boxUpload").css({display:"block"})
}

function closeBoxUpload() {
  $("#boxUpload").css({display:"none"})
}

function visualizeTablePdv() {
  $("#wheel").css({display:'block'})
  visualizeTable('Pdv', scroll=true)
}

function visualizeTable(table, scroll=true) {
  $("div.loader").css({display:'block'})
  data = {"action":"load"+table, "csrfmiddlewaretoken":token}
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : data,
    success : function(response) {
      console.log("vizualize generic", response)
      columnsTitle = []
      $.each(response['titles'], function( _, value ) {
        columnsTitle.push({title: value})
      })
      loadTable (columnsTitle, response['values'], 'table' + table, scroll)
      $("#wheel").css({display:'none'})
    },
    error : function(response) {
      console.log("error", response)
      $("#wheel").css({display:'none'})
    }
  })
}

function loadTable (columnsTitle, values, tableId, scroll) {
  $("#articleMain").css({display:'none'})
  $('#tableMain').empty()
  $('#tableMain').css({display:'block'})
  if (scroll) {
    $('#tableMain').append('<table id="'+tableId+'" class="display" style="width:100%">')
    $('#'+tableId).DataTable({"scrollX": scroll, data: values, columns: columnsTitle})
    console.log(scroll, tableId)
  } else {
    $('tableMain').append('<table id="'+tableId+'" class="display">')
    $('#'+tableId).DataTable({data: values, columns: columnsTitle})
  }
}

initApplication ()