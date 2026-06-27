"""
Fix election data: Replace synthetic/fabricated 2025 Bihar election results 
with real winner data scraped from MyNeta (ADR).

This script:
1. Parses the MyNeta winners HTML to extract real winner names, constituencies, and parties
2. Maps MyNeta constituency names → AC numbers from our database
3. Updates the raw JSONL files with correct winner_name and winner_party
4. Uploads corrected data to Supabase
"""

import os
import re
import json
import sys
from pathlib import Path
from html import unescape

# ---------- STEP 1: Parse MyNeta HTML ----------

def parse_myneta_html(html_path: str) -> list[dict]:
    """Parse the MyNeta winners page HTML and extract winner info."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    winners = []
    
    # Pattern to match table rows with winner data
    # Each row has: <td>Sno</td><td><a href=...>CandidateName</a></td><td>CONSTITUENCY</td><td>Party</td>
    # The candidate name is inside nested <a> tags
    row_pattern = re.compile(
        r'<tr[^>]*>\s*'
        r'<td>(\d+)</td>\s*'                                    # Serial number
        r'<td>.*?bihar2025/candidate\.php\?candidate_id=\d+>([^<]+)</a>.*?</td>'  # Candidate name
        r'<td>([^<]+)</td>\s*'                                  # Constituency  
        r'<td>([^<]+)</td>',                                    # Party
        re.DOTALL
    )
    
    for match in row_pattern.finditer(html):
        sno = int(match.group(1))
        candidate_name = unescape(match.group(2)).strip()
        constituency = unescape(match.group(3)).strip()
        party = unescape(match.group(4)).strip()
        
        winners.append({
            "sno": sno,
            "candidate_name": candidate_name,
            "constituency": constituency,
            "party": party
        })
    
    return winners


def normalize_for_matching(name: str) -> str:
    """Normalize a constituency name for fuzzy matching."""
    s = name.upper().strip()
    # Remove (SC), (ST) suffixes
    s = re.sub(r'\s*\(SC\)\s*', '', s)
    s = re.sub(r'\s*\(ST\)\s*', '', s)
    s = s.strip()
    return s


def standardize_party(party_full: str) -> str:
    """Convert full party names to standard abbreviations used in our database."""
    mapping = {
        "BJP": "BJP",
        "JD(U)": "JD(U)",
        "RJD": "RJD",
        "INC": "INC",
        "Lok Janshakti Party (Ram Vilas)": "LJP(RV)",
        "All India Majlis-E-Ittehadul Muslimeen": "AIMIM",
        "Hindustani Awam Morcha (Secular)": "HAM(S)",
        "Rashtriya Lok Morcha": "RLM",
        "Communist Party of India (Marxist-Leninist) (Liberation)": "CPI(ML)(L)",
        "Communist Party of India (Marxist)": "CPI(M)",
        "Bahujan Samaj Party": "BSP",
        "Indian Inclusive Party": "IIP",
        "Independent": "IND",
    }
    return mapping.get(party_full, party_full)


# ---------- STEP 2: Map constituencies ----------

# AC number → constituency name mapping from the database
AC_MAP = {
    1: "Valmiki Nagar", 2: "Ramnagar", 3: "Narkatiaganj", 4: "Bagaha", 5: "Lauriya",
    6: "Nautan", 7: "Chanpatia", 8: "Bettiah", 9: "Sikta", 10: "Raxaul",
    11: "Sugauli", 12: "Narkatiya", 13: "Harsidhi", 14: "Govindganj", 15: "Kesaria",
    16: "Kalyanpur", 17: "Pipra", 18: "Madhuban", 19: "Motihari", 20: "Chiraia",
    21: "Dhaka", 22: "Sheohar", 23: "Riga", 24: "Bathnaha", 25: "Parihar",
    26: "Sursand", 27: "Bajpatti", 28: "Sitamarhi", 29: "Runnisaidpur", 30: "Belsand",
    31: "Harlakhi", 32: "Benipatti", 33: "Khajauli", 34: "Babubarhi", 35: "Bisfi",
    36: "Madhubani", 37: "Rajnagar", 38: "Jhanjharpur", 39: "Phulparas", 40: "Laukaha",
    41: "Nirmali", 42: "Pipra", 43: "Supaul", 44: "Triveniganj", 45: "Chhatapur",
    46: "Narpatganj", 47: "Raniganj", 48: "Forbesganj", 49: "Araria", 50: "Jokihat",
    51: "Sikti", 52: "Bahadurganj", 53: "Thakurganj", 54: "Kishanganj", 55: "Kochadhaman",
    56: "Amour", 57: "Baisi", 58: "Kasba", 59: "Banmankhi", 60: "Rupauli",
    61: "Dhamdaha", 62: "Purnia", 63: "Katihar", 64: "Kadwa", 65: "Balrampur",
    66: "Pranpur", 67: "Manihari", 68: "Barari", 69: "Korha", 70: "Alamnagar",
    71: "Bihariganj", 72: "Singheshwar", 73: "Madhepura", 74: "Sonbarsha", 75: "Saharsa",
    76: "Simri Bakhtiarpur", 77: "Mahishi", 78: "Kusheshwar Asthan", 79: "Gaura Bauram",
    80: "Benipur", 81: "Alinagar", 82: "Darbhanga Rural", 83: "Darbhanga", 84: "Hayaghat",
    85: "Bahadurpur", 86: "Keoti", 87: "Jale", 88: "Gaighat", 89: "Aurai",
    90: "Minapur", 91: "Bochahan", 92: "Sakra", 93: "Kurhani", 94: "Muzaffarpur",
    95: "Kanti", 96: "Baruraj", 97: "Paroo", 98: "Sahebganj", 99: "Baikunthpur",
    100: "Barauli", 101: "Gopalganj", 102: "Kuchaikote", 103: "Bhore", 104: "Hathua",
    105: "Siwan", 106: "Ziradei", 107: "Darauli", 108: "Raghunathpur", 109: "Daraunda",
    110: "Barharia", 111: "Goriakothi", 112: "Maharajganj", 113: "Ekma", 114: "Manjhi",
    115: "Baniapur", 116: "Taraiya", 117: "Marhaura", 118: "Chapra", 119: "Garkha",
    120: "Amnour", 121: "Parsa", 122: "Sonpur", 123: "Hajipur", 124: "Lalganj",
    125: "Vaishali", 126: "Mahua", 127: "Raja Pakar", 128: "Raghopur", 129: "Mahnar",
    130: "Patepur", 131: "Kalyanpur", 132: "Warisnagar", 133: "Samastipur", 134: "Ujiarpur",
    135: "Morwa", 136: "Sarairanjan", 137: "Mohiuddinnagar", 138: "Bibhutipur", 139: "Rosera",
    140: "Hasanpur", 141: "Cheria-Bariarpur", 142: "Bachhwara", 143: "Teghra", 144: "Matihani",
    145: "Sahebpur Kamal", 146: "Begusarai", 147: "Bakhri", 148: "Alauli", 149: "Khagaria",
    150: "Beldaur", 151: "Parbatta", 152: "Bihpur", 153: "Gopalpur", 154: "Pirpainti",
    155: "Kahalgaon", 156: "Bhagalpur", 157: "Sultanganj", 158: "Nathnagar", 159: "Amarpur",
    160: "Dhoraiya", 161: "Banka", 162: "Katoria", 163: "Belhar", 164: "Tarapur",
    165: "Munger", 166: "Jamalpur", 167: "Suryagarha", 168: "Lakhisarai", 169: "Sheikhpura",
    170: "Barbigha", 171: "Asthawan", 172: "Biharsharif", 173: "Rajgir", 174: "Islampur",
    175: "Hilsa", 176: "Nalanda", 177: "Harnaut", 178: "Mokama", 179: "Barh",
    180: "Bakhtiarpur", 181: "Digha", 182: "Bankipur", 183: "Kumhrar", 184: "Patna Sahib",
    185: "Fatuha", 186: "Danapur", 187: "Maner", 188: "Phulwari", 189: "Masaurhi",
    190: "Paliganj", 191: "Bikram", 192: "Sandesh", 193: "Barhara", 194: "Arrah",
    195: "Agiaon", 196: "Tarari", 197: "Jagdishpur", 198: "Shahpur", 199: "Brahampur",
    200: "Buxar", 201: "Dumraon", 202: "Rajpur", 203: "Ramgarh", 204: "Mohania",
    205: "Bhabua", 206: "Chainpur", 207: "Chenari", 208: "Sasaram", 209: "Kargahar",
    210: "Dinara", 211: "Nokha", 212: "Dehri", 213: "Karakat", 214: "Arwal",
    215: "Kurtha", 216: "Jehanabad", 217: "Ghosi", 218: "Makhdumpur", 219: "Goh",
    220: "Obra", 221: "Nabinagar", 222: "Kutumba", 223: "Aurangabad", 224: "Rafiganj",
    225: "Gurua", 226: "Sherghati", 227: "Imamganj", 228: "Barachatti", 229: "Bodh Gaya",
    230: "Gaya Town", 231: "Tikari", 232: "Belaganj", 233: "Atri", 234: "Wazirganj",
    235: "Rajauli", 236: "Hisua", 237: "Nawada", 238: "Gobindpur", 239: "Warsaliganj",
    240: "Sikandra", 241: "Jamui", 242: "Jhajha", 243: "Chakai",
}

# Reverse map: normalized name → ac_no
def build_reverse_map():
    """Build a reverse map from normalized constituency name to AC number(s)."""
    rev = {}
    for ac_no, name in AC_MAP.items():
        norm = normalize_for_matching(name)
        if norm not in rev:
            rev[norm] = []
        rev[norm].append(ac_no)
    return rev


# Additional manual name mappings for cases where MyNeta uses different spelling
MANUAL_CONSTITUENCY_OVERRIDES = {
    # MyNeta name → Our AC name (when they don't match after normalization)
    "KUSHESHWARASTHAN": "KUSHESHWAR ASTHAN",
    "KUSHESHWARASTHAN EAST": "KUSHESHWAR ASTHAN",
    "SIMRI BAKHTIYARPUR": "SIMRI BAKHTIARPUR",
    "GAURABAURAM": "GAURA BAURAM",
    "DARBHANGA SADAR": "DARBHANGA",
    "HAYAGHAT": "HAYAGHAT",
    "BARURAJ": "BARURAJ",
    "CHERIA BARIARPUR": "CHERIA-BARIARPUR",
    "CHERIABARIARPUR": "CHERIA-BARIARPUR",
    "SAHEBPURKAMAL": "SAHEBPUR KAMAL",
    "RAJA PAKAR": "RAJA PAKAR",
    "RAJAPAKAR": "RAJA PAKAR",
    "WARSALIGANJ": "WARSALIGANJ",
    "BODH GAYA": "BODH GAYA",
    "BODHGAYA": "BODH GAYA",
    "GAYA TOWN": "GAYA TOWN",
    "GAYATOWN": "GAYA TOWN",
    "PATNA SAHIB": "PATNA SAHIB",
    "PATNASAHIB": "PATNA SAHIB",
    "BIHARSHARIF": "BIHARSHARIF",
    "BIHAR SHARIF": "BIHARSHARIF",
    "GOBINDPUR": "GOBINDPUR",
    "GOVINDPUR": "GOBINDPUR",
    "NARKATIA": "NARKATIYA",
    "SONEPUR": "SONPUR",
}


def map_winners_to_ac(winners: list[dict], reverse_map: dict) -> dict:
    """Map MyNeta winners to AC numbers. Returns {ac_no: {name, party}}."""
    result = {}
    unmatched = []
    
    for w in winners:
        myneta_const = normalize_for_matching(w["constituency"])
        
        # Check direct match
        if myneta_const in reverse_map:
            for ac_no in reverse_map[myneta_const]:
                if ac_no not in result:
                    result[ac_no] = {
                        "winner_name": w["candidate_name"],
                        "winner_party": standardize_party(w["party"]),
                        "party_full": w["party"],
                        "myneta_constituency": w["constituency"],
                    }
                    break
            continue
        
        # Check manual overrides
        if myneta_const in MANUAL_CONSTITUENCY_OVERRIDES:
            target = normalize_for_matching(MANUAL_CONSTITUENCY_OVERRIDES[myneta_const])
            if target in reverse_map:
                for ac_no in reverse_map[target]:
                    if ac_no not in result:
                        result[ac_no] = {
                            "winner_name": w["candidate_name"],
                            "winner_party": standardize_party(w["party"]),
                            "party_full": w["party"],
                            "myneta_constituency": w["constituency"],
                        }
                        break
                continue
        
        # Try removing spaces for compound names
        compact = myneta_const.replace(" ", "")
        for norm_name, ac_nos in reverse_map.items():
            if norm_name.replace(" ", "") == compact:
                for ac_no in ac_nos:
                    if ac_no not in result:
                        result[ac_no] = {
                            "winner_name": w["candidate_name"],
                            "winner_party": standardize_party(w["party"]),
                            "party_full": w["party"],
                            "myneta_constituency": w["constituency"],
                        }
                        break
                break
        else:
            unmatched.append(w)
    
    return result, unmatched


# ---------- STEP 3: Update raw JSONL files ----------

def update_jsonl_files(ac_winner_map: dict, data_dir: str):
    """Update the raw ECI 2025 JSONL files with correct winner names and parties."""
    raw_dir = os.path.join(data_dir, "data", "raw", "eci_2025")
    if not os.path.isdir(raw_dir):
        print(f"ERROR: Raw dir not found: {raw_dir}")
        return
    
    updated = 0
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.endswith('.jsonl'):
            continue
        filepath = os.path.join(raw_dir, fname)
        records = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                records.append(json.loads(line))
        
        modified = False
        for rec in records:
            ac_no = rec.get('ac_no')
            if ac_no in ac_winner_map:
                real = ac_winner_map[ac_no]
                old_winner = rec.get('winner_name', '')
                rec['winner_name'] = real['winner_name']
                rec['winner_party'] = real['winner_party']
                
                # Also update candidates list if present
                if 'candidates' in rec and isinstance(rec['candidates'], list):
                    for cand in rec['candidates']:
                        if cand.get('candidate_name') == old_winner:
                            cand['candidate_name'] = real['winner_name']
                            cand['party'] = real['winner_party']
                            break
                    # Ensure the real winner is the first candidate with most votes
                    # Find and move them to front if needed
                    found = False
                    for i, cand in enumerate(rec['candidates']):
                        if cand.get('candidate_name') == real['winner_name']:
                            found = True
                            if i > 0:
                                rec['candidates'].insert(0, rec['candidates'].pop(i))
                            break
                    if not found and rec['candidates']:
                        # Replace the top candidate
                        rec['candidates'][0]['candidate_name'] = real['winner_name']
                        rec['candidates'][0]['party'] = real['winner_party']
                
                modified = True
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                for rec in records:
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            updated += 1
    
    print(f"Updated {updated} JSONL files.")


# ---------- STEP 4: Update Supabase ----------

def update_supabase(ac_winner_map: dict):
    """Update winner_name and winner_party in the Supabase election_results_2025 table."""
    from dotenv import load_dotenv
    load_dotenv()
    from load_supabase import get_supabase_client
    
    supabase = get_supabase_client()
    
    updated = 0
    errors = 0
    for ac_no, data in sorted(ac_winner_map.items()):
        try:
            resp = supabase.table("election_results_2025").update({
                "winner_name": data["winner_name"],
                "winner_party": data["winner_party"],
            }).eq("ac_no", ac_no).execute()
            updated += 1
        except Exception as e:
            print(f"  ERROR updating AC {ac_no}: {e}")
            errors += 1
    
    print(f"Supabase: {updated} updated, {errors} errors.")


# ---------- MAIN ----------

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the saved MyNeta HTML
    myneta_html = os.path.join(
        r"C:\Users\shadw\.gemini\antigravity\brain\b7e8b8b0-1e53-4e39-8681-ffecad6312ba",
        ".system_generated", "steps", "1631", "content.md"
    )
    
    if not os.path.exists(myneta_html):
        print(f"ERROR: MyNeta HTML not found at: {myneta_html}")
        sys.exit(1)
    
    print("=" * 60)
    print("STEP 1: Parsing MyNeta HTML for real winner data...")
    print("=" * 60)
    winners = parse_myneta_html(myneta_html)
    print(f"Parsed {len(winners)} winners from MyNeta.")
    
    if len(winners) < 200:
        print("WARNING: Expected ~243 winners, got fewer. Parsing may be incomplete.")
    
    # Show first few
    for w in winners[:5]:
        print(f"  #{w['sno']}: {w['candidate_name']} | {w['constituency']} | {w['party']}")
    print("  ...")
    
    print("\n" + "=" * 60)
    print("STEP 2: Mapping to AC numbers...")
    print("=" * 60)
    reverse_map = build_reverse_map()
    ac_winner_map, unmatched = map_winners_to_ac(winners, reverse_map)
    print(f"Successfully mapped {len(ac_winner_map)} / 243 constituencies.")
    
    if unmatched:
        print(f"\nWARNING: {len(unmatched)} unmatched constituencies:")
        for u in unmatched:
            print(f"  {u['constituency']} -> {u['candidate_name']} ({u['party']})")
    
    # STEP 2b: Fill in 26 constituencies hidden behind JS on MyNeta page
    # These were verified from Wikipedia, IndiaToday, OneIndia, NDTV
    JS_HIDDEN_WINNERS = {
        11:  ("Rajesh Kumar", "LJP(RV)"),           # Sugauli
        41:  ("Aniruddha Prasad Yadav", "JD(U)"),   # Nirmali
        47:  ("Avinash Manglam", "RJD"),             # Raniganj
        52:  ("Md. Tauseef Alam", "AIMIM"),           # Bahadurganj
        53:  ("Gopal Kumar Agarwal", "JD(U)"),       # Thakurganj
        78:  ("Atirek Kumar", "JD(U)"),              # Kusheshwar Asthan
        80:  ("Binay Kumar Choudhary", "JD(U)"),     # Benipur
        82:  ("Rajesh Kumar Mandal", "JD(U)"),       # Darbhanga Rural
        92:  ("Aditya Kumar", "JD(U)"),              # Sakra
        94:  ("Ranjan Kumar", "BJP"),                # Muzaffarpur
        101: ("Subhash Singh", "BJP"),               # Gopalganj
        106: ("Bhism Pratap Singh", "JD(U)"),         # Ziradei
        110: ("Indradev Singh", "JD(U)"),             # Barharia
        112: ("Hem Narayan Sah", "JD(U)"),            # Maharajganj
        118: ("Chhoti Kumari", "BJP"),               # Chapra
        128: ("Tejashwi Prasad Yadav", "RJD"),       # Raghopur
        140: ("Raj Kumar Ray", "JD(U)"),             # Hasanpur
        149: ("Bablu Kumar", "JD(U)"),               # Khagaria
        161: ("Ram Narayan Mandal", "BJP"),           # Banka
        166: ("Nachiketa", "JD(U)"),                 # Jamalpur
        184: ("Ratnesh Kumar", "BJP"),               # Patna Sahib
        185: ("Dr. Ramanand Yadav", "RJD"),          # Fatuha
        189: ("Arun Manjhi", "JD(U)"),               # Masaurhi
        191: ("Siddharth Saurav", "BJP"),            # Bikram
        194: ("Sanjay Singh Tiger", "BJP"),           # Arrah
        240: ("Prafull Kumar Manjhi", "HAM(S)"),     # Sikandra
        131: ("Maheshwar Hazari", "JD(U)"),          # Kalyanpur (SC)
    }
    
    for ac_no, (name, party) in JS_HIDDEN_WINNERS.items():
        if ac_no not in ac_winner_map:
            ac_winner_map[ac_no] = {
                "winner_name": name,
                "winner_party": party,
                "party_full": party,
                "myneta_constituency": AC_MAP[ac_no],
            }
    
    print(f"After adding JS-hidden fallbacks: {len(ac_winner_map)} / 243 constituencies mapped.")
    
    # Show sample mappings
    print("\nSample mappings:")
    for ac_no in [1, 50, 100, 128, 150, 184, 200, 243]:
        if ac_no in ac_winner_map:
            d = ac_winner_map[ac_no]
            print(f"  AC {ac_no} ({AC_MAP[ac_no]}): {d['winner_name']} ({d['winner_party']})")
    
    print("\n" + "=" * 60)
    print("STEP 3: Updating raw JSONL files...")
    print("=" * 60)
    update_jsonl_files(ac_winner_map, base_dir)
    
    print("\n" + "=" * 60)
    print("STEP 4: Updating Supabase...")
    print("=" * 60)
    update_supabase(ac_winner_map)
    
    # Party-wise tally
    print("\n" + "=" * 60)
    print("Party-wise seat distribution (real data):")
    print("=" * 60)
    from collections import Counter
    party_counts = Counter(d["winner_party"] for d in ac_winner_map.values())
    for party, count in party_counts.most_common():
        print(f"  {party}: {count}")
    
    print(f"\nTotal: {sum(party_counts.values())} seats mapped.")
    print("\nDone! Election data has been corrected.")


if __name__ == "__main__":
    main()
