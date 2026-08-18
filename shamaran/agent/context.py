"""Construct bounded context from persistent local memory."""

from shamaran.memory import SQLiteMemory


def relevant_memory(memory: SQLiteMemory, request: str, limit: int = 5) -> str:
    terms = [term for term in request.split() if len(term) >= 4][:3]
    records = []
    seen: set[int] = set()
    for term in terms:
        for record in memory.search(term, limit=limit):
            if record.id not in seen:
                records.append(record)
                seen.add(record.id)
            if len(records) >= limit:
                break
    if not records:
        return ""
    lines = [f"- [{record.category}] {record.content}" for record in records]
    return "Relevant local memory:\n" + "\n".join(lines)
