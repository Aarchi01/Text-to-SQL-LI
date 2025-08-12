import time
from llama_index.core import VectorStoreIndex
from llama_index.core.prompts import PromptTemplate
from src.schema_loader import get_schema_text
from src.index_builder import build_index
from src.db import run_query
from src.few_shot import load_few_shot_examples, format_few_shot_prompt
from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv

#load env for OpenAI API key
load_dotenv()

def get_sql_prompt_template(few_shot_prompt):
    """
    Returns a PromptTemplate that instructs the LLM on how to generate SQL.
    """
    return PromptTemplate(f"""
You are an expert MySQL SQL assistant. You will be given:
1. A database schema
2. Some example questions and their SQL answers
3. A new user question
                          
Your task:
- First, explain your reasoning step-by-step about how you will build the SQL query:
  - What user intent you understood
  - Which tables and columns you plan to use
  - What filters, joins, or aggregations are needed
- Then write the final SQL query

Use a CTE (WITH clause) when it improves readability, reuse, or logical clarity:
- for filtered aggregates (HAVING, percentages, top-N)
- for multi-step calculations
- for reusing intermediate results
                          

Never invent tables or columns not present in the schema.
If something is impossible with the given schema, write: SELECT 'CANNOT_ANSWER';

Format your response as:
Reasoning: [Your step-by-step reasoning]
SQL: [Your SQL query]

### Complete Database Schema(these are the only tables and columns available):
{{context_str}}

### Few-Shot Examples:
{few_shot_prompt}

### Question:
Q: {{query_str}}

A:""")

def explain_result(user_question, columns, rows, llm):
    rows_str = "\n".join([str(dict(zip(columns, row))) for row in rows])
    prompt = f"""
You are a helpful assistant for non-technical users.
The user asked:
"{user_question}"

The system ran a SQL query and got this result:
{rows_str}

Summarize this in a simple, clear answer:
"""
    response = llm.complete(prompt)
    return response.text.strip()

def ask_question(user_question, show_sql=False, show_reasoning=False, show_schema=False):
    schema_text = get_schema_text()
    examples = load_few_shot_examples()
    few_shot_prompt = format_few_shot_prompt(examples)

    prompt = get_sql_prompt_template(few_shot_prompt)
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0, model='gpt-4', max_tokens=1024, top_p =1)

    index = build_index(schema_text)
    query_engine = index.as_query_engine(text_qa_template=prompt)

    response = query_engine.query(user_question)
    response_text = str(response).replace("```sql", "").replace("```", "").strip("` \n")

    #parsing reasoning and SQL from response
    reasoning = None
    sql_query = None
    
    if "Reasoning:" in response_text and "SQL:" in response_text:
        parts = response_text.split("SQL:", 1)
        reasoning_part = parts[0]
        sql_part = parts[1]

        reasoning = reasoning_part.replace("Reasoning:", "").strip()
        sql_query = sql_part.strip().strip("`")
    elif "SQL:" in response_text:
        sql_part = response_text.split("SQL:", 1)[1]
        sql_query = sql_part.strip().strip("`")
    else:
        sql_query = response_text

    sql_starts = ("select", "with", "insert", "update", "delete")
    if not sql_query.lower().startswith(sql_starts):
        return (None if show_sql else None,
                response_text,
                reasoning if show_reasoning else None,
                schema_text if show_schema else None)

    try:
        columns, result = run_query(sql_query)
        if not result:
            no_result_prompt = f"""
            the user asked: "{user_question}"
            the database query returned no results.
            Please explain this clearly and helpfully to the user.
        """
            explanation = llm.complete(no_result_prompt).text.strip()
            return (sql_query if show_sql else None,
                    explanation,
                    reasoning if show_reasoning else None,
                    schema_text if show_schema else None)
        
        explanation = explain_result(user_question, columns, result, llm)
        return (sql_query if show_sql else None,
                explanation,
                reasoning if show_reasoning else None,
                schema_text if show_schema else None)

    except Exception as e:
        error_message = f"SQL execution failed: {e}"
        return (sql_query if show_sql else None,
                error_message,
                reasoning if show_reasoning else None,
                schema_text if show_schema else None)



