import math

from pymunk.vec2d import Vec2d
import numpy as np
from script import Script, RootScript
from PIL import Image
from tqdm import tqdm


class SDF:
    def __init__(self, file_name: str):
        with open(file_name, 'r') as file:
            self.script = RootScript(file.read().strip().replace(' ', '').split('\n'))

        # print(self.script.interpret(Vec2d(1, 1)))

    def evaluate(self, domain: [[-1, 1], [-1, 1]], resolution: (100, 100)):
        domain = np.array(domain)
        assert domain.shape == (2, 2) and len(resolution) == 2

        image = Image.new('RGB', resolution)

        for i, x in enumerate(tqdm(np.linspace(domain[0][0], domain[0][1], resolution[0]))):
            for j, y in enumerate(tqdm(np.linspace(domain[1][0], domain[1][1], resolution[1]))):
                P = Vec2d(x, y)

                value = self.script.interpret(P, 0)

                f = lambda x: 1 / (1 + math.exp(-4 * x)) - 0.5

                proximity = 0.01
                color = (
                    f(max(value, 0)) * 255,
                    4 * (tmp := math.exp(-value / proximity)) / (1 + tmp) ** 2 * 255,
                    f(abs(min(value, 0))) * 255
                )
                color = tuple(round(channel) for channel in color)

                image.putpixel((i, j), color)


        return image
