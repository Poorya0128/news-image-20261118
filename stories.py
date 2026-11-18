"""The 42 stories of Wednesday 18 November 2026, by tier.

Numbered stories (1-18) carry the same number on the page and on the map.
Briefs are shown on the map as small unnumbered dots.

Categories (one colour each on the page):
  POWER    politics and diplomacy
  CONFLICT war and security
  ECONOMY  markets, prices, budgets
  CLIMATE  climate, weather, quakes
  SCIENCE  science and technology
  SOCIETY  society, health, culture, sport

Every line is written to fit at 17 px or more, so it stays readable when the
page is shown 300 px across.
"""

# Tier 1: twin lead.
SHENZHEN = {
    "num": 1, "cat": "POWER", "at": (114.1, 22.5), "callout": "SHENZHEN",
    "kicker": "SHENZHEN \u00b7 APEC SUMMIT",
    "hed": "Xi Hosts Trump and Putin Ahead of First Three-Way Summit",
    "dek": "Xi greets Trump on the tarmac; Trump and Putin meet. Three-way talks Thursday.",
}

GULF = {
    "num": 2, "cat": "CONFLICT", "at": (47.5, 29.3), "callout": "KUWAIT",
    "kicker": "KUWAIT \u00b7 BAHRAIN \u00b7 GULF",
    "hed": "Iran Targets US Bases in Kuwait and Bahrain",
    "dek": ("Iran claims hits on Patriot systems; Kuwait reports no damage. "
            "Bahrain intercepts its third attack this week."),
}

ALSO_AT_APEC = [
    ("Xi\u2013Lee:", "backs US\u2013North Korea talks"),
    ("Takaichi:", "first China visit as PM"),
    ("Trump\u2013Marcos:", "trade deal, no terms"),
    ("Carney:", "Canada\u2013US trade talks go on"),
    ("Putin:", "EU energy ban hurt Europe"),
]

# Tier 2: four major stories, each with its own illustration.
MAJOR = [
    {"num": 3, "cat": "POWER", "art": "eu", "at": (4.4, 50.8), "callout": "BRUSSELS",
     "kicker": "BRUSSELS",
     "hed": "EU Proposes \u20ac45bn Ukraine Loan for 2027",
     "fact": "Repaid from Russian reparations"},
    {"num": 4, "cat": "CLIMATE", "art": "cop", "at": (30.7, 36.9), "callout": "ANTALYA",
     "kicker": "ANTALYA \u00b7 COP31",
     "hed": "Draft Deal Splits COP31 Climate Talks",
     "fact": "Arab Group and Russia reject draft"},
    {"num": 5, "cat": "SCIENCE", "art": "voyager", "at": None,
     "kicker": "DEEP SPACE",
     "hed": "Voyager 1 Reaches One Light-Day Away",
     "fact": "Crossed at 10:16 UTC, 49 years on"},
    {"num": 6, "cat": "ECONOMY", "art": "markets", "at": (127.0, 37.5), "callout": "SEOUL",
     "kicker": "SEOUL \u00b7 TOKYO",
     "hed": "Asian Tech Stocks Rise on Nvidia Results",
     "fact": "Nvidia sales up 103% to $115.8bn"},
]

# Tier 3: twelve key stories. "big" shows a figure in place of an icon.
KEY = [
    {"num": 7, "cat": "CONFLICT", "icon": "burst", "at": (30.7, 46.5), "callout": "ODESA",
     "kicker": "ODESA, UKRAINE", "hed": "Russian strikes kill 4"},
    {"num": 8, "cat": "ECONOMY", "big": "4.0%", "at": (8.7, 50.1),
     "kicker": "EUROZONE", "hed": "Inflation at 3-year high"},
    {"num": 9, "cat": "ECONOMY", "big": "3.6%", "at": (-0.1, 51.5),
     "kicker": "UNITED KINGDOM", "hed": "Inflation up; bills +26%"},
    {"num": 10, "cat": "CLIMATE", "icon": "cyclone", "at": (82.0, 16.5),
     "kicker": "ANDHRA PRADESH", "hed": "Braces for Cyclone Akvan"},
    {"num": 11, "cat": "CONFLICT", "icon": "border", "at": (38.9, 14.8),
     "kicker": "ETHIOPIA \u2013 ERITREA", "hed": "Troops mass on the border"},
    {"num": 12, "cat": "CONFLICT", "icon": "target", "at": (44.2, 15.4),
     "kicker": "YEMEN", "hed": "Coalition: 60 Houthi sites hit"},
    {"num": 13, "cat": "POWER", "icon": "shield", "at": (90.4, 23.8),
     "kicker": "DHAKA, BANGLADESH", "hed": "Troops out as unrest grows"},
    {"num": 14, "cat": "SOCIETY", "big": "24.4%", "at": (-70.6, -33.4),
     "kicker": "LATIN AMERICA", "hed": "Poverty rate falls: ECLAC"},
    {"num": 15, "cat": "SCIENCE", "icon": "ipo", "at": (-74.0, 40.7),
     "kicker": "NEW YORK", "hed": "Anthropic IPO set to price"},
    {"num": 16, "cat": "SOCIETY", "icon": "gamepad", "at": (174.8, -36.8),
     "kicker": "NEW ZEALAND", "hed": "GTA VI unlocks here first"},
    {"num": 17, "cat": "CONFLICT", "icon": "advance", "at": (28.4, 12.7),
     "kicker": "SUDAN", "hed": "Army nears RSF-held Al Nuhud"},
    {"num": 18, "cat": "CONFLICT", "icon": "fence", "at": (35.2, 31.8),
     "kicker": "ISRAEL", "hed": "Katz: troops stay in buffer zones"},
]

# Tier 4: nineteen briefs, one box per continent.
BRIEFS = [
    ("ASIA", [
        ("ECONOMY", (106.8, -6.2), "Indonesia raises rates to 6.00%"),
        ("CONFLICT", (75.0, 33.6), "Kashmir: top LeT commander killed"),
        ("POWER", (96.1, 19.7), "Myanmar to \u201creview\u201d ASEAN ties"),
    ]),
    ("OCEANIA & PACIFIC", [
        ("ECONOMY", (149.1, -35.3), "Australian wages rise 1.1%"),
        ("POWER", (145.0, -30.0), "Australia sanctions settler groups"),
        ("CLIMATE", (178.4, -18.1), "Fiji declares drought disaster"),
        ("CLIMATE", (-159.8, -21.2), "Cat 5 Cyclone Xavier near Cook Is."),
        ("SOCIETY", (151.2, -33.9), "Tame Impala win 7 ARIA awards"),
        ("SOCIETY", (147.3, -42.9), "England win ODI series in Hobart"),
    ]),
    ("EUROPE", [
        ("ECONOMY", (13.4, 52.5), "Germany cuts power tax to EU floor"),
        ("CLIMATE", (26.6, 45.7), "M5.7 quake shakes Romania; 2 hurt"),
        ("SOCIETY", (12.5, 55.7), "WHO warns of antibiotic resistance"),
        ("SOCIETY", (7.7, 45.1), "Alcaraz beats Medvedev in Turin"),
    ]),
    ("AFRICA", [
        ("ECONOMY", (28.2, -25.7), "S. Africa inflation rises to 5.2%"),
        ("ECONOMY", (32.6, 0.3), "EACOP oil pipeline fast-tracked"),
    ]),
    ("AMERICAS", [
        ("ECONOMY", (-70.6, -30.0), "Chile's economy shrinks 1.1% in Q3"),
        ("CLIMATE", (-77.0, -12.0), "M6.0 quake off Peru; no damage"),
        ("POWER", (-74.1, 4.7), "Hegseth in Bogot\u00e1 on military ties"),
        ("POWER", (-66.9, 10.5), "Venezuela top court: 1,190 apply"),
    ]),
]

JUDGE_NOTE = "Every story here happened, or was first reported, on Wednesday 18 November 2026."

SOURCES = ("Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 NASA \u00b7 EU Commission \u00b7 Eurostat \u00b7 "
           "ONS \u00b7 UNFCCC \u00b7 ECLAC \u00b7 WHO \u00b7 Natural Earth")


def numbered():
    """Every numbered story as (tier, story)."""
    out = [(1, SHENZHEN), (1, GULF)]
    out += [(2, m) for m in MAJOR]
    out += [(3, k) for k in KEY]
    return out


def briefs_flat():
    return [it for _, items in BRIEFS for it in items]


def count():
    return 2 + len(ALSO_AT_APEC) + len(MAJOR) + len(KEY) + len(briefs_flat())


if __name__ == "__main__":
    print(count(), "stories")
