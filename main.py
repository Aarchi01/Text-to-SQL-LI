
from src.pipeline import ask_question
import time

if __name__ == "__main__":
    print("Text-to-SQL Assistant")
    show_sql = input("Show SQL? (yes/no): ").strip().lower() == "yes"
    show_reasoning = input("Show LLM Reasoning? (yes/no): ").strip().lower() == "yes"
    show_schema = input("Show full schema used? (yes/no): ").strip().lower() == "yes"

    while True:
        q = input("\nAsk a question (or type 'exit'): ")
        if q.lower() == 'exit':
            break

        start = time.time()
        sql, answer, reasoning, schema = ask_question(q, show_sql=show_sql, show_reasoning=show_reasoning, show_schema=show_schema)
        latency = time.time() - start

        if show_sql and sql:
            print(f"\nSQL:\n{sql}")

        if show_reasoning and reasoning:
            print(f"\nReasoning:\n{reasoning}")

        if show_schema and schema:
            print(f"\nFull schema:\n{schema}")


        print(f"\nAnswer:\n{answer}")
        print(f"⏱️ Query generation time: {latency:.2f} seconds\n")
        
        