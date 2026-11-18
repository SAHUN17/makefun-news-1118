"""Content of the 18 November 2026 edition, built from verified reporting.

Every headline below is a story published on Wednesday 18 November 2026 (RSS
pubDate), and every detail is that report's own summary sentence, trimmed to fit.
Nothing here is invented and nothing is a forecast.
"""

from render5 import Page, Story

PAGE = Page(
    lead=Story(
        kicker="THE GULF",
        head="US strikes Iran's Qeshm island as Tehran's drones hit Gulf states",
        detail="Iranian aerial attacks were intercepted over Bahrain and Kuwait while Washington hit the "
        "Strait of Hormuz island; the strait, the route for a fifth of the world's oil, is now the "
        "focus of the stalemated war.",
        art="burst",
        colour=(112, 40, 32),
    ),
    seconds=[
        Story(
            kicker="UKRAINE",
            head="Kyiv hits the Crimean bridge hours before Trump, Xi and Putin meet",
            detail="The strike is a display of strength as Kyiv fears the Shenzhen summit of the three "
            "leaders will heap pressure on it to accept a truce.",
            art="bridge",
            colour=(34, 58, 96),
        ),
        Story(
            kicker="CYBER",
            head="NSA network outage, Apple failures and hijacked sites rattle the web",
            detail="The spy agency's internal network degraded during maintenance, Apple fought outages "
            "across iCloud and the App Store, and BBC, IKEA and Air France pages were compromised "
            "to steal financial data.",
            art="globe",
            colour=(24, 74, 92),
        ),
    ],
    cards=[
        Story("SILICON VALLEY", "Nvidia rules out bringing Jensen Huang back after a bumper quarter",
              "The board said it does not intend to reinstate him while projecting $130bn of "
              "fourth-quarter revenue; the firm will also stop shipping Hopper chips to China.",
              "chart", (44, 78, 52)),
        Story("ISRAEL", "Eisenkot's bloc takes the Knesset speaker's chair from Netanyahu",
              "Matan Kahana was elected with the Arab bloc's backing, handing the bloc power to "
              "advance bills such as a probe of the October 7 attack.",
              "ballot", (54, 54, 96)),
        Story("CONGO", "Rival peace efforts fail to halt the fighting in the east",
              "Diplomatic pushes have not stopped the violence in eastern Congo, where civilians "
              "keep bearing the cost of the conflict.",
              "cross", (104, 40, 84)),
        Story("SHENZHEN", "APEC opens with Takaichi on the ice and Trump's tour under strain",
              "Japan's new premier meets a cold room at the China summit while cabinet feuds and a "
              "Kim Jong Un curveball shape the takeaways from the US president's Asia tour.",
              "plane", (108, 66, 30)),
        Story("SIBERIA", "Russian An-12 transport crashes with all 19 aboard dead",
              "The defence ministry said the military aircraft went down in the Kemerovo region of "
              "south-western Siberia.",
              "burst", (128, 62, 26)),
        Story("WASHINGTON", "Trump seeks $50bn to rebuild US aviation after a nationwide halt",
              "A technical failure stopped air travel on 13 November; the FAA has now paused "
              "installation of the gear blamed for it.",
              "plane", (38, 66, 58)),
    ],
    briefs=[
        ("GAZA", "Board of Peace warns the ceasefire faces collapse within days"),
        ("HAITI", "Gang violence blocks aid as child malnutrition worsens"),
        ("BRAZIL", "Rare images of an isolated Indigenous group highlight the threats it faces"),
        ("NEW YORK", "Forensic experts claim Epstein was strangled to death"),
        ("PERU", "Pope Leo forgives the pilgrim who struck his eye with a rosary"),
        ("DELHI", "Devotees wade through toxic foam in the Yamuna for Chhath"),
        ("ATLANTA", "US doctors lament a measles resurgence as eradication lapses"),
        ("CAMBRIDGE", "'Human' is named dictionary word of the year"),
        ("TOKYO", "Japan's trade gap narrows to ¥476.5bn despite energy imports"),
        ("SHANGHAI", "China's stock market suffers its worst month in a decade"),
        ("LONDON", "Sony defeats a £2bn claim over PlayStation Store pricing"),
        ("QUEBEC", "Government moves to ban religious symbols in schools"),
        ("TALLINN", "Estonia's plan to shut its Russian border splits families"),
        ("CHISINAU", "President says a Russian drone crossed the capital"),
        ("LONDON", "Britain sanctions eight firms building West Bank settlements"),
        ("BOGOTA", "Hegseth to visit Colombia with a delivery of military equipment"),
        ("WASHINGTON", "Pakistani man sentenced to 27 years over a plot to kill Trump"),
        ("MINNESOTA", "Suspect charged over an assault on a Somali American"),
        ("OXFORD", "Hundreds rally as the university hosts an academic accused of racism"),
        ("LONDON", "GTA VI leaker Arion Kurtaj pleads guilty to cybercrimes"),
        ("HOLLYWOOD", "Bezos says he was 'heavily involved' in casting the new Bond"),
        ("CALIFORNIA", "Waymo pulled from state freeways over an 'imminent hazard'"),
        ("MELBOURNE", "One Nation pledges a 90% cut to Australia's refugee intake"),
        ("TURIN", "Zverev beats Shelton to reach the ATP Finals semifinals"),
    ],
    note=[
        "Nine stories reported at length on this page, twenty-four more in brief below.",
        "Eighteen November, six continents: the world as it read on Wednesday.",
        "Disputed claims are attributed to the side that made them; nothing here is a forecast.",
    ],
    dots=[
        (56.3, 26.9), (36.5, 45.3), (-76.8, 39.1),
        (-122.0, 37.4), (35.2, 31.8), (15.3, -4.3),
        (114.1, 22.5), (86.0, 55.4), (-87.9, 41.9),
    ],
)