if __name__ == "__main__":
	from kmeans2 import Kmeans
	from kmedians import Kmedians
	from kmedoids import Kmedoids
	from pandas import DataFrame, read_csv
	import sys

	sys.path.insert(0, "../../validation-framework/")
	from clustering import ClusterMetrics


	if len(sys.argv) < 3:
		print("usage:", sys.argv[0], "<data_filepath> <clustering_method>",
			"\n\t[-k, default to 3]",
			"\n\t[-sep data_separator, default to \",\"]",
			"\n\t[-label column_label_to_remove]",
			"\n\t[-findbestk]",
			"\n\t[-metric metric_to_find_best_k, default is \"silhouette\"]",
			"\n\nNote: \"metric\" parameter must be in",
			"{\"silhouette\", \"bss\", \"sse\", \"jackard\", \"rand\"}",
			"\nNote: \"clustering_method\" must be in",
			"{\"kmeans\", \"kmedians\", \"kmedoids\"}")
		exit(1)

	clustering_method = sys.argv[2].lower()
	if clustering_method not in {"kmeans", "kmedians", "kmedoids"}:
		print("Error: unrecognized clustering method \"" 
			+ clustering_method + \
			"\". Run script without parameters to get more information.")
		exit(2)

	if clustering_method == "kmeans":
		clustering_method_addr = Kmeans.run
	if clustering_method == "kmedians":
		clustering_method_addr = Kmedians.run
	else:
		clustering_method_addr = Kmedoids.run

	find_best_k = "-findbestk" in sys.argv

	try:
		sep = sys.argv[1 + sys.argv.index("-sep")]
	except:
		sep = ","

	try:
		metric = sys.argv[1 + sys.argv.index("-metric")]
	except:
		metric = "silhouette"

	try:
		k = int(sys.argv[1 + sys.argv.index("-k")])
	except:
		k = 5

	dataset = read_csv(sys.argv[1], sep=sep)

	try:
		rem_label = sys.argv[1 + sys.argv.index("-label")]
		class_ids = dataset.pop(rem_label)
	except:
		class_ids = None
		if ("-label",) in sys.argv:
			print("Warning: can not remove column \"" +\
				rem_label + "\" from dataset.")

	if not find_best_k:
		ans = clustering_method_addr(
			dataset=dataset.loc[:,:].values, 
			k=k,
			labels=class_ids)
	else:
		ans = ClusterMetrics.best_cluster_num(\
			dataset=dataset.loc[:,:].values,
			clustering_func=clustering_method_addr,
			k_max=k,
			metric=metric,
			labels=class_ids,
			warnings=True,
			full_output=True,
			cluster_func_args = {"full_output" : False})

	if ans:
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


