import math

ADC_BUF_LEN = 1024
SAMPLE_FEQ = 52083 #Hz
NUM_BARS = 26

freq_val = []

segment_size = []

segments = []

pos = []

number_of_freq = 0


for i in range(0,ADC_BUF_LEN):
    print(f"{i}: {i*SAMPLE_FEQ/ADC_BUF_LEN}")
    freq_val.append(i*SAMPLE_FEQ/ADC_BUF_LEN)
    if i*SAMPLE_FEQ/ADC_BUF_LEN < 20000:
        number_of_freq += 1

print(number_of_freq)
i = 1
for j in range(0, NUM_BARS):
    curr_bin = []
    while freq_val[i] < 10**((math.log(20250/300, 10)*j/25) + math.log(300, 10))-249:
        curr_bin.append(freq_val[i])
        #print(f" while: {j}: {((math.log(20250/300, 10)*j/25) + math.log(300, 10))**10-249}")
        i += 1
    if not curr_bin:
        curr_bin.append(freq_val[i])
        segments.append(curr_bin)
        pos.append(i)
        i += 1
    else:
        segments.append(curr_bin)
        pos.append(i)


print(segments)
print(len(segments))
for s in segments:
    print(len(s))

print(pos)

#for s in segments:
#    print(s)

#for i in range(0,len(pos)):
#    print(f"{i}: {pos[i]}")