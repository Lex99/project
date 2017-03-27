import numpy as np

# sigmoid functie
def sigmoid(x):
    return 1/(1+np.exp(-x))

# misfit functie
def misfit(p):
    yt = sigmoid(np.dot(X,p[:-1]) + p[-1])
    residual = yt - y
    return np.dot(residual,residual)

# gradient
def gradient(p):
	s = np.dot(X,p[:-1]) + p[-1]
	yt = sigmoid(s)
	g = np.zeros(len(p))
	g[:-1] = 2*np.dot(np.transpose(X)*sigmoid(s)*(1 - sigmoid(s))*(yt - y),np.ones(len(yt)))
	g[-1]  = 2*np.dot(sigmoid(s)*(1 - sigmoid(s))*(yt - y),np.ones(len(yt)))
	return g
	
# invoer voor OF operatie
X = np.array([  [0,0],
                [0,1],
                [1,0],
                [1,1]])
    
# uitvoer        
y = np.array([0,1,1,1])

# beginschatting voor de gewichten
p = np.array([1,1,1])

# doe aan aantal iteraties
alpha = 1e1 # stapgrootte, kies deze zodat f steeds kleiner wordt
for iter in range(200):
	f = misfit(p)
	g = gradient(p)
	p = p - alpha*g
	
	# print
	print(iter,f,np.dot(g,g))

print('Weights               : ', p)
print('Training data         : ', y)
print('Output After Training : ', sigmoid(np.dot(X,p[:-1]) + p[-1]))