from SDF import SDF
from pymunk.vec2d import Vec2d
from PIL import Image

def main():
    sdf = SDF('test.sdf')

    sdf.evaluate([[-1, 1], [-1, 1]], [25, 25]).resize((1000, 1000),  Image.NEAREST).show()


if __name__ == '__main__':
    main()
