with open("names.txt", "r") as file_object:
    names_list = file_object.readlines()
    for line in names_list:
        print(line)

    print(f"Number of names: {len(names_list)}")