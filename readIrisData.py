import csv
import numpy as np

m = 150
label = {"Iris-setosa" : 1, "Iris-versicolor" : 2, "Iris-virginica" : 3}
X = np.zeros((150,4))
y = np.zeros(m)

with open('Iris.csv', newline='') as csvfile:
	     reader = csv.reader(csvfile, delimiter=',')
	     # skip headers
	     print(next(reader, None))
	     # loop over rows
	     for row in reader:
	     	# index
	     	k = int(row[0])-1
	     	# features
	     	X[k,:] = row[1:5]
	     	# labels
	     	y[k] = label[row[5]]
	     	
# Now, X contains 150 input samples with 4 features each and y contains 150 labels (1, 2, 3)