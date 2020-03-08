

# Function to convert SQLite result into an array
# currently sums AM + PM shifts together
def sql_to_arr(result):
    return [i[0] + i[1] for i in result]