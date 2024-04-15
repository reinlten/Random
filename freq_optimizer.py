target_freq = 51200
f_adc = 25000000
clk_div = [1,2,4,6,8,10,12,16,32,64,128,256]
smpl_time = [2.5,6.5,12.5,24.5,47.5,92.5,247.5,640.5]

guess = 2500000000
best_clk_div = 0
best_smpl_time = 0
adc_freq = 0

for clk in clk_div:
    for smpl in smpl_time:
        adc_freq = f_adc/(clk*(12.5+smpl))
        print(adc_freq)
        if abs(adc_freq-target_freq) <= abs(guess-target_freq):
            guess = adc_freq
            best_clk_div = clk
            best_smpl_time = smpl

print(guess)
print(best_clk_div)
print(best_smpl_time)
print("-"*25)

buff_size = 256

for clk in clk_div:
    for smpl in smpl_time:
        adc_freq = f_adc/(clk*(12.5+smpl))
        #print(adc_freq)
        f = adc_freq/(buff_size)
        if 0 <= (round(f, 6) - round(f, 0)) < 0.01 and adc_freq >4000:
            print(f"found solution:{adc_freq}")
            print(round(f, 6)-round(f, 0))
            print(adc_freq)
            print("*"*40)
