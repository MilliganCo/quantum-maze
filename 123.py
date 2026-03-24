SIZE = 5
arr = [None] * SIZE
for i in range(SIZE): arr[i] = [None] * SIZE
count = 1
start = 0

# Main loop
while (start < SIZE // 2):
    n = SIZE - start * 2 - 1
    for x in range(n):
        arr[start][start + x] = count
        count += 1
    for y in range(n):
        arr[start + y][SIZE - 1 - start] = count
        count += 1
    for x in range(n):
        arr[SIZE - 1 - start][SIZE - 1 - start - x] = count
        count += 1
    for y in range(n):
        arr[SIZE - 1 - start - y][start] = count
        count += 1

    start += 1

# Middle element for odd sizes
if (SIZE % 2): arr[start][start] = count

# Printing
out_str = f"{arr[0][0]}"
for y in range(1, SIZE):
    out_str = out_str + ",  " + str(arr[0][y])

print(f"[{out_str}]")

for y in range(1, SIZE):
    print(arr[y])
