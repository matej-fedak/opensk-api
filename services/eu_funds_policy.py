"""Reviewed, positive ITMS21+ production policy; no I/O or upstream access."""

COLLECTION_URL = "https://api.itms21.sk/public/v1/projekt"
TERMS_URL = "https://data.gov.sk/set/3dd34ab69156cd6dcdd6454f81727c88"
SOURCE_NOTICE = "MIRRI SR / ITMS21+ OpenData API — transformed and privacy-minimized by OpenSK API"
LICENCE_NOTICE = "CC BY, as declared by the Slovak national open-data catalogue (version not separately identified)"
PRIVACY_POLICY = "REVIEWED_LEGAL_ENTITY_PROJECTS_ONLY"
PROJECT_CODE_PATTERN = r"[A-Z0-9]{10}"
NUTS_PATTERN = r"[A-Z]{2}[A-Z0-9]{0,3}"
REVIEWED_NUTS_LABELS = {
    "SK010": "Bratislavský kraj", "SK021": "Trnavský kraj", "SK022": "Trenčiansky kraj",
    "SK023": "Nitriansky kraj", "SK031": "Žilinský kraj", "SK032": "Banskobystrický kraj",
    "SK041": "Prešovský kraj", "SK042": "Košický kraj",
}

# Positive review: corporations, registered associations, municipalities,
# public-law legal persons and statutory nonprofit organizations. New forms
# never become safe through absence from a denylist. Exact source labels are
# pinned too, so a changed meaning requires review rather than silent reuse.
APPROVED_LEGAL_FORM_LABELS = {
    "100904": "GmbH", "100906": "Verein", "100909": "Gebietskörperschaft - Gemeinde",
    "100910": "Körperschaft öffentlichen Rechts",
    "1009111": "Verejná obchodná spoločnosť", "1009112": "Spoločnosť s ručením obmedzeným",
    "1009113": "Komanditná spoločnosť", "1009117": "Nadácia", "1009119": "Nezisková organizácia",
    "1009120": "Nezisková organizácia poskytujúca všeobecne prospešné služby",
    "1009121": "Akciová spoločnosť", "1009123": "Európska spoločnosť", "1009125": "Jednoduchá spoločnosť na akcie",
    "100913": "Juristische Person des öffentlichen Rechts", "100914": "Anstalt des öffentlichen Rechts",
    "1009205": "Družstvo", "1009301": "Štátny podnik", "1009321": "Rozpočtová organizácia",
    "1009331": "Príspevková organizácia", "1009333": "Verejná výskumná inštitúcia",
    "1009382": "Verejnoprávna inštitúcia", "1009701": "Združenie (zväz, spolok, spoločnosť, klub ai.)",
    "1009721": "Cirkevná organizácia", "1009741": "Stavovská organizácia - profesná komora",
    "1009751": "Záujmové združenie právnických osôb",
    "1009801": "Obec (obecný úrad), mesto (mestský úrad)", "1009803": "Samosprávny kraj (úrad samosprávneho kraja)",
    "1009804": "Európske zoskupenie územnej spolupráce", "1009921": "Medzinárodné organizácie a združenia",
    "1009CZ141": "Obecně prospěšná společnost", "1009CZ301": "Státní podnik",
    "1009CZ331": "Příspěvková organizace", "1009CZ361": "Veřejnoprávní instituce (ČT,ČRo,ČTK)",
    "1009CZ601": "Vysoká škola", "1009CZ641": "Školská právnická osoba",
    "1009CZ661": "Veřejná výzkumná instituce", "1009CZ706": "Spolek",
    "1009CZ771": "Svazek obcí", "1009CZ801": "Obec nebo městská část hlavního města Prahy",
    "1009CZ804": "Kraj",
}
APPROVED_LEGAL_FORMS = frozenset(APPROVED_LEGAL_FORM_LABELS)
# Deliberately not approved: broad/unclear categories and organizational
# branches without established independent legal personality in this review.
# CZ325 was in the research seed allowlist; production review removes it.
AMBIGUOUS_LEGAL_FORMS = frozenset({"1009381", "1009383", "1009CZ325", "1009CZ736"})
