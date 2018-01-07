"""
Information:


"""
import pandas as pd
import numpy as np
import random
import math


class mlp:
	def __init__(self):
		self.wHidden = np.array([])
		self.wOutput = np.array([])
		self.outputLayerSize = 0
		self.hiddenLayerSize = 0
		self.inputLayerSize = 0
		self.hiddenLayerOutput = None
		self.predictOutput = None
		self.hiddenNet = np.array([])
		self.outputNet = np.array([])

	"""
	"""
	def _sigmoid(self, x, Lambda = 1.0):
		return 1.0/(1.0 + math.e**(-Lambda * x))

	def _d_sigmoid(self, x, Lambda = 1.0):
		sigRes = self._sigmoid(x, Lambda) 
		return sigRes * (1.0 - sigRes)

	"""
	Backward/backpropagation step
	"""
	def _adjustWeights(self, x, y, stepSize, Lambda = 1.0):
		predict = self.predict(x)
		error = y - predict

		delta_o = []
		for k in range(self.outputLayerSize):
			delta_o.append(error * self._d_sigmoid(self.outputNet[k], Lambda))

		delta_h = []
		for j in range(self.hiddenLayerSize):
			aux = np.sum([delta_o[k] * self.wOutput[k,j] for k in range(self.outputLayerSize)])
			delta_h.append(self._d_sigmoid(self.hiddenNet[j], Lambda) * aux)

		for k in range(self.outputLayerSize):
			self.wOutput[k] += stepSize * delta_o[k] * np.concatenate((self.hiddenLayerOutput, [1.0]))
		
		for j in range(self.hiddenLayerSize):
			self.wHidden[j] += stepSize * delta_h[j] * np.concatenate((x, [1.0]))

		return np.sum(np.power(error, 2.0))

	"""
	Foward step
	"""
	def predict(self, query, Lambda = 1.0):
		self.hiddenNet = np.array([np.sum(j * np.concatenate((query, [1.0]))) for j in self.wHidden])
		self.hiddenLayerOutput = np.array([self._sigmoid(i, Lambda) for i in self.hiddenNet])

		self.outputNet = np.array([np.sum(j * np.concatenate((self.hiddenLayerOutput, [1.0]))) for j in self.wOutput])
		self.predictOutput = np.array([self._sigmoid(j, Lambda) for j in self.outputNet])

		return self.predictOutput

	"""
	"""
	def _initWeights(self):
		self.wHidden = np.array([[random.random() - 0.5 
			for __ in range(self.inputLayerSize + 1)] for _ in range(self.hiddenLayerSize)])
		self.wOutput = np.array([[random.random() - 0.5 
			for __ in range(self.hiddenLayerSize + 1)] for _ in range(self.outputLayerSize)])
	
	"""
	"""
	def fit(self, x, y, hiddenLayerSize = 2, showError = False, stepSize = 0.2, maxError = 1.0e-2, maxIteration = 20000, Lambda = 1.0):
		n = x.shape[0]
		self.inputLayerSize = x.shape[1]
		self.hiddenLayerSize = hiddenLayerSize
		self.outputLayerSize = y.shape[1]

		self._initWeights()

		meanSqrError = maxError * 2.0
		curIteration = 0
		while meanSqrError > maxError and curIteration < maxIteration:
			curIteration += 1
			meanSqrError = 0.0

			for i in range(n):
				meanSqrError += self._adjustWeights(x[i], y[i], stepSize, Lambda)
			meanSqrError /= n

			if (showError):
				print('I:','{value:<{fill}}'.format(value = curIteration, fill = 15), 'MSE:', meanSqrError)
			if (curIteration == maxIteration):
				print('Warning: reached max iteration number (' + str(maxIteration) + ').')


# Program driver
if __name__ == '__main__':
	mlp = mlp()

	"""	dataset = pd.read_csv('./dataset/XOR.dat', sep = ' ')
	mlp.fit(x = dataset.iloc[:, :2].values, y = dataset.iloc[:, 2:].values)
	
	XORQueries = np.array([
			[1, 0],
			[0, 0],
			[0, 1],
			[1, 1],
		])

	for q in XORQueries:
		print('query:', q, 'result:', mlp.predict(q))
	"""

	dataset = pd.read_csv('./dataset/wine.data', sep = ',', header = 0, names = ['Class'] + ['X' + str(i) for i in range(13)])

	x = dataset.iloc[:, 1:]
	scaledDataset = (x - x.mean())/x.std()

	mlp.fit(x = scaledDataset.values, y = pd.get_dummies(dataset['Class']).values, showError = True)
	
	wineQuery = [13.24,2.59,2.87,21,118,2.8,2.69,.39,1.82,4.32,1.04,2.93,735]

	print('query:', wineQuery, 'result:', mlp.predict(wineQuery))



