"""
Prints super clear instructions + the exact current value of the ONE manual adjust line.
User can copy the file name and search string.
"""

from showcase.layout import get_showcase_scripts, get_showcase_styles

s = get_showcase_styles()
sc = get_showcase_scripts()

print("=" * 70)
print("THE FILE WITH THE ADJUST LINE: showcase/layout.py")
print("=" * 70)
print()
print("To find it instantly: Open showcase/layout.py and search (Ctrl+F or Cmd+F) for:")
print()
print("    *** THE SINGLE LINE OF CODE TO MANUALLY ADJUST (for 50px above titles) ***")
print()
print("It is printed as a GIANT BANNER COMMENT right at the VERY BEGINNING")
print("of the big return string in TWO places:")
print("  1. Inside get_showcase_styles()  -- for the CSS var")
print("  2. Inside get_showcase_scripts() -- for the JS const")
print()
print("There are also banners in the module docstring at the absolute top of the file.")
print()
print("CURRENT VALUES (change the 50):")
print("-" * 40)
css_line = [ln.strip() for ln in s.splitlines() if "--showcase-title-gap" in ln][0]
print("CSS (in styles):", css_line)
js_line = [ln.strip() for ln in sc.splitlines() if "SHOWCASE_TITLE_GAP = " in ln][0]
print("JS  (in scripts):", js_line)
print()
print("After you change the number:")
print("  - Save the file")
print("  - Hard refresh the showcase in your browser (Ctrl+Shift+R / Cmd+Shift+R)")
print(
    "  - Click around the sidebar tabs to see the 50px (or your new value) breathing above titles"
)
print()
print("We also restored the previous beautiful 4.75rem padding-top + no extra top border line,")
print("fixed the scroll so tabs actually show their content (not blank),")
print("added force-consistent side padding so ALL pages center like overview,")
print("kept the agents graph re-init for sidebar width changes.")
print("The per-page team is normalizing the HTML containers for long-term cleanliness.")
print("=" * 70)
