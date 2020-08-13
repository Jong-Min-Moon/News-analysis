from scipy.sparse import csr_matrix
import numpy as np

a = np.array([[0,0,1,1/2],[1/3,0,0,0],[1/3,1/2,0,1/2],[1/3,1/2,0,0]])
A = csr_matrix(a)

df=0.85
R = np.ones(A.shape[0]).reshape(-1,1)

#method 1
bias = (1 - df) * np.ones(A.shape[0]).reshape(-1,1)

for _ in range(20):
    R = df * (A * R) + bias
    
print('method 1:',R)

#method 2
M = df * A +  (1-df)* (1 / (A.shape[0]))*np.ones(A.shape)

R = (1 / (A.shape[0])) * np.ones(A.shape[0]).reshape(-1,1)
for _ in range(20):
    R = M * R
print('method 2:', R, sum(R))