enc = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
sol = "                     EASTNORTHEAST                             BERLINCLOCK                       "


def next_letter(buchstabe):
    if buchstabe.isalpha():
        if buchstabe == 'z':
            return 'a'
        elif buchstabe == 'Z':
            return 'A'
        else:
            return chr(ord(buchstabe) + 1)
    else:
        raise ValueError("Die Eingabe muss ein Buchstabe sein")


def generate_pairs(enc_string):
    pairs = []
    for i in range(len(enc_string)):
        for j in range(i,len(enc_string)):
            if next_letter(enc_string[i]) == enc_string[j]:
                pairs.append(f"{enc_string[i]} at {i}, {enc_string[j]} at {j}, dist: {j-i}, (sol is {sol[i]}, {sol[j]}")

    for pair in pairs:
        print(pair)


if __name__ == "__main__":
    generate_pairs(enc)