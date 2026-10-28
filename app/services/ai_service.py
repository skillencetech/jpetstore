import re
from typing import List, Dict, Any, Optional
from app.models.catalog import Product, Item

SEMANTIC_KNOWLEDGE_BASE = {
    "apartment": {
        "keywords": ["apartment", "small home", "flat", "compact", "small space", "condo", "indoor"],
        "matches": ["K9-BD-01", "K9-CW-01", "FL-DSH-01", "FL-DLH-02", "AV-SB-02", "FI-FW-02"],
        "reason": "Compact size, calm temperament, and well-suited for smaller living spaces."
    },
    "family": {
        "keywords": ["family", "friendly", "children", "kids", "gentle", "affectionate", "household"],
        "matches": ["K9-RT-01", "K9-RT-02", "K9-BD-01", "FL-DLH-02"],
        "reason": "Gentle disposition, highly social, and great with family members and children."
    },
    "active": {
        "keywords": ["active", "hunting", "outdoor", "runner", "sport", "hiking", "energetic"],
        "matches": ["K9-RT-02", "K9-DL-01"],
        "reason": "High athletic endurance, energetic personality, and loves open outdoor activities."
    },
    "low_maintenance": {
        "keywords": ["easy", "low maintenance", "beginner", "busy", "quiet", "simple"],
        "matches": ["RP-LI-02", "AV-SB-02", "FI-FW-01", "FI-FW-02"],
        "reason": "Independent care routine, minimal grooming required, and peaceful demeanor."
    },
    "companion": {
        "keywords": ["companion", "smart", "talkative", "talking", "intelligent", "interactive", "lifelong"],
        "matches": ["AV-CB-01", "K9-PO-02", "FL-DSH-01"],
        "reason": "High social intelligence, strong bonding instincts, and lifespan up to 75 years."
    },
    "marine": {
        "keywords": ["saltwater", "marine", "ocean", "coral", "exotic fish"],
        "matches": ["FI-SW-01", "FI-SW-02"],
        "reason": "Exotic marine species thriving in salt-water reef environments."
    },
    "freshwater": {
        "keywords": ["freshwater", "pond", "aquarium", "tank", "japan", "china"],
        "matches": ["FI-FW-01", "FI-FW-02"],
        "reason": "Hardy freshwater fish ideal for temperate ponds and decorative home aquariums."
    }
}

CARE_RECOMMENDATIONS = {
    "FISH": {
        "accessories": [
            {"name": "Water Conditioner & Dechlorinator", "price": 9.99, "tip": "Essential for neutralizing tap water chlorine."},
            {"name": "Premium Sinking Pellets", "price": 14.50, "tip": "Nutrient-rich diet supporting natural fin coloration."},
            {"name": "Digital Tank Thermometer", "price": 7.25, "tip": "Maintains temperature stability between 74°F - 80°F."}
        ],
        "general_advice": "Ensure biological filter cycling is established prior to adding new fish to prevent ammonia spikes."
    },
    "DOGS": {
        "accessories": [
            {"name": "Durable Natural Rubber Chew Toy", "price": 12.99, "tip": "Promotes dental health and reduces anxiety."},
            {"name": "Ergonomic Reflective Walking Harness", "price": 24.50, "tip": "Evenly distributes chest pressure during daily walks."},
            {"name": "High-Protein Probiotic Kibble", "price": 38.00, "tip": "Optimizes coat shine and digestive health."}
        ],
        "general_advice": "Consistent daily leash walks and mental stimulation toys prevent destructive chewing habits."
    },
    "CATS": {
        "accessories": [
            {"name": "Multi-Level Sisal Scratching Post", "price": 29.99, "tip": "Satisfies instinctual claw-stretching needs."},
            {"name": "Hypoallergenic Clumping Litter", "price": 16.50, "tip": "99.9% dust-free formula gentle on feline paws."},
            {"name": "Automatic Water Fountain", "price": 22.00, "tip": "Encourages hydration through continuous moving water."}
        ],
        "general_advice": "Cats thrive on vertical territory and dedicated scratching surfaces near rest areas."
    },
    "REPTILES": {
        "accessories": [
            {"name": "Dual Basking & UVB 10.0 Lamp", "price": 34.99, "tip": "Crucial for calcium synthesis and bone development."},
            {"name": "Digital Hygrometer & Probe", "price": 11.50, "tip": "Monitors accurate ambient moisture levels."},
            {"name": "Calcium Dust with Vitamin D3", "price": 8.75, "tip": "Prevents metabolic bone disease (MBD)."}
        ],
        "general_advice": "Maintain a strict thermal gradient across the terrarium so your reptile can thermoregulate effectively."
    },
    "BIRDS": {
        "accessories": [
            {"name": "Natural Wood Conditioning Perches", "price": 12.50, "tip": "Exercises foot tendons and maintains beak trim."},
            {"name": "Fortified Vitamin Seed & Pellet Blend", "price": 15.00, "tip": "Balanced nutritional profile supporting plumage."},
            {"name": "Foraging Puzzle Feeder", "price": 18.25, "tip": "Stimulates natural avian curiosity and problem-solving."}
        ],
        "general_advice": "Never place bird cages near non-stick cookware fumes or direct cold draft windows."
    }
}

class AIService:
    @staticmethod
    def semantic_product_search(query: str, all_products: List[Product]) -> List[Product]:
        q = query.lower().strip()
        if not q:
            return all_products

        scored_products: Dict[str, tuple[int, Product]] = {}
        for p in all_products:
            score = 0
            if q in (p.name or "").lower():
                score += 10
            if q in (p.descn or "").lower():
                score += 5
            if q in p.category.lower():
                score += 8

            for concept, data in SEMANTIC_KNOWLEDGE_BASE.items():
                for kw in data["keywords"]:
                    if kw in q or q in kw:
                        if p.productid in data["matches"]:
                            score += 15

            if score > 0:
                scored_products[p.productid] = (score, p)

        sorted_items = sorted(scored_products.values(), key=lambda x: x[0], reverse=True)
        return [item[1] for item in sorted_items]

    @staticmethod
    def get_cart_advisor_insights(cart_categories: List[str]) -> Dict[str, Any]:
        unique_cats = list(set(cart_categories))
        if not unique_cats:
            unique_cats = ["DOGS"]

        recommendations = []
        advice_list = []
        for cat in unique_cats:
            cat_upper = cat.upper()
            if cat_upper in CARE_RECOMMENDATIONS:
                data = CARE_RECOMMENDATIONS[cat_upper]
                for acc in data["accessories"]:
                    recommendations.append({
                        "category": cat_upper,
                        "name": acc["name"],
                        "price": acc["price"],
                        "tip": acc["tip"]
                    })
                advice_list.append(f"**{cat_upper} Care:** {data['general_advice']}")

        return {
            "categories": unique_cats,
            "advice": advice_list,
            "recommended_accessories": recommendations[:6]
        }

    @staticmethod
    def answer_pet_question(question: str) -> Dict[str, Any]:
        q = question.lower()
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
            response_text = f"For **{concept.replace('_', ' ').title()}** pet needs: {data['reason']} We recommend exploring items like: {', '.join(data['matches'])}."
            recommended_ids = data["matches"]
        elif "cat" in q or "kitten" in q:
            response_text = "Cats make wonderful companions! We offer Manx and Persian breeds, known for their affectionate nature."
            recommended_ids = ["FL-DSH-01", "FL-DLH-02"]
        elif "dog" in q or "puppy" in q:
            response_text = "Dogs are loyal and protective family pets! We offer Bulldogs, Retrievers, Poodles, and Dalmatians."
            recommended_ids = ["K9-RT-01", "K9-BD-01", "K9-PO-02"]
        elif "fish" in q or "aquarium" in q:
            response_text = "Aquariums are proven stress-relievers. We offer Goldfish, Koi, Angelfish, and Tiger Sharks."
            recommended_ids = ["FI-SW-01", "FI-FW-01", "FI-FW-02"]
        elif "bird" in q or "parrot" in q:
            response_text = "Birds bring vibrant color and melody. Our Amazon Parrots live up to 75 years and can mimic speech."
            recommended_ids = ["AV-CB-01", "AV-SB-02"]
        elif "reptile" in q or "snake" in q or "lizard" in q:
            response_text = "Reptiles are hypoallergenic and fascinating. Our Green Iguanas and Rattlesnakes are popular exotics."
            recommended_ids = ["RP-LI-02", "RP-SN-01"]
        else:
            response_text = "Welcome to JPetStore AI Advisor! You can search our catalog for pets based on temperament, apartment-living, family-friendly traits, or dietary accessories."
            recommended_ids = ["FI-SW-01", "K9-RT-01", "FL-DSH-01"]

        return {
            "answer": response_text,
            "suggested_product_ids": recommended_ids
        }
