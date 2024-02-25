import sqlite3

conn = sqlite3.connect("./db.sqlite3")
cur = conn.cursor()
import random

txt = open("c.txt").read()


questions = []

lines = txt.split("\n")
opts = ["a", "b", "c", "d"]

j = 0
for i in range(33):
    found = 0
    question = []
    options = []
    while True:
        try:
            line = lines[j]
        except:
            break
        if line.startswith(tuple((f"{x})" for x in opts))):
            for x in opts:
                if line.startswith(f"{x})"):
                    options.append(line.removeprefix(f"{x})").strip())
        elif line.startswith("Answer:"):
            correct = line.removeprefix("Answer:")
            correct = correct.strip()
            # correct = correct.strip().split()[0].removesuffix(".")
        elif line.startswith(tuple(f"{x}." for x in range(1, 51, 1))):
            if found == 1:
                break
            question.append(line)
            found += 1
        elif line == "\n":
            j += 1
            continue
        else:
            question.append(line)
        j += 1
    question = "\n".join(question)
    if not question or not options or not correct:
        print(1)
        continue
    questions.append(
        {"question": question, "options": options, "correct": opts.index(correct)}
    )


i = 0
qsets = []
while i < 33:
    quests = questions[i : i + 3]
    q = None
    for j in range(5 - len(quests)):
        while True:
            q = random.choice(questions)
            if q not in quests:
                quests.append(q)
                break
            else:
                continue
    i += 3
    qsets.append((quests, random.choice(range(9, 13, 1))))

# print(len(qsets))
# print(qsets[0])
# exit()

q_id = 57
for quiz in qsets:
    qset = quiz[0]
    c_id = quiz[1]
    cur.execute("Insert into api_quiz (creator_id, topic_id) values (?, ?)", (c_id, 4))
    for q in qset:
        question = q["question"]
        options = q["options"]
        # print(q)
        a = options[0]
        b = options[1]
        c = options[2]
        d = options[3]
        correct = q["correct"]
        cur.execute(
            "Insert into api_question (option0, option1, option2, option3, correct, quiz_id, question) values (?, ?, ?, ?, ?, ?, ?)",
            (a, b, c, d, correct, q_id, question),
        )
    q_id += 1
conn.commit()
