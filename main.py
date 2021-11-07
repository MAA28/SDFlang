from SDF import SDF
from pymunk.vec2d import Vec2d


def main():
    sdf = SDF('test.sdf')

    print(sdf.interpret(Vec2d(1, 0)))


if __name__ == '__main__':
    main()
