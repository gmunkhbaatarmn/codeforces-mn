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
  #:2 box_html = "..."
  box_html = """
  <div class="roundbox sidebox top-contributed top-translators">
    <div class="roundbox-lt">&nbsp;</div>
    <div class="roundbox-rt">&nbsp;</div>
    <div class="caption titled">→ Top translators</div>
    <table class="rtable ">
      <tr>
        <th class="left" style="width:2.25em">#</th>
        <th>User</th>
        <th style="font-size:13px">{ready}/{total}</th>
      </tr>
      {content}
    </table>
  </div>
  """

  #:2 row_tmpl = "..."
  row_tmpl = """
      <tr style="display:{display}" class="{class}">
        <td class="left">{place}</td>
        <td>{name}</td>
        <td>{score}</td>
      </tr>
  """
  # endfold

  # Contribution score panel
  $ ->
    $("head").append """
      <style>
        .top-translators table tr:last-child td {
          border-bottom: none
        }
        .top-translators .bottom-links {
          background: #f5f5f5;
          border-left: none !important;
          font-size: 11px !important;
          text-align: right !important
        }
      </style>
    """
    storage = JSON.parse(localStorage.mn or "{}")

    #:2 colorful = function(name, score)
    colorful = (name, score) ->
      score = Number(score)

      if score >= 0   then color = "gray"
      if score >= 25  then color = "green"
      if score >= 50  then color = "blue"
      if score >= 75  then color = "orange"
      if score >= 100 then color = "red"

      return """<a class="rated-user user-#{color}">#{name}</a>"""
    # endfold

    if storage.credits
      #:2 Middle rows
      content = ""
      ready = 0

      for [name, score], place in storage.credits
        row_html = row_tmpl.replace("{place}", place + 1)
        row_html = row_html.replace("{name}",  colorful(name, score))
        row_html = row_html.replace("{score}", score)

        if place % 2 == 0
          row_html = row_html.replace("{class}", "dark")
        else
          row_html = row_html.replace("{class}", "")

        if place >= 10
          row_html = row_html.replace("{display}", "none")
        else
          row_html = row_html.replace("{display}", "table-row")

        content += row_html
        ready += Number(score)

      #:2 Last row
      content += """
        <tr>
          <td class="bottom-links" colspan="3">
            <a href="javascript:;" class="js-more">View all &rarr;</a>
          </td>
        </tr>"""
      # endfold

      box_html = box_html.replace("{ready}", ready)
      box_html = box_html.replace("{total}", storage.total)
      box_html = box_html.replace("{content}", content)

      $("#sidebar .top-contributed:first").before(box_html)

      $(".top-translators .js-more").on "click", ->
        $(this).closest("table").find("tr").show()
        $(this).closest("tr").fadeOut().remove()


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
  # Content list with translated problem count
  $ ->
    $("head").append """
      <style>
        .mn      { font-size:0.9em; color:#666666 }
        .mn-full { font-size:0.9em; color:#c900a9; font-weight:bold }
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

      $(this).append """
        <span class="#{span}">Орчуулагдсан: #{ready} / #{total}</span>
      """


#:1 Page: /contest/ID/          - List of problems in contest
if location.pathname.match(/^\/contest\/\d+\/?$/)
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
      problem_id = location.pathname.replace("/contest/", "").replace("/", "")
      problem_id = problem_id + "-" + $(this).find("td.id").text().trim()

      if storage["problem:#{problem_id}"]
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

  $(".mn-please").fadeOut "fast", ->
    $(this).html("<strong>Орчуулж байна...</strong>").fadeIn("fast")

  $.get "http://codeforces.mn/extension/#{problem_id}.html?#{VERSION}", (r) ->
    $(".problem-statement").addClass("mn-statement")

    $r = $("<div/>").html(r)

    #:2 Replace: problem name
    $(".header .title").html "#{problem_id.slice(-1)}. #{$r.find("h1").html()}"

    #:2 Replace: problem statement
    body = []
    curr = $r.find("h1").next()
    while curr[0] and curr[0].tagName isnt "H3"
      body.push(curr[0].outerHTML)
      curr = curr.next()

    $(".header").next().html body.join("\n")

    #:2 Replace: input
    body = []
    curr = $r.find("h3").next()
    while curr[0] and curr[0].tagName isnt "H3"
      body.push(curr[0].outerHTML)
      curr = curr.next()

    $(".input-specification").html """
      <div class="section-title">Оролт</div>
      #{body.join("\n")}
    """

    #:2 Replace: output
    body = []
    curr = $r.find("h3:eq(1)").next()
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
    if $r.find("h3:eq(2)").length
      body = []
      curr = $r.find("h3:eq(2)").next()
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
