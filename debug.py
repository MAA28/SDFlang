from script import RootScript
from pymunk.vec2d import Vec2d

class Debug:
    def __init__(self, file_name: str):
        with open(file_name, 'r') as file:
            self.script = RootScript(file.read().strip().replace(' ', '').split('\n'), in_debug=True)

    def evaluate(self, P: Vec2d):
        print(self.script.interpret(P, 0))

if __name__ == '__main__':
    debug = Debug('test.sdf')
    debug.evaluate(Vec2d(0,0))