import pytest
from app.services.ai_service import AIService
from app.models.catalog import Product

def test_semantic_match_scoring():
    service = AIService()
    p1 = Product(
        productid="K9-BD-01",
        category="DOGS",
        name="Bulldog",
        descn="Friendly family dog, excellent companion for children and calm apartment living."
    )
    p2 = Product(
        productid="RP-SN-01",
        category="REPTILES",
        name="Rattlesnake",
        descn="Venomous pit viper requiring specialized handling and secure terrarium."
    )

    query = "friendly calm companion for kids"
    score_p1 = service.score_match(query, p1)
    score_p2 = service.score_match(query, p2)

    assert score_p1 > score_p2, "Friendly dog should rank higher than venomous rattlesnake for friendly companion query"

def test_advisor_recommendations():
    service = AIService()

    # Recommendations for FISH
    rec_fish = service.get_recommendations(["FISH"])
    assert any("aquarium" in item.get("name", "").lower() or "filter" in item.get("name", "").lower() or "conditioner" in item.get("name", "").lower() for item in rec_fish.get("recommended_accessories", []))
    assert len(rec_fish.get("care_advice", [])) > 0

    # Recommendations for multiple categories
    rec_multi = service.get_recommendations(["FISH", "CATS"])
    assert len(rec_multi.get("categories_analyzed", [])) == 2
    assert len(rec_multi.get("care_advice", [])) >= 2
