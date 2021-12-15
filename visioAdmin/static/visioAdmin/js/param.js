let dictSynonym = {}
let dictCreateAccount = {}
let dictSetupAccount = {}
let flagBuildTarget = false
let flagReady = true

// Initialisation
function loadInitParamEvent() {
  $('#paramTargetConsult').on('click', function(event) {displayTarget()})
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
// Traitement des objectifs
function displayTarget() {
  targetSetDisplay()
  title = $('<p class="tableHeaderHighLight">Gestion des objectifs</p>')
  $("#targetHeader").append(title)
  targetBuildDisplay()
}

function targetSetDisplay() {
  $("#wheel").css({display:'none'})
  $('#articleMain').css("display", "none")
  $('#target').css("display", "block")
  $('#headerTable').css("display", "block")
  $("#headerTable").on('click', function(event) {tableClose()})
}

function targetBuildDisplay () {
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "get",
    data: {"action":"buildTarget", "csrfmiddlewaretoken":token},
    success : function(response) {
      if (flagBuildTarget) {
        $.each(response["Finitions"], function(id, dictData) {
          $('#regionTarget input.inputTarget[data='+id+']').val(dictData["target"])
          $('#ratioTarget input.inputTarget[data='+id+']').val(dictData["ratio"])
        })
        $.each(response["Params"], function(label, value) {
          $('input.footerTarget[data="'+label+'"]').val(value)
        })
      } else {
        flagBuildTarget = true
        $('#regionTarget').append($('<p class="regionTargetElement subtitleTarget" style="width:15%;">Région</p>'))
        $('#ratioTarget').append($('<p class="regionTargetElement subtitleTarget" style="width:15%;">Ratio Nb Ciblé / Nb Total</p>'))
        $.each(response["Finitions"], function(id, dictData) {
          element = $('<div class="regionTargetElement" style="width:10%; background-color: rgb(240, 240, 240);" data="'+id+'">')
          $('#regionTarget').append(element)
          subTitle = $('<p class="subtitleTarget" data="'+id+'">'+dictData["agentFName"]+'</p>')
          element.append(subTitle)
          input = $('<input class="inputTarget" data="'+id+'" value='+dictData["target"]+'>')
          element.append(input)
          sep = $(' <div class="regionTargetElement" style="width:2%; background-color: white;">')
          $('#regionTarget').append(sep)

          element = $('<div class="regionTargetElement" style="width:10%; background-color: rgb(240, 240, 240);" data="'+id+'">')
          $('#ratioTarget').append(element)
          input = $('<input class="inputTarget" data="'+id+'" value='+dictData["ratio"]+'>')
          element.append(input)
          sep = $(' <div class="regionTargetElement" style="width:2%; background-color: white;">')
          $('#ratioTarget').append(sep)
        })
        $('#regionTarget > div:last-child').remove();
        $('#ratioTarget > div:last-child').remove();

        $.each(response["Params"], function(label, value) {
          element = $('<div class="footerTarget">')
          $('#footerTarget').append(element)
          element.append($('<p class="footerTarget">'+label+'</p>'))
          element.append($('<input class="footerTarget" data="'+label+'" value='+value+'>'))
        })
        element = $('<div class="footerTarget">')
        $('#footerTarget').append(element)
        $('#footerTarget').append($('<button id="modifyTarget" class="buttonHigh" style="width:150px;">Valider</button>'))
        $('#modifyTarget').on('click', function(event) {modifyTargetAction()})
      }
    }
  })
}

function modifyTargetAction() {
  jsonData = TargetActionData()
  formData = {"modifyTarget":true, "dictTarget":JSON.stringify(jsonData), "csrfmiddlewaretoken":token}
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'post',
    data : formData,
    success : function(response) {
      if ("error" in response) {
        displayWarning("Attention", response["error"])
      } else {
        targetBuildDisplay()
      }
    }
  })

}

function TargetActionData() {
  jsonData = {"target":{}, "ratio":{}, "params":{}}
  $.each($("#regionTarget :input"), function(_, input) {
    jsonData["target"][$(input).attr("data")] = $(input).val()
  })
  $.each($("#ratioTarget :input"), function(_, input) {
    jsonData["ratio"][$(input).attr("data")] = $(input).val()
  })
  $.each($("#footerTarget :input.footerTarget"), function(_, input) {
    jsonData["params"][$(input).attr("data")] = $(input).val()
  })
  return jsonData
}

// Traitement des comptes
function displayAccount(create=true) {
  accountSetDisplay()
  accountSetHeader(create)
  accountSetQuery()
}

function accountSetDisplay() {
  $('#articleMain').css("display", "none")
  $('#account').css("display", "block")
  $('#headerTable').css("display", "block")
  $('#boxButtonCreate').css("display", "block")
  $("#headerTable").on('click', function(event) {tableClose()})
  $('#boxButtonCreate').on('click', function() {activateCreationAccount()})
}

function accountSetHeader(create) {
  title = $('<p class="tableHeaderHighLight">Gestion des comptes</p>')
  $("#accountHeader").append(title)
  if (create) {
    divAction = $('<div id="actionsAccount">')
    $("#accountHeader").append(divAction)
    buttonCreate = $('<button class="accountButton" id="accountCreate">Créer un nouveau profil</button>')
    buttonCreate.append($('<img class="accountButton" src="/static/visioAdmin/images/Créer.svg">'))
    divAction.append(buttonCreate)
    $('#actionsAccount').on('click', function(event) {displayCreateAccount()})
  }
}

function accountSetQuery() {
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : {"action":"paramAccountInit", "csrfmiddlewaretoken":token},
    success : function(response) {
      dictSetupAccount = response
      buildAccountTable()
    }
  })
}

function buildAccountTable() {
  buildAccountTableTitle()
  scrollAccount = $('<div id="scrollAccount">')
  $('#accountMain').append(scrollAccount)
  buildAccountTableValues()
}

function buildAccountTableTitle() {
  lineTitle = $('<div class="accountLine">')
  $('#accountMain').append(lineTitle)
  $.each(dictSetupAccount["titles"], function(label, size) {
    title = $('<p class="cellAccount" style="width:'+size+'%">'+label+'</p>')
    title.css({color:etexColor, width:size+'%'})
    lineTitle.append(title)
  })
}

function buildAccountTableValues() {
  $.each(dictSetupAccount["values"], function(id, line) {
    lineTitle = $('<div class="accountLine">')
    lineTitle.attr("data", id)
    let index = 0
    $.each(dictSetupAccount["titles"], function(_, size) {
      title = $('<p class="cellAccount" style="width:'+size+'%">'+line[index]+'</p>')
      lineTitle.append(title)
      if (index == 0 || index== 2) {
        title.css({cursor:"pointer"})
        title.attr("data", id)
        title.hover(
          function () {$( this ).css({color:etexColor})},
          function () {$( this ).css({color:"black"})})
        if (index == 0) {
          title.on('click', function(event) {displayModifyAccount(event)})
          title.addClass("modifyAccount")
        } else {
          title.on('click', function(event) {displayModifySector(event)})
          title.addClass("modifyAgent")
        }
      }
      index++
    })
    img = $('<img class="account" data="'+id+'" src="/static/visioAdmin/images/Supprimer.svg">')
    lineTitle.append(img)
    img.on('click', function(event) {displayRemoveAccount(event)})
    img.hover(
      function () {$("div.accountLine[data=" + id + "]").css({color:etexColor})},
      function () {$("div.accountLine[data=" + id + "]").css({color:"black"})})
    $('#scrollAccount').append(lineTitle)
  })
}

function displayRemoveAccount(event) {
  siblings = $(event.target).siblings()
  id = $(siblings[0]).attr("data")
  name = $(siblings[0]).text()
  profil = $(siblings[1]).text()
  sector = $(siblings[2]).text()
  content = "Voulez vous vraiment effacer le compte " + name + " de profil " + profil + " sur le secteur " + sector +"?"
  displayWarning("Attention", content, true)
  $("#boxWarningOK").on('click', function(event) {removeAccountQuery(id)})
}

function removeAccountQuery(id) {
  if (flagReady) {
    flagReady = false
    closeBox()
    $.ajax({
      url : "/visioAdmin/principale/",
      type: "get",
      data: {"action":"removeAccount", "csrfmiddlewaretoken":token, "id":id},
      success : function(response) {
        if ("error" in response) {
          displayWarning("Attention", response["error"])
        } else {
          $("div.accountLine[data=" + id + "]").remove()
        }
        flagReady = true
      }
    })
  }
}

function displayModifyAccount(event) {
  id = $(event.target).attr("data")
  content = "Modification du speudo, ancienne valeur : " + $(event.target).text()
  $("#protect").css("display", "block")
  $("#boxWarningRename").css("display", "block")
  $("button.boxWarningOK").css("display", "block")
  $("#boxWarningRename p.warningTitle").text("Renommer un agent")
  $("#boxWarningRename p.warningContent").text(content)
  $("#boxWarningRename button.boxWarningOK").on('click', function(event) {modifyAccountQuery(id)})
  $('#renameText').val("")
}

function modifyAccountQuery(id) {
  closeBox()
  if (flagReady) {
    flagReady = false
    newName = $('#renameText').val()
    if (newName) {
      $.ajax({
        url : "/visioAdmin/principale/",
        type: "get",
        data: {"action":"modifyAccount", "csrfmiddlewaretoken":token, "id":id, "name":newName},
        success : function(response) {
          if ("error" in response) {
            displayWarning("Attention", response["error"])
          } else {
            $("p.modifyAccount[data=" + id + "]").text(newName)
          }
          flagReady = true
        }
      })
    } else {
      displayWarning("Attention", "Il n'est pas possible d'enregistrer un nom vide.")
    }
  }
}

function displayModifySector(event) {
  id = $(event.target).attr("data")
  siblings = $(event.target).siblings()
  profil = $(siblings[1]).text()
  if (profil == "Secteur") {
    content = "Modification du secteur, ancienne valeur : " + $(event.target).text()
    $("#protect").css("display", "block")
    $("#boxWarningRename").css("display", "block")
    $("button.boxWarningOK").css("display", "block")
    $("#boxWarningRename p.warningTitle").text("Renommer un secteur")
    $("#boxWarningRename p.warningContent").text(content)
    $("#boxWarningRename button.boxWarningOK").on('click', function(event) {modifySectorQuery(id)})
    $('#renameText').val("")
  } else {
    displayWarning("Attention", "Il n'est pas possible de renommer un autre niveau géographique que celui d'un agent.")
  }
}

function modifySectorQuery(id) {
  closeBox()
  if (flagReady) {
    flagReady = false
    newName = $('#renameText').val()
    if (newName) {
      $.ajax({
        url : "/visioAdmin/principale/",
        type: "get",
        data: {"action":"modifyAgent", "csrfmiddlewaretoken":token, "id":id, "name":newName},
        success : function(response) {
          if ("error" in response) {
            displayWarning("Attention", response["error"])
          } else {
            $("p.modifyAgent[data=" + id + "]").text(newName)
          }
          flagReady = true
        }
      })
    } else {
      displayWarning("Attention", "Il n'est pas possible d'enregistrer un nom vide.")
    }
  }
}

function displayCreateAccount () {
  $('#boxWarningCreate').css({display:"block"})
  $('#createMessage').css({display:"none"})
  displayCreateAccountQuery ()
}

function displayCreateAccountQuery () {
  if ($.isEmptyObject(dictCreateAccount)) {
    $.ajax({
      url : "/visioAdmin/principale/",
      type: "get",
      data: {"action":"setupCreateAccount", "csrfmiddlewaretoken":token},
      success : function(response) {
        dictCreateAccount = response
        console.log(dictCreateAccount)
        fillupCreateAccount()
      }
    })
  } else {
    fillupCreateAccount()
  }
}

function fillupCreateAccount () {
  $('#profilCreate').empty()
  $.each(dictCreateAccount["profile"], function(key, prettyPrint) {
    option = $('<option value="'+key+'">'+prettyPrint+'</option>')
    $('#profilCreate').append(option)
    $('#profilCreate').change(function () {changeProfileAccount()})
  })
  changeProfileAccount()
}

function changeProfileAccount() {
  $('#geoCreate').empty()
  selected = $( "#profilCreate option:selected" ).val()
  console.log("changeProfileAccount", selected)
  if (!$.isEmptyObject(dictCreateAccount[selected])) {
    $.each(dictCreateAccount[selected], function(key, name) {
      $('#geoCreate').append($('<option value="'+key+'">'+name+'</option>'))
    })
  }
}

function activateCreationAccount() {
  if (flagReady) {
    flagReady = false
    pseudo = $("#pseudoCreate").val()
    pwd = $("#pwdCreate").val()
    confPwd = $("#confirmPwdCreate").val()
    profile = $( "#profilCreate option:selected" ).val()
    idGeo = $( "#geoCreate option:selected" ).val()
    jsonData = {"pseudo":pseudo, "pwd":pwd, "confPwd":confPwd, "profile":profile, "idGeo":idGeo}
    formData = {"activateCreationAccount":true, "dictCreate":JSON.stringify(jsonData), "csrfmiddlewaretoken":token}
    $.ajax({
      url : "/visioAdmin/principale/",
      type : 'post',
      data : formData,
      success : function(response) {
        if ("error" in response) {
          $('#createMessage').text(response["error"])
          $('#createMessage').css({display:"block"})
          flagReady = true
        } else {
          $("#createMessage").text(response["activateCreationAccount"])
          $("#pseudoCreate").val("")
          $("#pwdCreate").val("")
          $("#confirmPwdCreate").val("")
          $.when($("#createMessage").show().delay(3000).fadeOut()).done(function() {flagReady = true});
        }
        
      }
    })
  }
}

// Status de l'AD
function switchAdStatus() {
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "get",
    data: {"action":"switchAdStatus", "csrfmiddlewaretoken":token},
    success : function(response) {
      loadInitParam (response)
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
  $("#wheel").css({display:'block'})
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
      $("#wheel").css({display:'none'})
    }
  })
}


// Chargement du loader dans formatMainBox.js
initApplication ()

