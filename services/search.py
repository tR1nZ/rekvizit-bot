import numpy as np

from utils.vector import blob_to_vector


class SearchService:
    def __init__(self, database, embedding_service, similarity_threshold: float):
        self.database = database
        self.embedding_service = embedding_service
        self.similarity_threshold = similarity_threshold

    async def hybrid_search(self, query: str, top_k: int = 5):
        keyword_results = await self.database.keyword_search(query, limit=top_k)

        query_vec = self.embedding_service.encode_text(query)
        rows = await self.database.get_all_props_for_similarity()

        semantic_scored = []

        for row in rows:
            prop_id, name, description, box_number, photo_file_id, total_quantity, emb_blob = row
            try:
                item_vec = blob_to_vector(emb_blob)
            except Exception:
                continue

            score = float(np.dot(query_vec, item_vec))
            if score >= self.similarity_threshold:
                semantic_scored.append((
                    score,
                    (prop_id, name, description, box_number, photo_file_id, total_quantity)
                ))

        semantic_scored.sort(key=lambda x: x[0], reverse=True)
        semantic_results = [item for _, item in semantic_scored[:top_k]]

        seen_ids = set()
        merged = []

        for item in keyword_results + semantic_results:
            prop_id = item[0]
            if prop_id not in seen_ids:
                seen_ids.add(prop_id)
                merged.append(item)

        return merged[:top_k]

    async def similar_items(self, query: str, top_k: int = 5):
        query_vec = self.embedding_service.encode_text(query)
        rows = await self.database.get_all_props_for_similarity()

        scored = []

        for row in rows:
            prop_id, name, description, box_number, photo_file_id, total_quantity, emb_blob = row
            try:
                item_vec = blob_to_vector(emb_blob)
            except Exception:
                continue

            score = float(np.dot(query_vec, item_vec))
            scored.append((
                score,
                (prop_id, name, description, box_number, photo_file_id, total_quantity)
            ))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]