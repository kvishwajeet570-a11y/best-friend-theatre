from pathlib import Path

file = Path("scenes/birthday_slides.py")

text = file.read_text(encoding="utf-8")

# A LITTLE MESSAGE
start = text.index('        lines = [', text.index('def _draw_message'))
end = text.index('        ]', start) + len('        ]')

new_message = '''        lines = [
            "Some bonds are not just made by moments,",
            "they are made by a lifetime of memories.",
            "",
            "You are not just my sister,",
            "you are a beautiful part of my life.",
            "",
            "Thank you for every smile,",
            "every little fight,",
            "and every unforgettable memory.",
            "",
            "Stay happy. Stay strong.",
            "Keep shining always.",
        ]'''

text = text[:start] + new_message + text[end:]

# FRIENDSHIP STATUS -> SISTER BOND
text = text.replace(
    '"FRIENDSHIP STATUS"',
    '"SISTER BOND"',
    1
)

text = text.replace(
    '"ACTIVE"',
    '"FOREVER"',
    1
)

text = text.replace(
    '"Same crazy"',
    '"Same family"',
    1
)

text = text.replace(
    '"Same silly"',
    '"Same craziness"',
    1
)

text = text.replace(
    '"Same supportive"',
    '"Same memories"',
    1
)

file.write_text(text, encoding="utf-8")

print("DONE - Sister messages updated successfully.")