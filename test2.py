import numpy as np 

a = np.array(list(range(11)))

n_chunk = 3
chunk_size = round(len(a)/3)

for i in range(n_chunk):
    print(a[i * chunk_size: i*chunk_size + chunk_size])