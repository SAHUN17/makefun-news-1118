"""Content of the 18 November 2026 edition, built from verified reporting.

Every headline below is a story published on Wednesday 18 November 2026 (RSS
pubDate), and every detail is that report's own summary sentence, cut to the
clause that fits, so no card ends mid-thought. Nothing here is invented and
nothing is a forecast.
"""

from render6 import Page, Story

PAGE = Page(
    lead=Story(
        kicker="THE GULF",
        head="US strikes Iran's Qeshm island as drones hit Gulf states",
        detail="Iranian attacks were intercepted over Bahrain and Kuwait; a fifth of the "
        "world's oil moves through the strait.",
        art="burst",
        colour=(112, 40, 32),
    ),
    seconds=[
        Story(
            kicker="UKRAINE",
            head="Kyiv hits the Crimean bridge hours before a Trump-Xi-Putin summit",
            detail="A show of strength before Shenzhen, where Kyiv fears pressure to accept "
            "a truce.",
            art="bridge",
            colour=(34, 58, 96),
        ),
        Story(
            kicker="CYBER",
            head="NSA outage, Apple failures and hijacked sites rattle the web",
            detail="BBC, IKEA and Air France pages were compromised to steal financial data.",
            art="globe",
            colour=(24, 74, 92),
        ),
    ],
    cards=[
        Story("SILICON VALLEY", "Nvidia rules out bringing Jensen Huang back",
              "Bumper quarter, $130bn guided for the fourth.", "chart", (44, 78, 52)),
        Story("ISRAEL", "Eisenkot's bloc takes the Knesset speaker's chair",
              "Kahana won with the Arab bloc's backing.", "ballot", (54, 54, 96)),
        Story("CONGO", "Rival peace efforts fail to halt fighting in the east",
              "Pushes have not stopped the violence.", "cross", (104, 40, 84)),
        Story("SHENZHEN", "APEC opens with Takaichi on the ice",
              "Japan's new premier meets a cold room in China.", "star",
              (108, 66, 30)),
        Story("SIBERIA", "Russian An-12 military transport crashes, 19 dead",
              "It went down in the Kemerovo region, the ministry said.", "plane",
              (128, 62, 26)),
        Story("WASHINGTON", "Trump seeks $50bn to rebuild US aviation",
              "The FAA paused the gear blamed for the 13 November halt.", "factory",
              (38, 66, 58)),
    ],
    briefs=[
        ("GAZA", "Ceasefire 'could collapse in days'"),
        ("HAITI", "Gangs block aid; malnutrition worsens"),
        ("BRAZIL", "Rare images of an isolated tribe"),
        ("NEW YORK", "Experts: Epstein was strangled"),
        ("PERU", "Pope forgives rosary pilgrim"),
        ("DELHI", "Devotees wade through toxic foam"),
        ("ATLANTA", "Measles resurgence alarms doctors"),
        ("CAMBRIDGE", "'Human' is word of the year"),
        ("TOKYO", "Trade gap narrows to ¥476.5bn"),
        ("SHANGHAI", "Worst month for stocks in a decade"),
        ("LONDON", "Sony defeats £2bn store claim"),
        ("QUEBEC", "Religious symbols ban in schools"),
        ("TALLINN", "Russian border closure splits families"),
        ("CHISINAU", "Russian drone crossed the capital"),
        ("LONDON", "Sanctions on settlement builders"),
        ("BOGOTA", "Hegseth to deliver equipment"),
        ("WASHINGTON", "27 years for a plot to kill Trump"),
        ("MINNESOTA", "Charge over assault on a Somali"),
        ("OXFORD", "Rally over an accused academic"),
        ("LONDON", "GTA VI leaker pleads guilty"),
        ("HOLLYWOOD", "Bezos 'heavily involved' in Bond"),
        ("CALIFORNIA", "Waymo pulled over 'imminent hazard'"),
        ("MELBOURNE", "One Nation: 90% refugee cut"),
        ("TURIN", "Zverev into the ATP semifinals"),
    ],
    note=[
        "Nine stories at length above, twenty-four more in brief at right.",
        "Six continents on one page: the world as it read on Wednesday.",
        "Disputed claims are attributed; nothing here is a forecast.",
    ],
    dots=[
        (56.3, 26.9), (36.5, 45.3), (-76.8, 39.1),
        (-122.0, 37.4), (35.2, 31.8), (15.3, -4.3),
        (114.1, 22.5), (86.0, 55.4), (-87.9, 41.9),
    ],
)