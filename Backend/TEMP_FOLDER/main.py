NUM1 = 25
NUM3 = 25
NUM2 = 15
NUM4 = 15

if NUM1 > NUM2:
    print("IN LOOP 1 - IF BLOCK")
    if NUM3 == NUM4:
        print("IN LOOP 2 - IF BLOCK")
    else:
        print("IN LOOP 2 - ELSE BLOCK")
else:
    print("IN LOOP 1 -ELSE BLOCK")

CHECK_VAL = 65
if 41 <= CHECK_VAL <= 100:
    print(f"PASSED WITH {CHECK_VAL} MARKS.")
if 0 <= CHECK_VAL <= 40:
    print(f"FAILED WITH {CHECK_VAL} MARKS.")

if NUM1 < 2:
    print("NUM1 LESS THAN 2")
elif NUM1 < 19:
    print("NUM1 LESS THAN 19")
elif NUM1 < 1000:
    print("NUM1 LESS THAN 1000")