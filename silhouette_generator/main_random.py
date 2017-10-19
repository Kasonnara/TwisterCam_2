import generation_lib as sgen

FILLED=False
COLOR = [0, 0, 0, 1]


def generate_random(color=[1, 1, 1, 1], filled=False):
    import random
    for k in range(20):
        print("Génération d'une image")
        aeg = random.randint(0, 360)
        aed = random.randint(0, 360)
        abg = random.randint(0, 360)
        abd = random.randint(0, 360)
        sgen.pregen(aeg, aed, abg, abd, color=color, filled=filled)


if __name__ == '__main__':
    generate_random(color=COLOR, filled=FILLED)

