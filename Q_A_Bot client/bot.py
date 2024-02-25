import json
import logging
import pickle
import random
import os
import sys
import aiohttp
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyromod import listen
from pyrogram.enums.poll_type import PollType
from pyrogram.errors import FloodWait
from pyrogram.types import Message, Poll, User


load_dotenv()


API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API = os.environ.get("API")
BERT_API = os.environ.get("BERT_API")

file_handler = logging.FileHandler(filename="bot.log", mode="w")
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
    format="%(name)s - %(levelname)s - %(message)s\n",
    level=logging.WARNING,
    handlers=handlers,
)

logger = logging.getLogger(__name__)

bot = Client(
    "bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, sleep_threshold=120
)

users_dict = {}
polls_dict = {}
bert_dict = pickle.load(open("bert.pkl", "rb"))


async def request(method: str, url: str, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, *args, **kwargs) as resp:
            return await resp.json(content_type=None)


async def save_user(bot: Client, user: User):
    global users_dict
    id = user.id
    first_name = user.first_name
    last_name = user.last_name
    if not last_name:
        name = f"{first_name}"
    else:
        name = f"{first_name} {last_name}"
    user = await request("GET", f"{API}/user/", json={"usertype": 0, "tgid": id})
    if not user:
        user = await request(
            "POST", f"{API}/user/", json={"usertype": 0, "tgid": id, "name": name}
        )
        await bot.send_message(id, "User Registered Successfully")
    users_dict[id] = {"user_id": user["id"]}


@bot.on_message(filters.command("start"))
async def start(bot: Client, message: Message):
    await message.reply("Q & A bot is running")


@bot.on_message(filters.command("addcontext"))
async def addcontext(bot: Client, message: Message):
    global bert_dict
    user = message.from_user.id
    msg: Message = await bot.ask(user, "Enter context text")
    if not msg.document:
        text = msg.text
    else:
        file = await msg.download()
        text = open(file).read()
        os.remove(file)
    resp = await request("POST", f"{BERT_API}/", json={"text": text})
    context_id = resp["id"]
    bert_dict[user] = context_id
    await message.reply("Context saved")
    pickle.dump(bert_dict, open("bert.pkl", "wb"))


@bot.on_message(filters.command("answerquestion"))
async def answerquestion(bot: Client, message: Message):
    global bert_dict
    user = message.from_user.id
    msg: Message = await bot.ask(user, "Enter question")
    question = msg.text
    context_id = bert_dict[user]
    resp = await request("GET", f"{BERT_API}/{context_id}", json={"question": question})
    answer = resp["answer"]
    await message.reply(answer)


@bot.on_message(filters.command("starttest"))
async def starttest(bot: Client, message: Message):
    await save_user(bot, message.from_user)
    global polls_dict
    # await message.reply("Choose topic")
    user = message.from_user.id
    question = "Choose topic"
    topics_resp = await request("GET", f"{API}/topic/")
    topics = [topic["name"] for topic in topics_resp]
    msg: Message = await message.reply_poll(
        question, topics, is_anonymous=True, type=PollType.REGULAR, quote=False
    )
    polls_dict.update({msg.poll.id: user})
    # print(msg)
    # message.reply(text)


async def handle_quiz(bot: Client, user: int, quiz):
    global users_dict
    user_dict = users_dict[user]
    quiz_id = quiz["id"]
    questions = quiz["question"]
    topic = quiz["topic_info"]["name"]
    user_dict.update(
        {
            "quiz": quiz,
            "score": 0,
            "answered": 0,
            "total": len(questions),
            "questions": {},
        }
    )
    created_by = quiz["creator_info"]["name"]
    avg_rating = quiz["avg_rating"]
    quiz_msg = f"Quiz id: {quiz_id}\nTopic: {topic}\nCreated By: {created_by}\nAvg Rating: {avg_rating}"
    await bot.send_message(user, quiz_msg)
    for ques in questions:
        question = ques["question"]
        options = [ques[f"option{x}"] for x in range(4)]
        correct = ques["correct"]
        msg: Message = await bot.send_poll(
            user,
            question,
            options,
            correct_option_id=correct,
            is_anonymous=True,
            type=PollType.QUIZ,
        )
        polls_dict.update({msg.poll.id: user})
        user_dict["questions"].update({msg.poll.id: correct})


async def handle_topic(bot: Client, user: int, poll: Poll):
    options = poll.options
    for option in options:
        text = option.text
        vc = option.voter_count
        if vc == 1:
            break
    chosen = text
    quizes = await request("GET", f"{API}/quizes/", data={"name": chosen})
    quiz = random.choice(quizes)
    await handle_quiz(bot, user, quiz)


async def handle_post_rating(bot: Client, user: User, liked):
    if liked:
        global users_dict
        user_dict = users_dict[user]
        user_id = user_dict["user_id"]
        quiz_id = user_dict["quiz"]["id"]
        topic_id = user_dict["quiz"]["topic_info"]["id"]
        rec_quizes = await request(
            "GET",
            f"{API}/recommend/",
            json={"quiz_id": quiz_id, "topic_id": topic_id},
        )
        user_dict["rec"] = {}
        rec_quizes_txt = []
        for i, rec_quiz in enumerate(rec_quizes):
            quiz_id = rec_quiz["id"]
            avg_rating = rec_quiz["avg_rating"]
            created_by = rec_quiz["creator_info"]["name"]
            topic = rec_quiz["topic_info"]["name"]
            quiz_txt = f"Quiz id: {quiz_id}\nTopic: {topic}\nCreated By: {created_by}\nAvg Rating: {avg_rating}"
            rec_quizes_txt.append(quiz_txt)
            user_dict["rec"][i] = quiz_id

        user_dict["rec"][i + 1] = 0
        question = "Recommended quizes"
        rec_quizes_txt.append("Quit")
        msg: Message = await bot.send_poll(
            user,
            question,
            rec_quizes_txt,
            is_anonymous=True,
            type=PollType.REGULAR,
        )
        polls_dict.update({msg.poll.id: user})

    else:
        await bot.send_message(user, "Good Bye.")
        return


async def handle_recommend(bot: Client, user: int, poll: Poll):
    global users_dict
    user_dict = users_dict[user]
    options = poll.options
    for i, option in enumerate(options):
        vc = option.voter_count
        if vc == 1:
            break

    chosen = int(i)
    quiz_id = user_dict["rec"][chosen]
    if quiz_id == 0:
        await bot.send_message(user, "Good Bye.")
        return
    quiz = await request("GET", f"{API}/quiz/", data={"id": quiz_id})
    await handle_quiz(bot, user, quiz)


async def handle_rating(bot: Client, user: int):
    global users_dict
    user_dict = users_dict[user]
    user_id = user_dict["user_id"]
    quiz_id = user_dict["quiz"]["id"]
    rating = await request(
        "GET", f"{API}/rating/", json={"quiz": quiz_id, "user": user_id}
    )
    quest_txt = "How would you rate this test (0.0 - 5.0) ?\nSend n to skip rating"
    if rating:
        prev_value = rating["value"]
        liked = prev_value > 2.5
        msg_txt = f"Your Previous Rating: {prev_value}\n{quest_txt}"
        msg: Message = await bot.ask(user, msg_txt)
    else:
        liked = False
        msg: Message = await bot.ask(user, quest_txt)
    ans: str = msg.text
    if ans.lower() == "n":
        await handle_post_rating(bot, user, liked)
        return
    try:
        value: float = float(ans)
    except:
        liked = False
        await handle_post_rating(bot, user, liked)
        return
    value = round(value, 1)
    if value > 5:
        value = 5.0
    elif value < 0:
        value = 0.0
    rating = await request(
        "POST",
        f"{API}/rating/",
        json={"quiz": quiz_id, "user": user_id, "value": value},
    )
    liked = value > 2.5
    await bot.send_message(user, "Thanks for rating!")
    await handle_post_rating(bot, user, liked)


async def handle_result(bot: Client, user: int):
    global users_dict
    user_dict = users_dict[user]
    score = user_dict["score"]
    total = user_dict["total"]
    percentage = score * 100 / total
    result_msg = f"Your score: {score}/{total}, {percentage} %"
    await bot.send_message(user, result_msg)
    await handle_rating(bot, user)


async def handle_answer(bot: Client, user: int, poll: Poll):
    global users_dict
    user_dict = users_dict[user]
    user_dict["answered"] += 1
    correct = user_dict["questions"][poll.id]
    options = poll.options
    correct_option = options[correct]
    if correct_option.voter_count == 1:
        user_dict["score"] += 1

    if user_dict["answered"] == user_dict["total"]:
        await handle_result(bot, user)


@bot.on_poll()
async def handle_poll(bot: Client, poll: Poll):
    try:
        user = polls_dict[poll.id]
    except:
        return
    question = poll.question
    if question == "Choose topic":
        await handle_topic(bot, user, poll)
    elif question == "Recommended quizes":
        await handle_recommend(bot, user, poll)
    else:
        await handle_answer(bot, user, poll)


if __name__ == "__main__":
    print("Starting bot...")
    bot.run()
