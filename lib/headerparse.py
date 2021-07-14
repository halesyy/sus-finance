def fromFile(fileName="header.string.txt", printHeader=False):
    input = str(open(fileName, "r+").read()).strip().split("\n")

    headers = {}

    for line in input:
        pieces = line.split(": ")
        if len(pieces) == 2:
            headers[pieces[0]] = pieces[1]

    if printHeader: print(headers)
    return headers
