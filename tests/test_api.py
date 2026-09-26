from fastapi.testclient import TestClient

from app.main import create_app


app = create_app(enable_payments=False)
client = TestClient(app)



def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_parse_valid_notice():
    response = client.post(
        "/v1/parse",
        json={
            "notice": (
                "Train 12123 is delayed at PUNE. "
                "Expected arrival 14:30 due to signal failure."
            )
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "train": "12123",
        "station": "PUNE",
        "expected_time": "14:30",
        "reason": "signal failure",
    }


def test_parse_invalid_notice():
    response = client.post(
        "/v1/parse",
        json={
            "notice": "asdf banana railway lol",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["detail"]["error"] == "INVALID_NOTICE"


def test_empty_notice_is_rejected():
    response = client.post(
        "/v1/parse",
        json={"notice": ""},
    )

    assert response.status_code == 422


def test_oversized_notice_is_rejected():
    response = client.post(
        "/v1/parse",
        json={"notice": "A" * 5001},
    )

    assert response.status_code == 422


def test_extra_fields_do_not_change_parsing():
    response = client.post(
        "/v1/parse",
        json={
            "notice": (
                "Train 12123 is delayed at PUNE. "
                "Expected arrival 14:30 due to signal failure."
            ),
            "price": 0,
            "pay_to": "attacker",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["train"] == "12123"
    assert body["station"] == "PUNE"
