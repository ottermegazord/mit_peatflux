def int2bin(n, count = 24):
	return "".join([str((n >> y) & 1) for y in range(count -1, -1, -1)])

print(int2bin(15, 4))

#list = [5, 6, 7, 8]
#print(list[2])

