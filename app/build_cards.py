import json

H = "hours"


def m(name, hours=None, unit=None):
    # one module: its name and, only when the AICTE document gives it, its duration
    return {"name": name, "hours": hours, "unit": unit}


CARDS = {
    "BSC-101": {
        "modules": [m("Electrostatics in vacuum"), m("Electrostatics in a linear dielectric medium"), m("Magneto statics"),
                    m("Magneto statics in a linear magnetic medium"), m("Faraday's law"),
                    m("Displacement current and time-dependent fields"), m("Electromagnetic waves")],
        "prerequisites": [],
        "note": "AICTE lists four Physics-I options. This card shows option 1 (Introduction to Electromagnetic Theory). "
                "AICTE states the prerequisite as a mathematics course with vector calculus (Mathematics-I runs in the same semester).",
    },
    "BSC-102": {
        "modules": [m("Basic Calculus", 6, H), m("Single-variable Calculus (Differentiation)", 6, H), m("Sequences and series", 10, H),
                    m("Multivariable Calculus (Differentiation)", 8, H), m("Multivariable Calculus (Integration)", 10, H)],
        "prerequisites": [], "note": "",
    },
    "ESC-101": {
        "modules": [m("DC circuits"), m("Single phase AC circuits"), m("Transformers"), m("DC machines"),
                    m("Three phase induction motors"), m("Sources of electrical power")],
        "prerequisites": [], "note": "",
    },
    "ESC-102": {
        "modules": [m("Introduction to engineering drawing"), m("Orthographic projections"), m("Projections of regular solids"),
                    m("Sections and sectional views of right angular solids"), m("Isometric projections"),
                    m("Overview of computer graphics"), m("Customisation and CAD drawing"),
                    m("Annotations, layering and other functions"), m("Demonstration of a simple team design project")],
        "prerequisites": [], "note": "",
    },
    "HSMC-102": {
        "modules": [m("An insight to learning"), m("Remembering memory"), m("Emotions: experience and expression"),
                    m("Basics of design thinking"), m("Being ingenious and fixing problems"), m("Process of product design"),
                    m("Prototyping and testing"), m("Celebrating the difference"), m("Design thinking and customer centricity")],
        "prerequisites": [], "note": "AICTE lists nine units without durations.",
    },
    "AU-101": {
        "modules": [], "prerequisites": [],
        "note": "AICTE gives a numbered topic list for the IDEA Lab, not modules with durations.",
    },
    "BSC-202": {
        "modules": [m("Atomic and molecular structure"), m("Spectroscopic techniques and applications"),
                    m("Intermolecular forces and potential energy surfaces"),
                    m("Use of free energy in chemical equilibria", 6, "lectures"), m("Periodic properties"),
                    m("Stereochemistry"), m("Organic reactions and synthesis of a drug molecule")],
        "prerequisites": [], "note": "AICTE gives a duration only for module 4 (6 lectures).",
    },
    "BSC-201": {
        "modules": [m("Matrices", 10, H), m("First order ordinary differential equations", 6, H),
                    m("Ordinary differential equations of higher orders", 8, H), m("Complex variable: differentiation", 8, H),
                    m("Complex variable: integration", 8, H)],
        "prerequisites": [{"code": "BSC-102", "basis": "inferred: Mathematics-II follows Mathematics-I"}], "note": "",
    },
    "ESC-201": {
        "modules": [m("Introduction to programming"), m("Arithmetic expressions and precedence"),
                    m("Conditional branching and loops"), m("Arrays and strings"), m("Basic algorithms (searching, sorting)"),
                    m("Functions"), m("Recursion"), m("Structures"), m("Pointers"), m("File handling")],
        "prerequisites": [], "note": "",
    },
    "HSMC-201": {
        "modules": [m("Vocabulary building"), m("Basic writing skills"), m("Identifying common errors in writing"),
                    m("Nature and style of sensible writing"), m("Writing practices"), m("Oral communication")],
        "prerequisites": [], "note": "",
    },
    "ESC-202": {
        "modules": [m("Manufacturing methods: casting, forming, machining, joining"), m("CNC machining and additive manufacturing"),
                    m("Fitting operations and power tools"), m("Electrical and electronics"), m("Carpentry"),
                    m("Plastic moulding and glass cutting"), m("Metal casting"), m("Welding and brazing")],
        "prerequisites": [], "note": "",
    },
    "AU-102": {
        "modules": [m("Introduction to physical education"), m("Olympic movement"), m("Physical fitness, wellness and lifestyle"),
                    m("Anatomy and physiology in physical education and sports"), m("Kinesiology, biomechanics and sports"),
                    m("Postures"), m("Yoga"), m("Yoga and lifestyle"), m("Training and planning in sports"),
                    m("Psychology and sports"), m("Doping"), m("Sports medicine"), m("Sports and games")],
        "prerequisites": [], "note": "",
    },
    "HSMC(H-102)": {
        "modules": [m("Introduction to value education", 6, "lectures"), m("Harmony in the human being", 6, "lectures"),
                    m("Harmony in the family and society", 6, "lectures"), m("Harmony in nature and existence", 4, "lectures"),
                    m("Implications of the holistic understanding: professional ethics", 6, "lectures")],
        "prerequisites": [],
        "note": "AICTE states: no prerequisite; Universal Human Values 1 (the induction programme) is desirable.",
    },
    "ESC-301": {
        "modules": [], "prerequisites": [{"code": "ESC-101", "basis": "inferred: circuits build on Basic Electrical Engineering"}],
        "note": "The AICTE document gives only the course table entry, no module list.",
    },
    "CS-301": {
        "modules": [m("Introduction and basic terminology", 1, "weeks"),
                    m("Abstract data types: arrays, linked lists, stacks, queues, dictionary, trees", 2.5, "weeks"),
                    m("Priority queues and heaps", 1, "weeks"), m("Binary search trees, AVL trees, 2-4 trees", 3, "weeks"),
                    m("Hash tables, tries", 2, "weeks"), m("Sorting, selection", 1.5, "weeks"),
                    m("Graphs: representations, traversal, BFS and DFS", 2.5, "weeks"),
                    m("Amortized complexity (desirable)", 1, "weeks"),
                    m("Randomization in data structures (desirable)", 1, "weeks")],
        "prerequisites": [{"code": "ESC-201", "basis": "inferred: data structures are programmed using Programming for Problem Solving"}],
        "note": "The last two modules are the desirable (optional) ones in the AICTE table.",
    },
    "ESC-302": {
        "modules": [], "prerequisites": [{"code": "ESC-101", "basis": "inferred: digital circuits build on Basic Electrical Engineering"}],
        "note": "The AICTE document gives only the course table entry, no module list.",
    },
    "CS-302": {
        "modules": [], "prerequisites": [{"code": "ESC-201", "basis": "inferred: MATLAB/Scilab work needs programming basics"}],
        "note": "The AICTE document gives only the course table entry, no module list.",
    },
    "BSC-301": {
        "modules": [m("Partial differential equations"), m("Numerical methods"), m("Transform calculus"),
                    m("Discrete mathematics"), m("Probability and statistics")],
        "prerequisites": [{"code": "BSC-201", "basis": "inferred: Mathematics-III follows Mathematics-II"}],
        "note": "AICTE calls this a need-based course: modules are chosen per branch from these five topics. No durations are given.",
    },
    "HSMC-301": {
        "modules": [], "prerequisites": [],
        "note": "The AICTE document gives only the course table entry, no module list.",
    },
}


if __name__ == "__main__":
    with open("data/records.json", encoding="utf-8") as f:
        codes = [r["course_code"] for r in json.load(f)]
    missing = [c for c in codes if c not in CARDS]
    extra = [c for c in CARDS if c not in codes]
    print("records without a card:", missing, "| cards without a record:", extra)
    with open("data/course_cards.json", "w", encoding="utf-8") as f:
        json.dump(CARDS, f, indent=1, ensure_ascii=False)
    print("Saved data/course_cards.json with", len(CARDS), "cards")