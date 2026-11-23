"""第5回発展課題: Vector+Tree検索の章境界・重複・件数制約テスト。"""
from unittest.mock import patch

from app.retrieval import search_hybrid


def _page(pid, number, section="A", document="lec03-main"):
    return {
        "page_id": pid, "document_id": document, "lecture": 3,
        "document_title": "第3回", "section": section,
        "page": number, "title": pid, "content": pid,
    }


def test_hybrid_adds_neighbors_only_in_same_section():
    pages = [
        _page("p1", 1),
        _page("p2", 2),
        _page("p3", 3),
        _page("p4", 4, "B"),
        _page("other", 3, "A", "lec02-main"),
    ]
    seeds = [{**pages[1], "distance": 0.1}]
    with patch("app.retrieval.search", return_value=seeds), patch(
        "app.retrieval.load_pages", return_value=pages
    ):
        result = search_hybrid("test")
    assert [p["page_id"] for p in result["seeds"]] == ["p2"]
    assert [p["page_id"] for p in result["expanded"]] == ["p1", "p3"]
    assert [p["reason"] for p in result["expanded"]] == [
        "same_section_previous", "same_section_next"
    ]


def test_hybrid_deduplicates_and_honors_budget():
    pages = [_page(f"p{i}", i) for i in range(1, 5)]
    seeds = [{**pages[1], "distance": 0.1}, {**pages[2], "distance": 0.2}]
    with patch("app.retrieval.search", return_value=seeds), patch(
        "app.retrieval.load_pages", return_value=pages
    ):
        result = search_hybrid("test", max_results=3)
    ids = [p["page_id"] for p in result["seeds"] + result["expanded"]]
    assert len(ids) == len(set(ids)) == 3
    assert ids == ["p2", "p3", "p1"]
