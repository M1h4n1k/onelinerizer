import dis


def decompile(bytecode: dis.Bytecode):
    stack_names = []  # names of variables and functions used

    indents = []

    def ind_print(*args, **kwargs):
        print('\t' * len(indents), end='')
        print(*args, **kwargs)

    instr_i = 0
    instructions = list(bytecode)

    while instr_i < len(instructions):
        instr = instructions[instr_i]
        instr_i += 1

        indents.sort(reverse=True)  # not cool for large number of elems, but I'm sure noone has more than 6-7 indents
        while len(indents) != 0 and instr.offset >= indents[-1]:
            indents.pop()
        match instr.opname:
            case 'RESUME': continue
            case 'NOP': continue
            case 'PRECALL': continue
            case 'BUILD_LIST': stack_names.append(list())
            case 'BUILD_TUPLE': stack_names.append(tuple())
            case 'BUILD_CONST_KEY_MAP':
                keys = stack_names.pop()
                values = [stack_names.pop() for _ in range(len(keys))][::-1]
                stack_names.append(
                    '{\n' + ',\n'.join(f'\t{k}: {v}' for k, v in zip(keys, values)) + '\n}'
                )

            case 'IMPORT_NAME':
                ind_print(f'import {instr.argval}')
                instr_i += 1

            case 'LIST_EXTEND':
                seq = stack_names.pop()
                list.extend(stack_names[-instr.argval], seq)
            case 'BINARY_SUBSCR':
                ind = stack_names.pop()
                stack_names.append(f'{stack_names.pop()}[{ind}]')

            case 'RETURN_VALUE':
                ind_print('return', stack_names.pop())
            case 'POP_TOP':
                ind_print(stack_names.pop())

            case 'LOAD_CONST':
                if type(instr.argval) in (list, tuple):
                    stack_names.append(instr.argval)
                else:
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
                args = [stack_names.pop() for _ in range(instr.argval)][::-1]
                func = stack_names.pop()
                stack_names.append(f'{func}({", ".join(map(str, args))})')
            case 'GET_ITER':
                # stack.append(iter(stack.pop()))
                stack_names.append(f'iter({stack_names.pop()})')
            case 'FOR_ITER':
                next_instr = instructions[instr_i]
                instr_i += 1
                if next_instr.opname == 'UNPACK_SEQUENCE':
                    iter_name = []
                    for _ in range(next_instr.argval):
                        next_instr = instructions[instr_i]
                        instr_i += 1
                        iter_name.append(next_instr.argval)
                    iter_name = ', '.join(iter_name)
                else:
                    iter_name = next_instr.argval
                ind_print(f'for {iter_name} in {stack_names.pop()}:')
                indents.append(instr.argval)
            case 'JUMP_BACKWARD':
                ...
            case 'JUMP_FORWARD':
                ...
                print('\t' * (len(indents) - 1) + 'else:')  # TODO this is a workaround
                indents.append(instr.argval)
            case 'BINARY_OP':
                sn = stack_names.pop()  # for some reason operands are reversed
                fn = stack_names.pop()
                match instr.argrepr.replace('=', ''):
                    case '+':
                        stack_names.append(f'({fn} + {sn})')
                    case '-':
                        stack_names.append(f'({fn} - {sn})')
                    case '*':
                        stack_names.append(f'({fn} * {sn})')
                    case '/':
                        stack_names.append(f'({fn} / {sn})')
                    case '%':
                        stack_names.append(f'({fn} % {sn})')
                    case '//':
                        stack_names.append(f'({fn} // {sn})')
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
