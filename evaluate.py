import json
from src.pipeline import ask_question
from tqdm import tqdm
from src.db import run_query
import time
import pandas as pd


def normalize(rows):
    return set(
        tuple(
            round(float(val), 2) if isinstance(val, float) else val 
            for val in row 
        ) for row in rows
    )

with open("eval/tests.json", "r") as f:
    tests = json.load(f)

results = []
accurate_count = 0

for t in tqdm(tests, desc="Execution Match Evaluation"):
    question = t["question"]
    expected_sql = t["expected_sql"]

    #Running LLM pipeline
    start = time.time()
    predicted_sql, _,_,_ = ask_question(t["question"], show_sql=True)
    latency = round(time.time() - start, 3)
    try:
        #Running expected SQL
        expected_cols, expected_rows = run_query(t["expected_sql"])
        #running predicted SQL
        pred_cols, pred_rows = run_query(predicted_sql)

        # Checking if results match (order-independent)
        expected_set = normalize(expected_rows)
        pred_set = normalize(pred_rows)

        match = expected_set == pred_set
        accurate_count += int(match)

        results.append({
            "Question": question,
            "Expected SQL": expected_sql,
            "Predicted SQL": predicted_sql,
            "Exec Match": match,
            "Latency (s)": latency
        })

    except Exception as e:
        results.append({
            "Question": question,
            "Expected SQL": expected_sql,
            "Predicted SQL": predicted_sql or "ERROR",
            "Exec Match": False,
            "Latency (s)": latency,
            "Error": str(e)
        })

df = pd.DataFrame(results)
df.to_csv("Evaluation_metrics.csv", index=False)
print("Metrics csv file saved!")

df = pd.read_csv("Evaluation_metrics.csv")

accuracy = round((df['Exec Match'].astype(int).sum() / len(df)) * 100, 2)
print(f"Accuracy: {accuracy}%")

average_latency = df["Latency (s)"].mean()
print(f"Average Latency: {average_latency:.3f} seconds")