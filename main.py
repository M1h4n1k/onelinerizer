import dis
from dataclasses import dataclass


@dataclass
class Indent:
    line_to: int
    ending: str



def linerize(bytecode: dis.Bytecode):
    stack_names = []  # names of variables and functions used

    start = '(lambda: ['
    end = '][-1])()'

    instr_i = 0
    instructions = list(bytecode)

    indents: list[Indent] = []

    while instr_i < len(instructions):
        instr = instructions[instr_i]
        instr_i += 1

        # indents.sort(reverse=True, key=lambda x: x.line_to)  # not cool for large number of elems, but I'm sure noone has more than 6-7 indents
        while len(indents) != 0 and instr.offset >= indents[-1].line_to:
            end = indents.pop().ending + end

        match instr.opname:
            case 'RESUME': continue
            case 'NOP': continue
            case 'PRECALL': continue
            case 'BUILD_LIST': stack_names.append(list())
            case 'BUILD_TUPLE': stack_names.append(tuple())
            case 'RETURN_VALUE':
                start += str(stack_names.pop()) + ', '  # + indents.pop().ending  # + '][-1], ['  # edit
                # print(stack_names.pop(), end=',\n')
                # print('return', stack_names.pop())
            case 'POP_TOP':
                start += stack_names.pop() + ', '
                # print(stack_names.pop(), end=',\n')

            case 'BUILD_CONST_KEY_MAP':
                keys = stack_names.pop()
                values = [stack_names.pop() for _ in range(len(keys))][::-1]
                stack_names.append(
                    '{' + ','.join(f'{k}: {v}' for k, v in zip(keys, values)) + '}'
                )

            case 'IMPORT_NAME':
                stack_names.append(f'__import__("{instr.argval}")')

            case 'LIST_EXTEND':
                seq = stack_names.pop()
                list.extend(stack_names[-instr.argval], seq)
            case 'BINARY_SUBSCR':
                ind = stack_names.pop()
                stack_names.append(f'{stack_names.pop()}[{ind}]')

            case 'LOAD_CONST':
                if type(instr.argval) in (list, tuple):
                    stack_names.append(instr.argval)
                else:
                    stack_names.append(instr.argrepr)
            case 'STORE_FAST':
                start = start + f'(lambda {instr.argval}: ['
                end = f'][-1])({stack_names.pop()})' + end
                # print(f'{instr.argval} = {stack_names.pop()}')
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
            case 'FOR_ITER':  # fixme doesnt take indentation into account
                next_instr = instructions[instr_i]
                instr_i += 1
                start += '[['
                if next_instr.opname == 'UNPACK_SEQUENCE':
                    iter_name = []
                    for _ in range(next_instr.argval):
                        next_instr = instructions[instr_i]
                        instr_i += 1
                        iter_name.append(next_instr.argval)
                    iter_name = ', '.join(iter_name)
                else:
                    iter_name = next_instr.argval
                # print(f'for {iter_name} in {stack_names.pop()}:')
                end = f'][-1] for {iter_name} in {stack_names.pop()}][-1]' + end
                # indents.append(Indent(instr.argval, f'][-1] for {iter_name} in {stack_names.pop()}][-1]'))
                # indents.append(Indent(instr.argval, f''))
                # try:
                #     # stack.append(next(stack[-1]))
                #     stack_names.append(f'next({stack_names[-1]})')
                # except StopIteration:
                #     stack.pop()
                    # instr_i = instr.argval // 2
            case 'JUMP_BACKWARD':
                ...
                # instr_i = instr.argval // 2
            case 'JUMP_FORWARD':
                ...
                # print('\t' * (len(indents) - 1) + 'else:')  # TODO this is a workaround
                start += '][-1]), False: (lambda: ['
                indents.append(Indent(instr.argval, ''))
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
                # I can probably use ternary operators, but in that case I'll have to deal
                # with inserting the if-statement into the middle
                start += '{True: (lambda: ['
                # end = f'][-1])}}.get({stack_names.pop()}, lambda: None)()' + end
                indents.append(Indent(instr.argval, f'][-1])}}.get({stack_names.pop()}, lambda: None)()'))
            case 'POP_JUMP_FORWARD_IF_TRUE':
                start += '{True: (lambda: ['
                # end = f'][-1])}}.get(not {stack_names.pop()}, lambda: None)()' + end
                indents.append(Indent(instr.argval, f'][-1])}}.get(not {stack_names.pop()}, lambda: None)()'))
            case _:
                raise ValueError(f'Unknown opname: {instr.opname}')
        # print(instr.opname, repr(instr.argval))

    print(start + end)


if __name__ == '__main__':
    from sample import main as sample

    dis.dis(sample)
    print()

    linerize(dis.Bytecode(sample))
