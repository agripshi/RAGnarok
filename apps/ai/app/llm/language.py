CLARIFICATION = {
    "sq": "Për cilën zyrë po pyet: Shqipëri apo Serbi?",
    "it": "Per quale ufficio stai chiedendo: Albania o Serbia?",
    "sr": "Za koju kancelariju pitate: Albanija ili Srbija?",
    "en": "Which office are you asking about: Albania or Serbia?",
}

NOT_FOUND = {
    "sq": "Nuk e gjeta këtë informacion në dokumentet HR të disponueshme. Ju lutem kontaktoni HR.",
    "it": "Non ho trovato questa informazione nei documenti HR disponibili. Contatta HR.",
    "sr": "Nisam pronašao ovu informaciju u dostupnim HR dokumentima. Kontaktirajte HR.",
    "en": "I could not find this information in the HR documents available to me. Please contact HR.",
}

ACCESS_DENIED = "Access denied."


def detect_language(text: str, hint: str | None = None) -> str:
    try:
        from langdetect import detect

        code = detect(text)
        if code in ("sq", "it", "sr", "en"):
            return code
        if code in ("hr", "bs", "mk"):
            return "sr"
    except Exception:
        pass
    return hint or "en"
