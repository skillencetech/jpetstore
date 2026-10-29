from typing import Any

from app.models.catalog import Product

# Grounded catalog dictionary matching sql/dataload.sql
CATALOG_PRODUCTS: dict[str, dict[str, Any]] = {
    "FI-SW-01": {
        "product_id": "FI-SW-01",
        "item_id": "EST-1",
        "name": "Angelfish",
        "category": "FISH",
        "price": 16.50,
        "description": "Saltwater reef fish from Australia with distinctive striped fins.",
    },
    "FI-SW-02": {
        "product_id": "FI-SW-02",
        "item_id": "EST-3",
        "name": "Tiger Shark",
        "category": "FISH",
        "price": 18.50,
        "description": "Saltwater predatory fish from Australia for experienced aquarists.",
    },
    "FI-FW-01": {
        "product_id": "FI-FW-01",
        "item_id": "EST-4",
        "name": "Aquarium Koi",
        "category": "FISH",
        "price": 18.50,
        "description": "Hardy freshwater ornamental fish from Japan, ideal for tranquil ponds and large aquariums.",
    },
    "FI-FW-02": {
        "product_id": "FI-FW-02",
        "item_id": "EST-20",
        "name": "Aquarium Goldfish",
        "category": "FISH",
        "price": 5.50,
        "description": "Peaceful freshwater aquarium favorite from China, perfect for all care levels.",
    },
    "K9-BD-01": {
        "product_id": "K9-BD-01",
        "item_id": "EST-6",
        "name": "Bulldog",
        "category": "DOGS",
        "price": 18.50,
        "description": "Calm, gentle companion dog from England, well-suited for families and apartments.",
    },
    "K9-PO-02": {
        "product_id": "K9-PO-02",
        "item_id": "EST-8",
        "name": "Poodle",
        "category": "DOGS",
        "price": 18.50,
        "description": "Hypoallergenic, highly intelligent companion dog from France.",
    },
    "K9-DL-01": {
        "product_id": "K9-DL-01",
        "item_id": "EST-9",
        "name": "Dalmation",
        "category": "DOGS",
        "price": 18.50,
        "description": "Energetic, active companion dog suited for outdoor runners and open spaces.",
    },
    "K9-RT-01": {
        "product_id": "K9-RT-01",
        "item_id": "EST-28",
        "name": "Golden Retriever",
        "price": 155.29,
        "description": "Affectionate, patient family dog renowned for loyalty with children.",
    },
    "K9-RT-02": {
        "product_id": "K9-RT-02",
        "item_id": "EST-22",
        "name": "Labrador Retriever",
        "category": "DOGS",
        "price": 135.50,
        "description": "Friendly, athletic retrieving and companion dog.",
    },
    "K9-CW-01": {
        "product_id": "K9-CW-01",
        "item_id": "EST-26",
        "name": "Chihuahua",
        "category": "DOGS",
        "price": 125.50,
        "description": "Compact, affectionate apartment companion with spirited personality.",
    },
    "RP-SN-01": {
        "product_id": "RP-SN-01",
        "item_id": "EST-11",
        "name": "Rattlesnake",
        "category": "REPTILES",
        "price": 18.50,
        "description": "Exotic terrarium reptile native to the American Southwest.",
    },
    "RP-LI-02": {
        "product_id": "RP-LI-02",
        "item_id": "EST-13",
        "name": "Green Iguana",
        "category": "REPTILES",
        "price": 18.50,
        "description": "Friendly vegetarian lizard companion suited for warm terrariums.",
    },
    "FL-DSH-01": {
        "product_id": "FL-DSH-01",
        "item_id": "EST-15",
        "name": "Manx Cat",
        "category": "CATS",
        "price": 23.50,
        "description": "Playful, affectionate companion cat renowned for natural mouse control.",
    },
    "FL-DLH-02": {
        "product_id": "FL-DLH-02",
        "item_id": "EST-16",
        "name": "Persian Cat",
        "category": "CATS",
        "price": 93.50,
        "description": "Gentle, regal indoor companion with a luxurious long coat.",
    },
    "AV-CB-01": {
        "product_id": "AV-CB-01",
        "item_id": "EST-18",
        "name": "Amazon Parrot",
        "category": "BIRDS",
        "price": 193.50,
        "description": "Intelligent, vocal companion bird capable of living up to 75 years.",
    },
    "AV-SB-02": {
        "product_id": "AV-SB-02",
        "item_id": "EST-19",
        "name": "Song Finch",
        "category": "BIRDS",
        "price": 15.50,
        "description": "Peaceful, melodic songbird companion with pleasant chirping.",
    },
}

SEMANTIC_KNOWLEDGE_BASE = {
    "apartment": {
        "keywords": ["apartment", "small home", "flat", "compact", "small space", "condo", "indoor"],
        "matches": ["K9-BD-01", "K9-CW-01", "FL-DSH-01", "FL-DLH-02", "AV-SB-02", "FI-FW-02"],
        "reason": "Compact size, calm temperament, and well-suited for smaller living spaces.",
    },
    "family": {
        "keywords": ["family", "friendly", "children", "kids", "gentle", "affectionate", "household"],
        "matches": ["K9-RT-01", "K9-RT-02", "K9-BD-01", "FL-DLH-02"],
        "reason": "Gentle disposition, highly social, and great with family members and children.",
    },
    "active": {
        "keywords": ["active", "hunting", "outdoor", "runner", "sport", "hiking", "energetic"],
        "matches": ["K9-RT-02", "K9-DL-01"],
        "reason": "High athletic endurance, energetic personality, and loves open outdoor activities.",
    },
    "low_maintenance": {
        "keywords": ["easy", "low maintenance", "beginner", "busy", "quiet", "simple"],
        "matches": ["RP-LI-02", "AV-SB-02", "FI-FW-01", "FI-FW-02"],
        "reason": "Independent care routine, minimal grooming required, and peaceful demeanor.",
    },
    "companion": {
        "keywords": ["companion", "smart", "talkative", "talking", "intelligent", "interactive", "lifelong"],
        "matches": ["AV-CB-01", "K9-PO-02", "FL-DSH-01"],
        "reason": "High social intelligence, strong bonding instincts, and lifelong companionship.",
    },
    "marine": {
        "keywords": ["saltwater", "marine", "ocean", "coral", "exotic fish"],
        "matches": ["FI-SW-01", "FI-SW-02"],
        "reason": "Exotic marine species thriving in salt-water reef environments.",
    },
    "freshwater": {
        "keywords": ["freshwater", "pond", "aquarium", "tank", "japan", "china"],
        "matches": ["FI-FW-01", "FI-FW-02"],
        "reason": "Hardy freshwater fish ideal for temperate ponds and decorative home aquariums.",
    },
}

CARE_ADVICE = {
    "FISH": "Ensure aquarium water is properly cycled, maintain temperature stability (74°F-80°F), and feed small portions twice daily.",
    "DOGS": "Establish daily walking routines, provide chew toys for dental stimulation, and keep up with regular vaccinations.",
    "CATS": "Provide vertical territory like cat trees and scratchers, clean litter boxes daily, and schedule regular playtime.",
    "REPTILES": "Maintain a strict thermal gradient across the terrarium and provide appropriate UVB lighting for healthy calcium synthesis.",
    "BIRDS": "Provide spacious cages away from cold drafts or kitchen fumes, with diverse perches and puzzle foraging toys.",
}

# Grounded catalog recommendations per category (all entities exist in JPetStore DB)
CATEGORY_CATALOG_COMPANIONS = {
    "FISH": [CATALOG_PRODUCTS["FI-FW-01"], CATALOG_PRODUCTS["FI-FW-02"], CATALOG_PRODUCTS["FI-SW-01"]],
    "DOGS": [CATALOG_PRODUCTS["K9-BD-01"], CATALOG_PRODUCTS["K9-PO-02"], CATALOG_PRODUCTS["K9-RT-01"]],
    "CATS": [CATALOG_PRODUCTS["FL-DSH-01"], CATALOG_PRODUCTS["FL-DLH-02"]],
    "REPTILES": [CATALOG_PRODUCTS["RP-LI-02"], CATALOG_PRODUCTS["RP-SN-01"]],
    "BIRDS": [CATALOG_PRODUCTS["AV-SB-02"], CATALOG_PRODUCTS["AV-CB-01"]],
}


class AIService:
    def score_match(self, query: str, product: Product) -> int:
        """Calculates semantic match score for automated regression testing and search ranking."""
        q = query.lower().strip()
        score = 0
        if q in (product.name or "").lower():
            score += 10
        if q in (product.descn or "").lower():
            score += 5
        if product.category and q in product.category.lower():
            score += 8

        for data in SEMANTIC_KNOWLEDGE_BASE.values():
            for kw in data["keywords"]:
                if kw in q:
                    if product.productid in data["matches"]:
                        score += 15
                    if kw in (product.descn or "").lower():
                        score += 10
        return score

    @staticmethod
    def semantic_product_search(query: str, all_products: list[Product]) -> list[Product]:
        q = query.lower().strip()
        if not q:
            return all_products

        service = AIService()
        scored_products: dict[str, tuple[int, Product]] = {}
        for p in all_products:
            score = service.score_match(q, p)
            if score > 0:
                scored_products[p.productid] = (score, p)

        sorted_items = sorted(scored_products.values(), key=lambda x: x[0], reverse=True)
        return [item[1] for item in sorted_items]

    @staticmethod
    def get_cart_advisor_insights(cart_categories: list[str]) -> dict[str, Any]:
        unique_cats = list(set(cart_categories))
        if not unique_cats:
            unique_cats = ["DOGS"]

        recommendations = []
        advice_list = []
        seen_pids = set()

        for cat in unique_cats:
            cat_upper = cat.upper()
            if cat_upper in CATEGORY_CATALOG_COMPANIONS:
                companions = CATEGORY_CATALOG_COMPANIONS[cat_upper]
                for comp in companions:
                    if comp["product_id"] not in seen_pids:
                        seen_pids.add(comp["product_id"])
                        recommendations.append(
                            {
                                "category": cat_upper,
                                "product_id": comp["product_id"],
                                "item_id": comp["item_id"],
                                "name": comp["name"],
                                "price": comp["price"],
                                "description": comp["description"],
                                "tip": comp["description"],
                            }
                        )
            if cat_upper in CARE_ADVICE:
                advice_list.append(f"**{cat_upper} Care:** {CARE_ADVICE[cat_upper]}")

        return {
            "categories": unique_cats,
            "categories_analyzed": unique_cats,
            "advice": advice_list,
            "care_advice": advice_list,
            "recommended_accessories": recommendations[:6],
        }

    def get_recommendations(self, categories: list[str]) -> dict[str, Any]:
        """Alias helper for test suite backwards compatibility."""
        return self.get_cart_advisor_insights(categories)

    @staticmethod
    def answer_pet_question(question: str | None) -> dict[str, Any]:
        q = (question or "").lower().strip()
        matched_concept = None
        for concept, data in SEMANTIC_KNOWLEDGE_BASE.items():
            for kw in data["keywords"]:
                if kw in q:
                    matched_concept = (concept, data)
                    break
            if matched_concept:
                break

        if matched_concept:
            concept, data = matched_concept
            matched_pids = data["matches"]
            response_text = (
                f"For **{concept.replace('_', ' ').title()}** pet seekers: {data['reason']} "
                f"Here are top-matched pets available in our store:"
            )
            recommended_ids = matched_pids
        elif any(
            g in q
            for g in ["hi", "hello", "hey", "good morning", "good evening", "howdy", "who are you", "what can you do"]
        ):
            response_text = "Hello! I am your JPetStore AI Shopping & Care Advisor. I can recommend pets tailored to your home and lifestyle, provide care advice, or help you add companion pets to your cart. Here are popular pets available today:"
            recommended_ids = ["K9-RT-01", "FL-DSH-01", "FI-FW-01"]
        elif any(w in q for w in ["ship", "deliver", "courier", "arrival", "fedex", "ups"]):
            response_text = "We ship live pets via express climate-controlled air transport across the USA. Flat-rate standard shipping is $10.00. Here are popular pets ready for priority delivery:"
            recommended_ids = ["FI-FW-02", "AV-SB-02", "K9-BD-01"]
        elif any(w in q for w in ["price", "cost", "cheap", "affordable", "expensive", "how much"]):
            response_text = "Our catalog features pets for all budgets, ranging from affordable freshwater fish ($5.50) to prized exotic parrots ($193.50). Explore popular pets across price ranges:"
            recommended_ids = ["FI-FW-02", "AV-SB-02", "K9-BD-01", "AV-CB-01"]
        elif any(w in q for w in ["food", "diet", "feed", "eat", "nutrition"]):
            response_text = "Dietary guidelines vary by species: our fish thrive on high-protein pellets, dogs and cats on balanced kibble, birds on fortified seeds, and iguanas on fresh greens. Here are popular pets with straightforward dietary needs:"
            recommended_ids = ["FI-FW-01", "K9-RT-01", "RP-LI-02"]
        elif "cat" in q or "kitten" in q:
            response_text = (
                "Cats make wonderful companions! We offer friendly Manx and luxurious Persian cats in our store:"
            )
            recommended_ids = ["FL-DSH-01", "FL-DLH-02"]
        elif "dog" in q or "puppy" in q:
            response_text = "Dogs are loyal and loving family companions! We offer Bulldogs, Retrievers, Poodles, Chihuahuas, and Dalmatians:"
            recommended_ids = ["K9-RT-01", "K9-BD-01", "K9-PO-02", "K9-CW-01"]
        elif "fish" in q or "aquarium" in q:
            response_text = "Aquariums bring natural tranquility to your home. We offer beautiful Goldfish, Koi, Angelfish, and Tiger Sharks:"
            recommended_ids = ["FI-SW-01", "FI-FW-01", "FI-FW-02"]
        elif "bird" in q or "parrot" in q:
            response_text = (
                "Birds bring vibrant song and intelligence. We offer cheerful Finches and talking Amazon Parrots:"
            )
            recommended_ids = ["AV-CB-01", "AV-SB-02"]
        elif "reptile" in q or "snake" in q or "lizard" in q:
            response_text = "Reptiles are hypoallergenic and fascinating terrarium companions. We offer Green Iguanas and Rattlesnakes:"
            recommended_ids = ["RP-LI-02", "RP-SN-01"]
        else:
            response_text = "I'd love to help you find the right pet! You can ask about living spaces (e.g. 'apartment living'), family pets, care routines, or click any of the categories above. Here are top recommended pets from our catalog:"
            recommended_ids = ["FI-SW-01", "K9-RT-01", "FL-DSH-01"]

        # Build grounded product list with real names, descriptions, prices, and SKUs
        recommended_pets = []
        for pid in recommended_ids:
            if pid in CATALOG_PRODUCTS:
                prod = CATALOG_PRODUCTS[pid]
                recommended_pets.append(
                    {
                        "product_id": prod["product_id"],
                        "item_id": prod["item_id"],
                        "name": prod["name"],
                        "category": prod["category"],
                        "price": float(prod["price"]),
                        "description": prod["description"],
                    }
                )

        return {"answer": response_text, "suggested_product_ids": recommended_ids, "recommended_pets": recommended_pets}
