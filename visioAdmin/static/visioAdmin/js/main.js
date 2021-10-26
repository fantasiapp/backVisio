var csrfmiddlewaretoken = $("nav.performancesNav input[name='csrfmiddlewaretoken']").val()
var numberOfLinesInMessage = 30

$("#PerfEmtpyBase").on('click', function(event) {perfEmptyBase(true)})
$("#PerfPopulateBase").on('click', function(event) {perfPopulateBase(true, "empty")})
$("#VisualizePdv").on('click', function(event) {visualizePdv()})
$("#VisualizeVentes").on('click', function(event) {visualizeVentes()})
$("#VisualizePdvXlsx").on('click', function(event) {VisualizePdvXlsx()})
$("#VisualizeVentesXlsx").on('click', function(event) {visualizeVentesXlsx()})
$("#OpenAd").on('click', function(event) {openAd()})
$("#Test").on('click', function(event) {test()})

function perfEmptyBase (start) {
  if (start) {
    $("div.loader").css({display:'block'})
    $('section').empty()
  }
  $.ajax({
    url : "/visioAdmin/performances/",
    type : 'get',
    data : {"action":"perfEmptyBase", "csrfmiddlewaretoken":csrfmiddlewaretoken, 'start':start},
    success : function(response) {
      if (response['errors'].length != 0) {
        if ($('section p').length >= numberOfLinesInMessage) {
          $('section p').last().remove()
        }
        $('section').prepend('<p>Error : '+ response["errors"][0] + '</p>')
        $("div.loader").css({display:'none'})
      } else {
        if ($('section p').length >= numberOfLinesInMessage) {
          $('section p').last().remove()
        }
        $('section').prepend('<p>'+ response["message"] + '</p>')
        if (!response['end']) {
          perfEmptyBase (false)
        } else {
          $("div.loader").css({display:'none'})
        }
      }
    },
    error : function(response) {
      console.log(response)
      $("div.loader").css({display:'none'})
    }
  })
}

function perfPopulateBase (start, method) {
  if (start && method == "empty") {
    $('section').empty()
    $("div.loader").css({display:'block'})
  }
  $.ajax({
    url : "/visioAdmin/performances/",
    type : 'get',
    data : {"action":"perfPopulateBase", 'method':method, 'start':start, "csrfmiddlewaretoken":csrfmiddlewaretoken},
    success : function(response) {
      if (response['errors'].length != 0) {
        if ($('section p').length >= numberOfLinesInMessage) {
          $('section p').last().remove()
        }
        $('section').prepend('<p>Error : '+ response["errors"][0] + '</p>')
        $("div.loader").css({display:'none'})
      } else {
        if ($('section p').length >= numberOfLinesInMessage) {
          $('section p').last().remove()
        }
        $('section').prepend('<p>'+ response["message"] + '</p>')
        if (response['query'] == "emptyDatabase") {
          if (response['end']) {
            perfPopulateBase (true, "populate")
          } else {
            perfPopulateBase (false, "empty")
          }
        } else {
          if (response['end']) {
            $("div.loader").css({display:'none'})
          } else {
            perfPopulateBase (false, "populate")
          }
        }
      }
    },
    error : function(response) {
      console.log("error", response)
      $("div.loader").css({display:'none'})
    }
  })
}

function visualizePdv () {
  visualizeGeneric('Pdv', scroll=true)
}

function visualizeVentes () {
  visualizeGeneric('Ventes', scroll=false)
}

function VisualizePdvXlsx () {
  visualizeGeneric('PdvSave', scroll=false, keep=true)
}

function visualizeVentesXlsx () {
  console.log("visualizeVentesXlsx")
  visualizeGeneric('VentesSave', scroll=false)
}

function visualizeGeneric(table, scroll=true) {
  $("div.loader").css({display:'block'})
  data = {"action":"perfImport"+table, "csrfmiddlewaretoken":csrfmiddlewaretoken}
  $.ajax({
    url : "/visioAdmin/performances/",
    type : 'get',
    data : data,
    success : function(response) {
      columnsTitle = []
      $.each(response['titles'], function( _, value ) {
        columnsTitle.push({title: value})
      })
      buildTable (columnsTitle, response['values'], 'table' + table, scroll)
      if ("follow" in response) {
        visualizeGeneric(response['follow'])
      } else {
        $("div.loader").css({display:'none'})
      }
    },
    error : function(response) {
      console.log("error", response)
      $("div.loader").css({display:'none'})
    }
  })
}

function buildTable (columnsTitle, values, tableId, scroll) {
  $('section').empty()
  if (scroll) {
    $('section').append('<table id="'+tableId+'" class="display" style="width:100%">')
    $('#'+tableId).DataTable({"scrollX": scroll, data: values, columns: columnsTitle})
  } else {
    $('section').append('<table id="'+tableId+'" class="display">')
    $('#'+tableId).DataTable({data: values, columns: columnsTitle})
  }
}

function openAd () {
  $('section').empty()
  $("div.loader").css({display:'block'})
  $.ajax({
    url : "/visioAdmin/performances/",
    type : 'get',
    data : {"action":"openAd", "csrfmiddlewaretoken":csrfmiddlewaretoken},
    success : function(response) {
      console.log(response)
      $('section').prepend('<p>'+ response["message"] + '</p>')
      $("div.loader").css({display:'none'})
    }
  })
}

function test () {
  $.ajax({
    url : "/visioAdmin/performances/",
    type : 'get',
    data : {"action":"test", "csrfmiddlewaretoken":csrfmiddlewaretoken},
    success : function(response) {
      console.log(response)
    }
  })
}