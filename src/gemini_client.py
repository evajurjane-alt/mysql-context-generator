"""
gemini_client.py
Google Gemini API integrācija.
"""

from google import genai


def init_gemini(api_key):
    return genai.Client(api_key=api_key)


def generate_sql(client, db_context, user_question):
    prompt = f"""Tu esi SQL eksperts. Tev ir šāda MySQL datubāze:

{db_context}

Uzraksti SQL vaicājumu kas atbild uz:
"{user_question}"

Prasības:
- Tikai SELECT (nedrīkst mainīt datus)
- Agregēti rādītāji (COUNT, SUM, AVG, MAX, MIN u.c.)
- Tikai SQL kods, bez paskaidrojumiem

SQL:"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    sql = response.text.strip()
    if "```" in sql:
        lines = sql.split("\n")
        sql = "\n".join(l for l in lines if not l.startswith("```")).strip()
    return sql


def describe_results(client, db_context, sql_query, results, user_question):
    results_text = "\n".join(
        " | ".join(str(v) for v in row.values()) for row in results[:50]
    )
    if results:
        header = " | ".join(results[0].keys())
        results_text = header + "\n" + "-" * len(header) + "\n" + results_text

    prompt = f"""Tu esi datu analītiķis. Datubāze:

{db_context}

Jautājums: "{user_question}"

SQL:
{sql_query}

Rezultāti:
{results_text}

Apraksti šos rezultātus skaidri latviešu valodā. Izceli galvenos secinājumus."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()
