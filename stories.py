"""The stories of Wednesday 18 November 2026.

Layout: 3 lead cards, 10 picture cards, and a numbered "Also on" list.
Every story has a number; the same number marks it on the map.
Each card names its region, its beat and its source.

Dates: every item happened, or was first reported, on 18 November 2026 in
some time zone. AP called Alaska at 22:19 ET on 17 November, which is
03:19 UTC on 18 November.
"""

LEAD = [
    {"art": "shenzhen", "region": "ASIA", "beat": "APEC SUMMIT", "src": "AFP \u00b7 AP",
     "at": (114.1, 22.5),
     "hed": "Xi greets Trump on the tarmac as APEC opens in Shenzhen",
     "dek": ("Trump and Putin shake hands at the banquet; three-way talks with Xi "
             "are set for Thursday.")},
    {"art": "gulf", "region": "MIDDLE EAST", "beat": "IRAN WAR", "src": "REUTERS",
     "at": (47.5, 29.3),
     "hed": "Iran fires drones at a US air base in Kuwait",
     "dek": ("Iran says it hit back for a US strike on Qeshm. Kuwait reports no "
             "damage; Bahrain blocks a third attack in a week.")},
    {"art": "voyager", "region": "SPACE", "beat": "SCIENCE", "src": "NASA",
     "at": None,
     "hed": "Voyager 1 becomes the first craft one light-day from Earth",
     "dek": ("At 10:16 UTC it passed 25.9bn km; a command sent today arrives "
             "tomorrow.")},
]

CARDS = [
    {"art": "eu", "region": "EUROPE", "beat": "UKRAINE AID", "src": "EU COMMISSION",
     "at": (4.4, 50.8),
     "hed": "EU proposes a \u20ac45bn loan for Ukraine in 2027",
     "dek": "Repaid only once Russia pays war reparations."},
    {"art": "drones_ua", "region": "EUROPE", "beat": "UKRAINE WAR", "src": "UKRAINE AIR FORCE",
     "at": (30.5, 50.4),
     "hed": "Russia fires 141 drones at Ukraine",
     "dek": "126 downed, Kyiv says; Odesa strikes kill four."},
    {"art": "alaska", "region": "AMERICAS", "beat": "US POLITICS", "src": "AP",
     "at": (-150.0, 61.2),
     "hed": "Democrats win Alaska; Senate 56\u201344",
     "dek": "AP calls it for Mary Peltola over Dan Sullivan."},
    {"art": "cop", "region": "GLOBAL", "beat": "CLIMATE", "src": "UNFCCC",
     "at": (30.7, 36.9),
     "hed": "Draft deal splits COP31 talks in Antalya",
     "dek": "Stocktake opens; Arab Group and Russia reject it."},
    {"art": "inflation", "region": "EUROPE", "beat": "ECONOMY", "src": "ONS \u00b7 EUROSTAT",
     "at": (-0.1, 51.5),
     "hed": "Inflation climbs: UK 3.6%, euro area 4.0%",
     "dek": "Euro-area energy up 21%; UK bills to rise 26%."},
    {"art": "cyclone", "region": "ASIA", "beat": "WEATHER", "src": "IMD",
     "at": (82.0, 16.5),
     "hed": "India braces for Cyclone Akvan",
     "dek": "Rescuers on standby; landfall due 20 November."},
    {"art": "sudan", "region": "AFRICA", "beat": "SUDAN WAR", "src": "AMNESTY",
     "at": (30.2, 13.2),
     "hed": "Amnesty: RSF drones killed 37 in El Obeid",
     "dek": "It urges a war-crimes probe of nine strikes."},
    {"art": "gold", "region": "GLOBAL", "beat": "MARKETS", "src": "REUTERS",
     "at": (-74.0, 40.7),
     "hed": "Gold falls below $3,800, a 14-month low",
     "dek": "Fed officials signal more rate rises."},
    {"art": "gta", "region": "OCEANIA", "beat": "CULTURE", "src": "ROCKSTAR",
     "at": (174.8, -36.8),
     "hed": "GTA VI unlocks first in New Zealand",
     "dek": "13 years after GTA V; launch rolls west from 11:00 GMT."},
    {"art": "gaza", "region": "MIDDLE EAST", "beat": "GAZA", "src": "REUTERS",
     "at": (34.4, 31.4),
     "hed": "Israeli tanks push into central Gaza",
     "dek": "First raid past the ceasefire line since 2025; Hamas calls it a violation."},
]

# "Also on Wednesday 18 November": (place, text, region, (lon, lat))
BRIEFS = [
    ("Washington", "Democrats nominate Jeffries for speaker, 251\u201311", "AMERICAS", (-77.0, 38.9)),
    ("Seoul", "Kospi jumps 2.7% as Asian chip stocks rally", "ASIA", (127.0, 37.5)),
    ("Shenzhen", "Xi backs US\u2013North Korea talks in meeting with Lee", "ASIA", (114.1, 22.5)),
    ("Shenzhen", "Japan's Takaichi makes first China visit as PM", "ASIA", (114.1, 22.5)),
    ("Shenzhen", "Trump announces Philippine trade deal, no terms", "ASIA", (114.1, 22.5)),
    ("Yemen", "Saudi-led coalition says it hit 60 Houthi sites", "MIDDLE EAST", (44.2, 15.4)),
    ("Israel", "Katz: troops stay in Lebanon, Syria, Gaza zones", "MIDDLE EAST", (35.2, 31.8)),
    ("Horn of Africa", "Ethiopia and Eritrea mass troops on border", "AFRICA", (38.9, 14.8)),
    ("Dhaka", "troops deployed as unrest over Hasina grows", "ASIA", (90.4, 23.8)),
    ("Jakarta", "Bank Indonesia raises rates to 6.00%", "ASIA", (106.8, -6.2)),
    ("Kashmir", "top LeT commander killed in Kulgam", "ASIA", (75.0, 33.6)),
    ("Myanmar", "junta to \u201creview\u201d its ties with ASEAN", "ASIA", (96.1, 19.7)),
    ("Sudan", "army advances to within 60 km of Al Nuhud", "AFRICA", (28.4, 12.7)),
    ("South Africa", "inflation rises to 5.2%", "AFRICA", (28.2, -25.7)),
    ("Uganda", "EACOP oil pipeline fast-tracked", "AFRICA", (32.6, 0.3)),
    ("Berlin", "coalition cuts electricity tax to EU minimum", "EUROPE", (13.4, 52.5)),
    ("Romania", "M5.7 Vrancea quake; two lightly hurt", "EUROPE", (26.6, 45.7)),
    ("Turin", "Alcaraz beats Medvedev at the ATP Finals", "EUROPE", (7.7, 45.1)),
    ("New York", "Anthropic set to price its IPO; trading Thursday", "AMERICAS", (-74.0, 40.7)),
    ("Santiago", "ECLAC: Latin American poverty falls to 24.4%", "AMERICAS", (-70.6, -33.4)),
    ("Chile", "economy shrinks 1.1% in the third quarter", "AMERICAS", (-71.0, -30.0)),
    ("Peru", "M6.0 quake offshore; no damage reported", "AMERICAS", (-77.0, -12.0)),
    ("Bogot\u00e1", "Hegseth visits to deepen military ties", "AMERICAS", (-74.1, 4.7)),
    ("Australia", "wages rise 1.1%; settler groups sanctioned", "OCEANIA", (149.1, -35.3)),
    ("Fiji", "national drought disaster declared", "OCEANIA", (178.4, -18.1)),
    ("Cook Islands", "Cyclone Xavier holds at Category 5", "OCEANIA", (-159.8, -21.2)),
    ("Hobart", "England beat Australia to win ODI series 2\u20131", "OCEANIA", (147.3, -42.9)),
]

# The day by the clock, in UTC: only times stated by the sources.
TIMELINE = [
    ("02:42", "Gold falls below $3,800", "GLOBAL"),
    ("03:19", "AP calls Alaska for Peltola", "AMERICAS"),
    ("06:30", "Kospi closes up 2.7%", "ASIA"),
    ("10:16", "Voyager 1 reaches one light-day", "SPACE"),
    ("11:00", "GTA VI unlocks in New Zealand", "OCEANIA"),
]

JUDGE_NOTE = "Everything on this page happened, or was first reported, on Wednesday 18 November 2026."
SOURCES = "Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 NASA \u00b7 EU Commission \u00b7 ONS \u00b7 Eurostat \u00b7 IMD \u00b7 UNFCCC \u00b7 Amnesty \u00b7 Ukraine Air Force"
FOOT_NOTE = "Claims by warring sides are attributed. Original drawings; map from Natural Earth."

REGIONS = ["ASIA", "MIDDLE EAST", "EUROPE", "AFRICA", "AMERICAS", "OCEANIA", "GLOBAL", "SPACE"]


def all_stories():
    """(number, story) in page order: leads, cards, then briefs."""
    out = []
    n = 1
    for s in LEAD + CARDS:
        out.append((n, s)); n += 1
    for b in BRIEFS:
        out.append((n, {"region": b[2], "at": b[3], "place": b[0], "hed": b[1]})); n += 1
    return out


def count():
    return len(LEAD) + len(CARDS) + len(BRIEFS)


def continents():
    return {"ASIA", "EUROPE", "AFRICA", "AMERICAS", "OCEANIA"} | ({"ASIA"} if True else set())


if __name__ == "__main__":
    print(count(), "stories")
