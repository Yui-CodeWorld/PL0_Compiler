keywords = [
    "program",
    "const",
    "var",
    "procedure",
    "begin",
    "end",
    "if",
    "then",
    "else",
    "while",
    "do",
    "call",
    "read",
    "write",
    "odd"
]
aop = ["+", "-"]
mop = ["*", "/"]
lop = ["<", "<=", ">", ">=", "=", "<>"]

col = 0
raw = 1


class struct:
    def __init__(self, type, value, row, column):
        self.type = type
        self.value = value
        self.row = row
        self.column = column

def init_l_d():
    l = []
    d = []
    for i in range(10):
        d.append(str(i))

    for i in range(97, 123):
        l.append(chr(i))

    for i in range(65, 91):
        l.append(chr(i))
    return l, d


l, d = init_l_d()


def isBC(ch):
    if ch == " " or ch == "\n":
        return True
    return False


def isLetter(ch):
    if ch in l:
        return True
    return False


def isDigit(ch):
    if ch in d:
        return True
    return False


def isKeyword(s):
    if s in keywords:
        return True
    return False


def isAop(ch):
    if ch in aop:
        return True
    return False


def isMop(ch):
    if ch in mop:
        return True
    return False


def isLop(ch):
    if ch in lop:
        return True
    return False


def isEof(ch):
    if ch == "":
        return True
    return False


flag = 0


def lexical():
    temp=[]
    fi = open("input.txt", "r")
    fo = open("output.txt", "w")

    global col, raw

    strtoken = ""
    ch = ""

    while True:
        ch = fi.read(1)
        col += 1

        if isEof(ch):
            fo.write("<EOF, EOF, {}, {}>\n".format(raw, col))
            break

        if isBC(ch):
            if ch == "\n":
                raw += 1
                col = 0
            continue

        if isLetter(ch):
            strtoken = ""
            while isLetter(ch) or isDigit(ch):
                strtoken += ch
                ch = fi.read(1)
                col += 1
            if not isEof(ch):
                fi.seek(fi.tell() - 1)
                col -= 1

            if isKeyword(strtoken):
                fo.write(
                    "<KEYWORD, {}, {}, {}>\n".format(
                        strtoken, raw, col - len(strtoken) + 1
                    )
                )
            else:
                fo.write(
                    "<ID, {}, {}, {}>\n".format(strtoken, raw, col - len(strtoken) + 1)
                )

        elif isDigit(ch):
            strtoken = ""
            while isDigit(ch) or isLetter(ch):
                strtoken += ch
                ch = fi.read(1)
                col += 1
            fi.seek(fi.tell() - 1)
            col -= 1

            for c in strtoken:
                if isLetter(c):
                    t1=struct("ERROR", "Invalid integer '{}' at {}, {}".format(strtoken, raw, col - len(strtoken) + 1), raw, col - len(strtoken) + 1)
                    temp.append(t1)
                    break
            else:
                fo.write(
                    "<INTEGER, {}, {}, {}>\n".format(
                        strtoken, raw, col - len(strtoken) + 1
                    )
                )

        elif isAop(ch):
            fo.write("<AOP, {}, {}, {}>\n".format(ch, raw, col))

        elif isMop(ch):
            fo.write("<MOP, {}, {}, {}>\n".format(ch, raw, col))

        elif isLop(ch):
            strtoken = ch
            ch_next = fi.read(1)
            col += 1
            if (strtoken + ch_next) in lop:
                strtoken += ch_next
            else:
                fi.seek(fi.tell() - 1)
                col -= 1
            fo.write(
                "<LOP, {}, {}, {}>\n".format(strtoken, raw, col - len(strtoken) + 1)
            )

        elif ch == ":":
            ch_next = fi.read(1)
            col += 1
            if ch_next == "=":
                fo.write("<ASSIGN, :=, {}, {}>\n".format(raw, col - 1))
            else:
                fi.seek(fi.tell() - 1)
                col -= 1
                t1=struct("ERROR", "Invalid character ':' at {}, {}".format(raw, col), raw, col)
                temp.append(t1)

        elif ch == ";":
            fo.write("<SEMICOLON, ;, {}, {}>\n".format(raw, col))

        elif ch == ",":
            fo.write("<COMMA, ,, {}, {}>\n".format(raw, col))

        elif ch == "(":
            fo.write("<LPAREN, (, {}, {}>\n".format(raw, col))
            flag = 1

        elif ch == ")":
            if flag == 1:
                fo.write("<RPAREN, ), {}, {}>\n".format(raw, col))
                flag = 0
            else:
                t1=struct("ERROR", "Unmatched ')' at {}, {}".format(raw, col), raw, col)
                temp.append(t1)

        else:
            t1=struct("ERROR", "Invalid character '{}' at {}, {}".format(ch, raw, col), raw, col)
            temp.append(t1)
    fi.close()

    for item in temp:
        fo.write("<{}, {}, {}, {}>\n".format(item.type, item.value, item.row, item.column))         

    fo.close()
    if len(temp) == 0:
        print("词法分析通过")
        return True
    else:
        print("词法分析失败")
        return False


if __name__ == "__main__":
    lexical()
