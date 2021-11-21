from colorama import Style, Fore
import math, numpy
from pymunk.vec2d import Vec2d
import re
from fake_list import fake_list


class Script:
    def __init__(self, lines: list[str], in_debug: bool = False):
        self.in_debug = in_debug

        self.keywords = {
            'for': ForLoop,
            'while': WhileLoop,
            'if': ifStatement
        }

        self.importables = {
            'math': math,
            'numpy': numpy,
            'complex': complex,
            'Vec2d': Vec2d,
            'List': fake_list
        }

        self.functions = {
            'add': lambda x, y: x + y,
            'sub': lambda x, y: x - y,
            'mul': lambda x, y: x * y,
            'div': lambda x, y: x / y,
            'pow': pow,
            'round': round,
            'abs': abs,
            'len': len
        }

        self.lines = []
        n = 0
        while n < len(lines):
            line, i = lines[n]
            if '#' in line:
                n += 1
                continue
            if '[' in line:
                keyword = line[:line.find('[')]
                if keyword not in self.keywords:
                    self.error(i, f'{keyword} is not a legal keyword.')

                key = self.keywords[keyword]

                parameter_tuple = line[line.find('[') + 1: line.find(']')].split(':')

                key_lines = []

                k = n + 2
                while k < len(lines):
                    loop_line, j = lines[k]
                    if loop_line == '}':
                        break
                    key_lines.append(lines[k])
                    k += 1
                n = k + 1

                self.lines.append((key(parameter_tuple, key_lines, self.in_debug), i))
            else:
                self.lines.append(lines[n])
            n += 1

    def warn(self, line, message: str):
        print(f'{Fore.YELLOW}Warning: {message}\n\t{line[1]}: {line[0]}{Style.RESET_ALL}')

    def error(self, line, message: str):
        print(f'{Fore.RED}Error:   {message}\n\t{line[1]}: {line[0]}{Style.RESET_ALL}')
        quit()

    def print(self, line, message: str):
        print(f'Print:   {message}\n\t{line[1]}: {line[0]}')

    def debug(self, line, message: str):
        if self.in_debug:
            print(f'{Fore.BLUE}Debug:   {message}\n\t{line[1]}: {line[0]}{Style.RESET_ALL}')

    def interpret(self, scopes):
        scopes.append({})
        for line in self.lines:
            if isinstance(line[0], Script):
                scopes = line[0].interpret(scopes)
            elif not '#' in line[0]:
                scopes = self.execute(line, scopes)
            self.debug(line, scopes)
        return scopes[:-1]

    def execute(self, line, scopes):
        if line == '':
            return scopes
        # check if line is variable assignment
        if '=' in line[0]:
            parts = line[0].split('=')

            variable = parts[0]

            scope = self.combine_scopes(scopes)
            value = self.evaluate(parts[1], scope)

            for scope in scopes:
                if variable in scope:
                    scope[variable] = value
                    break
            else:
                scopes[-1][variable] = value

        return scopes

    def combine_scopes(self, scopes):
        single_scope = {}
        for scope in scopes:
            for variable_name in scope:
                single_scope[variable_name] = scope[variable_name]

        return single_scope

    def evaluate(self, expression, scope):
        print(f'{expression=}')
        print(expression.split('.'))

        opening_brace = expression.find('(')
        closing_brace = len(expression) - expression[-1].find(')') if ')' in expression else -1

        if opening_brace == closing_brace == -1:
            if re.fullmatch(r'[-+]?\d+(\.\d+)?', expression):
                return eval(expression)
            elif expression.split('.')[0] in scope:
                return eval(expression, scope)

        function_name = expression[:opening_brace]

        parameters = ['']
        depth = 0
        for char in expression[opening_brace + 1: closing_brace - 1]:
            if depth == 0 and char == ',':
                parameters.append('')
                continue

            parameters[-1] += char
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    parameters.append('')

        for _ in range(parameters.count('')):
            parameters.remove('')

        parameters = [self.evaluate(parameter, scope) for parameter in parameters]
        print(f'{parameters=}')

        if function_name in self.functions:
            return self.functions[function_name](*parameters)
        elif '.' in function_name:
            module, method = function_name.split('.')
            method_to_call = getattr(scope[module], method)
            return method_to_call(*parameters)
        elif function_name in scope:
            return scope[function_name](*parameters)
        else:
            self.error((expression, -1), f'Function not defined: {function_name}')


class WhileLoop(Script):
    def __init__(self, parameter, lines, in_debug: bool = False):
        self.parameter = parameter
        super(WhileLoop, self).__init__(lines, in_debug)

    def interpret(self, scopes):
        broken = False

        scope = self.combine_scopes(scopes)

        while eval(self.parameter[0], scope) and not broken:
            for line in self.lines:
                if line[0] == 'break':
                    broken = True
                    break
                elif line[0] == 'continue':
                    break
                elif isinstance(line[0], Script):
                    scopes = line[0].interpret(scopes)
                elif not '#' in line[0]:
                    scopes = self.execute(line, scopes)
                self.debug(line, scopes)
        return scopes


class ForLoop(Script):
    def __init__(self, parameter, lines, in_debug: bool = False):
        self.parameter = parameter
        super(ForLoop, self).__init__(lines, in_debug)

    def interpret(self, scopes):
        broken = False

        scopes = self.execute((self.parameter[0], 'for loop parameters'), scopes + [{}])

        scope = self.combine_scopes(scopes)

        while eval(self.parameter[1], scope) and not broken:
            for line in self.lines:
                if line[0] == 'break':
                    broken = True
                    break
                elif line[0] == 'continue':
                    break
                elif isinstance(line[0], Script):
                    scopes = line[0].interpret(scopes)
                elif '#' not in line[0]:
                    scopes = self.execute(line, scopes)
                self.debug(line, scopes)
            if not broken:
                scopes = self.execute((self.parameter[2], 'for loop parameters'), scopes)
            scope = self.combine_scopes(scopes)


        return scopes[:-1]


class ifStatement(Script):
    def __init__(self, parameter, lines, in_debug: bool = False):
        self.parameter = parameter
        super(ifStatement, self).__init__(lines, in_debug)

    def interpret(self, scopes):
        scopes.append({})

        scope = self.combine_scopes(scopes)

        if eval(self.parameter[0], scope):
            for line in self.lines:
                if line[0] == 'break':
                    break
                elif isinstance(line[0], Script):
                    scopes = line[0].interpret(scopes)
                elif not '#' in line[0]:
                    scopes = self.execute(line, scopes)
                self.debug(line, scopes)
        return scopes[:-1]


class RootScript(Script):
    def __init__(self, lines: list[str], in_debug: bool = False):

        lines = [(line, i + 1) for i, line in enumerate(lines)]  # numbering lines

        # checking for empty scripts
        if len(lines) == 0 or lines == ['']:
            self.error(('', -1), 'Empty script.')

        # extracting imports
        if lines[0][0][0] == '>':
            self.imports = lines[0][0][1:].split(',')
            lines.pop(0)
        else:
            self.warn(lines[0], 'No imports...')

        # extracting exports
        if lines[-1][0][0] == '<':
            self.export = lines[-1][0][1:]
            lines.pop(-1)
        else:
            self.error(lines[-1], 'No exports. SDF can not be evaluated if you do not export anything.')

        # parsing rest of script
        super(RootScript, self).__init__(lines, in_debug)

    def interpret(self, P: Vec2d = None, T: float = None):
        scopes = [{}]
        for importable in self.imports:
            if importable == 'P':
                scopes[0]['P'] = P
            elif importable == 'T':
                scopes[0]['T'] = T
            elif importable in self.importables:
                scopes[0][importable] = self.importables[importable]
            else:
                self.error(self.lines[0], f'Failed to import {importable}')
        for line in self.lines:
            if isinstance(line[0], Script):
                scopes = line[0].interpret(scopes)
            elif not '#' in line[0]:
                scopes = self.execute(line, scopes)
            self.debug(line, scopes)

        results = self.execute((f'__result__={self.export}', -1), scopes)
        return results[0]['__result__']
