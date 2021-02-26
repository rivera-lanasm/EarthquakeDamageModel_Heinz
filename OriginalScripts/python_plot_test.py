import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import math

Bslight = 0.64
MedianSlight = 0.12
Bmoderate = 0.64
MedianModerate = 0.15
Bextensive = 0.64
MedianExtensive = 0.22
Bcomplete = 0.64
MedianComplete = 0.41

# x is array between 0 and 4 at step 0.1
x=np.linspace(.01, 3, 300)

slight_x = []
for i in x:
    print(i)
    p = (1/Bslight)*math.log(i/MedianSlight)
    slight_x.append(p)


moderate_x = []
for i in x:
    print(i)
    p = (1/Bmoderate)*math.log(i/MedianModerate)
    moderate_x.append(p)

extensive_x = []
for i in x:
    print(i)
    p = (1/Bextensive)*math.log(i/MedianExtensive)
    extensive_x.append(p)

complete_x = []
for i in x:
    print(i)
    p = (1/Bcomplete)*math.log(i/MedianComplete)
    complete_x.append(p)


y_cdf_slight = ss.norm.cdf(slight_x) # the normal cdf
y_cdf_moderate = ss.norm.cdf(moderate_x) # the normal cdf
y_cdf_extensive = ss.norm.cdf(extensive_x) # the normal cdf
y_cdf_complete = ss.norm.cdf(complete_x) # the normal cdf
#y_cdf = ss.norm.cdf((1/Bslight)*math.log(x/MedianSlight))

plt.gca().set_color_cycle(['blue', 'green','yellow','red'])
plt.plot(x, y_cdf_slight, label='Slight')
plt.plot(x, y_cdf_moderate, label='Moderate')
plt.plot(x, y_cdf_extensive, label='Extensive')
plt.plot(x, y_cdf_complete, label='Complete')

plt.ylim(0, 1.0)
plt.xlim(0, 3.0)
plt.legend(loc=4)
plt.title("RM2L - PC")
plt.show()