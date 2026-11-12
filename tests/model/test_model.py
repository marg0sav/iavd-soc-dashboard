from soc_dashboard.model.catboost_model import CatBoostModel

def test_model_loading():
    model = CatBoostModel()
    assert model.feature_names
    assert 0 < model.threshold < 1