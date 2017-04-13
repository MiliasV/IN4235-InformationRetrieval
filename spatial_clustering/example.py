import numpy as np
import pysal
np.random.seed(100)
w=pysal.weights.lat2W(5,5)
z=np.random.random_sample((w.n,2))
p=np.ones((w.n,1),float)
floor=3
solution=pysal.region.Maxp(w,z,floor,floor_variable=p,initial=100)
print("lol")
