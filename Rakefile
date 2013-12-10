task :default do
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

  open(".temp.md", "w+") {|f| f.write(data) }
end
