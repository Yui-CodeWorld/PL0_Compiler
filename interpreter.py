stack = [0 for i in range(0, 100)]  # 前三个分别为SL DL RA
code = []  # 存放代码


#  根据当前B的值和level层差获取SL的值
def get_sl(B, level):
    res_B = B
    while level > 0:
        res_B = stack[res_B]
        level -= 1
    return res_B


def add_code(f, l, a):
    operation = dict()
    operation["F"] = f
    operation["L"] = l
    operation["A"] = a
    code.append(operation)


def interpreter():
    B = 0  # 基址寄存器
    T = 0  # 栈顶寄存器
    I = None  # 存放要执行的代码
    P = 0  # 下一条指令地址寄存器
    # 开始执行
    I = code[P]
    P += 1
    while P != 0:  # 因为退出程序有一个 OPR 0 0 的，所以看到P要到0就说明退出了
        if I["F"] == "JMP":  # 直接跳转到对应指令
            P = I["A"]
        elif I["F"] == "JPC":
            if stack[T] == 0:  # 栈顶值为0才跳转
                P = I["A"]
            T -= 1  # 无论是否跳转都要去除栈顶的值
        elif I["F"] == "INT":
            T += I["A"] - 1  # 开辟空间
        elif I["F"] == "LOD":
            T += 1
            stack[T] = stack[
                get_sl(B, I["L"]) + I["A"]
            ]  # 到了那层 找到真正基地址 再加addr
        elif I["F"] == "STO":
            if I["L"] == -1:
                stack[T + I["A"]] = stack[T]
                T -= 1
            else:
                stack[get_sl(B, I["L"]) + I["A"]] = stack[T]
                T -= 1
        elif I["F"] == "LIT":
            T += 1
            stack[T] = I["A"]
        elif I["F"] == "CAL":  # 函数调用
            T += 1
            stack[T] = get_sl(B, I["L"])  # 静态链
            stack[T + 1] = B  # 动态链
            stack[T + 2] = P  # 返回地址-当前的下一条地址
            B = T  # 新的基地址
            P = I["A"]  # 跳转到函数地址
        elif I["F"] == "OPR":
            if I["A"] == 0:  # 函数返回
                T = B - 1  # 回到函数调用前的栈顶
                P = stack[B + 2]  # 返回地址
                B = stack[B + 1]  # 动态链
            elif I["A"] == 1:  # 栈顶取反
                stack[T] = -stack[T]
            elif I["A"] == 2:  # 加法
                T -= 1
                stack[T] = stack[T] + stack[T + 1]
            elif I["A"] == 3:  # 减法
                T -= 1
                stack[T] = stack[T] - stack[T + 1]
            elif I["A"] == 4:  # 乘法
                T -= 1
                stack[T] = stack[T] * stack[T + 1]
            elif I["A"] == 5:  # 除法
                T -= 1
                stack[T] = int(stack[T] / stack[T + 1])
            elif I["A"] == 6:  # 奇偶判断，栈顶为偶数则置1，否则置0
                if stack[T] % 2 == 0:
                    stack[T] = 1
                else:
                    stack[T] = 0
            elif I["A"] == 7:  # 相等
                T -= 1
                if stack[T] == stack[T + 1]:
                    stack[T] = 1
                else:
                    stack[T] = 0
            elif I["A"] == 8:  # 不等
                T -= 1
                if stack[T] != stack[T + 1]:
                    stack[T] = 1
                else:
                    stack[T] = 0
            elif I["A"] == 9:  # 小于
                T -= 1
                if stack[T] < stack[T + 1]:
                    stack[T] = 1
                else:
                    stack[T] = 0
            elif I["A"] == 10:  # 大于等于
                T -= 1
                if stack[T] >= stack[T + 1]:
                    stack[T] = 1
                else:
                    stack[T] = 0
            elif I["A"] == 11:  # 大于
                T -= 1
                if stack[T] > stack[T + 1]:
                    stack[T] = 1
                else:
                    stack[T] = 0
            elif I["A"] == 12:  # 小于等于
                T -= 1
                if stack[T] <= stack[T + 1]:
                    stack[T] = 1
                else:
                    stack[T] = 0
        elif I["F"] == "RED":
            T += 1
            stack[T] = int(input("输入："))
        elif I["F"] == "WRT":
            print("输出：", stack[T])
            T -= 1
        # print(P, stack[:T+8], T)
        I = code[P]  # 获取下一条指令
        # print(I)
        if P == 0:  # 因为退出程序有一个 OPR 0 0 的，所以看到P要到0就说明退出了
            break
        P += 1  # 默认P+1获取下一条指令 除非跳转

if __name__ == '__main__':
    origin = []
    with open("pcode.txt", 'r') as f:
        origin = f.readlines()
    for i in range(len(origin)):
        origin[i] = origin[i][:-1]
        x = origin[i].split()
        add_code(x[0], int(x[1]), int(x[2]))
    interpreter()