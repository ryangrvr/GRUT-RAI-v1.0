from fastapi.testclient import TestClient
from api.main import app


def test_synthetic_fsigma8_memory_positive():
    client = TestClient(app)

    # Generate synthetic memory-positive dataset
    r = client.post('/anamnesis/demo_fsigma8', json={})
    assert r.status_code == 200, r.text
    demo = r.json()

    dataset = demo.get('dataset')
    planted = float(demo.get('planted_tau_myr'))
    dt_myr = float(demo.get('dt_myr'))
    n_kernel = int(demo.get('n_kernel'))

    assert dataset and isinstance(dataset, dict)
    assert dataset.get('dataset_label') == 'fsigma8_synth_memory_positive'
    diag = demo.get('diagnostic', {})
    assert diag.get('synthetic') is True

    tau_grid = [10.0, 20.0, 30.0, 41.9, 50.0, 60.0]
    payload = {
        "data": dataset,
        "dt_myr": dt_myr,
        "tau_candidates_myr": tau_grid,
        "n_kernel": n_kernel,
        "prior": "smooth",
        "lam_smooth": 1e-3,
        "emd_warn": 0.5,
    }

    r2 = client.post('/anamnesis/search_tau_fsigma8', json=payload)
    assert r2.status_code == 200, r2.text
    result = r2.json()

    best_tau = result.get('best_tau_myr')
    best_nonbaseline = result.get('best_nonbaseline_tau_myr')
    comparison = result.get('comparison')

    assert best_tau is not None
    tol = max(0.5 * max(tau_grid), 0.5 * planted, 10.0)
    assert abs(float(best_tau) - planted) <= tol
    assert float(best_tau) > 0.0

    assert best_nonbaseline is not None
    assert comparison is not None
    assert comparison.get('delta', {}).get('winner') != 'baseline'

    # Ensure baseline candidate present and loses on objective
    baseline = next((s for s in result['scores'] if s.get('label') == 'tau0_baseline'), None)
    assert baseline is not None
    assert float(best_tau) != 0.0
