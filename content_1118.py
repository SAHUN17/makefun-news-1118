"""Content of the 18 November 2026 edition.

DRAFT STATUS: the items below are placeholders carried over from the previous
day's edition, used only to measure the layout while the day is still young.
They must be replaced with the events of Wednesday 18 November 2026 before the
image is committed as `entry.png` and submitted.
"""

DRAFT = True

from render5 import Page, Story

PAGE = Page(
    lead=Story(
        kicker="EUROPE",
        head="Placeholder lead: the day's biggest story will sit here",
        detail="Two or three sentences that let a reader who missed the day follow the lead: "
        "what happened, where, and why it matters.",
        art="bridge",
        colour=(34, 58, 96),
    ),
    seconds=[
        Story(
            kicker="PLACEHOLDER",
            head="Second story, illustrated",
            detail="A sentence of context for the secondary package.",
            art="ship",
            colour=(24, 74, 92),
        ),
        Story(
            kicker="PLACEHOLDER",
            head="Third story, illustrated",
            detail="A sentence of context for the secondary package.",
            art="chart",
            colour=(44, 78, 52),
        ),
    ],
    cards=[
        Story("PLACEHOLDER", "Developed story one", "One line of detail under the headline.", "ballot", (54, 54, 96)),
        Story("PLACEHOLDER", "Developed story two", "One line of detail under the headline.", "cross", (104, 40, 84)),
        Story("PLACEHOLDER", "Developed story three", "One line of detail under the headline.", "flame", (128, 62, 26)),
        Story("PLACEHOLDER", "Developed story four", "One line of detail under the headline.", "plane", (108, 66, 30)),
        Story("PLACEHOLDER", "Developed story five", "One line of detail under the headline.", "globe", (38, 66, 58)),
        Story("PLACEHOLDER", "Developed story six", "One line of detail under the headline.", "burst", (122, 46, 34)),
    ],
    briefs=[
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "One-line brief that fills the lower band of the page"),
        ("REGION", "Second column brief with a slightly longer line of its own"),
        ("REGION", "Second column brief with a slightly longer line of its own"),
        ("REGION", "Second column brief with a slightly longer line of its own"),
        ("REGION", "Second column brief with a slightly longer line of its own"),
        ("REGION", "Second column brief with a slightly longer line of its own"),
        ("REGION", "Second column brief with a slightly longer line of its own"),
    ],
    note=[
        "Nine stories reported at length on the front page, twenty more in brief below.",
        "One day, six continents, one page: the world as it read on Wednesday.",
        "Disputed claims are attributed in the text; nothing here is a forecast.",
    ],
    dots=[
        (44.0, 33.0), (32.0, 49.0), (121.0, 15.0),
        (-74.0, 40.7), (77.0, 21.0), (35.0, 31.5),
        (-1.0, 52.5), (139.0, 35.7), (-58.0, -34.6),
    ],
)