from app.recommendation.pipeline import RecommendationPipeline


def test_pipeline_cold_start():
    pipeline = RecommendationPipeline()
    result = pipeline.recommend(user_idx=None, n=5, product_ids=list(range(10)))
    assert isinstance(result, list)


def test_pipeline_returns_list():
    pipeline = RecommendationPipeline()
    result = pipeline.recommend(user_idx=None, n=3, product_ids=[1, 2, 3])
    assert isinstance(result, list)
    assert len(result) <= 3
