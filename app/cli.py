from app.records import load_records, search, count_by, get_by_id

records = load_records()

while True:
    print("\n1. Show all courses")
    print("2. Search by keyword")
    print("3. Count per category")
    print("4. Get course by code")
    print("0. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        for r in records:
            print(r["course_code"], r["course_title"], r["category"])
    elif choice == "2":
        word = input("Keyword: ")
        for r in search(records, word):
            print(r["course_code"], r["course_title"])
    elif choice == "3":
        counts = count_by(records, "category")
        for cat in counts:
            print(cat, counts[cat])
    elif choice == "4":
        code = input("Course code: ")
        course = get_by_id(records, code)
        if course:
            print(course)
        else:
            print("Course not found")
    elif choice == "0":
        break
    else:
        print("Invalid choice")