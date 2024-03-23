import dis


def decompile(bytecode: dis.Bytecode):
    stack_names = []  # names of variables and functions used

    indents = []

    def ind_print(*args, **kwargs):
        print('\t' * len(indents), end='')
        print(*args, **kwargs)

    for instr in bytecode:
        indents.sort(reverse=True)  # not cool for large number of elems, but I'm sure noone has more than 6-7 indents
        while len(indents) != 0 and instr.offset >= indents[-1]:
            indents.pop()
        match instr.opname:
            case 'RESUME':
                continue
            case 'NOP':
                continue
            case 'PRECALL':
                continue
            case 'RETURN_VALUE':
                ind_print('return', stack_names.pop())
            case 'POP_TOP':
                ind_print(stack_names.pop())

            case 'LOAD_CONST':
                stack_names.append(instr.argrepr)
            case 'STORE_FAST':
                ind_print(f'{instr.argval} = {stack_names.pop()}')
            case 'LOAD_FAST':
                stack_names.append(instr.argval)
            case 'LOAD_GLOBAL':
                stack_names.append(instr.argval)
            case 'LOAD_METHOD':
                stack_names.append(f'{stack_names.pop()}.{instr.argval}')
            case 'CALL':
                args = [stack_names.pop() for _ in range(instr.argval)]
                func = stack_names.pop()
                stack_names.append(f'{func}({", ".join(map(str, args))})')
            case 'GET_ITER':
                # stack.append(iter(stack.pop()))
                stack_names.append(f'iter({stack_names.pop()})')
            case 'FOR_ITER':
                ind_print(f'for i in {stack_names.pop()}:')
                indents.append(instr.argval)
                stack_names.append('i')
            case 'JUMP_BACKWARD':
                ...
            case 'JUMP_FORWARD':
                ...
                print('\t' * (len(indents) - 1) + 'else:')  # TODO this is a workaround
                indents.append(instr.argval)
            case 'BINARY_OP':
                sn = stack_names.pop()  # for some reason operands are reversed
                fn = stack_names.pop()
                match instr.argrepr:
                    case '+':
                        stack_names.append(f'{fn} + {sn}')
                    case '-':
                        stack_names.append(f'{fn} - {sn}')
                    case '*':
                        stack_names.append(f'{fn} * {sn}')
                    case '/':
                        stack_names.append(f'{fn} / {sn}')
                    case '%':
                        stack_names.append(f'{fn} % {sn}')
                    case _:
                        raise ValueError(f'Unknown binary operation: {instr.argrepr}')

            case 'COMPARE_OP':
                sn = stack_names.pop()  # for some reason operands are reversed
                fn = stack_names.pop()
                match instr.argrepr:
                    case '==':
                        stack_names.append(f'{fn} == {sn}')
                    case '!=':
                        stack_names.append(f'{fn} != {sn}')
                    case '<':
                        stack_names.append(f'{fn} < {sn}')
                    case '>':
                        stack_names.append(f'{fn} > {sn}')
                    case '<=':
                        stack_names.append(f'{fn} <= {sn}')
                    case '>=':
                        stack_names.append(f'{fn} >= {sn}')
                    case _:
                        raise ValueError(f'Unknown compare operation: {instr.argrepr}')
            case 'POP_JUMP_FORWARD_IF_FALSE':
                # if not stack.pop():
                #     instr_i = instr.argval // 2
                ind_print(f'if {stack_names.pop()}:')
                indents.append(instr.argval)
            case 'POP_JUMP_FORWARD_IF_TRUE':
                # if stack.pop():
                #     instr_i = instr.argval // 2
                ind_print(f'if not {stack_names.pop()}:')
                indents.append(instr.argval)
            case _:
                raise ValueError(f'Unknown opname: {instr.opname}')
        # print(instr.opname, repr(instr.argval))


if __name__ == '__main__':
    from sample import main as sample

    dis.dis(sample)
    print()

    decompile(dis.Bytecode(sample))
