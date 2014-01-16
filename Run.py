import os


def main():
    """
    Result: links
    """
    problem = {}
    for line in open("data-problems.txt").read().strip().split("\n"):
        hash = "%s-%s" % (line[:3], line[8:])
        code = "%s-%s" % (line[:3], line[4])
        problem[hash] = [code]

    for line in open("data-contests.txt").read().strip().split("\n"):
        hash = "%s-%s" % (line[:3], line[8:])
        code = "%s-%s" % (line[:3], line[4])

        for i in range(1, 11):
            if not hash in problem:
                hash = "%03d-%s" % (int(line[:3]) + i, line[8:])
            if not hash in problem:
                hash = "%03d-%s" % (int(line[:3]) - i, line[8:])

        if not problem.get(hash):
            print "Warning: %s" % hash

        if not code in problem.get(hash):
            problem[hash].append(code)

    links = {}
    count = 0
    for key, value in problem.items():
        if len(value) == 2:
            links[value[0]] = value[1]
            links[value[1]] = value[0]
            count += 1

        if len(value) >= 3:
            print "Warning: %s" % key
    print "count: %s" % count

    """
    Result: problem
    """
    problem = []

    for path in os.listdir("Translation/"):
        code = path.replace(".md", "")

        data = open("Translation/%s" % path).read()
        name = data.split("\n")[0]
        cred = data.strip().split("\n")[-1].replace("-- ", "")

        problem.append([code, [name, cred]])

    # orchuulagdsan bodloguud
    problem = dict(problem)

    for p in problem.copy():
        if p in links:
            problem[links[p]] = problem[p]

    # contest names
    contest_name = {}
    for line in open("contests.txt").read().strip().split("\n"):
        contest_name[line[:3]] = line[4:]

    data = {}
    for line in open("data-contests.txt").read().strip().split("\n"):
        code = line[:3]

        if not code in data:
            data[code] = [0, 1, contest_name[code[:3]]] # [ready, total]
        else:
            data[code][1] += 1  # increment total

    for code in problem:
        data[code[:3]][0] += 1 # increment ready
    open("out.txt", "w+").write("%s" % sorted(data.items()))


if __name__ == "__main__":
    main()
