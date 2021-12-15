let selectedTableConsult = "Ref"
let flagFree = true
function loadInitConsult() {
  $("#consultConnectionButton").on('click', function(event) {displayAccount(false)})
  $('#downloadConnectionButton').attr("href", "/visioAdmin/principale/?action=createTable&nature=connection&csrfmiddlewaretoken="+token)
  $("#consultTargetButton").on('click', function(event) {displayConsultTarget("Ref")})
  $('#downloadTargetButton').attr("href", "/visioAdmin/principale/?action=createTable&nature=target&csrfmiddlewaretoken="+token)
  $("#consultActionButton").on('click', function(event) {displayConsultAction()})
  $('#downloadActionButton').attr("href", "/visioAdmin/principale/?action=createTable&nature=action&csrfmiddlewaretoken="+token)
  $("#consultCurrentBaseButton").on('click', function(event) {tableHeaderSelect("Ref", "Saved", true)})
  $('#downloadCurrentBaseButton').attr("href", "/visioAdmin/principale/?action=createTable&nature=currentBase&csrfmiddlewaretoken="+token)
}

//Actions
function displayConsultAction() {
  if (flagFree) {
    flagFree = false
    $("#wheel").css({display:'block'})
    $("#tableMain").empty()
    $('#tableHeader').empty()
    visualizeActionTableQuery()
  }
}

function visualizeActionTableQuery() {
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : {"action":"visualizeActionTable", "csrfmiddlewaretoken":token},
    success : function(response) {
      console.log(response["titles"])
      loadActionTable (response)
      $("#wheel").css({display:'none'})
      flagFree = true
    },
    error : function(response) {
      console.log("error visualizeActionTableQuery", response)
      $("#wheel").css({display:'none'})
      flagFree = true
    }
  })
}

function loadActionTable(response) {
  addActionTableHeader ()
  buildStructureTitleValidate(response, "tableMain")
  buildStructureLineValidate(response["titles"], response["values"])
}

function addActionTableHeader () {
  title = $('<p class="tableHeaderHighLight">Historique des actions de l\'administratrice·eur</p>')
  $("#tableHeader").append(title)
  $("#articleMain").css({display:'none'})
  $('#tableArticle').css({display:'flex', 'flex-direction':'column', 'height':'80%'})
  $('#headerTable').css({display:'block'})
}

function displayConsultTarget(table) {
  if (flagFree) {
    flagFree = false
    console.log("displayConsultTarget", table)
    $("#wheel").css({display:'block'})
    $("#tableMain").empty()
    $('#tableHeader').empty()
    visualizeTargetTableQuery(table, tableHeader=true)
  }
}

function visualizeTargetTableQuery(table, tableHeader) {
  $.ajax({
    url : "/visioAdmin/principale/",
    type : 'get',
    data : {"action":"visualizeTargetTable", "table":table, "csrfmiddlewaretoken":token},
    success : function(response) {
      loadTargetTable (response, tableHeader)
      $("#wheel").css({display:'none'})
      flagFree = true
    },
    error : function(response) {
      console.log("error visualizeTargetTableQuery", response)
      $("#wheel").css({display:'none'})
      flagFree = true
    }
  })
}

function loadTargetTable(response, tableHeader) {
  if (tableHeader) {
    addTargetTableHeader()
  }
  buildStructureTitleValidate(response, "tableMain")
  buildStructureLineValidate(response["titles"], response["values"])
  $("#articleMain").css({display:'none'})
  $('#tableArticle').css({display:'flex', 'flex-direction':'column', 'height':'80%'})
  $('#headerTable').css({display:'block'})
}

function addTargetTableHeader() {
  $('#tableHeader').append('<div id="tableHeadeRow1" class="tableHeader"></div>')
  $('#tableHeader').append('<div id="tableHeadeRow2" class="tableHeader"></div>')
  title = $('<p class="tableHeaderHighLight">Rapport de ciblage</p>')
  $("#tableHeadeRow1").append(title)

  $('#tableHeadeRow2').append('<div id="tableTab">')
  $('#tableTab').append('<div id="tableHeaderRef" class="tableTab"><p class="tableHeader">Référentiel</p></div>')
  $('#tableTab').append('<div id="tableHeaderTarget"  class="tableTab"><p class="tableHeader">Ciblage</p></div>')
  $("#tableHeaderRef p").addClass("tableHeaderHighLight")
  $('#tableMain').css({'display':'flex', 'flex-direction':'column'})

  $("#tableHeaderRef").on('click', function(event) {TargetHeaderSelect("Ref")})
  $("#tableHeaderTarget").on('click', function(event) {TargetHeaderSelect("Target")})
}

function TargetHeaderSelect(table) {
  if (table == "Ref") {
    other = "Target"
  } else {
    other = "Ref"
  }
  console.log("TargetHeaderSelect", table)
  $("#tableMain").empty()
  $("#wheel").css("display", 'block')
  flagFree = false
  $("#tableHeader" + table +" p").addClass("tableHeaderHighLight")
  $("#tableHeader" + other +" p").removeClass("tableHeaderHighLight")
  visualizeTargetTableQuery(table, false)
}

function buildStructureLineValidate(titles, listLines) {
  let section = $('<div class="validateSection" style="height:100%">')
  $('#tableMain').append(section)
  $.each(listLines, function(_, line) {
    let row = $('<div class="validateLine">')
    section.append(row)
    let index = 0
    $.each(titles, function(_, size) {
      row.append($('<p class="validateCell" style="width:'+size+'%">'+(line[index] || "-")+'</p>'))
      index++
    })
  })
}

