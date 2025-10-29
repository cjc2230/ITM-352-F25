# take a list of tuples that are percentiles of household income in the US
# and print the list

import numpy as np

hh_income = [
    (10, 14629),
    (20, 25600),
    (30, 37002),
    (40, 50000),
    (50, 63179),
    (60, 79542),
    (70, 100162),
    (80, 130000),
    (90, 184292)
]

print(hh_income)

hh_income_array = np.array(hh_income)

# report demensions of the array
# num of elecments

print(f"dimensions: {hh_income_array.shape}")
print(f"dimensions version 2: {hh_income_array.ndim}")
print(f"number of elements: {hh_income_array.size}")

for i in range(len(hh_income_array[0])):
    print(hh_income_array[i, 0], hh_income_array[i, 1])
