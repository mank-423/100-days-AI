
from pathlib import Path


class Memory:

    def __init__(self):
        # Store memory folder in the project root
        self.mem = Path(__file__).resolve().parent.parent / "memory"
        self.mem.mkdir(parents=True, exist_ok=True)

    def _path(self, name):
        # Sanitize the filename
        safe = "".join(
            ch for ch in name
            if ch.isalnum() or ch in "-_"
        )

        if not safe:
            raise ValueError("Invalid memory note name")

        return self.mem / f"{safe}.md"

    def write_note(self, name, text):
        path = self._path(name)

        path.write_text(text, encoding="utf-8")

        return f"Saved: {name}"

    def read_note(self, name):
        path = self._path(name)

        if not path.exists():
            return f"Note not found: {name}"

        return path.read_text(encoding="utf-8")

    def list_notes(self):
        notes = sorted(
            path.stem
            for path in self.mem.glob("*.md")
        )

        return ", ".join(notes) if notes else "No notes yet"


# --------------------------------------------------
# 1. Create the Memory object
# --------------------------------------------------

memory = Memory()


# --------------------------------------------------
# 2. Define tools available to Claude
# --------------------------------------------------

MEMORY_TOOLS = [
    {
        "name": "list_notes",
        "description": "List saved memory notes.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "read_note",
        "description": "Read one memory note by name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "write_note",
        "description": "Save or overwrite a durable note about the student.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "text": {"type": "string"}
            },
            "required": ["name", "text"]
        }
    }
]


# --------------------------------------------------
# 3. Connect tool names to Python methods
# --------------------------------------------------

MEMORY_HANDLERS = {
    "list_notes": memory.list_notes,
    "read_note": memory.read_note,
    "write_note": memory.write_note
}


# --------------------------------------------------
# 4. Test the memory system
# --------------------------------------------------

if __name__ == "__main__":

    print("Writing memory notes...\n")

    print(memory.write_note(
        "learning_goals",
        "The student is learning Python, RAG and AI agents."
    ))

    print(memory.write_note(
        "preferences",
        "Explain concepts using simple language and practical examples."
    ))

    print("\nAvailable notes:")
    print(memory.list_notes())

    print("\nReading learning_goals:")
    print(memory.read_note("learning_goals"))

    print("\nReading preferences:")
    print(memory.read_note("preferences"))
