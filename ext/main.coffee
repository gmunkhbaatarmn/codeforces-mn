#:1 string: start_with, end_with, contain, is_numeric
String.prototype.start_with = (str) -> @substr(0, str.length) == str
String.prototype.end_with   = (str) -> @slice(-str.length) == str
String.prototype.contain    = (str) -> @indexOf(str) > -1
String.prototype.is_numeric = ()    -> !isNaN(parseFloat(@)) && isFinite(@)
# endfold


STYLE =
"""
<style>
  .mn-please a { color: green !important; font-weight: bold; padding: 1px 5px 2px; border-radius: 3px }
  .mn-please a:hover { color: #fff !important; background: #069100 !important }

  .problem-statement .math { font-size: 125%; font-family: times new roman,sans-serif }
  .sample-tests .section-title { margin-bottom: 0.5em }
  .sample-tests .title { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif !important; font-size: 1em !important; text-transform: none !important }
</style>
"""

#:1 Run in before and renew data
if location.pathname.match(/\/problemset(?!\/problem\/)/) or location.pathname.start_with("/contests")
  $.ajax
    url: "https://raw.github.com/gmunkhbaatarmn/codeforces-mn/master/out/data.txt"
    dataType: "text"
    # [todo] - make sure is async true is better idea?
    # async: false
    success: (text) ->
      storage = {}
      storage.updated = new Date().getTime() / 1000
      for id in text.split("|")
        storage[id] = 1
      localStorage.mn = JSON.stringify(storage)
# endfold


#:1 Page: /problemset/          - List of problems
if location.pathname.match(/\/problemset(?!\/problem\/)/)
  ### Highlight translated problems ###
  $ ->
    $("head").append """
      <style>
        .problems tr td:nth-child(2) > div:first-child { margin-left: 14px }
        .mn td:nth-child(2) > div:first-child { margin-left: 0 !important }
        .mn td:nth-child(2) > div:first-child a:before { content: "✱ "; color: #c900a9; text-decoration: none; display: inline-block; float: left; margin-right: 4px }
      </style>
      """
    storage = JSON.parse(localStorage.mn or "{}")

    $(".problems tr").each ->
      problem_id = $.trim($(this).find("td.id").text())
      problem_id = problem_id[0..-2] + "-" + problem_id[-1..-1]
      console.log problem_id

      if storage[problem_id] isnt undefined
        $(this).addClass("mn")


#:1 Page: /problemset/problem/  - Read a problem
if location.pathname.match(/\/problemset\/problem\//)
  ### Append "Монголоор унших" button ###
  $ ->
    $("head").append(STYLE)
    storage = JSON.parse(localStorage.mn or "{}")

    problem_id = location.pathname.replace("/problemset/problem/", "").replace("/", "-").toUpperCase()

    if storage[problem_id] isnt undefined
      $(".problem-statement .header .title").after """
        <div class="mn-please"><a href="javascript:;">Монголоор унших</a></div>
      """

    $(".mn-please a").on "click", translate


#:1 Page: /contests/            - List of contests
if location.pathname.start_with("/contests")
  # [todo] - parse contest id from location
  contest_id = ""

  ### Stats about translated problems ###
  $ ->
    $("head").append """
      <style>
        .mn      { font-size: 0.9em; color: #488b00 }
        .mn-full { font-size: 0.9em; color: #c900a9 }
      </style>
      """
    storage = JSON.parse(localStorage.mn or "{}")

    $(".contests-table tr td:nth-child(1)").each ->
      $(this).find("a:first").html("Enter").next()[0].outerHTML = "<span>&middot;</span> "
      $(this).find("a:last").html("Virtual participation")
      return

      # [todo] - fill ready, total variables
      # ready = storage["contest-#{contest_id}"]?.ready or 0
      # total = storage["contest-#{contest_id}"]?.total or 0
      ready = 2
      total = 5

      return if ready <= 0
      span = if ready is total then "mn-full" else "mn"

      $(this).append """<span class="#{span}">Орчуулагдсан: #{ready} / #{total}</span>"""


#:1 Page: /contest/ID/          - List of problems in contest
if location.pathname.match(/^\/contest\/\d+\/?$/)
  ### Highlight translated problems ###
  $ ->
    $("head").append """
      <style>
        .problems tr td:nth-child(2) > div:first-child { margin-left: 14px }
        .mn td:nth-child(2) > div:first-child { margin-left: 0 !important }
        .mn td:nth-child(2) > div:first-child a:before { content: "✱ "; color: #c900a9; text-decoration: none; display: inline-block; float: left; margin-right: 4px }
      </style>
      """
    storage = JSON.parse(localStorage.mn or "{}")

    $(".problems tr").each ->
      problem_id = location.pathname.replace("/contest/", "") + "-" + $.trim($(this).find("td.id").text())

      if storage[problem_id] isnt undefined
        $(this).addClass("mn")


#:1 Page: /contest/ID/problem/  - Read a problem in contest
if location.pathname.match(/^\/contest\/\d+\/problem\//)
  console.log("Read a problem in contest")
  ### Append "Монголоор унших" button ###
  $ ->
    $("head").append(STYLE)
    storage = JSON.parse(localStorage.mn or "{}")

    problem_id = location.pathname.replace("/contest/", "")
    problem_id = problem_id.replace("/problem/", "-").toUpperCase()
    console.log("problem_id: " + problem_id)

    if storage[problem_id] isnt undefined
      $(".problem-statement .header .title").after """
        <div class="mn-please"><a href="javascript:;">Монголоор унших</a></div>
      """

    $(".mn-please a").on "click", translate
# endfold


#:1 Function: translate problem statement
translate = ->
  if location.pathname.start_with("/problemset/problem/")
    problem_id = location.pathname.replace("/problemset/problem/", "").replace("/", "-").toUpperCase()

  if location.pathname.start_with("/contest/")
    problem_id = location.pathname.replace("/contest/", "")
    problem_id = problem_id.replace("/problem/", "-").toUpperCase()

  while problem_id.length < 5
    problem_id = "0#{problem_id}"

  $(".mn-please").fadeOut "fast", ->
    $(this).html("<strong>Орчуулж байна...</strong>").fadeIn("fast")

  $.ajax
    url: "https://raw.github.com/gmunkhbaatarmn/codeforces-mn/master/out/#{problem_id}.html"
    dataType: "html"
    success: (data) ->
      $data = $("<div/>").html(data)

      # Replace problem name
      $(".header .title").html "#{problem_id.slice(-1)}. #{$data.find("h1")[0].innerHTML}"

      # Replace problem statement
      body = []
      curr = $data.find("h1").next()
      while curr[0]?.tagName is "P"
        body.push(curr[0].outerHTML)
        curr = curr.next()
      $(".header").next().html body.join("\n")

      # Replace input
      body = []
      curr = $data.find("h3").next()
      while curr[0]?.tagName is "P"
        body.push(curr[0].outerHTML)
        curr = curr.next()
      $(".input-specification").html """<div class="section-title">Оролт</div>#{body.join("\n")}"""

      # Replace output
      body = []
      curr = $data.find("h3:last").next()
      while curr[0]?.tagName is "P"
        body.push(curr[0].outerHTML)
        curr = curr.next()
      $(".output-specification").html """<div class="section-title">Гаралт</div>#{body.join("\n")}"""

      # Replace sample test(s)
      $(".sample-tests .section-title").html "Жишээ тэстүүд"
      $(".sample-tests .section-title").html "Жишээ тэстүүд"
      $(".sample-tests .sample-test .input .title").html "Оролт"
      $(".sample-tests .sample-test .output .title").html "Гаралт"

      $(".mn-please").fadeOut("fast")
