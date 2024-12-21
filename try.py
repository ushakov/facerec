# %%
import io
import numpy as np
from PIL import Image
import rawpy
import time
import matplotlib.pyplot as plt
# %%
path = '/home/ushakov/photo/master/2024-09-15-london/DSC02759.ARW'
start = time.time()
with rawpy.imread(path) as raw:
    raw: rawpy.RawPy = raw
    print(raw.sizes)
    proctime = time.time()
    rgb = raw.extract_thumb()
end = time.time()
print(f'Loading time: {proctime - start}')
print(f'Processing time: {end - proctime}')
# %%
len(rgb.data)

# %%
print('aaa')
# %%


image = Image.open(io.BytesIO(rgb.data))
image = np.array(image)

# %%
image.shape
# %%
plt.imshow(image)