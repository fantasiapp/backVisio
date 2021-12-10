let flagBuildValidate = false

// Initialisation
function loadInitValidateEvent() {
  $('#validationConsult').on('click', function(event) {displayValidation()})
}

function displayValidation() {
  $("#wheel").css({display:'block'})
  validateSetDisplay()
  title = $('<p class="tableHeaderHighLight">Demandes en cours</p>')
  $("#validateHeader").append(title)
  validateBuildDisplay()
}

function validateSetDisplay() {
  $('#articleMain').css("display", "none")
  $('#validate').css("display", "block")
  $('#headerTable').css("display", "block")
  $("#headerTable").on('click', function(event) {tableClose()})
}

function validateBuildDisplay() {
  $.ajax({
    url : "/visioAdmin/principale/",
    type: "get",
    data: {"action":"buildValidate", "csrfmiddlewaretoken":token},
    success : function(response) {
      if (flagBuildValidate) {
        updateStructureValidate(response)
      } else {
        flagBuildValidate = true
        buildStructureValidate(response)
      }
      $("#wheel").css({display:'none'})
    }
  })
}

function updateStructureValidate(response) {
  $.each(response["values"], function(rowTitle, listLines) {
    let section = $('div.validateSection[data="'+rowTitle+'"')
    section.empty()
    $.each(listLines, function(id, line) {
      let row = $('<div class="validateLine">')
      section.append(row)
      buildStructureValidateRow(id, row, line, response["titles"], rowTitle)
    })
  })
}

function buildStructureValidate(response) {
  $('#validateHeader').append($('<div id="validateTitle">'))
  $.each(response["titles"], function(label, size) {
    $('#validateTitle').append($('<p class="validateTitle" style="width:'+size+'%">'+label+'</p>'))
  })
  $('#validateTitle').append($('<p class="validateTitle" style="width:10%">Confirmer</p>'))
  $('#validateTitle').append($('<p class="validateTitle" style="width:10%">Supprimer</p>'))

  $.each(response["values"], function(rowTitle, listLines) {
    let title = $('<div class="validateRowTitle"><p class="validateRowTitle">'+rowTitle+'</p>')
    $('#validateMain').append(title)
    selectAllAction(title, rowTitle)
    let section = $('<div class="validateSection" data="'+rowTitle+'">')
    $('#validateMain').append(section)
    $.each(listLines, function(id, line) {
      let row = $('<div class="validateLine" data='+id+'>')
      section.append(row)
      buildStructureValidateRow(id, row, line, response["titles"], rowTitle)
    })
  })
  let targetUpdate = $('<button id="targetUpdate" class="buttonHigh validate">Valider</button>')
  $('#validateMain').append(targetUpdate)
  targetUpdate.on('click', function(event) {targetUpdateAction()})
}

function selectAllAction(title, rowTitle) {
  if (rowTitle != "Bassin") {
    let selectAll = $('<div class="validationSelectAll">')
    title.append(selectAll)

    let confirmation = $('<img class="validateCell confirm" style="width:50%; padding:0" data="'+rowTitle+'" data-status="off" src="/static/visioAdmin/images/Check.svg">')
    let  suppression = $('<img class="validateCell delete" style="width:50%; padding:0" data="'+rowTitle+'" data-status="off" src="/static/visioAdmin/images/Delete.svg">')
    selectAll.append(confirmation)
    selectAll.append(suppression)
    confirmation.on('click', function(event) {confirmValidationAll(event)})
    suppression.on('click', function(event) {suppressValidationAll(event)})
  }
}

function buildStructureValidateRow(id, row, line, titles, rowTitle) {
  let index = 0
  $.each(titles, function(_, size) {
    row.append($('<p class="validateCell" style="width:'+size+'%">'+line[index]+'</p>'))
    index++
  })
  if (rowTitle != "Bassin") {
    confirmation = $('<img class="validateCell confirm" style="width:10%" data="'+id+'" data-status="off" src="/static/visioAdmin/images/Check.svg">')
    row.append(confirmation)
    suppression = $('<img class="validateCell delete" style="width:10%" data="'+id+'" data-status="off" src="/static/visioAdmin/images/Delete.svg">')
    row.append(suppression)
    confirmation.on('click', function(event) {confirmValidation(event)})
    suppression.on('click', function(event) {suppressValidation(event)})
  } else {
    row.append('<div style="width:20%">')
  }
}

function confirmValidation(event) {
  id = $(event.target).attr("data")
  suppressStatus = $('img.delete[data="'+id+'"]').attr("data-status")
  if (suppressStatus == "on") {
    displayWarning("Attention", "Impossible de valider une consigne sélectionnée en destruction. Veuillez retirer la destruction d'abord.")
  } else {
    if ($(event.target).attr("data-status") == "off") {
      $(event.target).css({content:'url("/static/visioAdmin/images/CheckConfirmed.svg")'})
      $(event.target).attr("data-status", "on")
    } else {
      $(event.target).css({content:'url("/static/visioAdmin/images/Check.svg")'})
      $(event.target).attr("data-status", "off")
    }
    grandPa = $(event.target).parent().parent()
  }
}

function suppressValidation(event) {
  id = $(event.target).attr("data")
  suppressStatus = $('img.confirm[data="'+id+'"]').attr("data-status")
  if (suppressStatus == "on") {
    displayWarning("Attention", "Impossible de supprimer une consigne confirmée. Veuillez retirer la confirmation d'abord.")
  } else {
    if ($(event.target).attr("data-status") == "off") {
      $(event.target).css({content:'url("/static/visioAdmin/images/DeleteConfirmed.svg")'})
      $(event.target).attr("data-status", "on")
    } else {
      $(event.target).css({content:'url("/static/visioAdmin/images/Delete.svg")'})
      $(event.target).attr("data-status", "off")
    }
  }
}

function confirmValidationAll(event) {
  let rowTitle = $(event.target).attr("data")
  let status = "on"
  if ($(event.target).attr("data-status") == "off") {
    $(event.target).css({content:'url("/static/visioAdmin/images/CheckConfirmed.svg")'})
    $(event.target).attr("data-status", "on")
  } else {
    $(event.target).css({content:'url("/static/visioAdmin/images/Check.svg")'})
    $(event.target).attr("data-status", "off")
    status = "off"
  }
  selectConfirmAllLine(rowTitle, status)
}

function selectConfirmAllLine(rowTitle, mainStatus) {
  $('img.delete[data="'+rowTitle+'"]').attr("data-status", "off")
  $('img.delete[data="'+rowTitle+'"]').css({content:'url("/static/visioAdmin/images/Delete.svg")'})
  let imageConfirm = 'url("/static/visioAdmin/images/CheckConfirmed.svg")'
  if (mainStatus == "off") {
    imageConfirm = 'url("/static/visioAdmin/images/Check.svg")'
  }
  $.each($('#validateMain').children(), function(_, div) {
    if ($(div).attr("data") == rowTitle) {
      $.each($(div).children(), function(_, line) {
        let confirm = $(line).children()[7]
        $(confirm).attr("data-status", mainStatus)
        $(confirm).css({content:imageConfirm})
        let suppress = $(line).children()[8]
        $(suppress).attr("data-status", "off")
        $(suppress).css({content:'url("/static/visioAdmin/images/Delete.svg")'})
        })
      }
  })
}

function suppressValidationAll(event) {
  let rowTitle = $(event.target).attr("data")
  let status = "on"
  if ($(event.target).attr("data-status") == "off") {
    $(event.target).css({content:'url("/static/visioAdmin/images/DeleteConfirmed.svg")'})
    $(event.target).attr("data-status", "on")
  } else {
    $(event.target).css({content:'url("/static/visioAdmin/images/Delete.svg")'})
    $(event.target).attr("data-status", "off")
    status = "off"
  }
  selectDeleteAllLine(rowTitle, status)
}

function selectDeleteAllLine(rowTitle, mainStatus) {
  $('img.confirm[data="'+rowTitle+'"]').attr("data-status", "off")
  $('img.confirm[data="'+rowTitle+'"]').css({content:'url("/static/visioAdmin/images/Check.svg")'})
  let imageDelete = 'url("/static/visioAdmin/images/DeleteConfirmed.svg")'
  if (mainStatus == "off") {
    imageDelete = 'url("/static/visioAdmin/images/Delete.svg")'
  }
  $.each($('#validateMain').children(), function(_, div) {
    if ($(div).attr("data") == rowTitle) {
      $.each($(div).children(), function(_, line) {
        let confirm = $(line).children()[7]
        $(confirm).attr("data-status", "off")
        $(confirm).css({content:'url("/static/visioAdmin/images/Check.svg")'})
        let suppress = $(line).children()[8]
        $(suppress).attr("data-status", mainStatus)
        $(suppress).css({content:imageDelete})
        })
      }
  })
}

function targetUpdateAction() {
  $("#wheel").css({display:'block'})
  dataJson = createDataValidation ()
  formData = {"updateValidate":true, "dictValidate":JSON.stringify(dataJson), "csrfmiddlewaretoken":token}
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'post',
    data : formData,
    success : function(response) {
      updateStructureValidate(response)
      $("#wheel").css({display:'none'})
    }
  })
}

function createDataValidation() {
  let dataJson = {"modify":[], "delete":[]}
  $.each($('#validateMain').children(), function(_, div) {
    if ($(div).attr("data")) {
      let action = $(div).attr("data")
      $.each($(div).children(), function(_, line) {
        let confirm = $(line).children()[7]
        if ($(confirm).attr("data-status") == "on") {
          let pdvId = $(confirm).attr("data")
          let cellValue = $(line).children()[6]
          value = $(cellValue).text() == "Non"
          dataJson["modify"].push({"pdvId":pdvId, "action":action, "value":value})
        }

        let suppress = $(line).children()[8]
        if ($(suppress).attr("data-status") == "on") {
          let pdvId = $(suppress).attr("data")
          let cellValue = $(line).children()[5]
          value = $(cellValue).text() == "Non"
          dataJson["delete"].push({"pdvId":pdvId, "action":action, "value":value})
        }
      })
    }
  })
  return dataJson
}