class Token:
    def __init__(self, token_type, value, line, col):
        self.type = token_type
        self.value = value
        self.line = int(line)
        self.col = int(col)


class OneCode:
    def __init__(self, f, l, a):
        self.func = f  # 伪操作码
        self.l = l  # 层差,调用层-定义层
        self.addr = a  # 相对地址,对于常数是记录数值


class Code:
    def __init__(self):
        self.code = []
        self.nextquad = 0  # 当前正要生成的指令编号

    def emit(self, f, l, a):
        oc = OneCode(f, l, a)
        self.code.append(oc)
        self.nextquad += 1

    def write2file(self, filename):
        fo = open(filename, "w")
        for c in self.code:
            fo.write("{} {} {}\n".format(c.func, c.l, c.addr))
        fo.close()

    def next_q(self):
        return self.nextquad


class Error:
    def __init__(self, line, col, info):
        self.line = line
        self.col = col
        self.info = info

    def write2file(self, filename):
        fo = open(filename, "a")
        fo.write("在第{}行，第{}列，{}\n".format(self.line, self.col, self.info))
        fo.close()

    def print_error(self):
        print("在第{}行，第{}列，{}".format(self.line, self.col, self.info))


class TableItem:
    def __init__(self, name, type, level, addr, value=None):
        self.name = name
        self.type = type
        self.level = level
        self.addr = addr
        self.value = value


class Table:
    def __init__(self):
        self.items = [[]]  # items[level][item1,item2,...]

    def find(self, name):  # 查找变量和常量
        global level
        i = level
        while i >= 0:
            for item in self.items[i]:
                if item.name == name:
                    return item
            i -= 1
        return None

    def record(self, name, type, level, addr, value=None):
        tmp = len(self.items)
        if level + 1 > tmp:
            self.items.append([])
        if type == "var":
            lenv = 3
            for item in self.items[level]:
                if item.type == "var":
                    lenv += 1
            addr = lenv
        self.items[level].append(TableItem(name, type, level, addr, value))

    def pop(self, level):
        self.items[level] = []

    def space_count(self, level):
        cnt = 0
        for item in self.items[level]:
            if item.type == "var":
                cnt += 1
        return cnt


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
    global code, space, current_token_index, level
    current = code.next_q()
    code.emit("JMP", 0, 0)  # 先跳过声明部分，直接跳到body开始处

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
        m = code.next_q()
        code.code[current].addr = m  # 回填JMP的地址
        space = 3
        space += table.space_count(level)
        code.emit("INT", 0, space)  # 为过程分配空间
        flag = body(token)
        code.emit("OPR", 0, 0)  # 过程结束返回
        if flag:
            return True
    else:
        print("{}行，{}列:期望一个 begin".format(token.line, token.col))

    while token.value not in follow_set["block"]:
        token = next_token()

    current_token_index -= 1
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
    global current_token_index, table, level
    id = token.value
    token = next_token()
    if token.type == "ASSIGN":
        token = next_token()
        if token.type == "INTEGER":
            table.record(id, "const", level, None, int(token.value))
            return True
        else:
            print("{}行，{}列:期望一个 integer".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 :=".format(token.line, token.col))

    while token.value not in follow_set["const_def"]:
        token = next_token()

    current_token_index -= 1
    return False


# <vardecl> → var <id>{,<id>};
def vardecl(token):
    global current_token_index, table, level
    token = next_token()
    if token.type == "ID":
        id = token.value
        tmp=table.find(id)
        if tmp != None:
            error = Error(token.line, token.col, id + "重复定义")
            error.print_error()
        else:
            table.record(id, "var", level, None)
        token = next_token()
        while token.type == "COMMA":
            token = next_token()
            if token.type == "ID":
                id = token.value
                tmp=table.find(id)
                if tmp != None:
                    error = Error(token.line, token.col, id + "重复定义")
                    error.print_error()
                else:
                    table.record(id, "var", level, None)
                token = next_token()
            else:
                print("{}行，{}列:期望一个 id".format(token.line, token.col))
        if token.type != "SEMICOLON":
            print("{}行，{}列:期望一个 ;".format(token.line, token.col))
        else:
            return True
    else:
        print("{}行，{}列:期望一个 id".format(token.line, token.col))

    while token.value not in follow_set["vardecl"]:
        token = next_token()
    current_token_index -= 1
    return False


# <proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}
def proc(token):
    global current_token_index, table, level, space
    space = 3
    token = next_token()
    if token.type == "ID":
        prc = len(table.items[level])
        table.record(token.value, "proc", level, None)
        token = next_token()
        if token.type == "LPAREN" and token.value == "(":
            token = next_token()
            if token.type == "ID":
                table.record(token.value, "var", level + 1, None)
                space += 1
                token = next_token()
                while token.type == "COMMA":
                    token = next_token()
                    if token.type == "ID":
                        table.record(token.value, "var", level + 1, None)
                        space += 1
                        token = next_token()
                    else:
                        print("{}行，{}列:期望一个 id".format(token.line, token.col))
                if token.type == "RPAREN" and token.value == ")":
                    token = next_token()
                    if token.type == "SEMICOLON":
                        table.items[level][prc].value = space - 3  # 记录过程的形参个数
                        level += 1
                        current=code.next_q()
                        table.items[level - 1][prc].addr = current  # 记录过程的起始地址
                        block()
                        table.pop(level)
                        level -= 1
                        token = next_token()
                        while token.type == "SEMICOLON":
                            token = next_token()
                            if token.value == "procedure":
                                flag=proc(token)
                                if flag:
                                    token= next_token()
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

    while token.value not in follow_set["proc"]:
        token = next_token()

    current_token_index -= 1
    return False


# <body> → begin <statement>{;<statement>}end
def body(token):
    global current_token_index
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
    global current_token_index, level, table, code
    tmp = table.find(token.value)
    if tmp == None:
        error = Error(token.line, token.col, token.value + "缺少定义")
        error.print_error()

    token = next_token()
    if token.type == "ASSIGN":
        if exp():
            if tmp != None:
                code.emit("STO", level - tmp.level, tmp.addr)
            return True
    else:
        print("{}行，{}列:期望一个 :=".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# <exp> → [+|-]<term>{<aop><term>}
def exp():
    global current_token_index, code
    token = next_token()
    flag2 = False
    if token.type == "AOP":
        if token.value == "-":
            flag2 = True
        if term():
            if flag2:
                code.emit("OPR", 0, 1)  # 取负操作
            token = next_token()
            flag = 1
            while token.type == "AOP":
                tmp = token.type
                if term():
                    if tmp == "+":
                        code.emit("OPR", 0, 2)  # 加法操作
                    else:
                        code.emit("OPR", 0, 3)  # 减法操作
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
                tmp = token.value
                if term():
                    if tmp == "+":
                        code.emit("OPR", 0, 2)  # 加法操作
                    else:
                        code.emit("OPR", 0, 3)  # 减法操作
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
    global current_token_index, code
    flag1 = 0
    if factor():
        flag1 = 1
        flag = 1
        token = next_token()
        while token.type == "MOP":
            tmp = token.value
            if factor():
                if tmp == "*":
                    code.emit("OPR", 0, 4)
                else:
                    code.emit("OPR", 0, 5)
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
    global current_token_index, table, level, code
    token = next_token()
    if token.type == "ID" or token.type == "INTEGER":
        if token.type == "ID":
            tmp = table.find(token.value)
            if tmp == None:
                error = Error(token.line, token.col, token.value + "缺少定义")
                error.print_error()

            else:
                if tmp.type == "const":
                    code.emit("LIT", 0, tmp.value)  # 加载常量值
                else:
                    code.emit("LOD", level - tmp.level, tmp.addr)  # 加载变量值
        else:
            code.emit("LIT", 0, int(token.value))  # 加载整数值
        return True
    elif token.value == "(":
        if exp():
            token = next_token()
            if token.value == ")":
                return True
            else:
                print("{}行，{}列:期望一个 )".format(token.line, token.col))

    while token.value not in follow_set["factor"]:
        token = next_token()

    current_token_index -= 1
    return False


# if <lexp> then <statement>[else <statement>]
def condition(token):
    global current_token_index, code
    if lexp():
        token = next_token()
        if token.value == "then":
            current = code.next_q()
            code.emit("JPC", 0, 0)  # 先生成条件跳转指令，地址待回填
            if statement():
                code.code[current].addr = code.next_q()  # 回填JPC的地址
                token = next_token()
                if token.value == "else":
                    code.code[current].addr = code.next_q() + 1  # 回填JPC的地址
                    current2 = code.next_q()
                    code.emit("JMP", 0, 0)  # 生成无条件跳转
                    if statement():
                        code.code[current2].addr = code.next_q()  # 回填JMP的地址
                        return True
                else:
                    current_token_index -= 1
                    return True
        else:
            print("{}行，{}列:期望一个 then".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# <lexp> → <exp> <lop> <exp>|odd <exp>
def lexp():
    global current_token_index, code
    token = next_token()
    if token.value == "odd":
        if exp():
            code.emit("OPR", 0, 6)  # 判断奇偶
            return True

    current_token_index -= 1
    flag = 0
    if exp():
        flag = 1
        token = next_token()
        if token.type == "LOP":
            sign = token.value
            if exp():
                if sign == "=":
                    code.emit("OPR", 0, 7)  # 等于
                elif sign == "<>":
                    code.emit("OPR", 0, 8)  # 不等于
                elif sign == "<":
                    code.emit("OPR", 0, 9)  # 小于
                elif sign == ">=":
                    code.emit("OPR", 0, 10)  # 大于等于
                elif sign == ">":
                    code.emit("OPR", 0, 11)  # 大于
                elif sign == "<=":
                    code.emit("OPR", 0, 12)  # 小于等于
                return True

    if flag:
        while token.value not in follow_set["lexp"]:
            token = next_token()

        current_token_index -= 1
    return False


# while <lexp> do <statement>
def cycle(token):
    global current_token_index, code
    whilestart = code.next_q()  # 记录循环开始位置
    if lexp():
        token = next_token()
        if token.value == "do":
            current = code.next_q()
            code.emit("JPC", 0, 0)  # 先生成条件跳转
            if statement():
                code.emit("JMP", 0, whilestart)  # 回到循环开始处
                code.code[current].addr = code.next_q()  # 回填JPC的地址
                return True
        else:
            print("{}行，{}列:期望一个 do".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# call <id>（[<exp>{,<exp>}]）
def call(token):
    global current_token_index, table, level, code
    para = 3
    callnun = 0
    token = next_token()
    if token.type == "ID":
        tmp = table.find(token.value)
        if tmp == None:
            error = Error(token.line, token.col, token.value + "缺少定义")
            error.print_error()

        token = next_token()
        if token.value == "(":
            if exp():
                callnun += 1
                code.emit("STO", -1, para)  # 将参数存到调用者的栈帧中
                para += 1
                flag = 1
                token = next_token()
                while token.type == "COMMA":
                    if exp():
                        callnun += 1
                        code.emit("STO", -1, para)  # 将参数存到调用者的栈帧中
                        para += 1
                        token = next_token()
                    else:
                        flag = 0
                if flag:
                    if token.value == ")":
                        if tmp != None and tmp.type == "proc":
                            if callnun != tmp.value:
                                error = Error(
                                    token.line, token.col, "实参个数与形参个数不匹配"
                                )
                                error.print_error()

                        else:
                            error = Error(
                                token.line, token.col, token.value + "不是过程名"
                            )
                            error.print_error()

                        code.emit("CAL", level - tmp.level, tmp.addr)  # 生成调用指令
                        return True
                    else:
                        current_token_index -= 1
                        print("{}行，{}列:期望一个 )".format(token.line, token.col))
            else:
                token = next_token()
                if token.value == ")":
                    return True
                else:
                    current_token_index -= 1
                    print("{}行，{}列:期望一个 )".format(token.line, token.col))

        else:
            print("{}行，{}列:期望一个 (".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 id".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# read (<id>{，<id>})
def read(token):
    global current_token_index, table, level, code
    token = next_token()
    if token.value == "(":
        token = next_token()
        if token.type == "ID":
            tmp = table.find(token.value)
            if tmp == None:
                error = Error(token.line, token.col, token.value + "缺少定义")
                error.print_error()

            else:
                code.emit("RED", 0, 0)  # 生成读指令
                code.emit("STO", level - tmp.level, tmp.addr)  # 将读到的值存到变量中
            flag = 1
            token = next_token()
            while token.type == "COMMA":
                token = next_token()
                if token.type == "ID":
                    tmp = table.find(token.value)
                    if tmp == None:
                        error = Error(token.line, token.col, token.value + "缺少定义")
                        error.print_error()

                    else:
                        code.emit("RED", 0, 0)  # 生成读指令
                        code.emit(
                            "STO", level - tmp.level, tmp.addr
                        )  # 将读到的值存到变量中
                    token = next_token()
                else:
                    flag = 0
                    print("{}行，{}列:期望一个 id".format(token.line, token.col))
            if flag:
                if token.value == ")":
                    return True
                else:
                    current_token_index -= 1
                    print("{}行，{}列:期望一个 )".format(token.line, token.col))
        else:
            print("{}行，{}列:期望一个 id".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 (".format(token.line, token.col))

    while token.value not in follow_set["statement"]:
        token = next_token()

    current_token_index -= 1
    return False


# write (<exp>{,<exp>})
def write(token):
    global current_token_index, code
    token = next_token()
    if token.value == "(":
        if exp():
            code.emit("WRT", 0, 0)  # 生成写指令
            flag = 1
            token = next_token()
            while token.type == "COMMA":
                if exp():
                    code.emit("WRT", 0, 0)
                    token = next_token()
                else:
                    flag = 0
            if flag:
                if token.value == ")":
                    return True
                else:
                    current_token_index -= 1
                    print("{}行，{}列:期望一个 )".format(token.line, token.col))
    else:
        print("{}行，{}列:期望一个 (".format(token.line, token.col))

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
    flag = lexical()
    if not flag:
        exit(0)

    fi = open("output.txt", "r")
    tokens = load_tokens()
    fi.close()

    current_token_index = 0
    # genrate = True  # 若有语法错误则不生成目标代码
    level = 0
    space = 3
    table = Table()
    code = Code()
    parse()
    code.write2file("pcode.txt")
