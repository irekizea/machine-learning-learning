# Helpful video: (in Portuguese)
# title: "Vídeo 48 - Planejamento de Experimentos: Agrupamento de Dados"
# canal: ML4U
# https://www.youtube.com/watch?v=OLwabj1WJj0

from numpy import array, random, argmin, mean as npmean, where, inf
from pandas import DataFrame, read_csv

class Kmeans():
	def __euclideandist__(inst_a, inst_b):
		return (sum((inst_a - inst_b)**2.0))**0.5

	def sse(dataset, centers_coord, inst_cluster_id):
		# SEE : Sum of Squared Errors
		# It measures Cluster's Cohesion quality
		# It is a INNER CRITERION for unsupervised quality metrics

		center_num = len(centers_coord)

		sse_value = 0.0
		for center_id in range(center_num):
			this_cluster_insts = where(inst_cluster_id == center_id)[0]
			cluster_mean = npmean(dataset[this_cluster_insts,:], axis=0)
			sse_value += max(sum((dataset[this_cluster_insts,:] \
				- cluster_mean)**2.0))

		return sse_value

	def bss(dataset, centers_coord, inst_cluster_id):
		# BSS : Between Sum of Squares
		# It measures Separation between clusters
		# It is a INNER CRITERION for unsupervised quality metrics

		center_num = len(centers_coord)

		dataset_mean = dataset.mean(axis=0)

		bss_value = 0.0
		for center_id in range(center_num):
			this_cluster_insts = where(inst_cluster_id == center_id)[0]
			cluster_mean = npmean(dataset[this_cluster_insts,:], axis=0)
			sqr_coord_diffs = (dataset_mean - cluster_mean)**2.0
			bss_value += len(this_cluster_insts) * max(sqr_coord_diffs)

		return bss_value

	def silhouette(dataset, centers_coord, inst_cluster_id):
		# Silhouette is a way of summarize the BSS and SSE
		# metrics into a single measure value. So, obvious enough,
		# it is also a INNER CRITERION for unsupervised quality metrics.
		inst_num = dataset.shape[0]
		inst_sil = array([0.0] * inst_num)
		center_num = len(centers_coord)

		for center_id in range(center_num):
			this_cluster_insts = \
				where(inst_cluster_id == center_id)[0]

			for inst_id in this_cluster_insts:
				# Calculate average distance of this 
				# instance with every other instance
				# of the SAME cluster
				inst_avg_dist_intracluster = \
					max(abs(npmean(dataset[this_cluster_insts,:] -\
						dataset[inst_id,:], axis=0)))

				# Calculate the MINIMAL average distance
				# of this instance with every other ins-
				# tance of DIFFERENT clusters for each 
				# other cluster
				inst_min_avg_dist_intercluster = inf
				for i in range(center_num):
					if i != center_id:
						inst_min_avg_dist_intercluster =\
							min(inst_min_avg_dist_intercluster, \
								max(abs(npmean(dataset[inst_cluster_id == i,:] -\
									dataset[inst_id,:], axis=0))))

				# Calculate this instance silhouette 
				inst_sil[inst_id] = \
					(inst_min_avg_dist_intercluster - \
						inst_avg_dist_intracluster)/\
					max(inst_min_avg_dist_intercluster, \
						inst_avg_dist_intracluster)

		return npmean(inst_sil)

	def rand_index(
		predictive_attr, 
		labels, 
		inst_cluster_id, 
		return_counters=False): 

		"""
			Rand Index definition:
			let
			f_00 : # of instance pairs with diff classes in diff clusters
			f_01 : # of instance pairs with diff classes in the same cluster
			f_10 : # of instance pairs with same class in diff clusters
			f_11 : # of instance pairs with same classes in the same cluster

			Therefore, the most significative "bit" tells about 
			the class label pair and the less significative one
			about the cluster pair.

					Same cluster	Diff Cluster
			Same class	f_11		f_10
			Diff class	f_01		f_00

			then:
			rand_index := (f_00 + f_11) / (f_00 + f_10 + f_01 + f_11)
		"""

		# The counter array will express the f_ij value
		# in terms of it's own index. (For example, the 
		# counter f_10 is counters[int("10", 2)] == counters[2]
		# and the counter f_11 is counters[int("11", 2)] == counters[3])
		counters = 4 * [0]

		for i in range(predictive_attr.shape[0]):
			for j in range(predictive_attr.shape[0]):
				pos = 2 * (labels[i] == labels[j]) + \
					(inst_cluster_id[i] == inst_cluster_id[j])
				counters[pos] += 1

			# Remove the i == j counter. I do not put an
			# extra "if" to speed up the process.
			counters[3] -= 1 # Remember: int("11", 2) == 3.

		# rand_index = (f_00 + f_11) / (f_00 + f_10 + f_01 + f_11)
		rand_index = (counters[int("00", 2)] + \
			counters[int("11", 2)]) / sum(counters)

		if return_counters:
			return rand_index, counters

		return rand_index
		
	
	def adjusted_rand_index(predictive_attr, labels, inst_cluster_id): 
		pass

	def jackard_index(predictive_attr, labels, inst_cluster_id): 
		"""
			The jackard index is pretty much just like
			rand index. However, it does not consider the
			f_00 measure. So,

			jackard_index := f_11 / (f_01 + f_10 + f_11)
		"""
		junk, counters = Kmeans.rand_index(\
			predictive_attr, 
			labels, 
			inst_cluster_id,
			return_counters=True)

		# f_00 is not considered, set it to the neutral element
		# of addition, 0.
		counters[int("00", 2)] = 0

		# jackard_index := f_11 / (f_01 + f_10 + f_11)
		jackard_index = counters[int("11", 2)] / sum(counters)

		return jackard_index

	def run(dataset, k, it_max=1000, min_variation=1.0e-4, labels=None):
		# Init centers_coord
		centers_id = random.randint(dataset.shape[0], size=k)
		centers_coord = dataset[centers_id,:]

		# Each instance will be put on a initial random cluster
		inst_cluster_id = random.randint(k, size=dataset.shape[0])
		
		# Auxiliary vectors to keep code cleaner
		auxvec_cur_distances = array([0.0] * k)

		prev_variation = 1.0 + min_variation
		it = 0
		while it < it_max and prev_variation >= min_variation:
			it += 1

			for inst_id in range(dataset.shape[0]):
				nearest_center = inst_cluster_id[inst_id]
				for center_id in range(k):
					# For each instance, calculate the distance between
					# each center
					auxvec_cur_distances[center_id] = \
						Kmeans.__euclideandist__(\
							dataset[inst_id,:],
							centers_coord[center_id,:])
					
				# For each instance, let it be part of the nearest
				# cluster
				inst_cluster_id[inst_id] = argmin(auxvec_cur_distances)

			# For each cluster, calculate the new center coordinates
			for center_id in range(k):
				new_cur_cluster_coords = npmean(dataset[\
					inst_cluster_id == center_id,:], axis=0)

				# Calculate variation between previous centers_coord and
				# new ones (using infinite norm)
				prev_variation = max(prev_variation, \
					max(abs(centers_coord[center_id] - \
						new_cur_cluster_coords)))

				centers_coord[center_id] = new_cur_cluster_coords

		# Build up answer
		ans = {
			"centers" : centers_coord,
			"clusters" : inst_cluster_id,
			"inner_metrics" : {
				"SSE/Cohesion" : Kmeans.sse(dataset, \
					centers_coord, inst_cluster_id),
				"BSS/Separation" : Kmeans.bss(dataset, \
					centers_coord, inst_cluster_id),
				"Silhouette" : Kmeans.silhouette(dataset, \
					centers_coord, inst_cluster_id),
			},
		}

		if labels is not None:
			# If true labels are given, then we can compute
			# OUTTER clustering quality measures
			ans = {
				**ans,
				"outter_metrics" : {
					"Rand_index:" : Kmeans.rand_index(\
						dataset, labels, inst_cluster_id),
					"Adjusted_rand_index:" : Kmeans.adjusted_rand_index(\
						dataset, labels, inst_cluster_id),
					"Jackard_index:" : Kmeans.jackard_index(\
						dataset, labels, inst_cluster_id),
				}
			}

		return ans

if __name__ == "__main__":
	import sys

	if len(sys.argv) < 3:
		print("usage:", sys.argv[0], "<data_filepath> <k>",
			"\n\t[-sep data_separator] [-label column_label_to_remove]")
		exit(1)

	try:
		sep = sys.argv[1 + sys.argv.index("-sep")]
	except:
		sep = ","

	dataset = read_csv(sys.argv[1], sep=sep)

	try:
		rem_label = sys.argv[1 + sys.argv.index("-label")]
		class_ids = dataset.pop(rem_label)
	except:
		class_ids = None
		if ("-label",) in sys.argv:
			print("Warning: can not remove column \"" +\
				rem_label + "\" from dataset.")
	ans = Kmeans.run(
		dataset=dataset.loc[:,:].values, 
		k=int(sys.argv[2]),
		labels=class_ids)

	print("Results:")
	for item in ans:
		if type(ans[item]) == type({}):
			print(item, ":", sep="")
			for val in ans[item]:
				print("\t", val, ":", 
					ans[item][val], sep="")
		else:
			print(item, ":\n", ans[item], sep="")
		print()


