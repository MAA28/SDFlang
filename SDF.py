from pymunk.vec2d import Vec2d
import math, numpy
from script import Script, RootScript


class SDF:
    def __init__(self, file_name: str):
        with open(file_name, 'r') as file:
            self.script = RootScript(file.read().strip().replace(' ', '').split('\n'))

        print(self.script.interpret(Vec2d(0,0)))
