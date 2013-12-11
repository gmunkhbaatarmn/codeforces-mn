console.log("Hello2. This message was sent from main.js")


chrome.extension.sendMessage {}, (response) ->
	readyStateCheckInterval = setInterval ->
    if document.readyState is "complete"
      clearInterval(readyStateCheckInterval)

      $("td.act").append """
        <span class="act-item" style="position: relative; bottom: 2px;">
          <span><img class="toggle-favourite add-favourite" title="Add to favourites" alt="Add to favourites" data-type="PROBLEM" data-entityid="3562" data-size="16" src="http://worker.codeforces.ru/static/images/icons/star_gray_16.png"></span>
        </span>
      """

      console.log "Hello. This message was sent from main.js"
  , 10
