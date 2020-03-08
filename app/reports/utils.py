

# Function to convert SQLite result into an array
# currently sums AM + PM shifts together
def sql_to_arr(result):
        arr = []
        for i in result:
            arr.append(i[0])
        return arr
    