#!/usr/bin/env python3
"""Generate simple SVG illustrations for image_description exercises."""
import os

IMAGES = {
    "couple_at_restaurant_waiter_taking_order": {
        "bg": "#1a1a2e", "accent": "#e8a87c",
        "icon": """
        <rect x="80" y="110" width="50" height="80" rx="8" fill="#5a7a8a"/>
        <circle cx="105" cy="95" r="20" fill="#f0c8a0"/>
        <rect x="170" y="120" width="50" height="70" rx="8" fill="#7a6a9a"/>
        <circle cx="195" cy="105" r="20" fill="#f0c8a0"/>
        <rect x="130" y="140" width="40" height="60" rx="5" fill="#4a6a5a"/>
        <circle cx="150" cy="125" r="18" fill="#f0c8a0"/>
        <rect x="125" y="155" width="50" height="5" rx="2" fill="#fff" opacity="0.6"/>
        <rect x="125" y="165" width="40" height="5" rx="2" fill="#fff" opacity="0.4"/>
        <text x="150" y="230" text-anchor="middle" font-size="13" fill="#e8a87c" font-family="sans-serif">ресторан</text>
        """,
    },
    "couple_moving_boxes_into_apartment": {
        "bg": "#1a2e1a", "accent": "#8bc34a",
        "icon": """
        <rect x="50" y="80" width="200" height="140" rx="8" fill="#3a4a3a"/>
        <rect x="70" y="100" width="60" height="80" rx="4" fill="#5a7a5a"/>
        <rect x="170" y="100" width="60" height="80" rx="4" fill="#5a7a5a"/>
        <rect x="90" y="150" width="40" height="40" rx="4" fill="#8bc34a" opacity="0.8"/>
        <rect x="170" y="150" width="40" height="40" rx="4" fill="#8bc34a" opacity="0.8"/>
        <circle cx="100" cy="130" r="18" fill="#f0c8a0"/>
        <circle cx="200" cy="130" r="18" fill="#f0c8a0"/>
        <text x="150" y="245" text-anchor="middle" font-size="13" fill="#8bc34a" font-family="sans-serif">переезд</text>
        """,
    },
    "factory_chimney_polluting_air": {
        "bg": "#1a1a1a", "accent": "#ff7043",
        "icon": """
        <rect x="80" y="130" width="60" height="100" fill="#555"/>
        <rect x="160" y="150" width="50" height="80" fill="#555"/>
        <rect x="90" y="100" width="15" height="40" fill="#666"/>
        <rect x="150" y="110" width="15" height="45" fill="#666"/>
        <ellipse cx="97" cy="95" rx="20" ry="15" fill="#888" opacity="0.8"/>
        <ellipse cx="107" cy="75" rx="25" ry="20" fill="#999" opacity="0.6"/>
        <ellipse cx="157" cy="105" rx="18" ry="12" fill="#888" opacity="0.8"/>
        <ellipse cx="168" cy="85" rx="22" ry="18" fill="#999" opacity="0.6"/>
        <text x="150" y="245" text-anchor="middle" font-size="13" fill="#ff7043" font-family="sans-serif">загрязнение</text>
        """,
    },
    "family_celebrating_greek_tradition_traditional_clothes": {
        "bg": "#1a1020", "accent": "#e91e63",
        "icon": """
        <circle cx="100" cy="110" r="20" fill="#f0c8a0"/>
        <rect x="80" y="130" width="40" height="70" rx="5" fill="#1565c0"/>
        <circle cx="150" cy="100" r="18" fill="#f0c8a0"/>
        <rect x="132" y="118" width="36" height="75" rx="5" fill="#e91e63"/>
        <circle cx="200" cy="115" r="20" fill="#f0c8a0"/>
        <rect x="180" y="135" width="40" height="65" rx="5" fill="#1565c0"/>
        <text x="150" y="225" text-anchor="middle" font-size="12" fill="#e91e63" font-family="sans-serif">традиция</text>
        """,
    },
    "family_paying_restaurant_bill": {
        "bg": "#1a1a2e", "accent": "#ffc107",
        "icon": """
        <rect x="60" y="120" width="180" height="100" rx="8" fill="#2a2a4a"/>
        <rect x="80" y="140" width="80" height="60" rx="4" fill="#3a3a5a"/>
        <rect x="90" y="150" width="60" height="8" rx="2" fill="#fff" opacity="0.6"/>
        <rect x="90" y="165" width="50" height="8" rx="2" fill="#fff" opacity="0.4"/>
        <rect x="90" y="180" width="40" height="8" rx="2" fill="#ffc107" opacity="0.8"/>
        <circle cx="200" cy="130" r="20" fill="#f0c8a0"/>
        <rect x="185" y="150" width="30" height="10" rx="3" fill="#ffc107"/>
        <text x="150" y="240" text-anchor="middle" font-size="13" fill="#ffc107" font-family="sans-serif">счёт</text>
        """,
    },
    "family_watching_evening_news_on_tv": {
        "bg": "#0a1020", "accent": "#42a5f5",
        "icon": """
        <rect x="60" y="80" width="180" height="120" rx="8" fill="#1a2a3a"/>
        <rect x="70" y="90" width="160" height="100" rx="4" fill="#0d47a1"/>
        <rect x="75" y="95" width="150" height="90" rx="3" fill="#1565c0"/>
        <text x="150" y="150" text-anchor="middle" font-size="14" fill="#fff" font-family="sans-serif">📺 НОВОСТИ</text>
        <circle cx="100" cy="225" r="18" fill="#f0c8a0"/>
        <circle cx="150" cy="225" r="18" fill="#f0c8a0"/>
        <circle cx="200" cy="225" r="18" fill="#f0c8a0"/>
        """,
    },
    "family_watching_tv_together_on_sofa": {
        "bg": "#1a1020", "accent": "#ab47bc",
        "icon": """
        <rect x="40" y="160" width="220" height="70" rx="15" fill="#4a2a5a"/>
        <rect x="55" y="140" width="190" height="30" rx="8" fill="#5a3a6a"/>
        <circle cx="90" cy="145" r="20" fill="#f0c8a0"/>
        <circle cx="150" cy="145" r="20" fill="#f0c8a0"/>
        <circle cx="210" cy="145" r="20" fill="#f0c8a0"/>
        <rect x="100" y="70" width="100" height="65" rx="6" fill="#1a1a3a"/>
        <rect x="105" y="75" width="90" height="55" rx="4" fill="#0d47a1"/>
        <text x="150" y="235" text-anchor="middle" font-size="12" fill="#ab47bc" font-family="sans-serif">диван, телевизор</text>
        """,
    },
    "friends_already_sitting_at_cafe": {
        "bg": "#1a1000", "accent": "#ff8f00",
        "icon": """
        <rect x="70" y="150" width="160" height="80" rx="8" fill="#3a2a1a"/>
        <circle cx="110" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="88" y="152" width="44" height="78" rx="5" fill="#5a4a8a"/>
        <circle cx="190" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="168" y="152" width="44" height="78" rx="5" fill="#4a7a5a"/>
        <circle cx="115" cy="180" r="10" fill="#fff" opacity="0.8"/>
        <circle cx="185" cy="180" r="10" fill="#fff" opacity="0.8"/>
        <text x="150" y="250" text-anchor="middle" font-size="13" fill="#ff8f00" font-family="sans-serif">кафе</text>
        """,
    },
    "graduate_receiving_diploma_at_ceremony": {
        "bg": "#001a0a", "accent": "#4caf50",
        "icon": """
        <circle cx="150" cy="100" r="25" fill="#f0c8a0"/>
        <rect x="120" y="125" width="60" height="90" rx="8" fill="#1a237e"/>
        <rect x="110" y="85" width="80" height="20" rx="10" fill="#1a237e"/>
        <rect x="145" y="60" width="10" height="30" fill="#1a237e"/>
        <rect x="100" y="180" width="100" height="70" rx="5" fill="#fff" opacity="0.9"/>
        <rect x="110" y="195" width="80" height="8" rx="3" fill="#333"/>
        <rect x="110" y="210" width="60" height="8" rx="3" fill="#333"/>
        <rect x="110" y="225" width="70" height="8" rx="3" fill="#4caf50"/>
        <text x="150" y="265" text-anchor="middle" font-size="12" fill="#4caf50" font-family="sans-serif">диплом</text>
        """,
    },
    "journalist_interviewing_with_microphone": {
        "bg": "#0a0a1a", "accent": "#ef5350",
        "icon": """
        <circle cx="100" cy="110" r="22" fill="#f0c8a0"/>
        <rect x="80" y="132" width="40" height="80" rx="5" fill="#424242"/>
        <rect x="140" y="90" width="20" height="50" rx="10" fill="#ef5350"/>
        <rect x="135" y="135" width="30" height="5" rx="2" fill="#666"/>
        <rect x="147" y="140" width="6" height="30" fill="#666"/>
        <circle cx="200" cy="110" r="22" fill="#f0c8a0"/>
        <rect x="180" y="132" width="40" height="80" rx="5" fill="#5a4a2a"/>
        <text x="150" y="230" text-anchor="middle" font-size="12" fill="#ef5350" font-family="sans-serif">интервью</text>
        """,
    },
    "landlord_showing_flat_to_tenant": {
        "bg": "#1a1500", "accent": "#ffa726",
        "icon": """
        <rect x="60" y="80" width="180" height="150" rx="8" fill="#2a2010"/>
        <rect x="75" y="95" width="70" height="120" rx="4" fill="#3a3020"/>
        <rect x="155" y="95" width="70" height="120" rx="4" fill="#3a3020"/>
        <rect x="90" y="130" width="40" height="50" rx="3" fill="#4a6a8a"/>
        <rect x="165" y="130" width="40" height="50" rx="3" fill="#4a6a8a"/>
        <circle cx="100" cy="115" r="18" fill="#f0c8a0"/>
        <circle cx="200" cy="115" r="18" fill="#f0c8a0"/>
        <rect x="95" y="195" width="10" height="35" rx="5" fill="#ffa726"/>
        <text x="150" y="245" text-anchor="middle" font-size="12" fill="#ffa726" font-family="sans-serif">квартира</text>
        """,
    },
    "man_at_atm_withdrawing_cash": {
        "bg": "#001020", "accent": "#00bcd4",
        "icon": """
        <rect x="90" y="80" width="120" height="160" rx="8" fill="#0d47a1"/>
        <rect x="100" y="95" width="100" height="70" rx="4" fill="#1565c0"/>
        <rect x="110" y="105" width="80" height="50" rx="3" fill="#42a5f5" opacity="0.5"/>
        <text x="150" y="138" text-anchor="middle" font-size="12" fill="#fff" font-family="sans-serif">💳 ATM</text>
        <rect x="115" y="175" width="70" height="8" rx="4" fill="#1976d2"/>
        <rect x="115" y="188" width="70" height="8" rx="4" fill="#1976d2"/>
        <rect x="115" y="201" width="70" height="8" rx="4" fill="#1976d2"/>
        <circle cx="75" cy="140" r="22" fill="#f0c8a0"/>
        <rect x="53" y="162" width="44" height="80" rx="5" fill="#37474f"/>
        <rect x="60" y="170" width="30" height="15" rx="3" fill="#00bcd4" opacity="0.8"/>
        <text x="150" y="255" text-anchor="middle" font-size="12" fill="#00bcd4" font-family="sans-serif">банкомат</text>
        """,
    },
    "man_at_pharmacy_buying_medicine": {
        "bg": "#001a0a", "accent": "#26a69a",
        "icon": """
        <rect x="50" y="80" width="200" height="140" rx="8" fill="#00695c"/>
        <text x="150" y="125" text-anchor="middle" font-size="30" fill="#fff">⚕️</text>
        <rect x="70" y="140" width="100" height="60" rx="4" fill="#00796b"/>
        <rect x="80" y="150" width="80" height="40" rx="3" fill="#4db6ac" opacity="0.5"/>
        <circle cx="210" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="188" y="152" width="44" height="70" rx="5" fill="#37474f"/>
        <text x="150" y="240" text-anchor="middle" font-size="12" fill="#26a69a" font-family="sans-serif">аптека</text>
        """,
    },
    "man_folding_clothes_at_home": {
        "bg": "#0a1020", "accent": "#7986cb",
        "icon": """
        <rect x="60" y="140" width="180" height="80" rx="8" fill="#3a3a5a"/>
        <rect x="75" y="150" width="150" height="60" rx="4" fill="#4a4a6a"/>
        <rect x="85" y="155" width="50" height="40" rx="3" fill="#ef9a9a"/>
        <rect x="145" y="155" width="50" height="40" rx="3" fill="#90caf9"/>
        <circle cx="150" cy="120" r="22" fill="#f0c8a0"/>
        <rect x="128" y="142" width="44" height="78" rx="5" fill="#37474f"/>
        <text x="150" y="238" text-anchor="middle" font-size="12" fill="#7986cb" font-family="sans-serif">стирка</text>
        """,
    },
    "man_hailing_taxi_on_street": {
        "bg": "#1a1000", "accent": "#ffca28",
        "icon": """
        <rect x="40" y="160" width="220" height="80" rx="5" fill="#333"/>
        <rect x="70" y="130" width="120" height="60" rx="10" fill="#ffca28"/>
        <rect x="80" y="140" width="40" height="35" rx="3" fill="#b3e5fc"/>
        <rect x="130" y="140" width="40" height="35" rx="3" fill="#b3e5fc"/>
        <circle cx="100" cy="190" r="20" fill="#222"/>
        <circle cx="200" cy="190" r="20" fill="#222"/>
        <circle cx="200" cy="115" r="22" fill="#f0c8a0"/>
        <rect x="178" y="137" width="44" height="80" rx="5" fill="#37474f"/>
        <line x1="200" y1="115" x2="230" y2="100" stroke="#f0c8a0" stroke-width="4" stroke-linecap="round"/>
        <text x="150" y="258" text-anchor="middle" font-size="12" fill="#ffca28" font-family="sans-serif">такси</text>
        """,
    },
    "man_in_yoga_meditation_pose": {
        "bg": "#0a1020", "accent": "#80cbc4",
        "icon": """
        <circle cx="150" cy="100" r="25" fill="#f0c8a0"/>
        <path d="M 90 170 Q 150 130 210 170" fill="#4db6ac" opacity="0.8"/>
        <line x1="90" y1="170" x2="60" y2="190" stroke="#f0c8a0" stroke-width="6" stroke-linecap="round"/>
        <line x1="210" y1="170" x2="240" y2="190" stroke="#f0c8a0" stroke-width="6" stroke-linecap="round"/>
        <line x1="90" y1="170" x2="70" y2="210" stroke="#f0c8a0" stroke-width="6" stroke-linecap="round"/>
        <line x1="210" y1="170" x2="230" y2="210" stroke="#f0c8a0" stroke-width="6" stroke-linecap="round"/>
        <text x="150" y="240" text-anchor="middle" font-size="13" fill="#80cbc4" font-family="sans-serif">медитация</text>
        """,
    },
    "man_looking_at_calendar_disappointed": {
        "bg": "#1a0010", "accent": "#ef9a9a",
        "icon": """
        <rect x="80" y="90" width="140" height="140" rx="8" fill="#3a2a3a"/>
        <rect x="90" y="100" width="120" height="120" rx="4" fill="#4a3a4a"/>
        <rect x="90" y="100" width="120" height="30" rx="4" fill="#c62828"/>
        <text x="150" y="122" text-anchor="middle" font-size="14" fill="#fff" font-family="sans-serif">МАРТ</text>
        <text x="140" y="175" text-anchor="middle" font-size="28" fill="#ef9a9a" font-family="sans-serif">✗</text>
        <circle cx="70" cy="130" r="22" fill="#f0c8a0"/>
        <path d="M 60 145 Q 70 155 80 145" fill="none" stroke="#555" stroke-width="3" stroke-linecap="round"/>
        <text x="150" y="250" text-anchor="middle" font-size="12" fill="#ef9a9a" font-family="sans-serif">разочарование</text>
        """,
    },
    "man_paying_at_cashier": {
        "bg": "#001020", "accent": "#4fc3f7",
        "icon": """
        <rect x="80" y="100" width="140" height="100" rx="8" fill="#0d47a1"/>
        <rect x="90" y="110" width="120" height="80" rx="4" fill="#1565c0"/>
        <rect x="100" y="120" width="100" height="50" rx="3" fill="#42a5f5" opacity="0.4"/>
        <text x="150" y="152" text-anchor="middle" font-size="12" fill="#fff" font-family="sans-serif">💳 касса</text>
        <circle cx="75" cy="115" r="22" fill="#f0c8a0"/>
        <rect x="53" y="137" width="44" height="80" rx="5" fill="#37474f"/>
        <rect x="60" y="150" width="30" height="15" rx="3" fill="#4fc3f7" opacity="0.8"/>
        <text x="150" y="215" text-anchor="middle" font-size="12" fill="#4fc3f7" font-family="sans-serif">платёж</text>
        """,
    },
    "man_working_at_computer_in_office": {
        "bg": "#001015", "accent": "#4dd0e1",
        "icon": """
        <rect x="60" y="150" width="180" height="80" rx="5" fill="#2a3a4a"/>
        <rect x="80" y="90" width="140" height="95" rx="6" fill="#0d47a1"/>
        <rect x="85" y="95" width="130" height="85" rx="4" fill="#1a237e"/>
        <rect x="90" y="100" width="120" height="75" rx="3" fill="#1565c0" opacity="0.7"/>
        <rect x="130" y="185" width="40" height="8" rx="3" fill="#37474f"/>
        <rect x="90" y="200" width="120" height="15" rx="5" fill="#37474f"/>
        <circle cx="150" cy="155" r="20" fill="#f0c8a0"/>
        <text x="150" y="245" text-anchor="middle" font-size="12" fill="#4dd0e1" font-family="sans-serif">офис</text>
        """,
    },
    "museum_guide_explaining_artifacts": {
        "bg": "#1a1000", "accent": "#d4a017",
        "icon": """
        <rect x="50" y="80" width="200" height="150" rx="8" fill="#2a2010"/>
        <rect x="80" y="100" width="80" height="100" rx="4" fill="#3a3020"/>
        <rect x="90" y="115" width="60" height="70" rx="3" fill="#8d6e63"/>
        <text x="120" y="158" text-anchor="middle" font-size="24" fill="#d4a017">🏛️</text>
        <circle cx="210" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="188" y="152" width="44" height="80" rx="5" fill="#4a6a4a"/>
        <line x1="205" y1="135" x2="175" y2="150" stroke="#d4a017" stroke-width="3" stroke-linecap="round"/>
        <text x="150" y="248" text-anchor="middle" font-size="12" fill="#d4a017" font-family="sans-serif">музей</text>
        """,
    },
    "person_counting_coins_on_table": {
        "bg": "#1a1000", "accent": "#ffb300",
        "icon": """
        <rect x="40" y="160" width="220" height="80" rx="5" fill="#3a2a10"/>
        <circle cx="100" cy="190" r="15" fill="#ffb300"/>
        <circle cx="130" cy="190" r="15" fill="#ffa000"/>
        <circle cx="160" cy="190" r="15" fill="#ff8f00"/>
        <circle cx="190" cy="190" r="15" fill="#ffb300"/>
        <circle cx="220" cy="190" r="15" fill="#ffa000"/>
        <circle cx="150" cy="120" r="25" fill="#f0c8a0"/>
        <rect x="125" y="145" width="50" height="15" rx="3" fill="#f0c8a0"/>
        <text x="150" y="250" text-anchor="middle" font-size="12" fill="#ffb300" font-family="sans-serif">монеты</text>
        """,
    },
    "person_eating_healthy_bowl_at_table": {
        "bg": "#001a05", "accent": "#66bb6a",
        "icon": """
        <rect x="60" y="160" width="180" height="80" rx="5" fill="#2a3a2a"/>
        <ellipse cx="150" cy="185" rx="70" ry="40" fill="#1b5e20"/>
        <ellipse cx="150" cy="180" rx="60" ry="35" fill="#2e7d32"/>
        <circle cx="130" cy="170" r="10" fill="#ff8f00"/>
        <circle cx="160" cy="165" r="8" fill="#ef5350"/>
        <circle cx="145" cy="180" r="12" fill="#66bb6a"/>
        <circle cx="170" cy="178" r="9" fill="#fff176"/>
        <circle cx="150" cy="95" r="25" fill="#f0c8a0"/>
        <rect x="125" y="120" width="50" height="40" rx="5" fill="#37474f"/>
        <text x="150" y="252" text-anchor="middle" font-size="12" fill="#66bb6a" font-family="sans-serif">здоровая еда</text>
        """,
    },
    "person_resting_in_bed_with_cold": {
        "bg": "#0a0a1a", "accent": "#90caf9",
        "icon": """
        <rect x="40" y="150" width="220" height="90" rx="10" fill="#1a2a3a"/>
        <rect x="40" y="150" width="220" height="25" rx="8" fill="#0d47a1"/>
        <rect x="40" y="145" width="70" height="80" rx="8" fill="#37474f"/>
        <ellipse cx="150" cy="155" rx="35" ry="25" fill="#f0c8a0"/>
        <rect x="115" y="160" width="70" height="10" rx="5" fill="#fff" opacity="0.4"/>
        <text x="150" y="145" text-anchor="middle" font-size="20" fill="#ef5350">🤧</text>
        <text x="150" y="250" text-anchor="middle" font-size="12" fill="#90caf9" font-family="sans-serif">болезнь</text>
        """,
    },
    "person_studying_travel_map_at_table": {
        "bg": "#0a1500", "accent": "#aed581",
        "icon": """
        <rect x="50" y="160" width="200" height="80" rx="5" fill="#2a3a2a"/>
        <rect x="70" y="140" width="160" height="110" rx="4" fill="#1b5e20"/>
        <rect x="80" y="150" width="140" height="90" rx="3" fill="#388e3c"/>
        <path d="M 80 180 Q 120 160 160 175 Q 200 190 220 170" fill="none" stroke="#aed581" stroke-width="3"/>
        <circle cx="130" cy="170" r="8" fill="#ef5350"/>
        <circle cx="180" cy="182" r="8" fill="#ffb300"/>
        <circle cx="150" cy="110" r="25" fill="#f0c8a0"/>
        <rect x="125" y="135" width="50" height="30" rx="5" fill="#37474f"/>
        <text x="150" y="258" text-anchor="middle" font-size="12" fill="#aed581" font-family="sans-serif">карта</text>
        """,
    },
    "person_working_on_laptop_at_cafe": {
        "bg": "#1a1000", "accent": "#ff8a65",
        "icon": """
        <rect x="40" y="160" width="220" height="80" rx="5" fill="#3a2a10"/>
        <rect x="70" y="140" width="160" height="100" rx="6" fill="#1a1a2a"/>
        <rect x="75" y="145" width="150" height="80" rx="4" fill="#1565c0" opacity="0.8"/>
        <rect x="65" y="225" width="170" height="8" rx="4" fill="#37474f"/>
        <circle cx="150" cy="110" r="25" fill="#f0c8a0"/>
        <circle cx="100" cy="195" r="12" fill="#fff" opacity="0.7"/>
        <text x="150" y="250" text-anchor="middle" font-size="12" fill="#ff8a65" font-family="sans-serif">ноутбук в кафе</text>
        """,
    },
    "politician_giving_speech_at_podium": {
        "bg": "#0a0a1a", "accent": "#7986cb",
        "icon": """
        <rect x="100" y="160" width="100" height="80" rx="5" fill="#283593"/>
        <rect x="110" y="155" width="80" height="15" rx="3" fill="#3949ab"/>
        <circle cx="150" cy="120" r="25" fill="#f0c8a0"/>
        <rect x="125" y="145" width="50" height="15" rx="3" fill="#37474f"/>
        <line x1="150" y1="140" x2="150" y2="165" stroke="#37474f" stroke-width="8"/>
        <line x1="125" y1="155" x2="150" y2="145" stroke="#f0c8a0" stroke-width="5" stroke-linecap="round"/>
        <line x1="175" y1="155" x2="150" y2="145" stroke="#f0c8a0" stroke-width="5" stroke-linecap="round"/>
        <rect x="80" y="70" width="140" height="40" rx="5" fill="#1a237e"/>
        <text x="150" y="97" text-anchor="middle" font-size="12" fill="#fff" font-family="sans-serif">РЕЧЬ</text>
        <text x="150" y="258" text-anchor="middle" font-size="12" fill="#7986cb" font-family="sans-serif">политик</text>
        """,
    },
    "professional_presenting_in_boardroom": {
        "bg": "#001020", "accent": "#4fc3f7",
        "icon": """
        <rect x="50" y="80" width="200" height="120" rx="6" fill="#0d47a1"/>
        <rect x="55" y="85" width="190" height="110" rx="4" fill="#1565c0" opacity="0.5"/>
        <rect x="70" y="95" width="100" height="70" rx="3" fill="#1976d2"/>
        <rect x="80" y="105" width="80" height="10" rx="3" fill="#fff" opacity="0.6"/>
        <rect x="80" y="120" width="60" height="10" rx="3" fill="#fff" opacity="0.4"/>
        <rect x="80" y="135" width="70" height="10" rx="3" fill="#4fc3f7" opacity="0.8"/>
        <circle cx="215" cy="120" r="22" fill="#f0c8a0"/>
        <rect x="193" y="142" width="44" height="90" rx="5" fill="#37474f"/>
        <line x1="195" y1="115" x2="170" y2="120" stroke="#4fc3f7" stroke-width="3"/>
        <text x="150" y="220" text-anchor="middle" font-size="12" fill="#4fc3f7" font-family="sans-serif">презентация</text>
        """,
    },
    "protest_march_people_with_signs": {
        "bg": "#1a0000", "accent": "#ef5350",
        "icon": """
        <circle cx="80" cy="120" r="18" fill="#f0c8a0"/>
        <circle cx="150" cy="110" r="20" fill="#f0c8a0"/>
        <circle cx="220" cy="120" r="18" fill="#f0c8a0"/>
        <rect x="62" y="138" width="36" height="70" rx="5" fill="#c62828"/>
        <rect x="130" y="130" width="40" height="80" rx="5" fill="#1565c0"/>
        <rect x="202" y="138" width="36" height="70" rx="5" fill="#2e7d32"/>
        <rect x="40" y="100" width="50" height="30" rx="3" fill="#fff"/>
        <text x="65" y="120" text-anchor="middle" font-size="10" fill="#333" font-family="sans-serif">МИР</text>
        <rect x="115" y="85" width="70" height="30" rx="3" fill="#fff"/>
        <text x="150" y="105" text-anchor="middle" font-size="10" fill="#c62828" font-family="sans-serif">ПРОТЕСТ</text>
        <text x="150" y="225" text-anchor="middle" font-size="12" fill="#ef5350" font-family="sans-serif">митинг</text>
        """,
    },
    "solar_panels_on_rooftop": {
        "bg": "#001020", "accent": "#ffca28",
        "icon": """
        <polygon points="50,180 150,100 250,180" fill="#37474f"/>
        <polygon points="55,180 150,105 245,180" fill="#455a64"/>
        <rect x="70" y="130" width="50" height="35" rx="2" fill="#1565c0"/>
        <rect x="75" y="133" width="20" height="12" rx="1" fill="#1976d2"/>
        <rect x="97" y="133" width="20" height="12" rx="1" fill="#1976d2"/>
        <rect x="75" y="147" width="20" height="12" rx="1" fill="#1976d2"/>
        <rect x="97" y="147" width="20" height="12" rx="1" fill="#1976d2"/>
        <rect x="130" y="120" width="50" height="35" rx="2" fill="#1565c0"/>
        <rect x="135" y="123" width="20" height="12" rx="1" fill="#1976d2"/>
        <rect x="157" y="123" width="20" height="12" rx="1" fill="#1976d2"/>
        <rect x="135" y="137" width="20" height="12" rx="1" fill="#1976d2"/>
        <rect x="157" y="137" width="20" height="12" rx="1" fill="#1976d2"/>
        <circle cx="220" cy="70" r="30" fill="#ffca28" opacity="0.8"/>
        <text x="150" y="220" text-anchor="middle" font-size="12" fill="#ffca28" font-family="sans-serif">солнечные панели</text>
        """,
    },
    "student_taking_notes_at_university_lecture": {
        "bg": "#0a0a1a", "accent": "#ce93d8",
        "icon": """
        <rect x="50" y="80" width="200" height="120" rx="6" fill="#1a0030"/>
        <rect x="55" y="85" width="190" height="110" rx="4" fill="#4a148c" opacity="0.4"/>
        <rect x="60" y="90" width="120" height="80" rx="3" fill="#6a1b9a" opacity="0.5"/>
        <text x="120" y="140" text-anchor="middle" font-size="12" fill="#ce93d8" font-family="sans-serif">лекция</text>
        <circle cx="80" cy="220" r="18" fill="#f0c8a0"/>
        <rect x="62" y="238" width="36" height="20" rx="3" fill="#4a148c"/>
        <rect x="80" y="220" width="80" height="50" rx="4" fill="#fff" opacity="0.9"/>
        <rect x="87" y="228" width="60" height="6" rx="2" fill="#333"/>
        <rect x="87" y="238" width="50" height="6" rx="2" fill="#333"/>
        <rect x="87" y="248" width="55" height="6" rx="2" fill="#333"/>
        <text x="150" y="268" text-anchor="middle" font-size="12" fill="#ce93d8" font-family="sans-serif">записи, лекция</text>
        """,
    },
    "students_studying_together_in_library": {
        "bg": "#0a1020", "accent": "#80deea",
        "icon": """
        <rect x="40" y="160" width="220" height="80" rx="5" fill="#1a2a3a"/>
        <rect x="60" y="130" width="80" height="100" rx="4" fill="#0d47a1" opacity="0.6"/>
        <rect x="160" y="130" width="80" height="100" rx="4" fill="#0d47a1" opacity="0.6"/>
        <circle cx="100" cy="115" r="20" fill="#f0c8a0"/>
        <circle cx="200" cy="115" r="20" fill="#f0c8a0"/>
        <rect x="70" y="170" width="60" height="40" rx="3" fill="#fff" opacity="0.8"/>
        <rect x="170" y="170" width="60" height="40" rx="3" fill="#fff" opacity="0.8"/>
        <rect x="75" y="178" width="50" height="6" rx="2" fill="#333"/>
        <rect x="75" y="188" width="40" height="6" rx="2" fill="#333"/>
        <text x="150" y="248" text-anchor="middle" font-size="12" fill="#80deea" font-family="sans-serif">библиотека</text>
        """,
    },
    "tourist_at_bus_stop_reading_schedule": {
        "bg": "#001015", "accent": "#4dd0e1",
        "icon": """
        <rect x="70" y="80" width="180" height="150" rx="5" fill="#1a2a3a"/>
        <rect x="75" y="85" width="170" height="140" rx="3" fill="#0d47a1"/>
        <text x="160" y="115" text-anchor="middle" font-size="12" fill="#fff" font-family="sans-serif">🚌 РАСПИСАНИЕ</text>
        <rect x="85" y="125" width="130" height="8" rx="3" fill="#fff" opacity="0.6"/>
        <rect x="85" y="138" width="110" height="8" rx="3" fill="#fff" opacity="0.4"/>
        <rect x="85" y="151" width="120" height="8" rx="3" fill="#4dd0e1" opacity="0.8"/>
        <rect x="60" y="75" width="10" height="185" fill="#546e7a"/>
        <circle cx="70" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="48" y="152" width="44" height="80" rx="5" fill="#455a64"/>
        <text x="150" y="258" text-anchor="middle" font-size="12" fill="#4dd0e1" font-family="sans-serif">остановка</text>
        """,
    },
    "tourist_checking_in_at_hotel_reception": {
        "bg": "#001a1a", "accent": "#4db6ac",
        "icon": """
        <rect x="50" y="80" width="200" height="50" rx="5" fill="#1a3a3a"/>
        <rect x="60" y="130" width="180" height="120" rx="5" fill="#0d3333"/>
        <rect x="70" y="140" width="70" height="100" rx="4" fill="#1a4a4a"/>
        <rect x="160" y="140" width="60" height="100" rx="4" fill="#1a4a4a"/>
        <rect x="60" y="130" width="180" height="20" rx="3" fill="#00695c"/>
        <text x="150" y="147" text-anchor="middle" font-size="11" fill="#fff" font-family="sans-serif">RECEPTION</text>
        <circle cx="90" cy="160" r="18" fill="#f0c8a0"/>
        <rect x="72" y="178" width="36" height="65" rx="5" fill="#37474f"/>
        <circle cx="210" cy="155" r="18" fill="#f0c8a0"/>
        <rect x="192" y="173" width="36" height="70" rx="5" fill="#00695c"/>
        <rect x="115" y="150" width="50" height="30" rx="4" fill="#fff" opacity="0.9"/>
        <rect x="120" y="157" width="40" height="5" rx="2" fill="#333"/>
        <rect x="120" y="166" width="30" height="5" rx="2" fill="#333"/>
        <text x="150" y="258" text-anchor="middle" font-size="12" fill="#4db6ac" font-family="sans-serif">регистрация в отеле</text>
        """,
    },
    "tourists_at_ancient_ruins_with_guide": {
        "bg": "#1a1000", "accent": "#d4a017",
        "icon": """
        <rect x="50" y="160" width="200" height="80" rx="5" fill="#3a2a10"/>
        <rect x="60" y="100" width="30" height="70" fill="#8d6e63"/>
        <rect x="105" y="80" width="30" height="90" fill="#8d6e63"/>
        <rect x="155" y="90" width="30" height="80" fill="#8d6e63"/>
        <rect x="200" y="105" width="30" height="65" fill="#8d6e63"/>
        <rect x="55" y="165" width="190" height="10" fill="#a1887f"/>
        <circle cx="90" cy="155" r="16" fill="#f0c8a0"/>
        <rect x="74" y="171" width="32" height="60" rx="4" fill="#5a4a2a"/>
        <circle cx="150" cy="150" r="18" fill="#f0c8a0"/>
        <rect x="132" y="168" width="36" height="65" rx="4" fill="#1565c0"/>
        <circle cx="210" cy="155" r="16" fill="#f0c8a0"/>
        <rect x="194" y="171" width="32" height="60" rx="4" fill="#2e7d32"/>
        <line x1="150" y1="155" x2="120" y2="165" stroke="#d4a017" stroke-width="3"/>
        <text x="150" y="250" text-anchor="middle" font-size="12" fill="#d4a017" font-family="sans-serif">древние руины, гид</text>
        """,
    },
    "tourists_photographing_ancient_ruins": {
        "bg": "#1a1500", "accent": "#ffa726",
        "icon": """
        <rect x="50" y="160" width="200" height="80" rx="5" fill="#3a2a10"/>
        <rect x="65" y="110" width="25" height="60" fill="#8d6e63"/>
        <rect x="105" y="90" width="25" height="80" fill="#8d6e63"/>
        <rect x="150" y="100" width="25" height="70" fill="#8d6e63"/>
        <rect x="195" y="105" width="25" height="65" fill="#8d6e63"/>
        <rect x="55" y="168" width="190" height="8" fill="#a1887f"/>
        <circle cx="90" cy="150" r="18" fill="#f0c8a0"/>
        <rect x="74" y="168" width="36" height="70" rx="4" fill="#c62828"/>
        <rect x="82" y="140" width="30" height="20" rx="4" fill="#333"/>
        <rect x="87" y="142" width="10" height="10" rx="5" fill="#b3e5fc"/>
        <circle cx="200" cy="150" r="18" fill="#f0c8a0"/>
        <rect x="184" y="168" width="36" height="70" rx="4" fill="#1565c0"/>
        <rect x="192" y="140" width="30" height="20" rx="4" fill="#333"/>
        <rect x="197" y="142" width="10" height="10" rx="5" fill="#b3e5fc"/>
        <text x="150" y="255" text-anchor="middle" font-size="12" fill="#ffa726" font-family="sans-serif">фото руин</text>
        """,
    },
    "two_people_debating_social_issue_in_square": {
        "bg": "#0a001a", "accent": "#b39ddb",
        "icon": """
        <circle cx="100" cy="110" r="22" fill="#f0c8a0"/>
        <rect x="78" y="132" width="44" height="80" rx="5" fill="#1565c0"/>
        <circle cx="200" cy="110" r="22" fill="#f0c8a0"/>
        <rect x="178" y="132" width="44" height="80" rx="5" fill="#c62828"/>
        <path d="M 125 120 Q 150 100 175 120" fill="none" stroke="#b39ddb" stroke-width="2" stroke-dasharray="5,3"/>
        <rect x="60" y="88" width="50" height="25" rx="4" fill="#fff" opacity="0.9"/>
        <text x="85" y="105" text-anchor="middle" font-size="10" fill="#333" font-family="sans-serif">ДА</text>
        <rect x="190" y="88" width="50" height="25" rx="4" fill="#fff" opacity="0.9"/>
        <text x="215" y="105" text-anchor="middle" font-size="10" fill="#c62828" font-family="sans-serif">НЕТ</text>
        <text x="150" y="230" text-anchor="middle" font-size="12" fill="#b39ddb" font-family="sans-serif">дискуссия</text>
        """,
    },
    "two_women_on_phone_planning_weekend_meetup": {
        "bg": "#1a001a", "accent": "#f48fb1",
        "icon": """
        <circle cx="80" cy="110" r="22" fill="#f0c8a0"/>
        <rect x="58" y="132" width="44" height="80" rx="5" fill="#ad1457"/>
        <rect x="65" y="98" width="20" height="30" rx="5" fill="#333"/>
        <rect x="68" y="102" width="14" height="20" rx="3" fill="#4fc3f7" opacity="0.6"/>
        <circle cx="220" cy="110" r="22" fill="#f0c8a0"/>
        <rect x="198" y="132" width="44" height="80" rx="5" fill="#6a1b9a"/>
        <rect x="215" y="98" width="20" height="30" rx="5" fill="#333"/>
        <rect x="218" y="102" width="14" height="20" rx="3" fill="#4fc3f7" opacity="0.6"/>
        <path d="M 90 108 Q 150 75 210 108" fill="none" stroke="#f48fb1" stroke-width="2" stroke-dasharray="6,3"/>
        <text x="150" y="95" text-anchor="middle" font-size="20" fill="#f48fb1">📅</text>
        <text x="150" y="230" text-anchor="middle" font-size="11" fill="#f48fb1" font-family="sans-serif">звонок, встреча</text>
        """,
    },
    "volunteers_collecting_trash_and_recycling_park": {
        "bg": "#001a00", "accent": "#81c784",
        "icon": """
        <rect x="40" y="180" width="220" height="60" rx="5" fill="#1b5e20"/>
        <circle cx="100" cy="150" r="18" fill="#f0c8a0"/>
        <rect x="82" y="168" width="36" height="75" rx="5" fill="#2e7d32"/>
        <circle cx="200" cy="150" r="18" fill="#f0c8a0"/>
        <rect x="182" y="168" width="36" height="75" rx="5" fill="#33691e"/>
        <rect x="70" y="195" width="40" height="50" rx="5" fill="#1565c0"/>
        <text x="90" y="225" text-anchor="middle" font-size="16" fill="#fff">♻️</text>
        <rect x="180" y="200" width="40" height="45" rx="5" fill="#37474f"/>
        <text x="200" y="228" text-anchor="middle" font-size="16" fill="#fff">🗑️</text>
        <text x="150" y="258" text-anchor="middle" font-size="11" fill="#81c784" font-family="sans-serif">волонтёры</text>
        """,
    },
    "woman_alone_at_cafe_drinking_coffee": {
        "bg": "#1a1000", "accent": "#ff8a65",
        "icon": """
        <rect x="50" y="160" width="200" height="80" rx="5" fill="#3a2a10"/>
        <circle cx="150" cy="120" r="25" fill="#f0c8a0"/>
        <rect x="125" y="145" width="50" height="80" rx="5" fill="#ad1457"/>
        <ellipse cx="150" cy="200" rx="30" ry="15" fill="#fff" opacity="0.8"/>
        <ellipse cx="150" cy="196" rx="22" ry="10" fill="#4e342e"/>
        <rect x="120" y="210" width="60" height="8" rx="4" fill="#5d4037"/>
        <text x="150" y="252" text-anchor="middle" font-size="12" fill="#ff8a65" font-family="sans-serif">кофе, одна</text>
        """,
    },
    "woman_asking_price_at_clothing_store": {
        "bg": "#1a0020", "accent": "#ce93d8",
        "icon": """
        <rect x="50" y="80" width="200" height="160" rx="6" fill="#2a0040"/>
        <rect x="70" y="90" width="60" height="100" rx="4" fill="#4a0060"/>
        <rect x="150" y="90" width="60" height="100" rx="4" fill="#4a0060"/>
        <rect x="75" y="100" width="50" height="70" rx="3" fill="#7b1fa2" opacity="0.5"/>
        <rect x="155" y="100" width="50" height="70" rx="3" fill="#7b1fa2" opacity="0.5"/>
        <circle cx="75" cy="200" r="20" fill="#f0c8a0"/>
        <rect x="55" y="220" width="40" height="20" rx="3" fill="#c62828"/>
        <circle cx="215" cy="195" r="20" fill="#f0c8a0"/>
        <rect x="195" y="215" width="40" height="20" rx="3" fill="#1565c0"/>
        <rect x="130" y="180" width="40" height="20" rx="4" fill="#fff" opacity="0.8"/>
        <text x="150" y="194" text-anchor="middle" font-size="10" fill="#333">цена?</text>
        <text x="150" y="255" text-anchor="middle" font-size="12" fill="#ce93d8" font-family="sans-serif">магазин одежды</text>
        """,
    },
    "woman_at_doctor_describing_symptoms": {
        "bg": "#001a1a", "accent": "#4db6ac",
        "icon": """
        <rect x="50" y="80" width="200" height="150" rx="6" fill="#004d4d"/>
        <rect x="160" y="90" width="80" height="130" rx="5" fill="#00695c"/>
        <text x="200" y="165" text-anchor="middle" font-size="30" fill="#fff">⚕️</text>
        <circle cx="90" cy="150" r="22" fill="#f0c8a0"/>
        <rect x="68" y="172" width="44" height="60" rx="5" fill="#37474f"/>
        <circle cx="200" cy="120" r="20" fill="#f0c8a0"/>
        <rect x="180" y="140" width="40" height="60" rx="5" fill="#00796b"/>
        <text x="150" y="250" text-anchor="middle" font-size="12" fill="#4db6ac" font-family="sans-serif">врач, симптомы</text>
        """,
    },
    "woman_at_job_interview_holding_cv": {
        "bg": "#001020", "accent": "#4fc3f7",
        "icon": """
        <rect x="50" y="80" width="200" height="150" rx="6" fill="#0a2a3a"/>
        <circle cx="90" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="68" y="152" width="44" height="80" rx="5" fill="#37474f"/>
        <rect x="85" y="175" width="40" height="55" rx="3" fill="#fff" opacity="0.9"/>
        <rect x="88" y="180" width="34" height="6" rx="2" fill="#333"/>
        <rect x="88" y="190" width="28" height="5" rx="2" fill="#333"/>
        <rect x="88" y="200" width="32" height="5" rx="2" fill="#333"/>
        <circle cx="210" cy="120" r="22" fill="#f0c8a0"/>
        <rect x="188" y="142" width="44" height="90" rx="5" fill="#1565c0"/>
        <rect x="140" y="160" width="50" height="30" rx="5" fill="#2a3a4a"/>
        <rect x="145" y="165" width="40" height="8" rx="3" fill="#4fc3f7" opacity="0.6"/>
        <text x="150" y="250" text-anchor="middle" font-size="12" fill="#4fc3f7" font-family="sans-serif">собеседование</text>
        """,
    },
    "woman_at_supermarket_with_cart": {
        "bg": "#001a00", "accent": "#81c784",
        "icon": """
        <rect x="50" y="80" width="200" height="160" rx="6" fill="#1b5e20" opacity="0.5"/>
        <rect x="90" y="160" width="120" height="70" rx="5" fill="#37474f"/>
        <rect x="90" y="160" width="120" height="15" rx="3" fill="#455a64"/>
        <circle cx="105" cy="240" r="12" fill="#666"/>
        <circle cx="195" cy="240" r="12" fill="#666"/>
        <rect x="85" y="155" width="15" height="90" rx="3" fill="#546e7a"/>
        <rect x="100" y="175" width="100" height="50" rx="3" fill="#4caf50" opacity="0.4"/>
        <circle cx="80" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="58" y="152" width="44" height="70" rx="5" fill="#880e4f"/>
        <text x="150" y="265" text-anchor="middle" font-size="12" fill="#81c784" font-family="sans-serif">супермаркет</text>
        """,
    },
    "woman_buying_ticket_at_machine": {
        "bg": "#001020", "accent": "#4fc3f7",
        "icon": """
        <rect x="100" y="80" width="110" height="160" rx="8" fill="#0d47a1"/>
        <rect x="110" y="90" width="90" height="100" rx="4" fill="#1565c0" opacity="0.7"/>
        <text x="155" y="150" text-anchor="middle" font-size="14" fill="#4fc3f7">🎫</text>
        <rect x="115" y="200" width="80" height="10" rx="5" fill="#1976d2"/>
        <rect x="115" y="215" width="80" height="10" rx="5" fill="#1976d2"/>
        <circle cx="80" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="58" y="152" width="44" height="80" rx="5" fill="#880e4f"/>
        <rect x="64" y="165" width="30" height="15" rx="3" fill="#4fc3f7" opacity="0.6"/>
        <text x="150" y="258" text-anchor="middle" font-size="12" fill="#4fc3f7" font-family="sans-serif">билет, автомат</text>
        """,
    },
    "woman_in_red_dress_at_boutique": {
        "bg": "#1a0010", "accent": "#f48fb1",
        "icon": """
        <circle cx="150" cy="100" r="25" fill="#f0c8a0"/>
        <path d="M 120 125 L 100 230 L 200 230 L 180 125 Z" fill="#c62828"/>
        <path d="M 120 125 L 150 145 L 180 125" fill="#e53935"/>
        <circle cx="80" cy="160" r="18" fill="#f0c8a0"/>
        <rect x="62" y="178" width="36" height="55" rx="5" fill="#37474f"/>
        <circle cx="220" cy="155" r="18" fill="#f0c8a0"/>
        <rect x="202" y="173" width="36" height="55" rx="5" fill="#4a148c"/>
        <rect x="60" y="80" width="60" height="80" rx="4" fill="#3a0040"/>
        <rect x="180" y="80" width="60" height="80" rx="4" fill="#3a0040"/>
        <text x="150" y="255" text-anchor="middle" font-size="12" fill="#f48fb1" font-family="sans-serif">бутик</text>
        """,
    },
    "woman_jogging_in_park_with_headphones": {
        "bg": "#001a00", "accent": "#aed581",
        "icon": """
        <rect x="40" y="200" width="220" height="40" rx="5" fill="#1b5e20"/>
        <circle cx="40" cy="170" r="25" fill="#2e7d32"/>
        <circle cx="100" cy="155" r="20" fill="#388e3c"/>
        <circle cx="170" cy="145" r="18" fill="#2e7d32"/>
        <circle cx="230" cy="155" r="20" fill="#388e3c"/>
        <circle cx="150" cy="120" r="25" fill="#f0c8a0"/>
        <path d="M 130 115 Q 150 110 170 115" fill="none" stroke="#333" stroke-width="5" stroke-linecap="round"/>
        <circle cx="128" cy="117" r="7" fill="#333"/>
        <circle cx="172" cy="117" r="7" fill="#333"/>
        <path d="M 120 145 L 100 190 L 130 200 L 150 160 L 170 200 L 200 190 L 180 145 Z" fill="#e91e63"/>
        <text x="150" y="258" text-anchor="middle" font-size="12" fill="#aed581" font-family="sans-serif">пробежка, парк</text>
        """,
    },
    "woman_paying_with_card_at_checkout": {
        "bg": "#001020", "accent": "#80deea",
        "icon": """
        <rect x="80" y="110" width="140" height="100" rx="8" fill="#0d47a1"/>
        <rect x="90" y="120" width="120" height="80" rx="4" fill="#1565c0" opacity="0.7"/>
        <text x="150" y="167" text-anchor="middle" font-size="12" fill="#80deea">💳 POS</text>
        <circle cx="70" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="48" y="152" width="44" height="80" rx="5" fill="#880e4f"/>
        <rect x="55" y="165" width="30" height="15" rx="3" fill="#80deea" opacity="0.8"/>
        <circle cx="230" cy="130" r="22" fill="#f0c8a0"/>
        <rect x="208" y="152" width="44" height="80" rx="5" fill="#1565c0"/>
        <text x="150" y="230" text-anchor="middle" font-size="12" fill="#80deea" font-family="sans-serif">оплата картой</text>
        """,
    },
    "woman_reading_news_on_phone_skeptical_expression": {
        "bg": "#0a0a1a", "accent": "#90a4ae",
        "icon": """
        <circle cx="150" cy="100" r="28" fill="#f0c8a0"/>
        <path d="M 130 108 Q 145 115 165 108" fill="none" stroke="#555" stroke-width="3" stroke-linecap="round"/>
        <line x1="135" y1="98" x2="142" y2="96" stroke="#555" stroke-width="2"/>
        <line x1="165" y1="98" x2="158" y2="96" stroke="#555" stroke-width="2"/>
        <rect x="115" y="128" width="70" height="120" rx="8" fill="#37474f"/>
        <rect x="120" y="135" width="60" height="105" rx="5" fill="#455a64"/>
        <rect x="125" y="145" width="50" height="8" rx="3" fill="#fff" opacity="0.6"/>
        <rect x="125" y="158" width="40" height="8" rx="3" fill="#fff" opacity="0.4"/>
        <rect x="125" y="171" width="45" height="8" rx="3" fill="#90a4ae" opacity="0.6"/>
        <text x="150" y="265" text-anchor="middle" font-size="11" fill="#90a4ae" font-family="sans-serif">новости, скептик</text>
        """,
    },
    "young_man_in_blue_shirt_looking_in_mirror": {
        "bg": "#001020", "accent": "#4fc3f7",
        "icon": """
        <rect x="160" y="80" width="90" height="160" rx="8" fill="#1a2a3a"/>
        <rect x="165" y="85" width="80" height="150" rx="5" fill="#0d47a1" opacity="0.4"/>
        <circle cx="200" cy="130" r="22" fill="#f0c8a0" opacity="0.7"/>
        <rect x="178" y="152" width="44" height="75" rx="5" fill="#1565c0" opacity="0.7"/>
        <circle cx="100" cy="110" r="25" fill="#f0c8a0"/>
        <rect x="75" y="135" width="50" height="100" rx="5" fill="#1565c0"/>
        <text x="150" y="258" text-anchor="middle" font-size="11" fill="#4fc3f7" font-family="sans-serif">зеркало, синяя рубашка</text>
        """,
    },
    "young_man_reading_apartment_rental_ad": {
        "bg": "#1a1000", "accent": "#ffb74d",
        "icon": """
        <circle cx="150" cy="100" r="25" fill="#f0c8a0"/>
        <rect x="125" y="125" width="50" height="100" rx="5" fill="#37474f"/>
        <rect x="70" y="145" width="100" height="130" rx="5" fill="#fff" opacity="0.95"/>
        <text x="120" y="170" text-anchor="middle" font-size="11" fill="#333" font-family="sans-serif">🏠 АРЕНДА</text>
        <rect x="78" y="178" width="84" height="6" rx="2" fill="#555"/>
        <rect x="78" y="189" width="70" height="6" rx="2" fill="#555"/>
        <rect x="78" y="200" width="80" height="6" rx="2" fill="#555"/>
        <rect x="78" y="211" width="60" height="6" rx="2" fill="#ffb74d"/>
        <rect x="78" y="222" width="75" height="6" rx="2" fill="#555"/>
        <text x="150" y="258" text-anchor="middle" font-size="12" fill="#ffb74d" font-family="sans-serif">объявление, аренда</text>
        """,
    },
    "young_person_addicted_to_phone_while_walking": {
        "bg": "#0a0a1a", "accent": "#ef9a9a",
        "icon": """
        <rect x="40" y="200" width="220" height="40" rx="5" fill="#2a2a3a"/>
        <circle cx="150" cy="110" r="25" fill="#f0c8a0"/>
        <path d="M 125 135 L 110 230 L 190 230 L 175 135 Z" fill="#37474f"/>
        <rect x="120" y="155" width="50" height="80" rx="8" fill="#1a1a2a"/>
        <rect x="124" y="160" width="42" height="70" rx="5" fill="#4fc3f7" opacity="0.5"/>
        <path d="M 145 165 Q 150 155 155 165" fill="none" stroke="#f0c8a0" stroke-width="4" stroke-linecap="round"/>
        <text x="150" y="258" text-anchor="middle" font-size="11" fill="#ef9a9a" font-family="sans-serif">зависимость от телефона</text>
        """,
    },
}

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SVG_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 280" width="300" height="280">
  <rect width="300" height="280" fill="{bg}"/>
  {icon}
</svg>'''

for name, data in IMAGES.items():
    svg = SVG_TEMPLATE.format(bg=data["bg"], icon=data["icon"])
    path = os.path.join(OUT_DIR, f"{name}.svg")
    with open(path, "w") as f:
        f.write(svg)
    print(f"Generated: {name}.svg")

print(f"\nDone! {len(IMAGES)} images generated.")
