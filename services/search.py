from rapidfuzz import fuzz


class SearchService:
    def __init__(self, database):
        self.database = database

        self.synonyms = {
            "фуражка": [
                "кепка",
                "головной убор",
                "форменная кепка",
                "шапка",
            ],
            "кепка": [
                "фуражка",
                "бейсболка",
                "головной убор",
            ],
            "шапка": [
                "головной убор",
                "фуражка",
                "кепка",
            ],
            "женское": [
                "женская",
                "женщина",
                "женский",
                "девушка",
            ],
            "мужское": [
                "мужская",
                "мужчина",
                "мужской",
                "парень",
            ],
            "одежда": [
                "вещи",
                "костюм",
                "наряд",
                "форма",
            ],
            "реквизит": [
                "предмет",
                "аксессуар",
                "бутафория",
            ],
        }

    def _normalize(self, text: str) -> str:
        return " ".join((text or "").lower().strip().split())

    def _expand_query(self, query: str) -> list[str]:
        query = self._normalize(query)
        expanded = [query]

        for key, values in self.synonyms.items():
            if key in query:
                expanded.extend(values)

        words = query.split()
        for word in words:
            if word in self.synonyms:
                expanded.extend(self.synonyms[word])

        # убираем дубли
        result = []
        seen = set()
        for item in expanded:
            item = self._normalize(item)
            if item and item not in seen:
                seen.add(item)
                result.append(item)

        return result

    def _score_item(self, query: str, expanded_queries: list[str], item_row) -> float:
        prop_id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type = item_row

        name_n = self._normalize(name)
        desc_n = self._normalize(description)
        gender_n = self._normalize(gender_group)
        item_type_n = self._normalize(item_type)

        combined = f"{name_n} {desc_n} {gender_n} {item_type_n}"

        score = 0.0

        # точные вхождения
        if query in name_n:
            score += 120
        if query in desc_n:
            score += 60
        if query == gender_n:
            score += 80
        if query == item_type_n:
            score += 80

        # отдельные бонусы за слова
        for q in expanded_queries:
            if q in name_n:
                score += 40
            if q in desc_n:
                score += 20
            if q == gender_n:
                score += 35
            if q == item_type_n:
                score += 35

        # fuzzy matching
        score += fuzz.partial_ratio(query, name_n) * 0.55
        score += fuzz.partial_ratio(query, desc_n) * 0.20
        score += fuzz.ratio(query, gender_n) * 0.35
        score += fuzz.ratio(query, item_type_n) * 0.35
        score += fuzz.token_set_ratio(query, combined) * 0.30

        # fuzzy по расширенным запросам
        for q in expanded_queries:
            score += fuzz.partial_ratio(q, name_n) * 0.18
            score += fuzz.partial_ratio(q, desc_n) * 0.08
            score += fuzz.token_set_ratio(q, combined) * 0.10

        return score

    async def hybrid_search(self, query: str, top_k: int = 10):
        query = self._normalize(query)
        if not query:
            return []

        items = await self.database.list_recent_props(limit=500)
        expanded_queries = self._expand_query(query)

        scored = []
        for item in items:
            score = self._score_item(query, expanded_queries, item)
            if score >= 35:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    async def similar_items(self, query: str, top_k: int = 10):
        return await self.hybrid_search(query, top_k=top_k)