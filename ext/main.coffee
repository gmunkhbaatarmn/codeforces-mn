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
if location.pathname is "/" or location.pathname.match(/\/problemset(?!\/problem\/)/) or location.pathname.start_with("/contests")
  $.ajax
    url: "https://raw.github.com/gmunkhbaatarmn/codeforces-mn/master/out/000-data.txt"
    dataType: "text"
    success: (text) ->
      storage = {}
      storage.updated = new Date().getTime() / 1000
      for i in text.split("\r")[0].split("|")
        storage["problem:#{i}"] = 1

      for c in text.split("\r")[1].split("|")
        i = c.split(":")[0]
        ready = Number(c.split(":")[1].split("/")[0])
        total = Number(c.split(":")[1].split("/")[1])
        storage["contest:#{i}"] = {ready: ready, total: total}

      storage.credits = []
      for t in text.split("\r")[2].split("|")
        storage.credits.push(t.split(":"))

      localStorage.mn = JSON.stringify(storage)
# endfold


#:1 Page: /                     - Home page
if location.pathname is "/"
  BOX = """
  <div class="roundbox sidebox top-contributed" style="">
    <div class="roundbox-lt">&nbsp;</div>
    <div class="roundbox-rt">&nbsp;</div>
    <div class="caption titled">→ Top translators :)</div>
    <table class="rtable ">
      <tr>
        <th class="left" style="width:2.25em">#</th>
        <th>User</th>
        <th></th>
      </tr>
      {content}
    </table>
  </div>
  """
  ROW = """
      <tr>
        <td class="left">{place}</td>
        <td class="mn-credit">{name}</td>
        <td>{score}</td>
      </tr>
  """

  ### Contribution score panel ###
  $ ->
    $("head").append """
      <style>
        .rtable tr:last-child td { border-bottom: none !important }
        .mn-credit { font-weight: bold; color: #000; font-size: 12px !important }
      </style>
      """
    storage = JSON.parse(localStorage.mn or "{}")
    if storage.credits
      content = []

      place = 0
      for t in storage.credits
        row = ROW.replace("{place}", ++place)
        row = row.replace("{name}",  t[0])
        row = row.replace("{score}", t[1])
        content.push(row)
      $("#sidebar .top-contributed:last")[0].outerHTML = BOX.replace("{content}", content.join("\n"))


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

      if storage["problem:#{problem_id}"] isnt undefined
        $(this).addClass("mn")


#:1 Page: /problemset/problem/  - Read a problem
if location.pathname.match(/\/problemset\/problem\//)
  ### Append "Монголоор унших" button ###
  $ ->
    $("head").append(STYLE)
    storage = JSON.parse(localStorage.mn or "{}")

    problem_id = location.pathname.replace("/problemset/problem/", "").replace("/", "-").toUpperCase()

    if storage["problem:#{problem_id}"] isnt undefined
      $(".problem-statement .header .title").after """
        <div class="mn-please"><a href="javascript:;">Монголоор унших</a></div>
      """

    $(".mn-please a").on "click", translate


#:1 Page: /contests/            - List of contests
if location.pathname.start_with("/contests")
  ### Stats about translated problems ###
  $ ->
    $("head").append """
      <style>
        .mn      { font-size: 0.9em; color: #666666 }
        .mn-full { font-size: 0.9em; color: #c900a9; font-weight: 600 }
      </style>
      """
    storage = JSON.parse(localStorage.mn or "{}")

    $(".contests-table tr td:nth-child(1)").each ->
      $(this).find("a")[0].innerHTML = "Enter"
      if $(this).find("a").length == 2
        $(this).find("a:first").next()[0].outerHTML = "<span>&middot;</span> "
        $(this).find("a")[1].innerHTML = "Virtual participation"
      else
        # Hide contest are not possible to practice
        $(this).closest("tr").hide()

      contest_id = $(this).find("a:first").attr("href").replace("/contest/", "")
      while contest_id.length < 3
        contest_id = "0#{contest_id}"

      ready = storage["contest:#{contest_id}"]?.ready or 0
      total = storage["contest:#{contest_id}"]?.total or 0

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

      if storage["problem:#{problem_id}"] isnt undefined
        $(this).addClass("mn")


#:1 Page: /contest/ID/problem/  - Read a problem in contest
if location.pathname.match(/^\/contest\/\d+\/problem\//)
  ### Append "Монголоор унших" button ###
  $ ->
    $("head").append(STYLE)
    storage = JSON.parse(localStorage.mn or "{}")

    problem_id = location.pathname.replace("/contest/", "")
    problem_id = problem_id.replace("/problem/", "-").toUpperCase()

    if storage["problem:#{problem_id}"] isnt undefined
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
      while curr[0] and curr[0].tagName isnt "H3"
        body.push(curr[0].outerHTML)
        curr = curr.next()
      $(".header").next().html body.join("\n")

      # Replace input
      body = []
      curr = $data.find("h3").next()
      while curr[0] and curr[0].tagName isnt "H3"
        body.push(curr[0].outerHTML)
        curr = curr.next()
      $(".input-specification").html """<div class="section-title">Оролт</div>#{body.join("\n")}"""

      # Replace output
      body = []
      curr = $data.find("h3:last").next()
      while curr[0] and curr[0].tagName isnt "H3"
        body.push(curr[0].outerHTML)
        curr = curr.next()
      $(".output-specification").html """<div class="section-title">Гаралт</div>#{body.join("\n")}"""

      # Replace sample test(s)
      $(".sample-tests .section-title").html "Жишээ тэстүүд"
      $(".sample-tests .section-title").html "Жишээ тэстүүд"
      $(".sample-tests .sample-test .input .title").html "Оролт"
      $(".sample-tests .sample-test .output .title").html "Гаралт"

      $(".mn-please").fadeOut("fast")
