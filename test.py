class Token:
    def __init__(self, token_type, value, line, col):
        self.type = token_type
        self.value = value
        self.line = int(line)
        self.col = int(col)

    # 修正：移除COMMA的特殊处理，统一解析
    def __str__(self):
        return f"[{self.line}:{self.col}] {self.type}='{self.value}'"


def parse_token_string(token_str):
    clean_str = token_str.strip().strip("<").strip(">")
    parts = [p.strip() for p in clean_str.split(",")]
    if len(parts) < 4:
        raise ValueError(f"无效的token字符串：{token_str}")
    return Token(token_type=parts[0], value=parts[1], line=parts[2], col=parts[3])


# 全局错误计数器（统计错误总数）
error_count = 0

# 通用报错函数，统一报错格式
def report_error(token, error_msg, expected=None):
    global error_count
    error_count += 1
    location = f"行{token.line}列{token.col}" if token else "未知位置"
    expected_str = f"，期望：{expected}" if expected else ""
    print(f"语法错误 {location}：{error_msg}{expected_str}")


# <prog> → program <id>；<block>
def prog():
    fp = fi.tell()
    try:
        strline = fi.readline()
        if not strline:
            report_error(None, "程序为空，缺少program关键字")
            return False
        
        token = parse_token_string(strline)
        if token.type == "KEYWORD" and token.value == "program":
            # 读取ID
            strline = fi.readline()
            if not strline:
                report_error(token, "program关键字后缺少标识符")
                fi.seek(fp)
                return False
            token2 = parse_token_string(strline)
            
            if token2.type == "ID":
                # 读取分号
                strline = fi.readline()
                if not strline:
                    report_error(token2, "标识符后缺少分号")
                    fi.seek(fp)
                    return False
                token3 = parse_token_string(strline)
                
                if token3.type == "SEMICOLON":
                    if block():
                        return True
                    else:
                        report_error(token3, "<block>语法错误", "合法的程序块")
                else:
                    report_error(token3, "标识符后应为分号", "SEMICOLON(;)")
            else:
                report_error(token2, "program关键字后应为标识符", "ID(标识符)")
        else:
            report_error(token, "程序应以program关键字开头", "KEYWORD(program)")
    except Exception as e:
        report_error(None, f"解析<prog>时发生错误：{str(e)}")
    
    fi.seek(fp)
    return False


# <block> → [<condecl>][<vardecl>][<proc>]<body>
def block():
    fp = fi.tell()
    success = False
    
    try:
        # 尝试解析常量说明（可选）
        condecl_ok = condecl()
        # 尝试解析变量说明（可选）
        vardecl_ok = vardecl()
        # 尝试解析过程（可选）
        proc_ok = True
        while True:
            proc_fp = fi.tell()
            if proc():
                continue
            else:
                fi.seek(proc_fp)
                break
        
        # 必须解析body（必选）
        if body():
            success = True
        else:
            report_error(None, "<block>缺少合法的<body>", "begin...end复合语句")
    except Exception as e:
        report_error(None, f"解析<block>时发生错误：{str(e)}")
    
    if not success:
        fi.seek(fp)
    return success


# <condecl> → const <const>{,<const>};
def condecl():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "const":
            # 必须有至少一个const定义
            if not const():
                report_error(token, "const关键字后缺少常量定义", "<id>:=<integer>")
                fi.seek(fp)
                return False
            
            # 处理逗号分隔的多个const
            while True:
                comma_fp = fi.tell()
                strline = fi.readline()
                if not strline:
                    report_error(current_token, "常量定义列表未结束，缺少分号")
                    fi.seek(fp)
                    return False
                
                token2 = parse_token_string(strline)
                current_token = token2
                
                if token2.type == "COMMA":
                    # 逗号后必须跟const
                    if not const():
                        report_error(token2, "逗号后应为常量定义", "<id>:=<integer>")
                        fi.seek(fp)
                        return False
                elif token2.type == "SEMICOLON":
                    # 正常结束
                    return True
                else:
                    # 既不是逗号也不是分号，错误
                    report_error(token2, "常量定义列表后应为分号", "SEMICOLON(;)")
                    fi.seek(comma_fp)
                    return False
        else:
            # 不是const关键字，回溯
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<condecl>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# <const> → <id>:=<integer>
def const():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "ID":
            # 读取赋值号
            strline = fi.readline()
            if not strline:
                report_error(token, "标识符后缺少赋值号:=")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "ASSIGN" and token2.value == ":=":
                # 读取整数
                strline = fi.readline()
                if not strline:
                    report_error(token2, "赋值号后缺少整数")
                    fi.seek(fp)
                    return False
                
                token3 = parse_token_string(strline)
                current_token = token3
                
                if token3.type == "INTEGER":
                    return True
                else:
                    report_error(token3, "赋值号后应为整数", "INTEGER(整数)")
            else:
                report_error(token2, "标识符后应为赋值号", "ASSIGN(:=)")
        else:
            report_error(token, "常量定义应以标识符开头", "ID(标识符)")
        
    except Exception as e:
        report_error(current_token, f"解析<const>时发生错误：{str(e)}")
    
    fi.seek(fp)
    return False


# <vardecl> → var <id>{,<id>};
def vardecl():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "var":
            # 读取第一个ID
            strline = fi.readline()
            if not strline:
                report_error(token, "var关键字后缺少标识符")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "ID":
                # 处理逗号分隔的多个ID
                while True:
                    comma_fp = fi.tell()
                    strline = fi.readline()
                    if not strline:
                        report_error(current_token, "变量列表未结束，缺少分号")
                        fi.seek(fp)
                        return False
                    
                    token3 = parse_token_string(strline)
                    current_token = token3
                    
                    if token3.type == "COMMA":
                        # 逗号后必须跟ID
                        strline = fi.readline()
                        if not strline:
                            report_error(token3, "逗号后缺少标识符")
                            fi.seek(fp)
                            return False
                        
                        token4 = parse_token_string(strline)
                        current_token = token4
                        
                        if token4.type == "ID":
                            continue
                        else:
                            report_error(token4, "逗号后应为标识符", "ID(标识符)")
                            fi.seek(fp)
                            return False
                    elif token3.type == "SEMICOLON":
                        # 正常结束
                        return True
                    else:
                        report_error(token3, "变量列表后应为分号", "SEMICOLON(;)")
                        fi.seek(comma_fp)
                        return False
            else:
                report_error(token2, "var关键字后应为标识符", "ID(标识符)")
        else:
            # 不是var关键字，回溯
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<vardecl>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# <proc> → procedure <id>（[<id>{,<id>}]）;<block>{;<proc>}
def proc():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "procedure":
            # 读取过程名ID
            strline = fi.readline()
            if not strline:
                report_error(token, "procedure关键字后缺少标识符")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "ID":
                # 读取左括号
                strline = fi.readline()
                if not strline:
                    report_error(token2, "过程名后缺少左括号")
                    fi.seek(fp)
                    return False
                
                token3 = parse_token_string(strline)
                current_token = token3
                
                if token3.type == "LPAREN" and token3.value == "(":
                    # 处理参数列表（可选）
                    param_ok = True
                    while True:
                        param_fp = fi.tell()
                        strline = fi.readline()
                        if not strline:
                            report_error(current_token, "参数列表未结束，缺少右括号")
                            fi.seek(fp)
                            return False
                        
                        token4 = parse_token_string(strline)
                        current_token = token4
                        
                        if token4.type == "ID":
                            # 处理参数后的逗号
                            while True:
                                comma_fp = fi.tell()
                                strline = fi.readline()
                                if not strline:
                                    report_error(token4, "参数后缺少右括号或逗号")
                                    fi.seek(fp)
                                    return False
                                
                                token5 = parse_token_string(strline)
                                current_token = token5
                                
                                if token5.type == "COMMA":
                                    # 逗号后必须跟ID
                                    strline = fi.readline()
                                    if not strline:
                                        report_error(token5, "逗号后缺少参数标识符")
                                        fi.seek(fp)
                                        return False
                                    
                                    token6 = parse_token_string(strline)
                                    current_token = token6
                                    
                                    if token6.type == "ID":
                                        break
                                    else:
                                        report_error(token6, "逗号后应为参数标识符", "ID(标识符)")
                                        fi.seek(fp)
                                        return False
                                elif token5.type == "RPAREN" and token5.value == ")":
                                    # 参数列表结束
                                    break
                                else:
                                    report_error(token5, "参数后应为逗号或右括号", "COMMA(,) 或 RPAREN())")
                                    fi.seek(fp)
                                    return False
                            break
                        elif token4.type == "RPAREN" and token4.value == ")":
                            # 无参数
                            break
                        else:
                            report_error(token4, "左括号后应为参数标识符或右括号", "ID(标识符) 或 RPAREN())")
                            fi.seek(param_fp)
                            param_ok = False
                            break
                    
                    if not param_ok:
                        fi.seek(fp)
                        return False
                    
                    # 读取分号
                    strline = fi.readline()
                    if not strline:
                        report_error(current_token, "右括号后缺少分号")
                        fi.seek(fp)
                        return False
                    
                    token7 = parse_token_string(strline)
                    current_token = token7
                    
                    if token7.type == "SEMICOLON":
                        # 解析过程体block
                        if block():
                            # 处理多个过程（;proc）
                            while True:
                                proc_fp = fi.tell()
                                strline = fi.readline()
                                if not strline:
                                    break
                                
                                token8 = parse_token_string(strline)
                                current_token = token8
                                
                                if token8.type == "SEMICOLON":
                                    if not proc():
                                        report_error(token8, "分号后应为过程定义", "procedure定义")
                                        fi.seek(fp)
                                        return False
                                else:
                                    fi.seek(proc_fp)
                                    break
                            return True
                        else:
                            report_error(token7, "过程分号后应为程序块", "<block>程序块")
                    else:
                        report_error(token7, "右括号后应为分号", "SEMICOLON(;)")
                else:
                    report_error(token3, "过程名后应为左括号", "LPAREN(()")
            else:
                report_error(token2, "procedure关键字后应为标识符", "ID(过程名)")
        else:
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<proc>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# <body> → begin <statement>{;<statement>}end
def body():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "begin":
            # 解析第一个语句
            if not statement():
                report_error(token, "begin后缺少合法语句", "<statement>语句")
                fi.seek(fp)
                return False
            
            # 处理多个语句（;statement）
            while True:
                stmt_fp = fi.tell()
                strline = fi.readline()
                if not strline:
                    report_error(current_token, "语句列表未结束，缺少end关键字")
                    fi.seek(fp)
                    return False
                
                token2 = parse_token_string(strline)
                current_token = token2
                
                if token2.type == "SEMICOLON":
                    if not statement():
                        report_error(token2, "分号后应为合法语句", "<statement>语句")
                        fi.seek(fp)
                        return False
                elif token2.type == "KEYWORD" and token2.value == "end":
                    # 正常结束
                    return True
                else:
                    report_error(token2, "语句后应为分号或end关键字", "SEMICOLON(;) 或 KEYWORD(end)")
                    fi.seek(stmt_fp)
                    fi.seek(fp)
                    return False
        else:
            report_error(token, "复合语句应以begin开头", "KEYWORD(begin)")
    except Exception as e:
        report_error(current_token, f"解析<body>时发生错误：{str(e)}")
    
    fi.seek(fp)
    return False


def statement():
    fp = fi.tell()
    # 尝试各种语句类型，不中断
    if assignment():
        return True
    fi.seek(fp)
    
    if condition():
        return True
    fi.seek(fp)
    
    if cycle():
        return True
    fi.seek(fp)
    
    if call():
        return True
    fi.seek(fp)
    
    if body():
        return True
    fi.seek(fp)
    
    if read():
        return True
    fi.seek(fp)
    
    if write():
        return True
    
    # 所有类型都不匹配
    try:
        # 读取当前token用于报错
        strline = fi.readline()
        if strline:
            token = parse_token_string(strline)
            report_error(token, "无效的语句", "赋值/条件/循环/call/复合语句/read/write")
            fi.seek(fp)
        else:
            report_error(None, "缺少语句", "合法的PL/0语句")
    except Exception as e:
        report_error(None, f"解析<statement>时发生错误：{str(e)}")
    
    return False


# <id> := <exp>
def assignment():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "ID":
            # 读取赋值号
            strline = fi.readline()
            if not strline:
                report_error(token, "标识符后缺少赋值号:=")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "ASSIGN" and token2.value == ":=":
                if exp():
                    return True
                else:
                    report_error(token2, "赋值号后应为表达式", "<exp>表达式")
            else:
                report_error(token2, "标识符后应为赋值号", "ASSIGN(:=)")
        else:
            # 不是ID，回溯
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<assignment>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# <exp> → [+|-]<term>{<aop><term>}
def exp():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        # 处理可选的正负号
        if token.type == "AOP" and token.value in ("+", "-"):
            # 符号后必须跟term
            if not term():
                report_error(token, "正负号后应为项", "<term>项")
                fi.seek(fp)
                return False
        else:
            # 无符号，直接解析term
            fi.seek(fp)
            if not term():
                report_error(token, "表达式应以项开头", "<term>项")
                fi.seek(fp)
                return False
        
        # 处理多个aop+term
        while True:
            aop_fp = fi.tell()
            strline = fi.readline()
            if not strline:
                break
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "AOP" and token2.value in ("+", "-"):
                if not term():
                    report_error(token2, "加法运算符后应为项", "<term>项")
                    fi.seek(aop_fp)
                    return False
            else:
                # 不是aop，回溯
                fi.seek(aop_fp)
                break
        
        return True
    except Exception as e:
        report_error(current_token, f"解析<exp>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# <term> → <factor>{<mop><factor>}
def term():
    fp = fi.tell()
    current_token = None
    try:
        # 必须有至少一个factor
        if not factor():
            # 读取当前token用于报错
            strline = fi.readline()
            if strline:
                token = parse_token_string(strline)
                report_error(token, "项应以因子开头", "<factor>因子")
            else:
                report_error(None, "项缺少因子", "<factor>因子")
            fi.seek(fp)
            return False
        
        # 处理多个mop+factor
        while True:
            mop_fp = fi.tell()
            strline = fi.readline()
            if not strline:
                break
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "MOP" and token2.value in ("*", "/"):
                if not factor():
                    report_error(token2, "乘法运算符后应为因子", "<factor>因子")
                    fi.seek(mop_fp)
                    return False
            else:
                # 不是mop，回溯
                fi.seek(mop_fp)
                break
        
        return True
    except Exception as e:
        report_error(current_token, f"解析<term>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# <factor>→<id>|<integer>|(<exp>)
def factor():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "ID" or token.type == "INTEGER":
            return True
        elif token.type == "LPAREN" and token.value == "(":
            # 解析括号内的exp
            if exp():
                # 读取右括号
                strline = fi.readline()
                if not strline:
                    report_error(token, "左括号后缺少右括号", "RPAREN())")
                    fi.seek(fp)
                    return False
                
                token2 = parse_token_string(strline)
                current_token = token2
                
                if token2.type == "RPAREN" and token2.value == ")":
                    return True
                else:
                    report_error(token2, "表达式后应为右括号", "RPAREN())")
            else:
                report_error(token, "左括号内应为表达式", "<exp>表达式")
        else:
            report_error(token, "因子应为标识符、整数或括号表达式", "ID/INTEGER/(<exp>)")
        
    except Exception as e:
        report_error(current_token, f"解析<factor>时发生错误：{str(e)}")
    
    fi.seek(fp)
    return False


# if <lexp> then <statement>[else <statement>]
def condition():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "if":
            # 解析lexp
            if not lexp():
                report_error(token, "if后应为条件表达式", "<lexp>条件表达式")
                fi.seek(fp)
                return False
            
            # 读取then
            strline = fi.readline()
            if not strline:
                report_error(current_token, "条件表达式后缺少then关键字")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "KEYWORD" and token2.value == "then":
                # 解析then后的statement
                if not statement():
                    report_error(token2, "then后应为语句", "<statement>语句")
                    fi.seek(fp)
                    return False
                
                # 处理可选的else
                else_fp = fi.tell()
                strline = fi.readline()
                if strline:
                    token3 = parse_token_string(strline)
                    current_token = token3
                    
                    if token3.type == "KEYWORD" and token3.value == "else":
                        if not statement():
                            report_error(token3, "else后应为语句", "<statement>语句")
                            fi.seek(fp)
                            return False
                    else:
                        # 不是else，回溯
                        fi.seek(else_fp)
                
                return True
            else:
                report_error(token2, "条件表达式后应为then关键字", "KEYWORD(then)")
        else:
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<condition>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# <lexp> → <exp> <lop> <exp>|odd <exp>
def lexp():
    fp = fi.tell()
    current_token = None
    try:
        # 尝试第一种形式：exp lop exp
        exp1_fp = fi.tell()
        if exp():
            strline = fi.readline()
            if not strline:
                # 没有lop，尝试第二种形式
                fi.seek(exp1_fp)
            else:
                token = parse_token_string(strline)
                current_token = token
                
                if token.type == "LOP" and token.value in ("=", "<>", "<", "<=", ">", ">="):
                    if exp():
                        return True
                    else:
                        report_error(token, "关系运算符后应为表达式", "<exp>表达式")
                        fi.seek(fp)
                        return False
                else:
                    # 不是合法的lop，尝试第二种形式
                    fi.seek(exp1_fp)
        
        # 尝试第二种形式：odd exp
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "odd":
            if exp():
                return True
            else:
                report_error(token, "odd后应为表达式", "<exp>表达式")
        else:
            report_error(token, "条件应为exp lop exp或odd exp形式", "<exp> <lop> <exp> 或 odd <exp>")
        
    except Exception as e:
        report_error(current_token, f"解析<lexp>时发生错误：{str(e)}")
    
    fi.seek(fp)
    return False


# while <lexp> do <statement>
def cycle():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "while":
            # 解析lexp
            if not lexp():
                report_error(token, "while后应为条件表达式", "<lexp>条件表达式")
                fi.seek(fp)
                return False
            
            # 读取do
            strline = fi.readline()
            if not strline:
                report_error(current_token, "条件表达式后缺少do关键字")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "KEYWORD" and token2.value == "do":
                if statement():
                    return True
                else:
                    report_error(token2, "do后应为语句", "<statement>语句")
            else:
                report_error(token2, "条件表达式后应为do关键字", "KEYWORD(do)")
        else:
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<cycle>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# call <id>（[<exp>{,<exp>}]）
def call():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "call":
            # 读取过程名ID
            strline = fi.readline()
            if not strline:
                report_error(token, "call后缺少标识符")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "ID":
                # 读取左括号
                strline = fi.readline()
                if not strline:
                    report_error(token2, "过程名后缺少左括号")
                    fi.seek(fp)
                    return False
                
                token3 = parse_token_string(strline)
                current_token = token3
                
                if token3.type == "LPAREN" and token3.value == "(":
                    # 修正：参数列表解析逻辑（移除EXP判断，直接调用exp）
                    param_ok = True
                    while True:
                        param_fp = fi.tell()
                        # 尝试解析表达式
                        if exp():
                            # 表达式解析成功，读取逗号或右括号
                            strline = fi.readline()
                            if not strline:
                                report_error(current_token, "参数列表未结束，缺少右括号")
                                fi.seek(fp)
                                return False
                            token4 = parse_token_string(strline)
                            current_token = token4
                            
                            if token4.type == "COMMA":
                                continue
                            elif token4.type == "RPAREN" and token4.value == ")":
                                break
                            else:
                                report_error(token4, "参数后应为逗号或右括号", "COMMA(,) 或 RPAREN())")
                                fi.seek(fp)
                                return False
                        else:
                            # 表达式解析失败，检查是否是右括号（无参数）
                            fi.seek(param_fp)
                            strline = fi.readline()
                            if not strline:
                                report_error(current_token, "参数列表未结束，缺少右括号")
                                fi.seek(fp)
                                return False
                            token4 = parse_token_string(strline)
                            current_token = token4
                            
                            if token4.type == "RPAREN" and token4.value == ")":
                                break
                            else:
                                report_error(token4, "参数列表中应为表达式或右括号", "<exp>表达式 或 RPAREN())")
                                fi.seek(fp)
                                return False
                    
                    return True
                else:
                    report_error(token3, "过程名后应为左括号", "LPAREN(()")
            else:
                report_error(token2, "call后应为标识符", "ID(过程名)")
        else:
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<call>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# read (<id>{，<id>})
def read():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "read":
            # 读取左括号
            strline = fi.readline()
            if not strline:
                report_error(token, "read后缺少左括号")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "LPAREN" and token2.value == "(":
                # 读取第一个ID
                strline = fi.readline()
                if not strline:
                    report_error(token2, "左括号后缺少标识符")
                    fi.seek(fp)
                    return False
                
                token3 = parse_token_string(strline)
                current_token = token3
                
                if token3.type == "ID":
                    # 处理逗号分隔的多个ID
                    while True:
                        comma_fp = fi.tell()
                        strline = fi.readline()
                        if not strline:
                            report_error(current_token, "read参数列表未结束，缺少右括号")
                            fi.seek(fp)
                            return False
                        
                        token4 = parse_token_string(strline)
                        current_token = token4
                        
                        if token4.type == "COMMA":
                            # 逗号后必须跟ID
                            strline = fi.readline()
                            if not strline:
                                report_error(token4, "逗号后缺少标识符")
                                fi.seek(fp)
                                return False
                            
                            token5 = parse_token_string(strline)
                            current_token = token5
                            
                            if token5.type == "ID":
                                continue
                            else:
                                report_error(token5, "逗号后应为标识符", "ID(标识符)")
                                fi.seek(fp)
                                return False
                        elif token4.type == "RPAREN" and token4.value == ")":
                            return True
                        else:
                            report_error(token4, "read参数后应为逗号或右括号", "COMMA(,) 或 RPAREN())")
                            fi.seek(comma_fp)
                            fi.seek(fp)
                            return False
                else:
                    report_error(token3, "左括号后应为标识符", "ID(标识符)")
            else:
                report_error(token2, "read后应为左括号", "LPAREN(()")
        else:
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<read>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


# write (<exp>{,<exp>})
def write():
    fp = fi.tell()
    current_token = None
    try:
        strline = fi.readline()
        if not strline:
            fi.seek(fp)
            return False
        
        token = parse_token_string(strline)
        current_token = token
        
        if token.type == "KEYWORD" and token.value == "write":
            # 读取左括号
            strline = fi.readline()
            if not strline:
                report_error(token, "write后缺少左括号")
                fi.seek(fp)
                return False
            
            token2 = parse_token_string(strline)
            current_token = token2
            
            if token2.type == "LPAREN" and token2.value == "(":
                # 解析第一个exp
                if not exp():
                    report_error(token2, "左括号后应为表达式", "<exp>表达式")
                    fi.seek(fp)
                    return False
                
                # 处理逗号分隔的多个exp
                while True:
                    comma_fp = fi.tell()
                    strline = fi.readline()
                    if not strline:
                        report_error(current_token, "write参数列表未结束，缺少右括号")
                        fi.seek(fp)
                        return False
                    
                    token3 = parse_token_string(strline)
                    current_token = token3
                    
                    if token3.type == "COMMA":
                        if not exp():
                            report_error(token3, "逗号后应为表达式", "<exp>表达式")
                            fi.seek(fp)
                            return False
                    elif token3.type == "RPAREN" and token3.value == ")":
                        return True
                    else:
                        report_error(token3, "write参数后应为逗号或右括号", "COMMA(,) 或 RPAREN())")
                        fi.seek(comma_fp)
                        fi.seek(fp)
                        return False
            else:
                report_error(token2, "write后应为左括号", "LPAREN(()")
        else:
            fi.seek(fp)
            return False
    except Exception as e:
        report_error(current_token, f"解析<write>时发生错误：{str(e)}")
        fi.seek(fp)
        return False


def parse():
    global error_count
    error_count = 0
    print("开始PL/0语法分析...")
    print("-" * 50)
    
    try:
        if prog():
            print("-" * 50)
            if error_count == 0:
                print("语法分析完成，未发现错误！")
            else:
                print(f"语法分析完成，共发现 {error_count} 个错误")
        else:
            print("-" * 50)
            print(f"语法分析失败，共发现 {error_count} 个错误")
    except Exception as e:
        print("-" * 50)
        print(f"分析过程中发生致命错误：{str(e)}")

def out():
    strline = fi.readlines()
    print(strline)

if __name__ == "__main__":
    try:
        fi = open("output.txt", "r", encoding="utf-8")  # 修改：增加编码指定，避免中文乱码
        fi.seek(0)
        parse()
        fi.close()
    except FileNotFoundError:
        print(f"找不到文件：output.txt")
    except Exception as e:
        print(f"程序运行错误：{str(e)}")