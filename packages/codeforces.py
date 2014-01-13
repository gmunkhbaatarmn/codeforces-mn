import markdown2


def markdown2html(markdown_source):#1
    html = markdown2.markdown(markdown_source, extras=["code-friendly"])
    html = html.replace("\n\n<p", "\n<p")
    html = html.replace("\n\n<h3", "\n<h3")
    html = html.replace("<p>-- ", '<p class="credit">')
    return html
# endfold


if __name__ == "__main__":
    print markdown2html(open("../test.md").read())
