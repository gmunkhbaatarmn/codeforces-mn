// todo: remove files: `main.js`, `main.js.coffee`
// todo: rename file: `main2.js` to `main.js`
// todo: update: `main2.js` to `main.js` on `manifest.json`
const VERSION = '0.2.5'
const STYLE = `
<style>
  .mn-please a          { font-weight:bold; cursor:pointer }
  .mn-statement ul      { margin-bottom:1em }
  .mn-statement .credit { text-align:right; font-style:italic }
  .sample-tests .title  { font-family:sans-serif !important;
                          font-size:1em !important;
                          text-transform:none !important }
</style>
`

//: Add Mongolian flag for language chooser
$(function() {
  $('#header .lang-chooser > div:first').prepend(`
    <a href="https://codeforces.mn/" style="text-decoration:none">
      <img src="https://codeforces.mn/images/flag-mn.png" title="Монголоор">
    </a>
  `)
})
// endfold

//: Update data
$.get(`https://codeforces.mn/extension?${VERSION}`, function(text) {
  let storage = {}

  // 1st line: problem codes. format: `{int}-{letter}|{int}-{letter}`
  for (let i = 0; i < text.split('\n')[0].split('|').length; i++) {
    let problem = text.split('\n')[0].split('|')[i]
    storage[`problem:${problem}`] = 1
  }

  // 2nd line: contest translated status. format: `{int}:{int}/{int}|{int}:{int}/{int}`
  for (let i = 0; i < text.split('\n')[1].split('|').length; i++) {
    let contest = text.split('\n')[1].split('|')[i]
    let id = contest.split(':')[0]
    let ready = Number(contest.split(':')[1].split('/')[0])
    let total = Number(contest.split(':')[1].split('/')[1])
    storage[`contest:${id}`] = {ready: ready, total: total}
  }

  // 3rd line: rank table of translators `{name}:{int}|{name}:{int}`
  storage.credits = []
  for (let i = 0; i < text.split('\n')[2].split('|').length; i++) {
    let translator = text.split('\n')[2].split('|')[i]
    storage.credits.push(translator.split(':'))
  }

  // 4th line: total count of translation
  storage.total = text.split('\n')[3]

  localStorage.mn = JSON.stringify(storage)
})
// endfold

//: Page: /                     Home page
if (location.pathname === '/') {
  //:2 box_tmpl = '...'
  let box_tmpl = `
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
  `

  //:2 row_tmpl = '...'
  let row_tmpl = `
      <tr style="display:{display}" class="{class}">
        <td class="left">{place}</td>
        <td>{name}</td>
        <td>{score}</td>
      </tr>
  `
  //:2 style = '...'
  let style = `
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
  `

  //:2 colorful(name, score)
  let colorful = function(name, score) {
    let score_number = Number(score)
    let color = 'gray'

    if (score_number >= 25) {
      color = 'green'
    }
    if (score_number >= 50) {
      color = 'blue'
    }
    if (score_number >= 75) {
      color = 'orange'
    }
    if (score_number >= 100) {
      color = 'violet'
    }

    return `<a class="rated-user user-${color}">${name}</a>`
  }
  // endfold2

  // Contribution score panel
  $(function() {
    $('head').append(style)
    let storage = JSON.parse(localStorage.mn || '{}')

    if (storage.credits) {
      //:2 Middle rows
      let content = ''
      let ready = 0

      for (let i = 0; i < storage.credits.length; i++) {
        let name = storage.credits[i][0]
        let score = storage.credits[i][1]
        let place = i + 1

        let row_html = row_tmpl.replace('{place}', place + 1)
        row_html = row_html.replace('{name}', colorful(name, score))
        row_html = row_html.replace('{score}', score)

        if (place % 2 === 0) {
          row_html = row_html.replace('{class}', 'dark')
        } else {
          row_html = row_html.replace('{class}', '')
        }

        if (place >= 10) {
          row_html = row_html.replace('{display}', 'none')
        } else {
          row_html = row_html.replace('{display}', 'table-row')
        }

        content += row_html
        ready += Number(score)
      }

      //:2 Last row
      content += `
        <tr>
          <td class="bottom-links" colspan="3">
            <a href="javascript:;" class="js-more">View all &rarr;</a>
          </td>
        </tr>
      `
      // endfold2

      let box_html = box_tmpl.replace('{ready}', ready)
      box_html = box_html.replace('{total}', storage.total)
      box_html = box_html.replace('{content}', content)

      $('#sidebar .top-contributed:first').before(box_html)

      $('.top-translators .js-more').on('click', function(e) {
        $(e.currentTarget).closest('table').find('tr').show()
        $(e.currentTarget).closest('tr').fadeOut().remove()
      })
    }
  })
}

//: Page: /problemset/          List of problems (empty)
if (location.pathname.match(/\/problemset(?!\/problem\/)/)) {
  // Highlight translated problems
  $(function() {
    $('head').append(`
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
    `)
    let storage = JSON.parse(localStorage.mn || '{}')

    $('.problems tr').each(function(idx, elm) {
      // Skip header
      if (! $(elm).find('td.id').text().trim()) {
        return
      }
      let problem_id = $(elm).find('td.id').text().trim()
      problem_id = problem_id.replace(/(\d+)/, '$1-')
      if (storage[`problem:${problem_id}`]) {
        $(elm).addClass('mn')
      }
    })
  })
}

//: Page: /problemset/problem   Read a problem (empty)
if (location.pathname.match(/\/problemset\/problem\//)) {
  // Button: "Монголоор унших"
  $(function() {
    $('head').append(STYLE)

    let storage = JSON.parse(localStorage.mn || '{}')
    let problem_id = location.pathname
    problem_id = problem_id.replace('/problemset/problem/', '')
    problem_id = problem_id.replace('/', '-').toUpperCase()

    if (storage[`problem:${problem_id}`]) {
      $('.problem-statement .header .title').after(`
        <div class="mn-please"><a>Монголоор унших</a></div>
      `)
      $('.mn-please a').on('click', function(e) {
        translate(problem_id)
      })
    }
  })
}

//: Page: /contests/            List of contests
if (location.pathname.startsWith('/contests')) {
  // Content list with translated problem count
  $(function() {
    $('head').append(`
      <style>
        .mn      { font-size:0.9em; color:#666666 }
        .mn-full { font-size:0.9em; color:#c900a9; font-weight:bold }
      </style>
    `)

    let storage = JSON.parse(localStorage.mn || '{}')

    $('.contests-table tr td:nth-child(1)').each(function(idx, elm) {
      // Select only contests are possible to practice
      // (possible contest has "Enter" and "Virtual participation" links both)
      if ($(elm).find('a').length < 2) {
        return
      }

      let contest_id = $(elm).find('a:first').attr('href').replace('/contest/', '')
      while (contest_id.length < 3) {
        contest_id = `0${contest_id}`
      }

      if (! storage[`contest:${contest_id}`]) {
        return
      }
      let ready = storage[`contest:${contest_id}`].ready || 0
      let total = storage[`contest:${contest_id}`].total || 0

      if (ready <= 0) {
        return
      }
      let class_ = ready === total ? 'mn-full' : 'mn'
      $(elm).append(`<span class="${class_}">Орчуулагдсан: ${ready} / ${total}</span>`)
    })
  })
}

//: Page: /contest/ID/          List of problems in contest
if (location.pathname.match(/^\/contest\/\d+\/?$/)) {
  // Highlight translated problems
  $(function() {
    $('head').append(`
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
    `)
    let storage = JSON.parse(localStorage.mn || '{}')

    $('.problems tr').each(function(idx, elm) {
      // Skip header
      if (! $(elm).find('td.id').text().trim()) {
        return
      }

      let problem_id = location.pathname.replace('/contest/', '').replace('/', '')
      problem_id = problem_id + '-' + $(elm).find('td.id').text().trim()

      if (storage[`problem:${problem_id}`]) {
        $(elm).addClass('mn')
      }
    })
  })
}

//: Page: /contest/ID/problem/  Read a problem in contest (empty)
if (location.pathname.match(/^\/contest\/\d+\/problem\//)) {
  // Button: "Монголоор унших"
  $(function() {
    $('head').append(STYLE)

    let storage = JSON.parse(localStorage.mn || '{}')
    let problem_id = location.pathname
    problem_id = problem_id.replace('/contest/', '')
    problem_id = problem_id.replace('/problem/', '-').toUpperCase()

    if (storage[`problem:${problem_id}`]) {
      $('.problem-statement .header .title').after(`
        <div class="mn-please"><a>Монголоор унших</a></div>
      `)
      $('.mn-please a').on('click', function(e) {
        translate(problem_id)
      })
    }
  })
}
// endfold

//: Function: translate problem statement
var translate = function(problem_id) {
  $('.mn-please').fadeOut('fast', function() {
    $(this).html('<strong>Орчуулж байна...</strong>').fadeIn('fast')
  })

  $.get(`https://codeforces.mn/extension/${problem_id}.html?${VERSION}`, function(r) {
    let $r = $('<div/>').html(r)

    $('.problem-statement').addClass('mn-statement')

    //:2 Replace: problem name
    $('.header .title').html(`${problem_id.slice(-1)}. ${$r.find('h1').html()}`)

    //:2 Replace: problem statement
    let body = []
    let curr = $r.find('h1').next()
    while (curr[0] && curr[0].tagName !== 'H3') {
      body.push(curr[0].outerHTML)
      curr = curr.next()
    }
    $('.header').next().html(body.join('\n'))

    //:2 Replace: input
    body = []
    curr = $r.find('h3').next()
    while (curr[0] && curr[0].tagName !== 'H3') {
      body.push(curr[0].outerHTML)
      curr = curr.next()
    }
    $('.input-specification').html(`
      <div class="section-title">Оролт</div>
      ${body.join('\n')}
    `)

    //:2 Replace: output
    body = []
    curr = $r.find('h3:eq(1)').next()
    while (curr[0] && curr[0].tagName !== 'H3') {
      body.push(curr[0].outerHTML)
      curr = curr.next()
    }
    $('.output-specification').html(`
      <div class="section-title">Гаралт</div>
      ${body.join('\n')}
    `)

    //:2 Replace: sample test(s)
    $('.sample-tests .section-title').html('Жишээ тэстүүд')
    $('.sample-tests .sample-test .input .title').html('Оролт')
    $('.sample-tests .sample-test .output .title').html('Гаралт')

    //:2 Replace: note
    if ($r.find('h3:eq(2)').length) {
      body = []
      curr = $r.find('h3:eq(2)').next()
      while (curr[0] && curr[0].tagName !== 'H3') {
        body.push(curr[0].outerHTML)
        curr = curr.next()
      }
      $('.problem-statement .note').html(`
        <div class="section-title">Тэмдэглэл</div>
        ${body.join('\n')}
      `)
    }
    // endfold2

    $('.mn-please').fadeOut('fast')

    // render MathJax
    let elm = document.createElement('script')
    elm.innerHTML = 'MathJax.Hub.Queue(["Typeset", MathJax.Hub])'
    document.head.appendChild(elm)
  })
}
