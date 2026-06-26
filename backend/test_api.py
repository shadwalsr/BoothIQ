import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path so python can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

client = TestClient(app)

def test_get_constituencies():
    print("Testing GET /api/constituencies ...")
    response = client.get("/api/constituencies")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Expected list of constituencies"
    assert len(data) == 243, f"Expected 243 constituencies, found {len(data)}"
    # Check first record keys
    first = data[0]
    for key in ['id', 'name', 'district', 'cluster_id']:
        assert key in first, f"Missing key '{key}' in constituencies list"
    print("  GET /api/constituencies passed!")

def test_get_constituency_dossier():
    ac_no = 1
    print(f"Testing GET /api/constituency/{ac_no} ...")
    response = client.get(f"/api/constituency/{ac_no}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data['id'] == ac_no, f"Expected id {ac_no}, got {data['id']}"
    assert 'name' in data
    assert 'district' in data
    assert 'state' in data
    assert 'electoral_history' in data
    assert 'demographics' in data
    assert 'scheme_exposure' in data
    assert 'nfhs_indicators' in data
    assert 'discourse_topics' in data
    assert 'cluster_assignment' in data
    assert 'messaging_recommendation' in data
    assert 'metadata' in data
    
    # Check RLS/crosstab integration fields
    assert data['cluster_assignment']['cluster_id'] is not None
    assert data['messaging_recommendation']['theme_inclusive'] is not None
    assert data['metadata']['electoral'] == "ECI Bihar Assembly Election Results (2020, 2025)"
    print("  GET /api/constituency/{id} passed!")

def test_get_cluster():
    cluster_id = 2
    print(f"Testing GET /api/cluster/{cluster_id} ...")
    response = client.get(f"/api/cluster/{cluster_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data['cluster_id'] == cluster_id
    assert 'persona_name' in data
    assert 'description' in data
    assert 'validation' in data
    assert 'members' in data
    assert len(data['members']) > 0, "Expected at least one member in cluster"
    print("  GET /api/cluster/{id} passed!")

def test_compare_constituencies():
    ids = "1,33,100"
    print(f"Testing GET /api/compare?ids={ids} ...")
    response = client.get(f"/api/compare?ids={ids}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3, f"Expected 3 dossiers, got {len(data)}"
    assert data[0]['id'] == 1
    assert data[1]['id'] == 33
    assert data[2]['id'] == 100
    print("  GET /api/compare passed!")

def test_export_briefing():
    ac_no = 1
    print(f"Testing GET /api/constituency/{ac_no}/export ...")
    response = client.get(f"/api/constituency/{ac_no}/export")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers['content-type'].startswith('application/pdf'), f"Expected application/pdf content type, got {response.headers['content-type']}"
    assert response.content.startswith(b'%PDF'), "Expected response content to start with PDF magic bytes %PDF"
    print("  GET /api/constituency/{id}/export passed!")

def main():
    print("Running Backend API Automated Test Suite...")
    try:
        test_get_constituencies()
        test_get_constituency_dossier()
        test_get_cluster()
        test_compare_constituencies()
        test_export_briefing()
        print("\nALL API TESTS PASSED SUCCESSFULLY!")
    except AssertionError as e:
        print("\nTEST SUITE FAILED!")
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    main()
