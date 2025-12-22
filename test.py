import re
from typing import List, Dict, Set, Tuple, Optional

# 定义单词结构
class OneWord:
    def __init__(self, type_: str, value: str, row: int, col: int):
        self.type = type_       # 单词类型（如SEMICOLON, ID, INTEGER等）
        self.value = value      # 单词值（如';', 'x', '123'等）
        self.row = row          # 行号
        self.col = col          # 列号

    def __repr__(self) -> str:
        return f"<{self.type}, {self.value}, {self.row}, {self.col}>"

# 错误信息结构
class Error:
    def __init__(self, info: str, row: int, col: int):
        self.info = info
        self.row = row
        self.col = col

# 词法分析器接口（假设已实现，此处仅做适配）
class WordAnalyse:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.file = open(input_path, 'r', encoding='utf-8')
        self.line = 1
        self.col = 1

    def analyse(self) -> Optional[OneWord]:
        """读取下一个单词，返回OneWord对象或None（文件结束）"""
        # 实际实现需根据词法规则解析，此处仅示例格式处理
        line = self.file.readline()
        if not line:
            return None
        
        # 假设词法分析结果格式为"<TYPE, value, row, col>"
        match = re.match(r'<(\w+),\s*(.*?)\s*,\s*(\d+)\s*,\s*(\d+)>', line.strip())
        if not match:
            return None
            
        type_ = match.group(1)
        value = match.group(2)
        row = int(match.group(3))
        col = int(match.group(4))
        return OneWord(type_, value, row, col)

    def close(self):
        self.file.close()

# 语法分析器实现
class GrammarAnalyse:
    def __init__(self, input_path: str):
        self.word_analyse = WordAnalyse(input_path)
        self.words: List[OneWord] = []
        self.errors: List[Error] = []
        self.now_num = 0  # 当前单词索引
        self.wrong = False  # 语法错误标记
        self.wrong2 = False  # 语义错误标记
        
        # 初始化单词列表
        self._init_words()
        
        # FIRST集和FOLLOW集（保持C++逻辑）
        self.first_set: Dict[str, Set[str]] = {
            "<prog>": {"PROGRAM"},
            "<block>": {"CONST", "VAR", "PROCEDURE", "BEGIN"},
            "<condecl>": {"CONST"},
            "<const>": {"ID", "NID"},
            "<vardecl>": {"VAR"},
            "<proc>": {"PROCEDURE"},
            "<body>": {"BEGIN"},
            "<statement>": {"NID", "ID", "IF", "WHILE", "CALL", "BEGIN", "READ", "WRITE"},
            "<lexp>": {"ODD", "PLUS", "MINUS", "NID", "ID", "LPAREN", "INTEGER"},
            "<exp>": {"ODD", "PLUS", "MINUS", "NID", "ID", "LPAREN", "INTEGER"},
            "<term>": {"ID", "NID", "LPAREN", "INTEGER"},
            "<factor>": {"ID", "NID", "LPAREN", "INTEGER"},
        }
        
        self.follow_set: Dict[str, Set[str]] = {
            "<prog>": {"#"},
            "<block>": {"#", "SEMICOLON", "BEGIN"},
            "<condecl>": {"VAR", "PROCEDURE", "BEGIN"},
            "<const>": {"COMMA", "SEMICOLON"},
            "<vardecl>": {"PROCEDURE", "BEGIN"},
            "<proc>": {"BEGIN", "SEMICOLON"},
            "<body>": {"#", "ELSE", "END", "SEMICOLON", "PERIOD", "BEGIN"},
            "<statement>": {"ELSE", "END", "SEMICOLON"},
            "<lexp>": {"THEN", "DO"},
            "<exp>": {"ELSE", "END", "THEN", "DO", "COMMA", "RPAREN", "SEMICOLON", "EQ", "NEQ", "LT", "LE", "GT", "GE"},
            "<term>": {"PLUS", "MINUS", "ELSE", "END", "THEN", "DO", "COMMA", "RPAREN", "SEMICOLON", "EQ", "NEQ", "LT", "LE", "GT", "GE"},
            "<factor>": {"MULT", "DIV", "PLUS", "MINUS", "ELSE", "END", "THEN", "DO", "COMMA", "RPAREN", "SEMICOLON", "EQ", "NEQ", "LT", "LE", "GT", "GE"},
            "ID": {"COMMA", "ASSIGN", "SEMICOLON", "LPAREN", "RPAREN", "MULT", "DIV", "PLUS", "MINUS", "ELSE", "END", "THEN", "DO", "EQ", "NEQ", "LT", "LE", "GT", "GE"},
            "INTEGER": {"MULT", "DIV", "PLUS", "MINUS", "ELSE", "END", "THEN", "DO", "COMMA", "RPAREN", "SEMICOLON", "EQ", "NEQ", "LT", "LE", "GT", "GE"},
        }

    def _init_words(self):
        """初始化单词列表，读取词法分析结果"""
        while True:
            word = self.word_analyse.analyse()
            if not word:
                break
            self.words.append(word)
        # 添加程序结束标记
        self.words.append(OneWord("PROEND", "#", self.words[-1].row + 1, 0) if self.words else OneWord("PROEND", "#", 1, 0))

    def print_error(self, info: str, row: int, col: int):
        """打印语法错误"""
        self.wrong = True
        print(f"语法错误：row:{row:2d}, column:{col:2d} {info}")
        self.errors.append(Error(info, row, col))

    def print_error2(self, info: str, row: int, col: int):
        """打印语义错误"""
        self.wrong2 = True
        print(f"语义错误：row:{row:2d}, column:{col:2d} {info}")
        self.errors.append(Error(info, row, col))

    def next_word(self):
        """移动到下一个单词"""
        if self.now_num < len(self.words) - 1:
            self.now_num += 1

    def current_word(self) -> OneWord:
        """获取当前单词"""
        return self.words[self.now_num]

    def analyse(self):
        """语法分析入口"""
        self.prog()
        if not self.wrong:
            print("语法分析结束,程序无语法错误")
            if not self.wrong2:
                print("语义分析结束,代码已经生成")
            else:
                print("语义分析结束,程序出现语义错误")
        else:
            print("语法分析结束,程序出现语法错误")

    def prog(self):
        """处理<prog>非终结符：program <id>;<block>"""
        current = self.current_word()
        if current.type != "PROGRAM":
            self.print_error("缺少program关键字", current.row, current.col)
        
        self.next_word()  # 跳过program
        current = self.current_word()
        
        if current.type not in ("ID", "NID"):
            self.print_error("program后应为标识符", current.row, current.col)
        
        self.next_word()  # 跳过id
        current = self.current_word()
        
        if current.type != "SEMICOLON":
            self.print_error("缺少分号", current.row, current.col)
        
        self.next_word()  # 跳过;
        self.block()  # 分析程序块

    def block(self):
        """处理<block>非终结符：[condecl] [vardecl] [proc] <body>"""
        current = self.current_word()
        
        # 处理常量声明
        if current.type == "CONST":
            self.condecl()
        
        current = self.current_word()
        # 处理变量声明
        if current.type == "VAR":
            self.vardecl()
        
        current = self.current_word()
        # 处理过程声明
        if current.type == "PROCEDURE":
            self.proc()
        
        # 处理语句体
        self.body()

    def condecl(self):
        """处理<condecl>非终结符：const <const>{,<const>};"""
        self.next_word()  # 跳过const
        self._const()  # 处理第一个常量定义
        
        current = self.current_word()
        # 处理后续常量定义
        while current.type == "COMMA":
            self.next_word()  # 跳过,
            self._const()
            current = self.current_word()
        
        # 检查分号结束
        if current.type != "SEMICOLON":
            self.print_error("常量声明缺少分号结束", current.row, current.col)
        else:
            self.next_word()  # 跳过;

    def _const(self):
        """处理<const>非终结符：<id>:=<integer>"""
        current = self.current_word()
        # 检查标识符
        if current.type not in ("ID", "NID"):
            self.print_error("常量定义缺少标识符", current.row, current.col)
            return
        
        const_name = current.value
        self.next_word()  # 跳过id
        current = self.current_word()
        
        # 检查赋值符号
        if current.type != "ASSIGN":  # :=对应类型为ASSIGN
            self.print_error("常量定义缺少赋值符号(:=)", current.row, current.col)
            return
        
        self.next_word()  # 跳过:=
        current = self.current_word()
        
        # 检查整数
        if current.type != "INTEGER":
            self.print_error("常量定义值应为整数", current.row, current.col)
            return
        
        # 记录常量到符号表（此处省略符号表实现）
        self.next_word()  # 跳过integer

    def vardecl(self):
        """处理<vardecl>非终结符：var id ( , id ) ;"""
        self.next_word()  # 跳过var
        current = self.current_word()
        
        # 处理变量列表
        if current.type in ("ID", "NID"):
            # 记录变量到符号表（此处省略）
            self.next_word()  # 跳过id
        else:
            self.print_error("变量声明缺少标识符", current.row, current.col)
            return
        
        current = self.current_word()
        # 处理后续变量
        while current.type == "COMMA":
            self.next_word()  # 跳过,
            if current.type in ("ID", "NID"):
                # 记录变量到符号表（此处省略）
                self.next_word()  # 跳过id
            else:
                self.print_error("变量声明缺少标识符", current.row, current.col)
            current = self.current_word()
        
        # 检查分号结束
        if current.type != "SEMICOLON":
            self.print_error("变量声明缺少分号结束", current.row, current.col)
        else:
            self.next_word()  # 跳过;

    def proc(self):
        """处理<proc>非终结符：procedure id ( [param] ) ; block ;"""
        current = self.current_word()
        if current.type != "PROCEDURE":
            self.print_error("缺少procedure关键字", current.row, current.col)
            return
        
        self.next_word()  # 跳过procedure
        current = self.current_word()
        
        # 检查过程名
        if current.type not in ("ID", "NID"):
            self.print_error("过程声明缺少标识符", current.row, current.col)
            return
        
        proc_name = current.value
        self.next_word()  # 跳过id
        current = self.current_word()
        
        # 检查参数列表开始
        if current.type != "LPAREN":  # (对应类型为LPAREN
            self.print_error("过程声明缺少左括号", current.row, current.col)
            return
        
        self.next_word()  # 跳过(
        current = self.current_word()
        
        # 处理参数（简化版）
        if current.type in ("ID", "NID"):
            # 记录参数到符号表（此处省略）
            self.next_word()  # 跳过param
            current = self.current_word()
        
        # 检查参数列表结束
        if current.type != "RPAREN":  # )对应类型为RPAREN
            self.print_error("过程声明缺少右括号", current.row, current.col)
            return
        
        self.next_word()  # 跳过)
        # 后续可添加过程体分析逻辑

    def body(self):
        """处理<body>非终结符：begin statement ( ; statement )* end"""
        current = self.current_word()
        if current.type != "BEGIN":
            self.print_error("缺少begin关键字", current.row, current.col)
            return
        
        self.next_word()  # 跳过begin
        # 处理语句序列（简化版）
        while self.current_word().type != "END":
            self.statement()
            current = self.current_word()
            if current.type == "SEMICOLON":
                self.next_word()  # 跳过;
        
        if self.current_word().type != "END":
            self.print_error("缺少end关键字", self.current_word().row, self.current_word().col)
        else:
            self.next_word()  # 跳过end

    def statement(self):
        """处理<statement>非终结符（简化版）"""
        current = self.current_word()
        if current.type in ("ID", "NID"):
            # 赋值语句
            self.next_word()  # 跳过id
            if self.current_word().type == "ASSIGN":
                self.next_word()  # 跳过:=
                self.exp()  # 处理表达式
        elif current.type == "IF":
            # if语句（简化版）
            self.next_word()  # 跳过if
            self.lexp()  # 处理条件表达式
            if self.current_word().type == "THEN":
                self.next_word()  # 跳过then
                self.statement()
        # 可扩展其他语句类型（while、call等）

    def lexp(self):
        """处理<lexp>非终结符（条件表达式）"""
        self.exp()  # 简化处理，实际需判断关系运算符

    def exp(self):
        """处理<exp>非终结符（算术表达式）"""
        self.term()  # 简化处理，实际需处理加减运算符

    def term(self):
        """处理<term>非终结符（项）"""
        self.factor()  # 简化处理，实际需处理乘除运算符

    def factor(self):
        """处理<factor>非终结符（因子）"""
        current = self.current_word()
        if current.type in ("ID", "NID", "INTEGER"):
            self.next_word()  # 跳过标识符或整数
        elif current.type == "LPAREN":
            self.next_word()  # 跳过(
            self.exp()
            if self.current_word().type == "RPAREN":
                self.next_word()  # 跳过)
            else:
                self.print_error("缺少右括号", self.current_word().row, self.current_word().col)
        else:
            self.print_error("表达式语法错误", current.row, current.col)

# 使用示例
if __name__ == "__main__":
    grammar = GrammarAnalyse("lex_result.txt")  # 词法分析结果文件
    grammar.analyse()
    grammar.word_analyse.close()