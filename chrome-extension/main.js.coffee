#:1 string: start_with, end_with, contain, is_numeric
String.prototype.start_with = (str) -> @substr(0, str.length) == str
String.prototype.end_with   = (str) -> @slice(-str.length) == str
String.prototype.contain    = (str) -> @indexOf(str) > -1
String.prototype.is_numeric = ()    -> !isNaN(parseFloat(@)) && isFinite(@)
# endfold

# Note: Also set on `manifest.json`
VERSION = "0.2.4"


STYLE =
"""
<style>
  .mn-please a          { font-weight:bold; cursor:pointer }
  .mn-statement ul      { margin-bottom:1em }
  .mn-statement .credit { text-align:right; font-style:italic }
  .sample-tests .title  { font-family:sans-serif !important;
                          font-size:1em !important;
                          text-transform:none !important }
</style>
"""

#:1 Mongolian flag for language chooser
$ ->
  $("#header .lang-chooser > div:first").prepend """
    <a href="http://codeforces.mn/">
      <img src="http://codeforces.mn/images/flag-mn.png" title="Монголоор">
    </a>
  """
# endfold

#:1 Update data
$.get "http://codeforces.mn/extension?#{VERSION}", (text) ->
  storage = {}
  for i in text.split("\n")[0].split("|")
    storage["problem:#{i}"] = 1

  for c in text.split("\n")[1].split("|")
    i = c.split(":")[0]
    ready = Number(c.split(":")[1].split("/")[0])
    total = Number(c.split(":")[1].split("/")[1])
    storage["contest:#{i}"] = {ready: ready, total: total}

  storage.credits = []
  for t in text.split("\n")[2].split("|")
    storage.credits.push(t.split(":"))

  storage.total = text.split("\n")[3]

  localStorage.mn = JSON.stringify(storage)
# endfold


#:1 Page: /                     - Home page
if location.pathname is "/"
  BOX = """
  <div class="roundbox sidebox top-contributed" style="">
    <div class="roundbox-lt">&nbsp;</div>
    <div class="roundbox-rt">&nbsp;</div>
    <div class="caption titled">→ Top translators</div>
    <table class="rtable ">
      <tr>
        <th class="left" style="width:2.25em">#</th>
        <th>User</th>
        <th style="font-weight:normal;font-size:13px">{total}</th>
      </tr>
      {content}
    </table>
  </div>
  """
  ROW = """
      <tr{style}>
        <td class="left">{place}</td>
        <td class="mn-credit">{name}</td>
        <td>{score}</td>
      </tr>
  """

  ### Contribution score panel ###
  $ ->
    $("head").append """
      <style>
        .rtable tr:last-child td { border-bottom:none !important }
        .mn-credit               { font-weight:bold; color:#000; font-size:12px !important }
      </style>
      """
    storage = JSON.parse(localStorage.mn or "{}")
    color = (name, score) ->
      score = Number(score)
      r = '<span class="user-gray">'+name+'</span>'
      if score >= 25
        r = '<span class="user-green">'+name+'</span>'
      if score >= 50
        r = '<span class="user-blue">'+name+'</span>'
      if score >= 75
        r = '<span class="user-orange">'+name+'</span>'
      if score >= 100
        r = '<span class="user-red">'+name+'</span>'
      return r

    if storage.credits
      content = []

      place = 0
      ready = 0
      count = 0
      for t in storage.credits
        row = ROW.replace("{place}", ++place)
        row = row.replace("{name}",  color(t[0], t[1]))
        row = row.replace("{score}", t[1])

        count++
        if count > 10
          row = row.replace("{style}", ' style="display:none"')
        else
          row = row.replace("{style}", '')

        ready += Number(t[1])
        content.push(row)
      content.push """
				<tr>
					<td colspan="2"></td>
					<td style="border-left:0"><a href="javascript:;" onclick='$(this).closest("table").find("tr").show();$(this).closest("tr").fadeOut().remove()' class="js-more">бүгд &rarr;</a></td>
				</tr>
      """

      $("#sidebar .top-contributed:last")[0].outerHTML = BOX.replace("{total}", "#{ready}/#{storage.total}").replace("{content}", content.join("\n"))


#:1 Page: /problemset/          - List of problems
if location.pathname.match(/\/problemset(?!\/problem\/)/)
  # Highlight translated problems
  $ ->
    $("head").append """
      <style>
        .problems tr td:nth-child(2) > div:first-child {
          margin-left: 14px
        }
        .problems .mn td:nth-child(2) > div:first-child {
          margin-left: 0
        }
        .problems .mn td:nth-child(2) > div:first-child a:before {
          content: "✱ ";
          color: #c900a9;
          display: inline-block;
          float: left;
          margin-right: 4px;
          text-decoration: none
        }
      </style>
      """
    storage = JSON.parse(localStorage.mn or "{}")

    $(".problems tr").each ->
      problem_id = $(this).find("td.id").text().trim().replace(/(\d+)/, "$1-")
      if storage["problem:#{problem_id}"]
        $(this).addClass("mn")


#:1 Page: /problemset/problem/  - Read a problem
if location.pathname.match(/\/problemset\/problem\//)
  # Button: "Монголоор унших"
  $ ->
    $("head").append(STYLE)
    storage = JSON.parse(localStorage.mn or "{}")

    problem_id = location.pathname.replace("/problemset/problem/", "")
    problem_id = problem_id.replace("/", "-").toUpperCase()

    if storage["problem:#{problem_id}"]
      $(".problem-statement .header .title").after """
        <div class="mn-please"><a>Монголоор унших</a></div>
      """

    $(".mn-please a").on("click", translate)


#:1 Page: /contests/            - List of contests
if location.pathname.start_with("/contests")
  ### Stats about translated problems ###
  $ ->
    $("head").append """
      <style>
        .mn      { font-size:0.9em; color:#666666 }
        .mn-full { font-size:0.9em; color:#c900a9; font-weight:600 }
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
        .problems tr td:nth-child(2) > div:first-child { margin-left:14px }
        .mn td:nth-child(2) > div:first-child          { margin-left:0 !important }
        .mn td:nth-child(2) > div:first-child a:before { content:"✱ "; color:#c900a9; text-decoration:none; display:inline-block; float:left; margin-right:4px }
      </style>
      """
    storage = JSON.parse(localStorage.mn or "{}")

    $(".problems tr").each ->
      problem_id = location.pathname.replace("/contest/", "").replace("/", "") + "-" + $.trim($(this).find("td.id").text())
      while $.isNumeric(problem_id.slice(-1))
        problem_id = problem_id.slice(0, -1)

      if storage["problem:#{problem_id}"] isnt undefined
        $(this).addClass("mn")


#:1 Page: /contest/ID/problem/  - Read a problem in contest
if location.pathname.match(/^\/contest\/\d+\/problem\//)
  # Button: "Монголоор унших"
  $ ->
    $("head").append(STYLE)
    storage = JSON.parse(localStorage.mn or "{}")

    problem_id = location.pathname.replace("/contest/", "")
    problem_id = problem_id.replace("/problem/", "-").toUpperCase()

    if storage["problem:#{problem_id}"]
      $(".problem-statement .header .title").after """
        <div class="mn-please"><a>Монголоор унших</a></div>
      """

    $(".mn-please a").on "click", translate
# endfold


#:1 Function: translate problem statement
translate = ->
  if location.pathname.start_with("/problemset/problem/")
    problem_id = location.pathname.replace("/problemset/problem/", "")
    problem_id = problem_id.replace("/", "-").toUpperCase()

  if location.pathname.start_with("/contest/")
    problem_id = location.pathname.replace("/contest/", "")
    problem_id = problem_id.replace("/problem/", "-").toUpperCase()

  while $.isNumeric(problem_id.slice(-1))
    problem_id = problem_id.slice(0, -1)

  while problem_id.length < 5
    problem_id = "0#{problem_id}"

  $(".mn-please").fadeOut "fast", ->
    $(this).html("<strong>Орчуулж байна...</strong>").fadeIn("fast")

  $.get "http://codeforces.mn/extension/#{problem_id}.html?#{VERSION}", (data) ->
    $(".problem-statement").addClass("mn-statement")

    $data = $("<div/>").html(data)

    #:2 Replace: problem name
    $(".header .title").html "#{problem_id.slice(-1)}. #{$data.find("h1")[0].innerHTML}"

    #:2 Replace: problem statement
    body = []
    curr = $data.find("h1").next()
    while curr[0] and curr[0].tagName isnt "H3"
      body.push(curr[0].outerHTML)
      curr = curr.next()

    $(".header").next().html body.join("\n")

    #:2 Replace: input
    body = []
    curr = $data.find("h3").next()
    while curr[0] and curr[0].tagName isnt "H3"
      body.push(curr[0].outerHTML)
      curr = curr.next()

    $(".input-specification").html """
      <div class="section-title">Оролт</div>
      #{body.join("\n")}
    """

    #:2 Replace: output
    body = []
    curr = $data.find("h3:eq(1)").next()
    while curr[0] and curr[0].tagName isnt "H3"
      body.push(curr[0].outerHTML)
      curr = curr.next()

    $(".output-specification").html """
      <div class="section-title">Гаралт</div>
      #{body.join("\n")}
    """

    #:2 Replace: sample test(s)
    $(".sample-tests .section-title").html "Жишээ тэстүүд"
    $(".sample-tests .section-title").html "Жишээ тэстүүд"
    $(".sample-tests .sample-test .input .title").html "Оролт"
    $(".sample-tests .sample-test .output .title").html "Гаралт"

    #:2 Replace: note
    if $data.find("h3:eq(2)").length
      body = []
      curr = $data.find("h3:eq(2)").next()
      while curr[0] and curr[0].tagName isnt "H3"
        body.push(curr[0].outerHTML)
        curr = curr.next()
      $(".problem-statement .note").html """
        <div class="section-title">Тэмдэглэл</div>
        #{body.join("\n")}
      """
    # endfold

    $(".mn-please").fadeOut("fast")

    #:2 Include: mathjax config
    script = document.createElement("script")
    script.type = "text/x-mathjax-config"
    script.text = """
      MathJax.Hub.Config({
        tex2jax: {
          inlineMath: [["$", "$"]],
          displayMath: [["$$", "$$"]]
        },
        TeX: {
          extensions: [
            "AMSmath.js",
            "AMSsymbols.js",
            "noErrors.js"
          ]
        },
        jax: ["input/TeX", "output/HTML-CSS"],
        extensions: ["tex2jax.js"],
        showMathMenu: false
      });
    """
    document.head.appendChild(script)

    #:2 Include: mathjax source
    script = document.createElement("script")
    script.type = "text/javascript"
    script.src = "//cdn.mathjax.org/mathjax/latest/MathJax.js"
    document.head.appendChild(script)
