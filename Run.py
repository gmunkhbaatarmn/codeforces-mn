import os


def contest_names():#1
    """
    Examples
        "001": "Codeforces Round #1"
        "123": "Codeforces Round #123"

    Returns dict of {code: name}
    """
    values = {}
    for line in open("contest-names.txt").read().strip().split("\n"):
        code = line[:3]
        name = line[4:]
        values[code] = name
    return values


def problem_links():#1
    """
    Examples
        "380-A" => "381-C" (381-C not listed in problemset)

    Returns {..., "380-A": "381-C", ...}
    """
    # {contest_id: name}
    problems = set(open("problem-set.txt").read().strip().split("\n"))

    # problems not listed in problemset
    find_link = []
    for line in open("problem-contest.txt").read().strip().split("\n"):
        if not line in problems:
            find_link.append(line)

    # {contest_id name: code}
    problem_hash = {l[:3] + l[5:]: l[:5] for l in open("problem-set.txt").read().strip().split("\n")}
    # print problem_hash

    values = {}
    for line in find_link:
        code = line[:5]
        link = None

        for i in range(1, 11):
            link = link or problem_hash.get("%03d %s" % (int(line[:3]) + i, line[6:]))
            link = link or problem_hash.get("%03d %s" % (int(line[:3]) - i, line[6:]))

        if not link:
            print "Warning link not found for: %s" % code
        values[link] = code

    return values


def main():#1
    # ("Rating:contribution")
    value = {}
    for path in os.listdir("Translation/"):
        line = open("Translation/%s" % path).read().strip().split("\n")[-1]
        assert line.startswith("-- "), 'Credit line must be start with: "-- "'

        for name in line[3:].split(", "):
            value[name] = value.get(name, 0) + 1.0 / len(line[3:].split(", "))
    open("migrate.py", "w+").write("CONTRIBUTION = %s\n" % sorted(value.items(), key=lambda x: -x[1]))

    # ("Total:problems")
    value = {}
    for line in open("problem-set.txt").read().strip().split("\n"):
        code = line[:5]
        name = line[6:]
        value[code] = name
    open("migrate.py", "a+").write("TOTAL_PROBLEMS = %s\n" % sorted(value.items()))

    # ("Total:contests")
    value = {}
    for line in open("problem-contest.txt").read().strip().split("\n"):
        code = line[:5]
        name = line[6:]
        value[code] = name
    open("migrate.py", "a+").write("TOTAL_CONTESTS = %s\n" % sorted(value.items()))

    # ("Ready:problems")
    value = {}
    for path in os.listdir("Translation/"):
        code = path[:-3]
        name = open("Translation/%s" % path).read().strip().split("\n")[0]
        cred = open("Translation/%s" % path).read().strip().split("\n")[-1][3:]
        value[code] = [name, cred]
    open("migrate.py", "a+").write("READY_PROBLEMS = %s\n" % sorted(value.items()))

    # ("Ready:contests")
    CONTEST_NAMES = contest_names()
    PROBLEM_LINKS = problem_links()
    value = {}
    for code, name in CONTEST_NAMES.items():
        ready, total = 0, 0
        value[code] = [ready, total, name]

    for line in open("problem-contest.txt").read().strip().split("\n"):
        value[line[:3]][1] += 1

    for path in os.listdir("Translation/"):
        value[path[:3]][0] += 1
        if PROBLEM_LINKS.get(path[:5]):
            value[PROBLEM_LINKS[path[:5]][:3]][0] += 1
    # print sorted(value.items())
    open("migrate.py", "a+").write("READY_CONTESTS = %s\n" % sorted(value.items()))


if __name__ == "__main__":#1
    main()
