function loadInitConsult() {
  $("#consultConnectionButton").on('click', function(event) {displayAccount(false)})
  $('#downloadConnectionButton').attr("href", "/visioAdmin/principale/?action=createTable&nature=connection&csrfmiddlewaretoken="+token)
  $("#consultCurrentBaseButton").on('click', function(event) {tableHeaderSelect("Ref", "Saved", true)})
  $('#downloadCurrentBaseButton').attr("href", "/visioAdmin/principale/?action=createTable&nature=currentBase&csrfmiddlewaretoken="+token)
  
}
