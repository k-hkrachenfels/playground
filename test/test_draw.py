from lib2to3.pgen2.token import TILDE
from PIL import Image
import numpy as np

SIZE_X = 172
SIZE_Y = 174
N_TILES_X = 8
N_TILES_Y = 8
TILES = ['tiles/h.png','tiles/v.png','tiles/lu.png','tiles/ru.png','tiles/rl.png','tiles/ll.png']
img = Image.new(mode='RGB', size=(N_TILES_X*SIZE_X, N_TILES_Y*SIZE_Y))
for tile_x in range(N_TILES_X):
    pos_x = SIZE_X*tile_x
    for tile_y in range(N_TILES_Y):
        pos_y = SIZE_Y*tile_y
        pos=(pos_x,pos_y)
        tile = Image.open(np.random.choice(TILES,1)[0])
        img.paste(tile,pos)
img.save('output/out.png')


