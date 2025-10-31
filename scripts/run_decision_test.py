from fastapi.testclient import TestClient
from api.main import app
import json


def main():
    c = TestClient(app)
    r = c.post('/api/v1/solana/decision', json={'features': {'price': 100, 'trend': 0.02}})
    print('STATUS', r.status_code)
    print('BODY', json.dumps(r.json(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
