from pymunk.vec2d import Vec2d
import math, numpy
from importlib import __import__


class SDF:
    def __init__(self, file_name: str):
        with open(file_name, 'r') as file:
            self.script = file.read()

        self.functions = {
            'add': lambda x, y: x + y,
            'sub': lambda x, y: x - y,
            'mul': lambda x, y: x * y,
            'div': lambda x, y: x / y,
            'pow': pow,
            'round': round,
            'abs': abs,
            'math': math,
            'numpy': numpy,
            'complex': complex
        }

    def interpret(self, P: Vec2d, T: float = 0):
        lines = self.script.split('\n')
        if len(lines) == 0:
            print('No Code in the script...')
            return

        scope = {}

        if lines[0][0] == '>':
            imports = lines[0][1:].strip().split(',')
            for request in imports:
                if 'P' == request:
                    scope['P'] = P
                elif 'T' == request:
                    scope['T'] = T

        for i, line in enumerate(lines[1:-1]):
            print(i+1, line)

        if lines[-1][0] == '<':
            return self.evaluate(lines[-1][1:], scope)
        else:
            print('Last line does not return anything')

    def evaluate(self, line: str, scope):

        line = line.strip()
        opening_brace = line.find('(')
        closing_brace = len(line) - line[-1].find(')') if ')' in line else -1

        if opening_brace != -1 and closing_brace == -1:
            print('Missing closing braces')
            return None
        elif opening_brace == closing_brace == -1:
            if line.isnumeric():
                return float(line) if '.' in line else int(line)
            elif line.split('.')[0] in scope:
                return eval(line, scope)

        function_name = line[:opening_brace]

        parameters = [self.evaluate(parameter, scope) for parameter in
                      line[opening_brace + 1:closing_brace - 1].split(',')]

        if function_name in self.functions:
            return self.functions[function_name](*parameters)
        elif '.' in function_name:
            module, method = function_name.split('.')
            method_to_call = getattr(globals()[module], method)
            return method_to_call(*parameters)
        else:
            print(f'Function not defined: {function_name}')
