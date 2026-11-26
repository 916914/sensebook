import cv2
import numpy as np

from sensebook.camera import synthetic_page
from sensebook.pages import (Block, PageCache, PageContent, hamming, phash, reading_units, split_sentences)


def test_phash_stable_under_noise_and_resize_but_differs_between_pages():
    p = synthetic_page(1)
    noisy = np.clip(p.astype(int) + np.random.default_rng(0).normal(0, 6, p.shape), 0, 255).astype(np.uint8)
    small = cv2.resize(p, (320, 360))
    assert hamming(phash(p), phash(noisy)) <= 6
    assert hamming(phash(p), phash(small)) <= 6
    assert hamming(phash(p), phash(synthetic_page(7))) > 10


def test_cache_roundtrip_and_hit_avoids_second_cloud_call(db):
    cache = PageCache(db)
    p = synthetic_page(3)
    h = phash(p)
    assert cache.lookup(h) is None
    pc = PageContent([Block("heading", "Title"), Block("paragraph", "Hello world. Second one.")], "en", 0.9, "12")
    pid = cache.store(h, pc)
    hit = cache.lookup(phash(cv2.resize(p, (500, 450))))
    assert hit and hit.page_id == pid and hit.from_cache and hit.blocks[1].text.startswith("Hello")
    assert db.one("SELECT seen_count c FROM pages")["c"] == 2
    assert cache.lookup(phash(synthetic_page(9))) is None


def test_sentence_split_english_and_bangla():
    assert split_sentences("One. Two! Three?") == ["One.", "Two!", "Three?"]
    bn = "গাছ খাবার তৈরি করে। আলো লাগে।"
    assert len(split_sentences(bn)) == 2
    pc = PageContent([Block("heading", "H. x"), Block("paragraph", "A. B.")])
    assert [u[1] for u in reading_units(pc)] == ["H. x", "A.", "B."]
