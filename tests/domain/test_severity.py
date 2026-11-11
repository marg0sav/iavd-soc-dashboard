from soc_dashboard.domain.severity import SEVERITY_COLORS, UNSPECIFIED, Severity


def test_severity_colors_go_from_unspecified_to_critical():
    assert len(list(SEVERITY_COLORS)) == 6
    assert list(SEVERITY_COLORS) == [
        UNSPECIFIED,
        Severity.INFORMATIONAL.label,
        Severity.LOW.label,
        Severity.MEDIUM.label,
        Severity.HIGH.label,
        Severity.CRITICAL.label,
    ]
