let dictSynonym = {}

// Initialisation
function loadInitParamEvent() {
  $('#paramAccountConsult').on('click', function(event) {displayAccount()})
  $('#AdOpenButton').on('click', function(event) {switchAdStatus()})
  $('#manageSynonyms').on('click', function(event) {displayManageSynonyms()})
  $('#manageSynonymsOK').on('click', function(event) {manageSynonymsOK()})
}

function loadInitParam (response) {
  if (response["isAdOpen"]) {
    $("#AdOpenBox p.file").text("Actuellement l'AD est ouverte")
    $("#AdOpenButton span").text("Fermer l'AD")
  } else {
    $("#AdOpenBox p.file").text("Actuellement l'AD est fermée")
    $("#AdOpenButton span").text("Ouvrir l'AD")
  }
}

// Actions
// Status de l'AD
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
// Traitements des synonymes
function displayManageSynonyms() {
  closeBox()
  $("#protect").css("display", "block")
  $("#synonyms").css("display", "block")
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : {"action":"paramSynonymsInit", "csrfmiddlewaretoken":token},
    success : function(response) {
      dictSynonym = response
      builSynonymsdInterface()
    }
  })
}

function builSynonymsdInterface() {
  $("#synonymsAxis select").remove()
  select = $('<select class="synonyms" name="axis" id="SynonymsSelect">')
  $.each(dictSynonym, function(name, _) {
    select.append('<option value="'+name+'">'+name+'</option>')
  })
  $("#synonymsAxis").append(select)
  select.change(function() {buildSynonymsList()})
  buildSynonymsList()
}

function buildSynonymsList() {
  selection = $("#SynonymsSelect").val()
  $("#synonymsContent").empty()
  $.each(dictSynonym[selection], function(originalName, synonym) {
    input = $('<input type="text" class="lineSynonym" name="'+originalName+'">')
    if (synonym != null) {
      input.val(synonym)
    }
    line = $('<div class="lineSynonym"><span class="lineSynonym">' + originalName +'</span></div>')
    line.append(input)
    $("#synonymsContent").append(line)
  })
}

function manageSynonymsOK() {
  selection = $("#SynonymsSelect").val()
  dictValue = dictSynonym[selection]
  $.each($("#synonymsContent input"), function(_, input) {
    originalName =  $(input).attr("name")
    synonym = $(input).val()
    dictValue[originalName] = synonym
  })
  formData = {"defineSynonym":true, "dictSynonym":JSON.stringify(dictSynonym), "csrfmiddlewaretoken":token}
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'post',
    data : formData,
    success : function(response) {
      $("#synonymsMessage").text(response["fillupSynonym"])
      $("#synonymsMessage").show().delay(3000).fadeOut();
    }
  })
}
// Traitement des comptes
function displayAccount() {
  console.log("displayAccount")
  accountSetDisplay()
  accountSetHeader()
  accountSetQuery()
}

function accountSetDisplay() {
  $('#articleMain').css("display", "none")
  $('#account').css("display", "block")
  $('#headerTable').css("display", "block")
  $("#headerTable").on('click', function(event) {tableClose()})
}

function accountSetHeader() {
  title = $('<p class="tableHeaderHighLight">Gestion des comptes</p>')
  divAction = $('<div id="actionsAccount">')
  $("#accountHeader").append(title)
  $("#accountHeader").append(divAction)
  buttonModify = $('<button class="accountButton" id="accountModify">Modifier un profil</button>')
  buttonCreate = $('<button class="accountButton" id="accountCreate">Créer un nouveau profil</button>')
  buttonModify.append($('<img class="accountButton" src="/static/visioAdmin/images/Modifier.svg">'))
  buttonCreate.append($('<img class="accountButton" src="/static/visioAdmin/images/Créer.svg">'))
  divAction.append(buttonModify)
  divAction.append(buttonCreate)
}

function accountSetQuery() {
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : {"action":"paramAccountInit", "csrfmiddlewaretoken":token},
    success : function(response) {
      console.log(response)
      buildAccountTable(response)
    }
  })
}

function buildAccountTable(dictData) {
  mainAccount = $('<div id="mainAccount">')
  $('#accountMain').append(mainAccount)
  lineTitle = $('<div class="accountLine">')
  mainAccount.append(lineTitle)
  $.each(dictData["titles"], function(label, size) {
    title = $('<p class="cellAccount" style="font-weigth:bold; width:'+size+'%">'+label+'</p>')
    lineTitle.append(title)
  })
}


// Chargement du loader dans formatMainBox.js
initApplication ()

