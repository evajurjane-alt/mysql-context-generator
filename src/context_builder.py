"""
context_builder.py
Veido strukturētu kontekstu no datubāzes shēmas LLM lietošanai.
"""


def build_context(tables, database_name):
    lines = [f"# Datubāze: `{database_name}`", f"Tabulu skaits: {len(tables)}\n"]
    for table in tables:
        lines.append(f"## Tabula: `{table.name}`")
        if table.comment:
            lines.append(f"Apraksts: {table.comment}")
        lines.append("")
        lines.append("| Kolonna | Datu tips | Ierobežojumi |")
        lines.append("|---------|-----------|--------------|")
        for col in table.columns:
            constraints = ", ".join(col.constraints) if col.constraints else "—"
            lines.append(f"| `{col.name}` | `{col.full_type}` | {constraints} |")
        lines.append("")
    return "\n".join(lines)


def build_compact_context(tables, database_name):
    lines = [f"Datubāze: {database_name}", ""]
    for table in tables:
        lines.append(f"{table.name}:")
        for col in table.columns:
            constraints = ", ".join(col.constraints) if col.constraints else ""
            entry = f"  - {col.name} {col.full_type}"
            if constraints:
                entry += f" [{constraints}]"
            lines.append(entry)
        lines.append("")
    return "\n".join(lines)
