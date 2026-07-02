from unittest.mock import Mock, patch

from services.ai_analyzer import AIAnalyzer


def test_analyze_performance_degradation_uses_groq_payload():
    analyzer = AIAnalyzer("test-key", model="llama-3.3-70b-versatile")

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Análise de teste"}}]
    }

    commits = [
        {
            "sha": "abc123",
            "message": "Initial commit",
            "complexity": 2.5,
            "lines_added": 10,
            "lines_removed": 0,
            "files_changed": 1,
            "author": "dev",
        }
    ]

    with patch("services.ai_analyzer.requests.post", return_value=mock_response) as post_mock:
        result = analyzer.analyze_performance_degradation(commits, {"name": "demo", "url": "https://example.com"})

    assert result["analysis"] == "Análise de teste"
    assert result["degradation_points"] == []
    assert post_mock.called

    _, kwargs = post_mock.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"]["model"] == "llama-3.3-70b-versatile"
    assert kwargs["json"]["messages"][0]["role"] == "user"


def test_select_top_commits_for_ai_prioritizes_recent_commits():
    analyzer = AIAnalyzer("test-key")

    commits = [
        {"sha": f"commit{i}", "complexity": 1.0 + i, "files_changed": 1, "lines_added": 10, "lines_removed": 5}
        for i in range(10)
    ]

    selected = analyzer._select_top_commits_for_ai(commits, top_n=5)

    assert len(selected) == 5
    assert selected[0]["sha"] == "commit9"
