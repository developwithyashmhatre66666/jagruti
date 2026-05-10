from asyncio import run
from dotenv import dotenv_values
from Backend.Automation import Automation
from Backend.Chatbot import ChatBot
from Backend.ImageGeneration import GenerateImages
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import realtime_search_engine
from Backend.realtime_search.intent_local import upgrade_general_to_realtime
from Backend.SIE import try_society_intelligence
env_vars = dotenv_values(".env")
USERNAME = env_vars.get("Username", "User")
ASSISTANT_NAME = env_vars.get("Assistantname", "Assistant")
AUTOMATION_PREFIXES = (
    "open ",
    "close ",
    "play ",
    "system ",
    "content ",
    "google search ",
    "youtube search ",
)
def normalize_query(text: str) -> str:
    return " ".join(text.strip().split())
def handle_intent(query: str) -> bool:
    try:
        sie_reply = try_society_intelligence(query)
    except Exception as exc:
        print(f"{ASSISTANT_NAME}: Society engine error: {exc}")
        sie_reply = None
    if sie_reply is not None:
        print(f"{ASSISTANT_NAME}: {sie_reply}\n")
        return True
    try:
        decision = FirstLayerDMM(query)
    except Exception as exc:
        print(f"{ASSISTANT_NAME}: Intent parsing error: {exc}")
        return True
    print(f"\n[{ASSISTANT_NAME}] Decision: {decision}")
    if decision:
        decision = upgrade_general_to_realtime(list(decision), query)
    if not decision:
        answer = ChatBot(query)
        print(f"{ASSISTANT_NAME}: {answer}\n")
        return True
    if any(task.startswith("exit") for task in decision):
        print(f"{ASSISTANT_NAME}: Okay, bye!")
        return False
    if any(task.startswith(AUTOMATION_PREFIXES) for task in decision):
        try:
            run(Automation(list(decision)))
        except Exception as exc:
            print(f"{ASSISTANT_NAME}: Automation error: {exc}")
            return True
    for task in decision:
        if task.startswith("generate image"):
            prompt = task.replace("generate image", "", 1).strip() or query
            print(f"{ASSISTANT_NAME}: Generating images for '{prompt}'...")
            try:
                GenerateImages(prompt)
            except Exception as exc:
                print(f"{ASSISTANT_NAME}: Image generation error: {exc}")
                return True
    general_or_realtime = [
        task for task in decision if task.startswith("general") or task.startswith("realtime")
    ]
    if not general_or_realtime:
        return True
    if any(task.startswith("realtime") for task in general_or_realtime):
        merged_query = " and ".join(
            " ".join(task.split()[1:]).strip() for task in general_or_realtime
        ).strip()
        try:
            answer = realtime_search_engine(normalize_query(merged_query or query))
        except Exception as exc:
            print(f"{ASSISTANT_NAME}: Realtime search error: {exc}")
            return True
        print(f"{ASSISTANT_NAME}: {answer}\n")
        return True
    for task in general_or_realtime:
        if task.startswith("general"):
            pure_query = task.replace("general", "", 1).strip()
            try:
                answer = ChatBot(normalize_query(pure_query or query))
            except Exception as exc:
                print(f"{ASSISTANT_NAME}: Chat error: {exc}")
                return True
            print(f"{ASSISTANT_NAME}: {answer}\n")
            return True
    return True
def main() -> None:
    print(f"{ASSISTANT_NAME} CLI ready for {USERNAME}. Type 'exit' to quit.\n")
    while True:
        try:
            query = input(f"{USERNAME}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{ASSISTANT_NAME}: Goodbye!")
            break
        if not query:
            continue
        if query.lower() in {"exit", "quit", "bye"}:
            print(f"{ASSISTANT_NAME}: Goodbye!")
            break
        should_continue = handle_intent(query)
        if not should_continue:
            break
if __name__ == "__main__":
    main()


