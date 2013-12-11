String.prototype.start_with = (str) -> @substr(0, str.length) == str
String.prototype.end_with   = (str) -> @slice(-str.length) == str
String.prototype.contain    = (str) -> @indexOf(str) > -1
String.prototype.is_numeric = ()    -> !isNaN(parseFloat(@)) && isFinite(@)


###
localStorage["mn-123-A"] = true
###


$ ->
  storage = JSON.parse(localStorage.mn or "{}")

  if location.pathname.start_with "/problemset"
    if storage.updated is undefined or storage.updated + 3600 > (new Date().getTime() / 1000)
      $.ajax
        url: "https://raw.github.com/gmunkhbaatarmn/codeforces-mn/master/out/data.txt"
        dataType: "text"
        async: false
        success: (text) ->
          storage = {}
          storage.updated = new Date().getTime() / 1000
          for id in text.split("|")
            storage[id] = 1
          localStorage.mn = JSON.stringify(storage)

  if location.pathname.start_with "/problemset"
    $("head").append """
      <style>
        .mn-translated td a { color: green; font-weight: bold; text-decoration: none }
        .mn-translation a { color: green !important; font-weight: bold; padding: 1px 5px 2px; border-radius: 3px }
        .mn-translation a:hover { color: #fff !important; background: #069100 !important }
        .problem-statement .math { font-size: 125%; font-family: times new roman,sans-serif }
      </style>
    """

    $("table.problems tr").each ->
      problem_id = $.trim $(this).find("td.id").text()
      console.log "problem id: " + problem_id
      problem_id = problem_id[0..-2] + "-" + problem_id[-1..-1]
      console.log "problem id: " + problem_id
      if storage[problem_id] isnt undefined
        $(this).addClass("mn-translated")

  if location.pathname.start_with "/problemset/problem/"
    problem_id = location.pathname.replace("/problemset/problem/", "").replace("/", "-").toUpperCase()

    if storage[problem_id] isnt undefined
      $(".problem-statement .header .title").after """
        <div class="mn-translation"><a href="javascript:;">Монголоор унших</a></div>
      """
      # https://raw.github.com/gmunkhbaatarmn/codeforces-mn/master/out/001-A.html

  $(".mn-translation a").on "click", ->
    problem_id = location.pathname.replace("/problemset/problem/", "").replace("/", "-").toUpperCase()
    while problem_id.length < 5
      problem_id = "0#{problem_id}"

    console.log("problem_id: " + problem_id)

    $.ajax
      url: "https://raw.github.com/gmunkhbaatarmn/codeforces-mn/master/out/#{problem_id}.html"
      dataType: "html"
      async: false
      success: (data) ->
        $data = $("<div/>").html(data)

        $(".header .title").html($data.find("h1").html())

        curr = $data.find("h1").next()
        body = []
        while curr.length
          if curr[0].tagName is "P"
            body.push("<p>" + curr.html() + "</p>")
            curr = curr.next()
          else
            curr = []
        console.log("body: " + body.join("\n"))

        $(".header").next().html body.join("\n")

        curr = $data.find("h3").next()
        body = []
        while curr.length
          if curr[0].tagName is "P"
            body.push("<p>" + curr.html() + "</p>")
            curr = curr.next()
          else
            curr = []

        $(".input-specification").html """<div class="section-title">Оролт</div>#{body.join("\n")}"""

        curr = $data.find("h3:last").next()
        body = []
        while curr.length
          if curr[0].tagName is "P"
            body.push("<p>" + curr.html() + "</p>")
            curr = curr.next()
          else
            curr = []
        $(".output-specification").html """<div class="section-title">Гаралт</div>#{body.join("\n")}"""

        $(".mn-translation").fadeOut()
