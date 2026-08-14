"""Integration coverage for completed scaffold endpoints."""

from pathlib import Path

from fastapi.testclient import TestClient


def test_progress_and_recap_require_auth(client: TestClient) -> None:
    assert client.get("/api/progress").status_code == 401
    assert client.get("/api/recap/weekly").status_code == 401


def test_progress_and_recap(client: TestClient, auth_headers: dict) -> None:
    assert client.get("/api/progress", headers=auth_headers).status_code == 200
    assert client.get("/api/recap/weekly", headers=auth_headers).status_code == 200


def test_create_and_list_private_group(client: TestClient, auth_headers: dict) -> None:
    created = client.post("/api/groups", json={"name": "Amigos"}, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["members"][0]["role"] == "owner"
    groups = client.get("/api/groups", headers=auth_headers)
    assert [group["name"] for group in groups.json()] == ["Amigos"]


def test_content_sources_and_pronunciation_evaluation(
    client: TestClient, auth_headers: dict, monkeypatch
) -> None:
    from backend.app.routers import capabilities

    sources = client.get("/api/content/sources", headers=auth_headers)
    assert [source["name"] for source in sources.json()] == ["Español", "Vitamina"]
    monkeypatch.setattr(
        capabilities,
        "transcribe_spanish",
        lambda _path, _phrase: "Este sábado voy a visitar Madrid",
    )
    response = client.post(
        "/api/pronunciation/evaluate",
        data={"phrase_id": "test-phrase", "phrase": "Este sábado voy a visitar Madrid"},
        files={"audio": ("voice.webm", b"audio")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["score"] == 100
    assert response.json()["transcription"] == "Este sábado voy a visitar Madrid"
    assert all(word["score"] == 100 for word in response.json()["word_scores"])


def test_spanish_example_audio(
    client: TestClient, auth_headers: dict, monkeypatch, tmp_path: Path
) -> None:
    from backend.app.routers import capabilities

    audio = tmp_path / "example.mp3"
    audio.write_bytes(b"ID3 example audio")
    monkeypatch.setattr(capabilities, "spanish_example_audio", lambda _phrase: audio)

    response = client.post(
        "/api/speech/example",
        json={"phrase": "Hola, vecinos"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"ID3 example audio"


def test_every_unit_has_its_own_conversation(
    client: TestClient, auth_headers: dict, monkeypatch
) -> None:
    from backend.app.routers import capabilities

    lessons = client.get("/api/lessons").json()
    setups = [
        client.get(
            "/api/conversation/setup",
            params={"lesson_id": lesson["id"]},
            headers=auth_headers,
        ).json()
        for lesson in lessons
    ]
    assert len(setups) == 30
    assert {setup["lesson_id"] for setup in setups} == {lesson["id"] for lesson in lessons}
    assert all(setup["title"] and setup["goal"] and setup["greeting"] for setup in setups)
    assert all(len(setup["vocabulary"]) == 4 for setup in setups)
    assert len({setup["scene"] for setup in setups}) == 30
    vitamina_a2 = [setup for setup in setups if setup["title"].startswith("Vitamina A2 · U")]
    assert vitamina_a2[0]["greeting"] != vitamina_a2[1]["greeting"]
    assert vitamina_a2[0]["prompts"] != vitamina_a2[1]["prompts"]

    monkeypatch.setattr(capabilities, "transcribe_spanish", lambda _path, _prompt: "Me gusta la mesa junto a la ventana")
    first = setups[0]
    response = client.post(
        "/api/conversation/respond",
        data={"turn": 0, "lesson_id": first["lesson_id"]},
        files={"audio": ("voice.webm", b"audio")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["reply"] == first["prompts"][0]
    assert response.json()["correction"]["has_error"] is False

    monkeypatch.setattr(capabilities, "transcribe_spanish", lambda _path, _prompt: "Vamos escuchar música")
    response = client.post(
        "/api/conversation/respond",
        data={"turn": 0, "lesson_id": first["lesson_id"]},
        files={"audio": ("voice.webm", b"audio")},
        headers=auth_headers,
    )
    correction = response.json()["correction"]
    assert correction["has_error"] is True
    assert correction["corrected"] == "Vamos a escuchar música"
    assert "infinitivo" in correction["explanation"]
