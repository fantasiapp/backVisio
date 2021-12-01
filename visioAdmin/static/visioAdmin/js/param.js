let dictSynonym = {}

// Initialisation
function loadInitParamEvent() {
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
  console.log($("#SynonymsSelect").val())
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
      console.log("manageSynonymsOK", response)
      $("#synonymsMessage").text(response["fillupSynonym"])
      $("#synonymsMessage").show().delay(3000).fadeOut();
    }
  })
}

initApplication ()

