task :default do
  links = problem_link

  # Compile each file to HTML
  Dir["*-*.md"].each do |input|
    code = input[0..-4]

    fix input
    `pandoc .temp.md -o out/#{code}.html`

    if links[code]
      `cp out/#{code}.html out/#{links[code]}.html`
    end
  end

  data = []
  Dir["out/*-*.html"].each do |input|
    data << "#{input[4..-6].split("-")[0].to_i}-#{input[4..-6].split("-")[1]}"
  end
  open("out/000-data.txt", "w+") { |f| f.write(data.join("|")) }

  # Remove temp file
  `[ -f ".temp.md" ] && rm .temp.md`

  data = contest_data
  Dir["out/*-*.html"].each do |input|
    print input, " ", data[input[4..6]], "\n"
    data[input[4..6]][0] += 1
  end

  # Contest translation status
  open("out/000-data.txt", "a+") do |f|
    formatted = data.find_all{|c| c[1][0] > 0}.map{|c| "%s:%s/%s" % [c[0], c[1][0], c[1][1]]}
    f.write("\r#{formatted.join("|")}")
    f.write("\r" + TRANSLATOR_POINT.sort_by {|k,v| v}.reverse.map{|t| "%s:%s" % [t[0], t[1]]}.join("|"))
    f.write("\r1654") #Total problems
  end

  `git add out`
  `git commit -m '[auto] problems compiled'`

  puts "Done!"
  print TRANSLATOR_POINT
end


task :pdf do#:1
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

  puts TRANSLATOR_POINT
  print "Done!\n"
end#endfold


TRANSLATOR_POINT = {}


#:1 Prepare markdown file compile to PDF
def fix(input)
  data = open(input, "r").read
  data.gsub! "≤", "\\leq"
  data.gsub! "×", "\\times"
  data.gsub! "≠", "\\neq"

  translators = data.split("\n")[-1].strip()[3..-1].split(", ")
  translators.each do |t|
    TRANSLATOR_POINT[t] = (TRANSLATOR_POINT[t] or 0.0) + 1.0 / translators.length
  end

  data = data.split("\n")[0..-2].join("\n")
  data += "\n<p class=\"math\" style=\"text-align:right;font-style:italic\">Орчуулсан: #{translators.join(", ")}</p>"
  print "Converting to HTML: #{input} Translated by: #{translators.join(", ")}\n"

  open(".temp.md", "w+") { |f| f.write(data) }
end


#:1 Problem link
def problem_link
  problem = {}
  for line in open("data-problems.txt").read().split("\n")
    hash = line[0..2] +" - "+ line[8..-1]
    problem[hash] = [line[0..2] + "-" + line[4]]
  end

  for line in open("data-contest.txt").read().split("\n")
    code = line[0..2] + "-" + line[4]
    hash = line[0..2] +" - "+ line[8..-1]

    1.upto(10) do |i|
      hash = ("%03d" % (line[0..2].to_i + i)).to_s + " - " + line[8..-1] unless problem[hash]
      hash = ("%03d" % (line[0..2].to_i - i)).to_s + " - " + line[8..-1] unless problem[hash]
    end

    unless problem[hash].include?(code)
      problem[hash] <<= code
    end
  end

  links = {}

  problem.each do |key, value|
    if value.length >= 2
      links[value[0]] = value[1]
      links[value[1]] = value[2]
    end
  end

  links
end


def contest_data
  data = {}

  for line in open("data-contest.txt").read().split("\n")
    code = line[0..2]
    unless data[code]
      data[code] = [0, 1] # [ready, total]
    else
      data[code][1] += 1
    end
  end

  data
end
