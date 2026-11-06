while True:
    print("\n1. About CurriculumBuddy")
    print("2. Sample questions")
    print("3. rule check from your domain")
    print("0. Exit")


    choice = input("Enter choice: ")

    if choice == "1":
        print("- CurriculumBuddy answers questions about AICTE model curricula.")

    elif choice == "2":
        print("- What modules are in the Operating Systems course?")
        print("- Which textbooks are suggested for Engineering Graphics?")

#in 3rd choice block we calculate lectures, practicals and tutorial and calculate with formula l+t+(p/2)
# we are using bodmas rule to calculate for easy understanding the brackets are applied in formula
# compare it with creadits provided by AICTE
# and print if they are equal, higer or lower
    elif choice == "3":
        l = int(input("Lecture hours: "))
        t = int(input("Tutorial hours: "))
        p = int(input("Practical hours: "))
        listed = float(input("Credits in curriculum table: "))
        credits = l + t + (p / 2)
        if credits == listed:
            print("- Credits match the table.")
        elif credits > listed:
            print("- Mismatch: calculated credits are higher.")
        else:
            print("- Mismatch: calculated credits are lower.")

    elif choice == "0":
        print("- You are out of the loops/exit")
        break
    else:
        print("- Invalid choice")
