class fake_list(list):
    def __init__(self, *args):
        super(fake_list, self).__init__(args)

    def get(self, i):
        return self[i]


if __name__ == '__main__':
    fl = fake_list(1, 2, 3)
