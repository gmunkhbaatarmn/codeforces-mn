// todo: remove files: `main.js`, `main.js.coffee`
// todo: rename file: `main2.js` to `main.js`
// todo: update: `main2.js` to `mani.js` on `manifest.json`
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

//: Page: /problemset/problem   Read a problem (empty)
// endfold

//: Function: translate problem statement

