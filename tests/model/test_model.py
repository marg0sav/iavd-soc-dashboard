from pathlib import Path
from soc_dashboard.model.catboost_model import CatBoostModel

def test_model_loading():
    model = CatBoostModel(Path("ml_models/verdict"))
    assert model.feature_names
    assert 0 < model.threshold < 1