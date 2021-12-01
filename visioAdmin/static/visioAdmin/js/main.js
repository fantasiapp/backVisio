let token = $("#mainMain input[name='csrfmiddlewaretoken']").val()
let etexColor = "rgb(241,100,39)"
let selectedAction = null
// let selectedTableState = {"kpi":"Pdv", "table":"Current"}
let statusAgent = {}

// Navigation
$("#updateRef").on('click', function(event) {selectNav("updateRef")})
$("#upload").on('click', function(event) {selectNav("upload")})
$("#validation").on('click', function(event) {selectNav("validation")})
$("#param").on('click', function(event) {selectNav("param")})
$("img.boxClose").on('click', function(event) {closeBox()})

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
  loadInitParamEvent ()
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "get",
    data: {"action":"loadInit", "csrfmiddlewaretoken":token},
    success : function(response) {
      loadInitRef(response)
      loadInitParam(response)
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