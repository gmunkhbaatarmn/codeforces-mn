import os


def similar():#1
    """
    Examples
        "380-A" => "381-C" (381-C not listed in problemset)

    Returns {..., "380-A": "381-C", ...}
    """
    # {contest_id: name}
    problems = set(open("problem-set.txt").read().decode("utf-8").strip().split("\n"))

    # problems not listed in problemset
    find_link = []
    for line in open("problem-contest.txt").read().decode("utf-8").strip().split("\n"):
        if not line in problems:
            find_link.append(line)

    # {contest_id name: code}
    problem_hash = {l[:3] + l[5:]: l[:5] for l in open("problem-set.txt").read().decode("utf-8").strip().split("\n")}

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
    "Rating:contribution => Dict of {name: points}"
    value = {}
    for path in os.listdir("Translation/"):
        line = open("Translation/%s" % path).read().decode("utf-8").strip().split("\n")[-1]
        assert line.startswith("-- "), 'Credit line must be start with: "-- "'

        for name in line[3:].split(", "):
            value[name] = value.get(name, 0) + 1.0 / len(line[3:].split(", "))
    open("migrate.py", "w+").write("CONTRIBUTION = %s\n" % sorted(value.items(), key=lambda x: -x[1]))

    "All:problem => list of [english name, mongolian name, credits]"
    value = {}
    # fill english name
    for line in open("problem-set.txt").read().decode("utf-8").strip().split("\n"):
        value[line[:5]] = [line[6:], "", ""]
    # fill mongolian name, credits
    for path in os.listdir("Translation/"):
        data = open("Translation/%s" % path).read().decode("utf-8").strip()
        code = path[:-3]
        name = data.split("\n")[0]
        cred = data.split("\n")[-1][3:]
        value[code][1] = name
        value[code][2] = cred
    ALL_PROBLEM = value
    open("migrate.py", "a+").write("ALL_PROBLEM = %s\n" % sorted(value.items()))

    "All:similar"
    SIMILAR = similar()
    open("migrate.py", "a+").write("ALL_SIMILAR = %s\n" % SIMILAR)

    "All:contest => list of [contest name, done, full]"
    value = {}
    # fill contest name
    for line in open("contest-names.txt").read().decode("utf-8").strip().split("\n"):
        value[line[:3]] = [line[4:], 0, 0]
    # fill full
    for line in open("problem-contest.txt").read().decode("utf-8").strip().split("\n"):
        value[line[:3]][2] += 1
    # fill done
    for line in open("problem-contest.txt").read().decode("utf-8").strip().split("\n"):
        code = SIMILAR.get(line[:5]) or line[:5]
        value[line[:3]][1] += code in ALL_PROBLEM
    open("migrate.py", "a+").write("ALL_CONTEST = %s\n" % sorted(value.items()))


if __name__ == "__main__":#1
    main()
