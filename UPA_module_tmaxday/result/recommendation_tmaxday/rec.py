from result.recommendation_tmaxday.recommendation import MatrixFactorization, MatrixFactorization_test
import numpy as np
import pandas as pd
import surprise
import copy

slicing_param = 66667
epoch = 10


if __name__ == "__main__":
	# rating matrix
	data = surprise.Dataset.load_builtin('ml-100k')
	df = pd.DataFrame(data.raw_ratings, columns=["user", "item", "rate", "id"])
	del df["id"]

	# Test error Table
	test_er = []

	for i in range(epoch):

		# Shuffle Tuple
		df.sample(frac=1).reset_index(drop=True)

		# splicing training data and test data by 2:1
		print("Training epoch = %d *********************************" % (i+1))
		df_train = copy.copy(df) # shallow copy
		train_dummy = copy.copy(df)
		train = train_dummy[0:slicing_param]
		lst = list(train["rate"])
		dummy = np.zeros([100000-slicing_param])
		lst = np.hstack([lst, dummy])
		df_train["rate"] = tuple(lst)

		# generating test data
		df_test = copy.copy(df)
		test_dummy = copy.copy(df)
		test = test_dummy[slicing_param:]
		lst = list(test["rate"])
		dummy = np.zeros([slicing_param])
		lst = np.hstack([dummy, lst])
		df_test["rate"] = tuple(lst)

		# unstack
		train_table = df_train.set_index(["user", "item"]).unstack()
		test_table = df_test.set_index(["user", "item"]).unstack()

		# convert to numpy array
		train_data_array = train_table.values
		test_data_array = test_table.values
		R_train = np.nan_to_num(train_data_array)
		R_test = np.nan_to_num(test_data_array)

		# Train
		factorizer = MatrixFactorization(R_train, k=7, learning_rate=0.005, reg_param=0.01, epochs=300, verbose=True)
		factorizer.fit()
		factorizer.print_results()
		trained_R = factorizer.get_complete_matrix()


		# Test
		tester = MatrixFactorization_test(trained_R, R_test)
		tester.print_result()

		# Save RMSE result
		np.savetxt("./result/k7_Training_result_lr0.005_ep%d.csv"%(i+1), trained_R, delimiter=",")

		errorrr = tester.test()
		test_er.append(errorrr)
	print ("Test errors *****************************************")
	for i in range(epoch):
		print ("Epoch%d : %.6f" % (i+1, test_er[i]))

	# Save Test Result
	np.savetxt("k7_Training_result_lr0.005.csv", test_er, delimiter=",")
