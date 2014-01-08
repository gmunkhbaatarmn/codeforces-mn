$ ->
  $(".js-more").on "click", ->
    $(this).closest("table").find("tr.hidden").removeClass("hidden")
    $(this).closest("tr").fadeOut().remove()
