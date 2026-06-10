#!/usr/bin/env python3
"""Generate synthetic Vietnamese credit card transaction data for research.

The output is a relational CSV dataset built around users, cards, merchants,
MCCs, reward rules, and transactions. It is deterministic by default so the
same seed produces the same dataset.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MCC_PATH = ROOT / "mcc.json"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "synthetic"

VN_CITIES = [
    "Ho Chi Minh City",
    "Ha Noi",
    "Da Nang",
    "Can Tho",
    "Hai Phong",
    "Nha Trang",
    "Hue",
    "Binh Duong",
    "Dong Nai",
    "Quang Ninh",
]

FIRST_NAMES = [
    "An",
    "Bao",
    "Binh",
    "Chau",
    "Duc",
    "Giang",
    "Hanh",
    "Khanh",
    "Linh",
    "Long",
    "Mai",
    "Minh",
    "Nam",
    "Ngoc",
    "Phuc",
    "Quang",
    "Thao",
    "Trang",
    "Tuan",
    "Vy",
]

LAST_NAMES = [
    "Nguyen",
    "Tran",
    "Le",
    "Pham",
    "Hoang",
    "Huynh",
    "Phan",
    "Vu",
    "Vo",
    "Dang",
    "Bui",
    "Do",
]

JOBS = [
    "Office Worker",
    "Engineer",
    "Teacher",
    "Student",
    "Sales Executive",
    "Healthcare Worker",
    "Small Business Owner",
    "Designer",
    "Accountant",
    "Freelancer",
]

BANKS = [
    ("ASCBVNVX", "Ngân hàng Á Châu", "ACB"),
    ("ABBKVNVX", "Ngân hàng An Bình", "ABBANK"),
    ("ANZBVNVX", "Ngân hàng ANZ Việt Nam", "ANZVL"),
    ("NASCVNVX", "Ngân hàng Bắc Á", "Bac A Bank"),
    ("VCBCVNVX", "Ngân hàng Bản Việt", "BVBank"),
    ("BVBVVNVX", "Ngân hàng Bảo Việt", "BAOVIET Bank"),
    ("CIBBVNVN", "Ngân hàng CIMB Việt Nam", "CIMB"),
    ("ICBVVNVX", "Ngân hàng Công thương Việt Nam", "VietinBank"),
    ("WBVNVNVX", "Ngân hàng Đại Chúng Việt Nam", "PVcomBank"),
    ("GBNKVNVX", "Ngân hàng Dầu khí toàn cầu", "GPBank"),
    ("BIDVVNVX", "Ngân hàng Đầu tư và Phát triển Việt Nam", "BIDV"),
    ("SEAVVNVX", "Ngân hàng Đông Nam Á", "SeABank"),
    ("MCOBVNVX", "Ngân hàng Hàng Hải", "MSB"),
    ("HLBBVNVX", "Ngân hàng Hong Leong Việt Nam", "HLBVN"),
    ("HSBCVNVX", "Ngân hàng HSBC Việt Nam", "HSBC"),
    ("IABBVNVX", "Ngân hàng Indovina", "IVB"),
    ("KLBKVNVX", "Ngân hàng Kiên Long", "Kienlongbank"),
    ("VTCBVNVX", "Ngân hàng Kỹ Thương", "Techcombank"),
    ("LVBKVNVX", "Ngân hàng Lộc Phát Việt Nam", "LVBank"),
    ("NAMAVNVX", "Ngân hàng Nam Á", "Nam A Bank"),
    ("GTBAVNVX", "Ngân hàng Ngoại thương Công nghệ số", "VCBNeo"),
    ("BFTVVNVX", "Ngân hàng Ngoại Thương Việt Nam", "Vietcombank"),
    ("VBAAVNVX", "Ngân hàng NN&PT Nông thôn Việt Nam", "Agribank"),
    ("HDBCVNVX", "Ngân hàng Phát triển TPHồ Chí Minh", "HDBank"),
    ("ORCOVNVX", "Ngân hàng Phương Đông", "OCB"),
    ("VIDPVNV5", "Ngân hàng Public Bank Việt Nam", "PBVN"),
    ("MSCBVNVX", "Ngân hàng Quân Đội", "MB"),
    ("NVBAVNVX", "Ngân hàng Quốc dân", "NCB"),
    ("VNIBVNVX", "Ngân hàng Quốc Tế", "VIB"),
    ("SHBAVNVX", "Ngân hàng Sài Gòn - Hà Nội", "SHB"),
    ("SACLVNVX", "Ngân hàng Sài Gòn", "SCB"),
    ("SBITVNVX", "Ngân hàng Sài Gòn Công Thương", "SAIGONBANK"),
    ("SGTTVNVX", "Ngân hàng Sài Gòn Thương Tín", "Sacombank"),
    ("SHBKVNVX", "Ngân hàng Shinhan Việt Nam", "SHBVN"),
    ("EACBVNVX", "Ngân hàng Số Vikki", "Vikki Bank"),
    ("SCBLVNVX", "Ngân hàng Standard Chartered Việt Nam", "SCBVL"),
    ("PGBLVNVX", "Ngân hàng Thịnh vượng và Phát triển", "PGBank"),
    ("TPBVVNVX", "Ngân hàng Tiên Phong", "TPBank"),
    ("UOVBVNVX", "Ngân hàng UOB Việt Nam", "UOB"),
    ("VRBAVNVX", "Ngân hàng Việt - Nga", "VRB"),
    ("VNTTVNVX", "Ngân hàng Việt Á", "VietABank"),
    ("OJBAVNVX", "Ngân hàng Việt Nam Hiện Đại", "MBV"),
    ("VPBKVNVX", "Ngân hàng Việt Nam Thịnh Vượng", "VPBank"),
    ("VNACVNVX", "Ngân hàng Việt Nam Thương Tín", "Vietbank"),
    ("HVBKVNVX", "Ngân hàng Woori Việt Nam", "Woori"),
    ("EBVIVNVX", "Ngân hàng Xuất Nhập Khẩu", "Eximbank"),
]

CARD_PRODUCTS = [
    ("BFTVVNVX", "Vietcombank Cashback Plus", "Visa", 800000, "everyday"),
    ("BFTVVNVX", "Vietcombank Travel Signature", "Visa", 1500000, "travel"),
    ("VTCBVNVX", "Techcombank Everyday Rewards", "Mastercard", 990000, "shopping"),
    ("VTCBVNVX", "Techcombank Dining Cashback", "Visa", 900000, "dining"),
    ("VPBKVNVX", "VPBank Online Cashback", "Mastercard", 1200000, "online"),
    ("VPBKVNVX", "VPBank Family Care", "Visa", 700000, "family"),
    ("ASCBVNVX", "ACB Lifestyle", "Visa", 600000, "lifestyle"),
    ("ASCBVNVX", "ACB Travel Rewards", "Mastercard", 1300000, "travel"),
    ("MSCBVNVX", "MB Daily Cashback", "JCB", 500000, "everyday"),
    ("MSCBVNVX", "MB Premium Miles", "Visa", 1600000, "travel"),
    ("TPBVVNVX", "TPBank Digital Cashback", "Visa", 750000, "online"),
    ("TPBVVNVX", "TPBank Health & Education", "Mastercard", 850000, "care"),
]

REWARD_RULE_TEMPLATES = {
    "everyday": [
        ("Dining cashback", "cashback", Decimal("0.0500"), 300000, 50000, "any", ["dining"]),
        ("Grocery cashback", "cashback", Decimal("0.0400"), 250000, 50000, "any", ["grocery"]),
        ("Base cashback", "cashback", Decimal("0.0020"), 100000, 0, "any", ["other"]),
    ],
    "travel": [
        ("Travel cashback", "cashback", Decimal("0.0600"), 500000, 100000, "any", ["travel"]),
        ("Dining abroad cashback", "cashback", Decimal("0.0400"), 250000, 50000, "any", ["dining"]),
        ("Base miles", "miles", Decimal("0.0000"), 0, 0, "any", ["other"]),
    ],
    "shopping": [
        ("Shopping cashback", "cashback", Decimal("0.0500"), 350000, 50000, "any", ["shopping"]),
        ("Online retail cashback", "cashback", Decimal("0.0600"), 300000, 50000, "online", ["online"]),
        ("Base cashback", "cashback", Decimal("0.0020"), 100000, 0, "any", ["other"]),
    ],
    "dining": [
        ("Dining cashback", "cashback", Decimal("0.0800"), 400000, 50000, "any", ["dining"]),
        ("Entertainment cashback", "cashback", Decimal("0.0400"), 200000, 50000, "any", ["entertainment"]),
        ("Base cashback", "cashback", Decimal("0.0020"), 100000, 0, "any", ["other"]),
    ],
    "online": [
        ("Digital and online cashback", "cashback", Decimal("0.0700"), 350000, 50000, "online", ["online", "digital"]),
        ("Food delivery cashback", "cashback", Decimal("0.0500"), 250000, 50000, "online", ["dining"]),
        ("Base cashback", "cashback", Decimal("0.0020"), 100000, 0, "any", ["other"]),
    ],
    "family": [
        ("Family grocery cashback", "cashback", Decimal("0.0600"), 350000, 50000, "any", ["grocery"]),
        ("Healthcare cashback", "cashback", Decimal("0.0400"), 250000, 50000, "any", ["healthcare"]),
        ("Base cashback", "cashback", Decimal("0.0020"), 100000, 0, "any", ["other"]),
    ],
    "lifestyle": [
        ("Lifestyle cashback", "cashback", Decimal("0.0500"), 300000, 50000, "any", ["beauty", "entertainment"]),
        ("Shopping cashback", "cashback", Decimal("0.0400"), 250000, 50000, "any", ["shopping"]),
        ("Base cashback", "cashback", Decimal("0.0020"), 100000, 0, "any", ["other"]),
    ],
    "care": [
        ("Healthcare cashback", "cashback", Decimal("0.0500"), 300000, 50000, "any", ["healthcare"]),
        ("Education cashback", "cashback", Decimal("0.0400"), 250000, 50000, "any", ["education"]),
        ("Base cashback", "cashback", Decimal("0.0020"), 100000, 0, "any", ["other"]),
    ],
}

SEGMENT_WEIGHTS = {
    "young_lifestyle": {"dining": 0.28, "online": 0.22, "shopping": 0.20, "digital": 0.10, "transport": 0.10, "entertainment": 0.10},
    "family_essentials": {"grocery": 0.30, "healthcare": 0.18, "education": 0.15, "utilities": 0.14, "shopping": 0.13, "dining": 0.10},
    "travel_premium": {"travel": 0.38, "dining": 0.18, "shopping": 0.14, "transport": 0.12, "entertainment": 0.10, "grocery": 0.08},
    "commuter_daily": {"transport": 0.26, "dining": 0.23, "grocery": 0.22, "utilities": 0.12, "shopping": 0.10, "healthcare": 0.07},
    "low_spend": {"grocery": 0.25, "dining": 0.18, "transport": 0.17, "utilities": 0.15, "shopping": 0.15, "healthcare": 0.10},
}

SEGMENT_AMOUNT_RANGES = {
    "young_lifestyle": (45000, 1200000),
    "family_essentials": (60000, 2500000),
    "travel_premium": (150000, 12000000),
    "commuter_daily": (20000, 900000),
    "low_spend": (20000, 500000),
}

# Source: Citibank Merchant Category Codes PDF, "Valid Payment Brand(s)" column.
# The default is VM because most listed MCCs are valid for both Visa and Mastercard.
MCC_VALID_PAYMENT_OVERRIDES = {
    "3019": "TSYS",
    "3081": "TSYS",
    "3086": "V",
    "3110": "V",
    "3126": "V",
    "3133": "V",
    "3135": "V",
    "3137": "V",
    "3138": "V",
    "3143": "V",
    "3145": "V",
    "3154": "V",
    "3165": "V",
    "3170": "V",
    "3176": "V",
    "3203": "V",
    "3215": "V",
    "3216": "V",
    "3218": "V",
    "3233": "V",
    "3235": "V",
    "3238": "V",
    "3251": "V",
    "3253": "M",
    "3254": "V",
    "3259": "V",
    "3262": "V",
    "3273": "TSYS",
    "3274": "TSYS",
    "3281": "TSYS",
    "3284": "V",
    "3414": "V",
    "3437": "V",
    "3547": "M",
    "3605": "M",
    "3606": "M",
    "3610": "M",
    "3611": "M",
    "3616": "M",
    "3733": "M",
    "3757": "TSYS",
    "3803": "M",
    "3804": "M",
    "3805": "M",
    "3806": "M",
    "3809": "M",
    "3810": "M",
    "3817": "M",
    "4723": "V",
    "4761": "TSYS",
    "4813": "M",
    "5299": "TSYS",
    "5961": "TSYS",
    "5974": "TSYS",
    "6050": "M",
    "6236": "TSYS",
    "6381": "TSYS",
    "6529": "TSYS",
    "6530": "TSYS",
    "6535": "TSYS",
    "6536": "M",
    "6537": "M",
    "6538": "M",
    "6539": "M",
    "6540": "M",
    "6611": "TSYS",
    "6760": "TSYS",
    "7280": "TSYS",
    "7295": "TSYS",
    "7332": "TSYS",
    "7524": "TSYS",
    "7833": "TSYS",
    "8044": "TSYS",
    "8743": "TSYS",
    "9034": "TSYS",
    "9401": "TSYS",
    "9700": "V",
    "9701": "V",
    "9702": "V",
    "9751": "TSYS",
    "9752": "TSYS",
    "9754": "M",
}


def stable_uuid(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{namespace}:{value}"))


def money(value: Decimal | float | int) -> str:
    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def classify_mcc(code: str, description: str) -> str:
    text = description.lower()
    if code in {"5812", "5813", "5814"} or any(word in text for word in ["restaurant", "fast food", "drinking"]):
        return "dining"
    if code in {"5411", "5499", "5300"} or "grocery" in text or "food stores" in text:
        return "grocery"
    if code in {"4511", "4722", "7011", "4411", "4112", "3722"} or any(word in text for word in ["airlines", "travel", "lodging", "hotel", "cruise"]):
        return "travel"
    if code in {"4121", "4111", "4131", "4784", "5541"} or any(word in text for word in ["taxicabs", "transport", "tolls", "service stations"]):
        return "transport"
    if code in {"4814", "4899", "4900"} or any(word in text for word in ["utilities", "telecommunication", "cable"]):
        return "utilities"
    if code in {"5732", "5815", "5816", "5045"} or any(word in text for word in ["digital", "computer", "electronics"]):
        return "digital"
    if code in {"5942", "5192"} or any(word in text for word in ["book", "schools", "education"]):
        return "education"
    if code in {"5912", "8011", "8021", "8041", "8043", "8049", "8062", "8099"} or any(word in text for word in ["medical", "hospital", "dentist", "doctor", "pharmacies"]):
        return "healthcare"
    if code in {"7832", "7995", "7996", "7922", "7801", "7802"} or any(word in text for word in ["amusement", "theater", "sports", "betting"]):
        return "entertainment"
    if code in {"7230", "5977"} or any(word in text for word in ["cosmetic", "beauty", "barber"]):
        return "beauty"
    if any(word in text for word in ["stores", "shops", "retail", "clothing", "shoe", "department"]):
        return "shopping"
    return "other"


def broad_mcc_category(research_category: str) -> str:
    mapping = {
        "dining": "Retail outlet services",
        "grocery": "Retail outlet services",
        "shopping": "Retail outlet services",
        "online": "Business services",
        "digital": "Business services",
        "travel": "Transportation services",
        "transport": "Transportation services",
        "utilities": "Utility services",
        "education": "Professional services and membership organizations",
        "healthcare": "Professional services and membership organizations",
        "entertainment": "Miscellaneous shops",
        "beauty": "Miscellaneous shops",
    }
    return mapping.get(research_category, "Miscellaneous shops")


def valid_payment_for_mcc(code: str) -> str:
    return MCC_VALID_PAYMENT_OVERRIDES.get(code, "VM")


def weighted_choice(rng: random.Random, weights: dict[str, float]) -> str:
    total = sum(weights.values())
    point = rng.random() * total
    current = 0.0
    for item, weight in weights.items():
        current += weight
        if point <= current:
            return item
    return next(reversed(weights))


def random_date(rng: random.Random, start: date, end: date) -> datetime:
    days = (end - start).days
    selected = start + timedelta(days=rng.randint(0, days))
    hour = rng.choices(range(24), weights=[1, 1, 1, 1, 1, 2, 4, 6, 7, 7, 8, 10, 9, 8, 8, 8, 9, 11, 12, 11, 8, 5, 3, 2])[0]
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return datetime(selected.year, selected.month, selected.day, hour, minute, second, tzinfo=timezone.utc)


def iso(dt: datetime | date) -> str:
    return dt.isoformat()


def generate_users(rng: random.Random, count: int) -> tuple[list[dict], dict[str, str]]:
    users = []
    user_segments = {}
    now = datetime.now(timezone.utc).replace(microsecond=0)
    segment_names = list(SEGMENT_WEIGHTS)
    segment_probs = [0.27, 0.25, 0.12, 0.23, 0.13]

    for index in range(1, count + 1):
        user_id = stable_uuid("user", str(index))
        segment = rng.choices(segment_names, weights=segment_probs)[0]
        if segment == "young_lifestyle":
            age = rng.randint(20, 30)
        elif segment == "family_essentials":
            age = rng.randint(31, 48)
        elif segment == "travel_premium":
            age = rng.randint(28, 55)
        elif segment == "commuter_daily":
            age = rng.randint(23, 45)
        else:
            age = rng.randint(20, 60)

        first_name = rng.choice(FIRST_NAMES)
        last_name = rng.choice(LAST_NAMES)
        email = f"user{index:05d}@synthetic-credit.vn"
        created_at = now - timedelta(days=rng.randint(30, 1200))
        users.append(
            {
                "id": user_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "gender": rng.choice(["true", "false"]),
                "born_date": date(now.year - age, rng.randint(1, 12), rng.randint(1, 28)).isoformat(),
                "city": rng.choice(VN_CITIES),
                "job": rng.choice(JOBS),
                "last_login": iso(now - timedelta(days=rng.randint(0, 60))),
                "provider": rng.choices(["GOOGLE", "EMAIL", "FACEBOOK"], weights=[0.52, 0.38, 0.10])[0],
                "created_at": iso(created_at),
                "updated_at": iso(now),
            }
        )
        user_segments[user_id] = segment
    return users, user_segments


def generate_banks_and_cards() -> tuple[list[dict], list[dict], dict[str, str]]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    banks = []
    bank_ids = {}
    for swift, name, short_name in BANKS:
        bank_id = stable_uuid("bank", f"{swift}:{name}")
        bank_ids[swift] = bank_id
        banks.append(
            {
                "id": bank_id,
                "swift_code": swift,
                "name": name,
                "short_name": short_name,
                "created_at": iso(now),
            }
        )

    cards = []
    card_profiles = {}
    for index, (bank_swift, name, network, annual_fee, profile) in enumerate(CARD_PRODUCTS, start=1):
        card_id = stable_uuid("card", name)
        card_profiles[card_id] = profile
        cards.append(
            {
                "id": card_id,
                "bank_id": bank_ids[bank_swift],
                "name": name,
                "network": network,
                "card_type": "credit",
                "annual_fee": money(annual_fee),
                "source_url": f"https://example.com/cards/{index}",
                "is_active": "true",
                "created_at": iso(now),
            }
        )
    return banks, cards, card_profiles


def generate_user_cards(rng: random.Random, users: list[dict], cards: list[dict]) -> list[dict]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    user_cards = []
    cards_by_id = {card["id"]: card for card in cards}
    card_ids = list(cards_by_id)

    for user in users:
        card_count = rng.choices([1, 2, 3], weights=[0.68, 0.25, 0.07])[0]
        selected_cards = rng.sample(card_ids, card_count)
        for offset, card_id in enumerate(selected_cards):
            user_card_id = stable_uuid("user-card", f"{user['id']}:{card_id}")
            user_cards.append(
                {
                    "id": user_card_id,
                    "user_id": user["id"],
                    "credit_card_id": card_id,
                    "nickname": cards_by_id[card_id]["name"].split()[0],
                    "billing_cycle_day": rng.randint(1, 28),
                    "is_default": "true" if offset == 0 else "false",
                    "has_annual_fee": "true" if Decimal(cards_by_id[card_id]["annual_fee"]) > 0 else "false",
                    "created_at": iso(now - timedelta(days=rng.randint(15, 900))),
                }
            )
    return user_cards


def generate_mcc_rows(mcc_data: dict[str, str]) -> tuple[list[dict], dict[str, list[str]], dict[str, str]]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    rows = []
    category_to_mccs = defaultdict(list)
    mcc_to_research_category = {}
    for code, description in sorted(mcc_data.items()):
        research_category = classify_mcc(code, description)
        category_to_mccs[research_category].append(code)
        mcc_to_research_category[code] = research_category
        rows.append(
            {
                "code": code,
                "description": description,
                "category": broad_mcc_category(research_category),
                "is_active": "true",
                "valid_payment": valid_payment_for_mcc(code),
                "created_at": iso(now),
                "updated_at": iso(now),
            }
        )
    return rows, dict(category_to_mccs), mcc_to_research_category


def generate_merchants(rng: random.Random, count: int, category_to_mccs: dict[str, list[str]]) -> list[dict]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    brand_names = {
        "dining": ["Highlands Coffee", "Phuc Long", "The Coffee House", "Pizza 4P's", "Pho 24", "Com Tam Cali"],
        "grocery": ["WinMart", "Co.opmart", "Bach Hoa Xanh", "Lotte Mart", "GO! Market"],
        "travel": ["Vietnam Airlines", "Vietjet Air", "Bamboo Airways", "Muong Thanh Hotel", "Saigontourist"],
        "transport": ["Grab", "Be", "Mai Linh Taxi", "Vinasun Taxi", "Petrolimex", "BusMap"],
        "utilities": ["EVN", "VNPT", "Viettel Telecom", "MobiFone", "Saigon Water"],
        "digital": ["FPT Shop", "The Gioi Di Dong", "CellphoneS", "Netflix", "Spotify"],
        "education": ["FAHASA", "PNC Bookstore", "ILA Vietnam", "Apollo English", "Topica"],
        "healthcare": ["Pharmacity", "Long Chau", "Medlatec", "Hoan My Clinic", "Nha Khoa Kim"],
        "entertainment": ["CGV Cinemas", "Lotte Cinema", "Galaxy Cinema", "VinWonders", "California Fitness"],
        "beauty": ["Hasaki", "Guardian", "Watsons", "The Face Shop", "Seoul Spa"],
        "online": ["Shopee", "Lazada", "Tiki", "Sendo", "GrabFood"],
        "shopping": ["Uniqlo", "H&M", "Canifa", "PNJ", "Vincom Retail", "Nguyen Kim"],
        "other": ["Payoo", "MoMo", "Local Service", "General Supply", "Viet Service"],
    }
    outlet_suffixes = [
        "District 1",
        "District 3",
        "District 7",
        "Binh Thanh",
        "Tan Binh",
        "Thu Duc",
        "Cau Giay",
        "Hoan Kiem",
        "Hai Ba Trung",
        "Da Nang Center",
        "Nha Trang Center",
        "Can Tho",
        "Aeon Mall",
        "Vincom",
        "Lotte Mall",
        "Airport",
    ]
    channel_suffixes = ["Online", "App", "Website", "Payoo", "MoMo", "VNPay"]
    categories = list(category_to_mccs)
    category_weights = [0.13 if category == "other" else 1.0 for category in categories]
    merchants = []

    for index in range(1, count + 1):
        category = rng.choices(categories, weights=category_weights)[0]
        mcc_code = rng.choice(category_to_mccs[category])
        brand = rng.choice(brand_names.get(category, brand_names["other"]))
        suffix_pool = channel_suffixes if category in {"online", "digital", "utilities"} else outlet_suffixes
        branch = f"{brand} {rng.choice(suffix_pool)}"
        merchants.append(
            {
                "id": stable_uuid("merchant", str(index)),
                "branch": branch,
                "brand": brand,
                "mcc_code": mcc_code,
                "created_at": iso(now - timedelta(days=rng.randint(30, 2000))),
            }
        )
    return merchants


def generate_reward_rules(cards: list[dict], card_profiles: dict[str, str], category_to_mccs: dict[str, list[str]]) -> tuple[list[dict], list[dict]]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    reward_rules = []
    reward_rule_mccs = []
    for card in cards:
        profile = card_profiles[card["id"]]
        templates = REWARD_RULE_TEMPLATES[profile]
        for index, (name, reward_type, cashback_rate, cap, minimum, channel, categories) in enumerate(templates, start=1):
            rule_id = stable_uuid("reward-rule", f"{card['id']}:{name}")
            reward_rules.append(
                {
                    "id": rule_id,
                    "credit_card_id": card["id"],
                    "name": name,
                    "reward_type": reward_type,
                    "cashback_rate": f"{cashback_rate:.4f}",
                    "points_rate": "1.0000" if reward_type in {"points", "miles"} else "",
                    "monthly_cap_amount": money(cap),
                    "minimum_transaction_amount": money(minimum),
                    "minimum_monthly_spend": money(0),
                    "eligible_channel": channel,
                    "conditions_text": f"Synthetic rule for {name.lower()} on {card['name']}.",
                    "effective_from": "2025-01-01",
                    "effective_to": "2026-12-31",
                    "source_url": f"https://example.com/reward-rules/{index}",
                    "is_active": "true",
                    "created_at": iso(now),
                }
            )
            for category in categories:
                mcc_codes = category_to_mccs.get(category, [])
                if category == "other":
                    mcc_codes = [code for values in category_to_mccs.values() for code in values]
                for mcc_code in mcc_codes:
                    reward_rule_mccs.append(
                        {
                            "id": stable_uuid("reward-rule-mcc", f"{rule_id}:{mcc_code}:eligible"),
                            "reward_rule_id": rule_id,
                            "mcc_code": mcc_code,
                            "match_type": "eligible",
                        }
                    )
    return reward_rules, reward_rule_mccs


def build_reward_lookup(reward_rules: list[dict], reward_rule_mccs: list[dict]) -> dict[tuple[str, str], list[dict]]:
    rules_by_id = {rule["id"]: rule for rule in reward_rules}
    lookup = defaultdict(list)
    for link in reward_rule_mccs:
        if link["match_type"] != "eligible":
            continue
        rule = rules_by_id[link["reward_rule_id"]]
        lookup[(rule["credit_card_id"], link["mcc_code"])].append(rule)
    for key in lookup:
        lookup[key].sort(key=lambda rule: Decimal(rule["cashback_rate"] or "0"), reverse=True)
    return dict(lookup)


def generate_transactions(
    rng: random.Random,
    count: int,
    users: list[dict],
    user_segments: dict[str, str],
    user_cards: list[dict],
    merchants: list[dict],
    mcc_to_research_category: dict[str, str],
    reward_lookup: dict[tuple[str, str], list[dict]],
) -> list[dict]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    user_cards_by_user = defaultdict(list)
    user_card_to_card = {}
    for user_card in user_cards:
        user_cards_by_user[user_card["user_id"]].append(user_card)
        user_card_to_card[user_card["id"]] = user_card["credit_card_id"]

    merchants_by_category = defaultdict(list)
    for merchant in merchants:
        merchants_by_category[mcc_to_research_category[merchant["mcc_code"]]].append(merchant)

    users_by_id = {user["id"]: user for user in users}
    user_ids = list(users_by_id)
    start = date(2025, 1, 1)
    end = date(2025, 12, 31)
    monthly_cashback = defaultdict(Decimal)
    transactions = []

    for index in range(1, count + 1):
        user_id = rng.choice(user_ids)
        segment = user_segments[user_id]
        spending_category = weighted_choice(rng, SEGMENT_WEIGHTS[segment])
        if spending_category == "online":
            merchant_pool = merchants_by_category.get("online", []) + merchants_by_category.get("digital", []) + merchants_by_category.get("shopping", [])
        else:
            merchant_pool = merchants_by_category.get(spending_category) or merchants
        if not merchant_pool:
            merchant_pool = merchants
        merchant = rng.choice(merchant_pool)
        selected_user_card = rng.choice(user_cards_by_user[user_id])
        transaction_dt = random_date(rng, start, end)

        low, high = SEGMENT_AMOUNT_RANGES[segment]
        amount_float = rng.triangular(low, high, low + ((high - low) * 0.28))
        if spending_category == "travel":
            amount_float *= rng.uniform(1.5, 3.0)
        elif spending_category in {"transport", "dining"}:
            amount_float *= rng.uniform(0.55, 1.15)
        amount = Decimal(str(round(amount_float / 1000) * 1000))

        mcc_code = merchant["mcc_code"]
        credit_card_id = user_card_to_card[selected_user_card["id"]]
        eligible_rules = reward_lookup.get((credit_card_id, mcc_code), [])
        best_rule = eligible_rules[0] if eligible_rules else None
        cashback = Decimal("0.00")
        if best_rule and best_rule["reward_type"] == "cashback":
            minimum = Decimal(best_rule["minimum_transaction_amount"] or "0")
            rate = Decimal(best_rule["cashback_rate"] or "0")
            cap = Decimal(best_rule["monthly_cap_amount"] or "0")
            if amount >= minimum and rate > 0:
                candidate = amount * rate
                cap_key = (selected_user_card["id"], best_rule["id"], transaction_dt.strftime("%Y-%m"))
                if cap > 0:
                    remaining = max(Decimal("0.00"), cap - monthly_cashback[cap_key])
                    cashback = min(candidate, remaining)
                else:
                    cashback = candidate
                monthly_cashback[cap_key] += cashback

        transactions.append(
            {
                "id": stable_uuid("transaction", str(index)),
                "user_card_id": selected_user_card["id"],
                "merchant_id": merchant["id"],
                "transaction_date": iso(transaction_dt),
                "amount": money(amount),
                "mcc_source": rng.choices(["bank_statement", "admin_verified", "predicted", "user_feedback"], weights=[0.70, 0.15, 0.10, 0.05])[0],
                "cashback_estimated_amount": money(cashback),
                "source": rng.choices(["manual", "receipt_scan", "notification", "import"], weights=[0.20, 0.18, 0.42, 0.20])[0],
                "note": "",
                "location": users_by_id[user_id]["city"],
                "created_at": iso(now),
                "updated_at": iso(now),
            }
        )
    return transactions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic credit card usage data.")
    parser.add_argument("--transactions", type=int, default=50000, help="Number of transactions to generate.")
    parser.add_argument("--users", type=int, default=5000, help="Number of users to generate.")
    parser.add_argument("--merchants", type=int, default=1200, help="Number of merchants to generate.")
    parser.add_argument("--seed", type=int, default=2205, help="Random seed.")
    parser.add_argument("--mcc-path", type=Path, default=DEFAULT_MCC_PATH, help="Path to mcc.json.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for generated CSV files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    with args.mcc_path.open(encoding="utf-8") as file:
        mcc_data = json.load(file)

    users, user_segments = generate_users(rng, args.users)
    banks, cards, card_profiles = generate_banks_and_cards()
    user_cards = generate_user_cards(rng, users, cards)
    mcc_rows, category_to_mccs, mcc_to_research_category = generate_mcc_rows(mcc_data)
    category_to_mccs["online"] = sorted(set(category_to_mccs.get("digital", []) + category_to_mccs.get("shopping", [])))
    merchants = generate_merchants(rng, args.merchants, category_to_mccs)
    reward_rules, reward_rule_mccs = generate_reward_rules(cards, card_profiles, category_to_mccs)
    reward_lookup = build_reward_lookup(reward_rules, reward_rule_mccs)
    transactions = generate_transactions(
        rng,
        args.transactions,
        users,
        user_segments,
        user_cards,
        merchants,
        mcc_to_research_category,
        reward_lookup,
    )

    output_dir = args.output_dir
    write_csv(output_dir / "users.csv", users, list(users[0]))
    write_csv(output_dir / "banks.csv", banks, list(banks[0]))
    write_csv(output_dir / "cards.csv", cards, list(cards[0]))
    write_csv(output_dir / "user_cards.csv", user_cards, list(user_cards[0]))
    write_csv(output_dir / "merchant_category_codes.csv", mcc_rows, list(mcc_rows[0]))
    write_csv(output_dir / "merchants.csv", merchants, list(merchants[0]))
    write_csv(output_dir / "reward_rules.csv", reward_rules, list(reward_rules[0]))
    write_csv(output_dir / "reward_rule_mccs.csv", reward_rule_mccs, list(reward_rule_mccs[0]))
    write_csv(output_dir / "transactions.csv", transactions, list(transactions[0]))

    print(f"Generated synthetic dataset in {output_dir}")
    print(f"users={len(users)}")
    print(f"cards={len(cards)}")
    print(f"user_cards={len(user_cards)}")
    print(f"merchant_category_codes={len(mcc_rows)}")
    print(f"merchants={len(merchants)}")
    print(f"reward_rules={len(reward_rules)}")
    print(f"reward_rule_mccs={len(reward_rule_mccs)}")
    print(f"transactions={len(transactions)}")


if __name__ == "__main__":
    main()
