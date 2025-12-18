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


# <prog> → program <id>；<block>
def prog():
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "program":
        strline = fi.readline()
        token2 = parse_token_string(strline)
        if token2.type == "ID":
            fp2 = fi.tell()
            strline = fi.readline()
            token3 = parse_token_string(strline)
            if token3.type == "SEMICOLON":
                if block():
                    return True
                else:
                    print("<prog>:<block> error")
            else:
                fi.seek(fp2)
                print("raw{},col{}:Expected SEMICOLON").format(token3.line, token3.col)
                return True
        else:
            print("<prog>:<id> error").format(token2.line, token2.col)
    # else:
    #     print("<prog>:no program").format(token.line, token.col)

    fi.seek(fp)
    print("<prog>:error")
    return False


# <block> → [<condecl>][<vardecl>][<proc>]<body>
def block():
    fp = fi.tell()
    if condecl():
        if vardecl():
            if proc():
                if body():
                    return True
                else:
                    print("<block>:<body> error")
            elif body():
                return True
            else:
                print("<block>:<proc>/<body> error")
        elif body():
            return True
        else:
            print("<block>:<vardecl>/<body> error")
    elif body():
        return True
    else:
        print("<block>:<condecl>/<body> error")

    fi.seek(fp)
    print("<block>:error")
    return False


# <condecl> → const <const>{,<const>};
def condecl():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "const":
        flag=1
        if const():
            fp2 = fi.tell()
            strline = fi.readline()
            token2 = parse_token_string(strline)
            while token2.type == "COMMA":
                if const():
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token2 = parse_token_string(strline)
                else:
                    print("<condecl>:, <const> error")
                    return False
            if token2.type == "SEMICOLON":
                return True
            else:
                fi.seek(fp2)
                print("raw{},col{}:Expected SEMICOLON").fomat(token2.line, token2.col)
                return True
        else:
            print("<condecl>:<const> error")
    # else:
    #     print("<condecl>:no const")

    fi.seek(fp)
    if flag:
        print("<condecl>:error")
    return False


# <const> → <id>:=<integer>
def const():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "ID":
        flag=1
        strline = fi.readline()
        token2 = parse_token_string(strline)
        if token2.type == "ASSIGN":
            strline = fi.readline()
            token3 = parse_token_string(strline)
            if token3.type == "INTEGER":
                return True
            else:
                print("<const>:<integer> error")
        else:
            print("<const>:no :=")
    # else:
    #     print("<const>:<id> error")

    fi.seek(fp)
    if flag:
        print("<const>:error")
    return False


# <vardecl> → var <id>{,<id>};
def vardecl():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "var":
        flag=1
        strline = fi.readline()
        token2 = parse_token_string(strline)
        if token2.type == "ID":
            fp2 = fi.tell()
            strline = fi.readline()
            token3 = parse_token_string(strline)
            while token3.type == "COMMA":
                strline = fi.readline()
                token4 = parse_token_string(strline)
                if token4.type == "ID":
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token3 = parse_token_string(strline)
                else:
                    print("<vardecl>:, <id> error")
                    return False
            if token3.type == "SEMICOLON":
                return True
            else:
                fi.seek(fp2)
                print("raw{},col{}:Expected SEMICOLON").format(token3.line, token3.col)
                return True
        else:
            print("<vardecl>:<id> error")
    # else:
    #     print("<vardecl>:no var")

    fi.seek(fp)
    if flag:
        print("<vardecl>:error")
    return False


# <proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}
def proc():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "procedure":
        flag=1
        strline = fi.readline()
        token2 = parse_token_string(strline)
        if token2.type == "ID":
            strline = fi.readline()
            token3 = parse_token_string(strline)
            if token3.type == "LPAREN" and token3.value == "(":
                strline = fi.readline()
                token4 = parse_token_string(strline)
                if token4.type == "ID":
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token5 = parse_token_string(strline)
                    while token5.type == "COMMA":
                        strline = fi.readline()
                        token6 = parse_token_string(strline)
                        if token6.type == "ID":
                            fp2 = fi.tell()
                            strline = fi.readline()
                            token5 = parse_token_string(strline)
                        else:
                            print("<proc>:, <id> error")
                            return False
                    if token5.type == "RPAREN" and token5.value == ")":
                        fp3 = fi.tell()
                        strline = fi.readline()
                        token7 = parse_token_string(strline)
                        if token7.type == "SEMICOLON":
                            if block():
                                fp4 = fi.tell()
                                strline = fi.readline()
                                token8 = parse_token_string(strline)
                                while token8.type == "SEMICOLON":
                                    if proc():
                                        fp4 = fi.tell()
                                        strline = fi.readline()
                                        token8 = parse_token_string(strline)
                                    else:
                                        print("<proc>:; <proc> error")
                                        return False
                                fi.seek(fp4)
                                return True
                            else:
                                print("<proc>:<block> error")
                                return False
                        else:
                            fi.seek(fp3)
                            print("raw{},col{}:Expected SEMICOLON").format(
                                token7.line, token7.col
                            )
                            return True
                    else:
                        fi.seek(fp2)
                        print("raw{},col{}:Expected ')'").format(
                            token5.line, token5.col
                        )
                        return True
            else:
                print("<proc>:no (")
        else:
            print("<proc>:<id> error")
    # else:
    #     print("<proc>:no procedure")

    fi.seek(fp)
    if flag:
        print("<proc>:error")
    return False


# <body> → begin <statement>{;<statement>}end
def body():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "begin":
        flag=1
        if statement():
            fp2 = fi.tell()
            strline = fi.readline()
            token2 = parse_token_string(strline)
            while token2.type == "SEMICOLON":
                if statement():
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token2 = parse_token_string(strline)
                else:
                    print("<body>:; <statement> error")
                    return False
            if token2.type == "KEYWORD" and token2.value == "end":
                return True
            else:
                fi.seek(fp2)
                print("raw{},col{}:Expected 'end'").format(token2.line, token2.col)
                return True
        else:
            print("<body>:<statement> error")
    # else:
    #     print("<body>:no begin")

    fi.seek(fp)
    if flag:
        print("<body>:error")
    return False


def statement():
    fp = fi.tell()
    if assignment():
        return True
    elif condition():
        return True
    elif cycle():
        return True
    elif call():
        return True
    elif body():
        return True
    elif read():
        return True
    elif write():
        return True

    fi.seek(fp)
    print("<statement>:error")
    return False


# <id> := <exp>
def assignment():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "ID":
        flag=1
        strline = fi.readline()
        token2 = parse_token_string(strline)
        if token2.type == "ASSIGN":
            if exp():
                return True
            else:
                print("<assignment>:<exp> error")
        else:
            print("<assignment>:no :=")
    # else:
    #     print("<assignment>:<id> error")

    fi.seek(fp)
    if flag:
        print("<assignment>:error")
    return False


# <exp> → [+|-]<term>{<aop><term>}
def exp():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "AOP":
        flag=1
        if term():
            fp2 = fi.tell()
            strline = fi.readline()
            token2 = parse_token_string(strline)
            while token2.type == "AOP":
                if term():
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token2 = parse_token_string(strline)
                else:
                    print("<exp>:aop <term> error")
            fi.seek(fp2)
            return True
        else:
            print("<exp>:aop <term> error")
    else:
        flag=1
        fi.seek(fp)
        if term():
            fp2 = fi.tell()
            strline = fi.readline()
            token2 = parse_token_string(strline)
            while token2.type == "AOP":
                if term():
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token2 = parse_token_string(strline)
                else:
                    print("<exp>:aop <term> error")
            fi.seek(fp2)
            return True
        # else:
        #     print("<exp>:<term> error")

    fi.seek(fp)
    if flag:
        print("<exp>:error")
    return False


# <term> → <factor>{<mop><factor>}
def term():
    flag=0
    fp = fi.tell()
    if factor():
        flag=1
        fp2 = fi.tell()
        strline = fi.readline()
        token2 = parse_token_string(strline)
        while token2.type == "MOP":
            if factor():
                fp2 = fi.tell()
                strline = fi.readline()
                token2 = parse_token_string(strline)
            else:
                print("<term>:mop <factor> error")
                return False
        fi.seek(fp2)
        return True
    # else:
    #     print("<term>:<factor> error")

    fi.seek(fp)
    if flag:
        print("<term>:error")
    return False


# <factor>→<id>|<integer>|(<exp>)
def factor():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "ID" or token.type == "INTEGER":
        return True
    elif token.type == "LPAREN" and token.value == "(":
        flag=1
        if exp():
            fp2 = fi.tell()
            strline = fi.readline()
            token2 = parse_token_string(strline)
            if token2.type == "RPAREN" and token2.value == ")":
                return True
            else:
                fi.seek(fp2)
                print("raw{},col{}:Expected ')'").format(token2.line, token2.col)
                return True

    fi.seek(fp)
    if flag:
        print("<factor>:error")
    return False


# if <lexp> then <statement>[else <statement>]
def condition():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "if":
        flag=1
        if lexp():
            strline = fi.readline()
            token2 = parse_token_string(strline)
            if token2.type == "KEYWORD" and token2.value == "then":
                if statement():
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token3 = parse_token_string(strline)
                    if token3.type == "KEYWORD" and token3.value == "else":
                        if statement():
                            return True
                        else:
                            print("<condition>:else <statement> error")
                            return False
                    else:
                        fi.seek(fp2)
                        return True
                else:
                    print("<condition>:<statement> error")
            else:
                print("<condition>:no then")
        else:
            print("<condition>:<lexp> error")
    # else:
    #     print("<condition>:no if")

    fi.seek(fp)
    if flag:
        print("<condition>:error")
    return False


# <lexp> → <exp> <lop> <exp>|odd <exp>
def lexp():
    flag=0
    fp = fi.tell()
    if exp():
        flag=1
        strline = fi.readline()
        token = parse_token_string(strline)
        if token.type == "LOP":
            if exp():
                return True
        else:
            print("<lexp>:<lop> <exp> error")
    else:
        strline = fi.readline()
        token = parse_token_string(strline)
        if token.type == "KEYWORD" and token.value == "odd":
            flag=1
            if exp():
                return True

    fi.seek(fp)
    if flag:
        print("<lexp>:error")
    return False


# while <lexp> do <statement>
def cycle():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "while":
        flag=1
        if lexp():
            strline = fi.readline()
            token2 = parse_token_string(strline)
            if token2.type == "KEYWORD" and token2.value == "do":
                if statement():
                    return True
                else:
                    print("<cycle>:<statement> error")
            else:
                print("<cycle>:no do")
        else:
            print("<cycle>:<lexp> error")
    # else:
    #     print("<cycle>:no while")

    fi.seek(fp)
    if flag:
        print("<cycle>:error")
    return False


# call <id>（[<exp>{,<exp>}]）
def call():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "call":
        flag=1
        strline = fi.readline()
        token2 = parse_token_string(strline)
        if token2.type == "ID":
            strline = fi.readline()
            token3 = parse_token_string(strline)
            if token3.type == "LPAREN" and token3.value == "(":
                if exp():
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token4 = parse_token_string(strline)
                    while token4.type == "COMMA":
                        if exp():
                            fp2 = fi.tell()
                            strline = fi.readline()
                            token4 = parse_token_string(strline)
                        else:
                            print("<call>:, <exp> error")
                            return False
                    if token4.type == "RPAREN" and token4.value == ")":
                        return True
                    else:
                        fi.seek(fp2)
                        print("Expected ')'")
                        return False
                else:
                    fp2 = fi.tell()
                    strline = fi.readline()
                    token4 = parse_token_string(strline)
                    if token4.type == "RPAREN" and token4.value == ")":
                        return True
                    else:
                        fi.seek(fp2)
                        print("raw{},col{}:Expected ')'").format(
                            token4.line, token4.col
                        )
                        return True
            else:
                print("<call>:no (")
        else:
            print("<call>:<id> error")
    # else:
    #     print("<call>:no call")

    fi.seek(fp)
    if flag:
        print("<call>:error")
    return False


# read (<id>{，<id>})
def read():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "read":
        flag=1
        strline = fi.readline()
        token2 = parse_token_string(strline)
        if token2.type == "LPAREN" and token2.value == "(":
            strline = fi.readline()
            token3 = parse_token_string(strline)
            if token3.type == "ID":
                fp2 = fi.tell()
                strline = fi.readline()
                token4 = parse_token_string(strline)
                while token4.type == "COMMA":
                    strline = fi.readline()
                    token5 = parse_token_string(strline)
                    if token5.type == "ID":
                        fp2 = fi.tell()
                        strline = fi.readline()
                        token4 = parse_token_string(strline)
                    else:
                        print("<read>:, <id> error")
                        return False
                if token4.type == "RPAREN" and token4.value == ")":
                    return True
                else:
                    fi.seek(fp2)
                    print("raw{},col{}:Expected ')'").format(token4.line, token4.col)
                    return True
            else:
                print("<read>:<id> error")
        else:
            print("<read>:no (")
    # else:
    #     print("<read>:no read")

    fi.seek(fp)
    if flag:
        print("<read>:error")
    return False


# write (<exp>{,<exp>})
def write():
    flag=0
    fp = fi.tell()
    strline = fi.readline()
    token = parse_token_string(strline)
    if token.type == "KEYWORD" and token.value == "write":
        flag=1
        strline = fi.readline()
        token2 = parse_token_string(strline)
        if token2.type == "LPAREN" and token2.value == "(":
            if exp():
                fp2 = fi.tell()
                strline = fi.readline()
                token3 = parse_token_string(strline)
                while token3.type == "COMMA":
                    if exp():
                        fp2 = fi.tell()
                        strline = fi.readline()
                        token3 = parse_token_string(strline)
                    else:
                        print("<write>:, <exp> error")
                        return False
                if token3.type == "RPAREN" and token3.value == ")":
                    return True
                else:
                    fi.seek(fp2)
                    print("raw{},col{}:Expected ')'").format(token3.line, token3.col)
                    return True
            else:
                print("<write>:<exp> error")
        else:
            print("<write>:no (")
    # else:
    #     print("<write>:no write")

    fi.seek(fp)
    if flag:
        print("<write>:error")
    return False


def parse():
    if prog():
        print("Parsing completed successfully.")
    else:
        print("Parsing failed.")


if __name__ == "__main__":
    fi = open("output.txt", "r")
    parse()
    fi.close()
