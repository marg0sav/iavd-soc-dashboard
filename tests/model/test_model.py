from pathlib import Path
from soc_dashboard.model.catboost_model import SocCatBoostModel

def test_model_loading():
    model = SocCatBoostModel(Path("ml_models/verdict"))
    assert model.feature_names
    assert 0 < model.threshold < 1