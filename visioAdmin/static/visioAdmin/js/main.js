let token = $("#mainMain input[name='csrfmiddlewaretoken']").val()
let etexColor = "rgb(241,100,39)"
let selectedAction = null

// Navigation
$("#updateRef").on('click', function(event) {selectNav("updateRef")})
$("#upload").on('click', function(event) {selectNav("upload")})
$("#validation").on('click', function(event) {selectNav("validation")})
$("#param").on('click', function(event) {selectNav("param")})
$("#boxUploadClose").on('click', function(event) {closeBoxUpload()})

$("#updateBase").on('click', function(event) {updateBase()})

function initApplication () {
  selectNav("updateRef")
  formatMainBox()
  loadInit()
}

function loadInit() {
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "get",
    data: {"action":"loadInit", "csrfmiddlewaretoken":token},
    success : function(response) {
      console.log(response)
    },
    error: function() {
      console.log("query loadInit error")
    }
  })
}

function formatMainBox() {
  height = $("div.mainBox").height()
  width = (height *0.94).toString() + "px"
  marginLeft = ($("div.mainBox").width() - height - $("div.boxTextButton").width()).toString() + "px"
  marginTop = (height *0.03).toString() + "px"
  $("div.mainBoxImage").css({"margin-left":marginLeft, "margin-top":marginTop ,"width": width, "height":width})
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
  let dt = event.originalEvent.dataTransfer
  let files = event.originalEvent.dataTransfer.files
  $.each(files, function(index, file) {
    let formData = new FormData()
    formData.append('file', file)
    formData.append("uploadFile", "referentiel")
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
        $("#updateRefMbSave p.date").text("Mis à jour le : " + response["date"])
        $("#updateRefMbSave p.file").text("Fichier xlsx : " + response["fileName"])
      },
      error: function(response) {
        // console.log("query error")
      }
    })
  })
})

function updateBase() {
  console.log("updateBase")
  $("#boxUpload").css({display:"block"})
}

function closeBoxUpload() {
  $("#boxUpload").css({display:"none"})
}

initApplication ()