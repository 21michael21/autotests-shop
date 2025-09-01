def sum_all(*args):
    count = 0 
    for i in args:
        count += i
    lenght_args = len(args)
        
    return count, lenght_args

result = sum_all(3,454,65,43,2,32,443,54,43 )

print(f"Первым числом сумма всех числел, вторрым колличество: {result}")