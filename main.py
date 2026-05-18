"""
main.py
Galvenais skripts — MySQL shēmas analīze + Gemini SQL ģenerēšana.
"""

import os
from dotenv import load_dotenv
from src.db_explorer import connect, explore_database
from src.context_builder import build_context, build_compact_context
from src.gemini_client import init_gemini, generate_sql, describe_results

load_dotenv()


def run_query(connection, sql):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    return results


def save_context(context, filename):
    os.makedirs("output", exist_ok=True)
    path = os.path.join("output", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(context)
    print(f"  Saglabāts: {path}")


def main():
    print("=" * 55)
    print("  MySQL konteksta generators ar Gemini AI")
    print("=" * 55)

    db_config = {
        "host": os.getenv("DB_HOST", "87.110.123.151"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not all([db_config["user"], db_config["password"], db_config["database"]]):
        print("KĻŪDA: Aizpildi .env failu ar DB_USER, DB_PASSWORD, DB_NAME")
        return
    if not gemini_key:
        print("KĻŪDA: Nav GEMINI_API_KEY .env failā")
        return

    print(f"\nSavienojas ar {db_config['host']}...")
    try:
        conn = connect(**db_config)
        print("Savienojums veiksmīgs!")
    except Exception as e:
        print(f"Kļūda: {e}")
        return

    print(f"\nAnalizē datubāzi '{db_config['database']}'...")
    tables = explore_database(conn, db_config["database"])
    print(f"Atrastas {len(tables)} tabulas:")
    for t in tables:
        print(f"  • {t.name} ({len(t.columns)} kolonnas)")

    print("\nVeido kontekstu...")
    full_ctx = build_context(tables, db_config["database"])
    compact_ctx = build_compact_context(tables, db_config["database"])
    save_context(full_ctx, "db_context_full.md")
    save_context(compact_ctx, "db_context_compact.txt")

    print("\n" + "-" * 55)
    print(compact_ctx)
    print("-" * 55)

    print("\nInicializē Gemini...")
    try:
        client = init_gemini(gemini_key)
        print("Gemini gatavs!")
    except Exception as e:
        print(f"Kļūda: {e}")
        conn.close()
        return

    print("\n" + "=" * 55)
    print("  Uzdodi jautājumu (raksti 'iziet' lai beigtu)")
    print("=" * 55)

    while True:
        print()
        question = input("Jautājums: ").strip()
        if question.lower() in ("iziet", "exit", "q"):
            print("Uz redzēšanos!")
            break
        if not question:
            continue

        print("\nĢenerē SQL...")
        try:
            sql = generate_sql(client, compact_ctx, question)
            print(f"\nSQL:\n{'-'*40}\n{sql}\n{'-'*40}")
        except Exception as e:
            print(f"Kļūda: {e}")
            continue

        print("\nIzpilda vaicājumu...")
        try:
            results = run_query(conn, sql)
            print(f"Iegūtas {len(results)} rindas")
        except Exception as e:
            print(f"SQL kļūda: {e}")
            continue

        if not results:
            print("Nav rezultātu.")
            continue

        print("\nAnalizē ar Gemini...")
        try:
            desc = describe_results(client, compact_ctx, sql, results, question)
            print(f"\nANALĪZE:\n{'-'*55}\n{desc}\n{'-'*55}")
        except Exception as e:
            print(f"Kļūda: {e}")

    conn.close()


if __name__ == "__main__":
    main()
