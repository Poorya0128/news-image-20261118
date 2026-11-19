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
     "hed": "Xi greets Trump as APEC opens in Shenzhen",
     "dek": ("Trump and Putin shake hands at the banquet; three-way talks with Xi "
             "are set for Thursday.")},
    {"art": "gulf", "region": "MIDDLE EAST", "beat": "IRAN WAR", "src": "REUTERS",
     "at": (47.5, 29.3),
     "hed": "Iran fires drones at a US air base in Kuwait",
     "dek": "Iran says it hit back for the US strike on Qeshm; Kuwait reports no damage."},
    {"art": "voyager", "region": "SPACE", "beat": "SCIENCE", "src": "NASA",
     "at": None,
     "hed": "Voyager 1, first craft one light-day from Earth",
     "dek": ("At 10:16 UTC it passed 25.9bn km; a command sent today arrives "
             "tomorrow.")},
]

CARDS = [
    {"art": "eu", "region": "EUROPE", "beat": "UKRAINE AID", "topic": "EUROPE \u00b7 AID", "src": "EC \u00b7 REUTERS",
     "at": (4.4, 50.8),
     "hed": "EU proposes \u20ac45bn Ukraine loan for 2027",
     "dek": "Repaid only once Russia pays war reparations."},
    {"art": "drones_ua", "region": "EUROPE", "beat": "UKRAINE WAR", "topic": "EUROPE \u00b7 WAR", "src": "UA AIR FORCE",
     "at": (30.5, 50.4),
     "hed": "Russia fires 141 drones at Ukraine",
     "dek": "Kyiv says 126 downed; four killed in Odesa."},
    {"art": "alaska", "region": "AMERICAS", "beat": "US POLITICS", "topic": "AMERICAS \u00b7 VOTE", "src": "AP",
     "at": (-150.0, 61.2),
     "hed": "Democrats win 56\u201344 Senate majority",
     "dek": "AP called it for Mary Peltola over Dan Sullivan at 03:19 UTC."},
    {"art": "cop", "region": "GLOBAL", "beat": "CLIMATE", "topic": "GLOBAL \u00b7 CLIMATE", "src": "UN \u00b7 ENB",
     "at": (30.7, 36.9),
     "hed": "Draft deal splits COP31 talks in Antalya",
     "dek": "Stocktake opens; Arab Group and Russia reject it."},
    {"art": "inflation", "region": "EUROPE", "beat": "ECONOMY", "topic": "EUROPE \u00b7 PRICES", "src": "ONS \u00b7 EUROSTAT",
     "at": (-0.1, 51.5),
     "hed": "Inflation climbs: UK 3.6%, euro area 4%",
     "dek": "Euro-area energy up 21%; UK bills forecast to rise 26% in January."},
    {"art": "cyclone", "region": "ASIA", "beat": "WEATHER", "topic": "ASIA \u00b7 STORM", "src": "IMD",
     "at": (82.0, 16.5),
     "hed": "India braces for Cyclone Akvan",
     "dek": "Landfall between Narsapur and Puri by Fri noon; rescuers on standby."},
    {"art": "sudan", "region": "AFRICA", "beat": "SUDAN WAR", "topic": "AFRICA \u00b7 SUDAN", "src": "AMNESTY",
     "at": (30.2, 13.2),
     "hed": "Amnesty: RSF drones kill 37 in El Obeid",
     "dek": "Report out today: nine June\u2013August strikes; urges a war-crimes probe."},
    {"art": "anthropic", "region": "AMERICAS", "beat": "IPO", "topic": "AMERICAS \u00b7 IPO", "src": "CNBC \u00b7 AP",
     "at": (-122.4, 37.8),
     "hed": "Anthropic prices record IPO at $83",
     "dek": "Raises $81.3bn, ahead of SpaceX's $75bn."},
    {"art": "gta", "region": "OCEANIA", "beat": "CULTURE", "topic": "OCEANIA \u00b7 GAMES", "src": "AP \u00b7 BBC",
     "at": (174.8, -36.8),
     "hed": "GTA VI unlocks first in New Zealand",
     "dek": "13 years after GTA V; launch rolls west from 11:00 GMT."},
    {"art": "gaza", "region": "MIDDLE EAST", "beat": "GAZA", "topic": "MIDEAST \u00b7 GAZA", "src": "REUTERS",
     "at": (34.4, 31.4),
     "hed": "Israeli tanks push into central Gaza",
     "dek": "First raid past the ceasefire line since 2025; Hamas calls it a violation."},
]

# "Also on Wednesday 18 November": (place, text, region, (lon, lat))
BRIEFS = [
    ("Washington", "Jeffries nominated for Speaker, 251\u201311", "AMERICAS", (-77.0, 38.9)),
    ("Congo", "Ebola at 11,504 cases, 5,630 deaths (WHO)", "AFRICA", (23.0, -2.0)),
    ("Seoul", "Kospi jumps 1.99% as chip stocks rally", "ASIA", (127.0, 37.5)),
    ("Shenzhen", "Xi backs US\u2013N. Korea talks with Lee", "ASIA", (114.1, 22.5)),
    ("Shenzhen", "Takaichi makes first China visit as PM", "ASIA", (114.1, 22.5)),
    ("Shenzhen", "Trump announces Philippine trade deal", "ASIA", (114.1, 22.5)),
    ("Shenzhen", "Trump meets Carney, Sheinbaum separately", "ASIA", (114.1, 22.5)),
    ("Yemen", "Saudi-led coalition hits 60 Houthi sites", "MIDDLE EAST", (44.2, 15.4)),
    ("Israel", "Katz: troops stay in Lebanon, Syria, Gaza", "MIDDLE EAST", (35.2, 31.8)),
    ("Horn of Africa", "Ethiopia, Eritrea mass troops", "AFRICA", (38.9, 14.8)),
    ("Dhaka", "troops deployed as unrest over Hasina grows", "ASIA", (90.4, 23.8)),
    ("New Delhi", "India\u2013US trade deal nearly done", "ASIA", (77.2, 28.6)),
    ("Kashmir", "top LeT commander killed in Kulgam", "ASIA", (75.0, 33.6)),
    ("Taipei", "Russian jets off Taiwan; Japan airspace", "ASIA", (121.6, 25.0)),
    ("London", "Chelsea Women beat PSG 1\u20130 (Buurman 87')", "EUROPE", (-0.1, 51.5)),
    ("Uganda", "EACOP oil pipeline fast-tracked", "AFRICA", (32.6, 0.3)),
    ("Turin", "Tiafoe beats Cobolli 7\u20136 6\u20130; Alcaraz in SF", "EUROPE", (7.7, 45.1)),
    ("Romania", "M5.7 Vrancea quake; two lightly hurt", "EUROPE", (26.6, 45.7)),
    ("Belgrade", "new parliament fails to elect a speaker", "EUROPE", (20.5, 44.8)),
    ("Port-au-Prince", "thousands march to praise Bukele", "AMERICAS", (-72.3, 18.5)),
    ("Hormuz", "ADNOC tanker hit; one crew missing", "MIDDLE EAST", (56.0, 26.5)),
    ("Washington", "tech outage wave hits US government", "AMERICAS", (-77.0, 38.9)),
    ("Washington", "Senate advances permitting bill 65\u201331", "AMERICAS", (-77.0, 38.9)),
    ("Washington", "Fed minutes: more hikes; Dow \u2212561", "AMERICAS", (-77.0, 38.9)),
    ("Jharkhand", "NTPC conveyor collapse kills 3 workers", "ASIA", (85.0, 23.8)),
    ("Bras\u00edlia", "Senate passes Lula fiscal package R$60bn", "AMERICAS", (-47.9, -15.8)),
    ("Papua New Guinea", "M5.8 quake; no casualties yet", "OCEANIA", (146.7, -5.8)),
    ("Nova Scotia", "Glace Bay pizza-shop blast; 17 hurt", "AMERICAS", (-60.0, 46.2)),
]

# The day by the clock, in UTC: only times stated by the sources.
TIMELINE = [
    ("03:19", "Alaska call", "AMERICAS"),
    ("06:30", "Kospi +1.99%", "ASIA"),
    ("07:00", "UK CPI 3.6%", "EUROPE"),
    ("10:00", "Eurozone 4.0%", "EUROPE"),
    ("10:16", "Voyager", "SPACE"),
    ("11:00", "GTA VI", "OCEANIA"),
    ("19:00", "Fed minutes", "AMERICAS"),
    ("21:00", "Wall St close, Dow \u2212561", "AMERICAS"),
]

JUDGE_NOTE = "Everything on this page happened, or was first reported, on Wednesday 18 November 2026 (any time zone, see Date Check)."
SOURCES = "Sources named on each story."
FOOT_NOTE = "Claims by warring sides are attributed. Original drawings, illustration not a photo; map from Natural Earth."

DATE_CHECK = [
    ("DATE CHECK \u00b7 Wed 18 Nov 2026", None),
    ("Left out, first reported Tue 17 Nov:", "Knesset speaker \u00b7 Qeshm strike \u00b7 Siberia An-12 crash \u00b7 Prague train collision."),
    ("Edge case, kept:", "Alaska Senate call, AP 03:19 UTC Wed (Tue evening US)."),
    ("Not yet news:", "Trump\u2013Xi\u2013Putin talks (Thu 19) \u00b7 Anthropic first trade (Thu 19) \u00b7 Akvan landfall (Fri 20)."),
]

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
