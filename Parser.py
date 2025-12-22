class Token:
    def __init__(self, token_type, value, line, col):
        self.type = token_type
        self.value = value
        self.line = int(line)
        self.col = int(col)


def parse_token_string(token_str):
    clean_str = token_str.strip().strip("<").strip(">")
    parts = [p.strip() for p in clean_str.split(",")]
    if parts[0] == "COMMA":
        parts[1] = ","
        parts = [parts[0], parts[1], parts[3], parts[4]]
    return Token(token_type=parts[0], value=parts[1], line=parts[2], col=parts[3])


def load_tokens():
    tokens = []
    while next_token_flag():
        tokens.append(next_token_def())
    return tokens


def next_token_flag():
    fp = fi.tell()
    strline = fi.readline()
    if not strline:
        return None
    fi.seek(fp)
    return True


def next_token_def():
    strline = fi.readline()
    if not strline:
        return None
    return parse_token_string(strline)


def next_token():
    global current_token_index
    if current_token_index < len(tokens):
        token = tokens[current_token_index]
        current_token_index += 1
        return token
    else:
        return None


follow_set = {
    "prog": {"EOF"},
    "block": {"end", ";", "EOF", "."},
    "condecl": {"var", "procedure", "begin"},
    "const_def": {",", ";"},
    "vardecl": {"procedure", "begin"},
    "proc": {"begin", ";", "EOF"},
    "body": {"end", ";", "else", "EOF"},
    "statement": {"end", ";", "else"},
    "lexp": {"then", "do"},
    "exp": {
        "<",
        "<=",
        ">",
        ">=",
        "=",
        "<>",
        ")",
        ",",
        ";",
        "then",
        "do",
        "else",
        "end",
    },
    "term": {
        "+",
        "-",
        "<",
        "<=",
        ">",
        ">=",
        "=",
        "<>",
        ")",
        ",",
        ";",
        "then",
        "do",
        "else",
        "end",
    },
    "factor": {
        "*",
        "/",
        "+",
        "-",
        "<",
        "<=",
        ">",
        ">=",
        "=",
        "<>",
        ")",
        ",",
        ";",
        "then",
        "do",
        "else",
        "end",
    },
}


# <prog> → program <id>；<block>
def prog():
    token = next_token()
    if token.value != "program":
        print("{}行，{}列:期望一个 program".format(token.line, token.col))

    token = next_token()
    if token.type != "ID":
        print("{}行，{}列:期望一个 id".format(token.line, token.col))
    token = next_token()
    if token.type != "SEMICOLON":
        print("{}行，{}列:期望一个 ;".format(token.line, token.col))

    if block():
        return True

    return False


# <block> → [<condecl>][<vardecl>][<proc>]<body>
def block():
    token = next_token()

    if token.value == "const":
        condecl(token)
        token = next_token()

    if token.value == "var":
        vardecl(token)
        token = next_token()

    if token.value == "procedure":
        proc(token)
        token = next_token()

    if token.value == "begin":
        if body(token):
            return True
    else:
        print("{}行，{}列:期望一个 begin".format(token.line, token.col))

    return False


# <condecl> → const <const>{,<const>};
def condecl(token):
    # if token.value != "const":
    #     print("{}行，{}列:期望一个 const").format(token.line, token.col)
    global current_token_index
    token = next_token()

    if token.type == "ID":
        const(token)
        token = next_token()
        while token.type == "COMMA":
            token = next_token()
            if token.type == "ID":
                const(token)
                token = next_token()
            else:
                print("{}行，{}列:期望一个 id".format(token.line, token.col))
        if token.type != "SEMICOLON":
            print("{}行，{}列:期望一个 ;".format(token.line, token.col))
        else:
            return True
    else:
        print("{}行，{}列:期望一个 id".format(token.line, token.col))

    while token.value not in follow_set["condecl"]:
        token = next_token()

    current_token_index -= 1
    return False


# <const> → <id>:=<integer>
def const(token):
    global current_token_index
    if token.type == "ID":
        token = next_token()
        if token.type == "ASSIGN":
            token = next_token()
            if token.type == "INTEGER":
                return True
            else:
                print("{}行，{}列:期望一个 integer".format(token.line, token.col))
        else:
            print("{}行，{}列:期望一个 :=".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 id".format(token.line, token.col))

    while token.value not in follow_set["const_def"]:
        token = next_token()

    current_token_index -= 1
    return False


# <vardecl> → var <id>{,<id>};
def vardecl(token):
    global current_token_index
    if token.type == "KEYWORD" and token.value == "var":
        token = next_token()
        if token.type == "ID":
            token = next_token()
            while token.type == "COMMA":
                token = next_token()
                if token.type == "ID":
                    token = next_token()
                else:
                    print("{}行，{}列:期望一个 id".format(token.line, token.col))
            if token.type != "SEMICOLON":
                print("{}行，{}列:期望一个 ;".format(token.line, token.col))
            else:
                return True
        else:
            print("{}行，{}列:期望一个 id".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 var".format(token.line, token.col))

    while token.value not in follow_set["vardecl"]:
        token = next_token()
    current_token_index -= 1
    return False


# <proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}
def proc(token):
    global current_token_index
    if token.type == "KEYWORD" and token.value == "procedure":
        token = next_token()
        if token.type == "ID":
            token = next_token()
            if token.type == "LPAREN" and token.value == "(":
                token = next_token()
                if token.type == "ID":
                    token = next_token()
                    while token.type == "COMMA":
                        token = next_token()
                        if token.type == "ID":
                            token = next_token()
                        else:
                            print(
                                "{}行，{}列:期望一个 id".format(token.line, token.col)
                            )
                    if token.type == "RPAREN" and token.value == ")":
                        token = next_token()
                        if token.type == "SEMICOLON":
                            if block():
                                token = next_token()
                                while token.type == "SEMICOLON":
                                    token = next_token()
                                    if (
                                        token.type == "KEYWORD"
                                        and token.value == "procedure"
                                    ):
                                        proc()
                                    else:
                                        print(
                                            "{}行，{}列:期望一个 procedure".format(
                                                token.line, token.col
                                            )
                                        )
                                current_token_index -= 1
                                return True
                        else:
                            print("{}行，{}列:期望一个 ;".format(token.line, token.col))
                    else:
                        print("{}行，{}列:期望一个 )".format(token.line, token.col))
                else:
                    print("{}行，{}列:期望一个 id".format(token.line, token.col))
            else:
                print("{}行，{}列:期望一个 (".format(token.line, token.col))
        else:
            print("{}行，{}列:期望一个 id".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 procedure".format(token.line, token.col))

    while token.value not in follow_set["proc"]:
        token = next_token()

    current_token_index -= 1
    return False


# <body> → begin <statement>{;<statement>}end
def body(token):
    global current_token_index
    if token.type == "KEYWORD" and token.value == "begin":
        if statement():
            token = next_token()
            while token.type == "SEMICOLON":
                if statement():
                    token = next_token()
                else:
                    print("<body>:; <statement> error")
                    return False
            if token.value != "end":
                print("{}行，{}列:期望一个 end".format(token.line, token.col))
            else:
                return True
    else:
        print("{}行，{}列:期望一个 begin".format(token.line, token.col))

    while token.value not in follow_set["body"]:
        token = next_token()

    current_token_index -= 1
    return False


def statement():
    token = next_token()
    if token.value == "if":
        if condition(token):
            return True

    if token.value == "while":
        if cycle(token):
            return True

    if token.value == "call":
        if call(token):
            return True

    if token.value == "read":
        if read(token):
            return True

    if token.value == "write":
        if write(token):
            return True

    if token.type == "ID":
        if assignment(token):
            return True
    
    if token.value == "begin":
        if body(token):
            return True

    return False


# <id> := <exp>
def assignment(token):
    global current_token_index
    if token.type == "ID":
        token = next_token()
        if token.type == "ASSIGN":
            if exp():
                return True
        else:
            print("{}行，{}列:期望一个 :=".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 id".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# <exp> → [+|-]<term>{<aop><term>}
def exp():
    global current_token_index
    token = next_token()
    if token.type == "AOP":
        if term():
            token = next_token()
            flag = 1
            while token.type == "AOP":
                if term():
                    token = next_token()
                else:
                    flag = 0
            if flag:
                current_token_index -= 1
                return True
    else:
        current_token_index -= 1
        if term():
            token = next_token()
            flag = 1
            while token.type == "AOP":
                if term():
                    token = next_token()
                else:
                    flag = 0
            if flag:
                current_token_index -= 1
                return True

    while token.value not in follow_set["exp"]:
        token = next_token()

    current_token_index -= 1
    return False


# <term> → <factor>{<mop><factor>}
def term():
    global current_token_index
    flag1 = 0
    if factor():
        flag1 = 1
        flag = 1
        token = next_token()
        while token.type == "MOP":
            if factor():
                token = next_token()
            else:
                flag = 0
        if flag:
            current_token_index -= 1
            return True

    if flag1:
        while token.value not in follow_set["term"]:
            token = next_token()
        current_token_index -= 1

    return False


# <factor>→<id>|<integer>|(<exp>)
def factor():
    global current_token_index
    token = next_token()
    if token.type == "ID" or token.type == "INTEGER":
        return True
    elif token.type == "LPAREN" and token.value == "(":
        if exp():
            token = next_token()
            if token.type == "RPAREN" and token.value == ")":
                return True
            else:
                print("{}行，{}列:期望一个 )".format(token.line, token.col))

    while token.value not in follow_set["factor"]:
        token = next_token()

    current_token_index -= 1
    return False


# if <lexp> then <statement>[else <statement>]
def condition(token):
    global current_token_index
    if token.type == "KEYWORD" and token.value == "if":
        if lexp():
            token = next_token()
            if token.type == "KEYWORD" and token.value == "then":
                if statement():
                    token = next_token()
                    if token.type == "KEYWORD" and token.value == "else":
                        if statement():
                            return True
                    else:
                        current_token_index -= 1
                        return True
            else:
                print("{}行，{}列:期望一个 then".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 if".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# <lexp> → <exp> <lop> <exp>|odd <exp>
def lexp():
    global current_token_index
    token = next_token()
    if token.type == "KEYWORD" and token.value == "odd":
        if exp():
            return True

    current_token_index -= 1
    flag = 0
    if exp():
        flag = 1
        token = next_token()
        if token.type == "LOP":
            if exp():
                return True

    if flag:
        while token.value not in follow_set["lexp"]:
            token = next_token()

        current_token_index -= 1
    return False


# while <lexp> do <statement>
def cycle(token):
    global current_token_index
    if token.type == "KEYWORD" and token.value == "while":
        if lexp():
            token = next_token()
            if token.type == "KEYWORD" and token.value == "do":
                if statement():
                    return True
            else:
                print("{}行，{}列:期望一个 do".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 while".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# call <id>（[<exp>{,<exp>}]）
def call(token):
    global current_token_index
    if token.type == "KEYWORD" and token.value == "call":
        token = next_token()
        if token.type == "ID":
            token = next_token()
            if token.type == "LPAREN" and token.value == "(":
                if exp():
                    flag = 1
                    token = next_token()
                    while token.type == "COMMA":
                        if exp():
                            token = next_token()
                        else:
                            flag = 0
                    if flag:
                        if token.type == "RPAREN" and token.value == ")":
                            return True
                        else:
                            current_token_index -= 1
                            print("{}行，{}列:期望一个 )".format(token.line, token.col))
                else:
                    token = next_token()
                    if token.type == "RPAREN" and token.value == ")":
                        return True
                    else:
                        current_token_index -= 1
                        print("{}行，{}列:期望一个 )".format(token.line, token.col))

            else:
                print("{}行，{}列:期望一个 (".format(token.line, token.col))
        else:
            print("{}行，{}列:期望一个 id".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 call".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# read (<id>{，<id>})
def read(token):
    global current_token_index
    if token.type == "KEYWORD" and token.value == "read":
        token = next_token()
        if token.type == "LPAREN" and token.value == "(":
            token = next_token()
            if token.type == "ID":
                flag = 1
                token = next_token()
                while token.type == "COMMA":
                    token = next_token()
                    if token.type == "ID":
                        token = next_token()
                    else:
                        flag = 0
                        print("{}行，{}列:期望一个 id".format(token.line, token.col))
                if flag:
                    if token.type == "RPAREN" and token.value == ")":
                        return True
                    else:
                        current_token_index -= 1
                        print("{}行，{}列:期望一个 )".format(token.line, token.col))
            else:
                print("{}行，{}列:期望一个 id".format(token.line, token.col))
        else:
            print("{}行，{}列:期望一个 (".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 read".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# write (<exp>{,<exp>})
def write(token):
    global current_token_index
    if token.type == "KEYWORD" and token.value == "write":
        token = next_token()
        if token.type == "LPAREN" and token.value == "(":
            if exp():
                flag = 1
                token = next_token()
                while token.type == "COMMA":
                    if exp():
                        token = next_token()
                    else:
                        flag = 0
                if flag:
                    if token.type == "RPAREN" and token.value == ")":
                        return True
                    else:
                        current_token_index -= 1
                        print("{}行，{}列:期望一个 )".format(token.line, token.col))
        else:
            print("{}行，{}列:期望一个 (".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 write".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


def parse():
    if prog():
        print("语法分析通过")
    else:
        print("语法分析失败")

from LA import lexical
if __name__ == "__main__":
    flag=lexical()
    if not flag:
        exit(0)
    current_token_index = 0
    fi = open("output.txt", "r")
    tokens = load_tokens()
    fi.close()
    parse()
