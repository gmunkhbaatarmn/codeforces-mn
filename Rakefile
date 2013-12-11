task :default do
  data = []
  Dir["*-*.md"].each do |input|
    data << "#{input[0..-4].split("-")[0].to_i}-#{input[0..-4].split("-")[1]}"
  end
  open("out/data.txt", "w+") { |f| f.write(data.join("|")) }

  # Compile each file to HTML
  Dir["*-*.md"].each do |input|
    fix input
    print "Converting to HTML: #{input}\n"
    `pandoc .temp.md -o out/#{input[0..-4]}.html`
  end

  # Remove temp file
  `[ -f ".temp.md" ] && rm .temp.md`

  `git add out`
  `git commit -m '[auto] problems compiled'`
  print "Done!\n"
end

task :pdf do
  # Compile each file
  Dir["*-*.md"].each do |input|
    fix input
    print "Processing: #{input}\n"
    `pandoc .temp.md -o #{input[0..-4]}.pdf --latex-engine=xelatex \
      -V mainfont="Arial" \
      -V monofont="Monaco" \
      -V geometry="top=11mm,bottom=11mm,left=11mm,right=11mm,paperwidth=148mm,paperheight=210mm" \
      -V documentclass="article"`
  end

  # Remove temp file
  `[ -f ".temp.md" ] && rm .temp.md`

  print "Done!\n"
end


# Prepare markdown file compile to PDF
def fix(input)
  data = open(input, "r").read
  data.gsub! "≤", "\\leq"
  data.gsub! "×", "\\times"
  data.gsub! "≠", "\\neq"

  open(".temp.md", "w+") { |f| f.write(data) }
end
