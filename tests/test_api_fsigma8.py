from fastapi.testclient import TestClient
from api.main import app


def make_simple_fs8():
    # Simple synthetic dataset: monotonic z and a simple bump in fsigma8
    z = [0.0, 0.1, 0.2, 0.5, 1.0]
    fs8 = [0.45, 0.47, 0.5, 0.55, 0.52]
    return {"z": z, "fsigma8": fs8}


def test_fsigma8_tau_search_endpoint_and_save():
    client = TestClient(app)
    payload = {
        "data": make_simple_fs8(),
        "dt_myr": 10.0,
        "tau_candidates_myr": [10.0, 30.0, 100.0],
        "n_kernel": 64,
        "lam": 0.02,
    }

    r = client.post('/anamnesis/search_tau_fsigma8', json=payload)
    assert r.status_code == 200, r.text
    j = r.json()

    assert "best_tau_myr" in j
    assert "scores" in j and isinstance(j["scores"], list)
    # Baseline candidate present
    assert any(s.get('label') == 'tau0_baseline' for s in j['scores'])

    # Adapter diagnostic present
    assert 'adapter_diagnostic' in j
    diag = j['adapter_diagnostic']
    assert 't_lookback_gyr_min' in diag and 'dataset_hash' in diag
    assert 'dt_used_myr' in diag and 'dt_used_s' in diag

    # Ensure the scores have tau_myr equal to input candidates (and baseline tau_myr==0)
    input_candidates = payload['tau_candidates_myr']
    candidate_set = set(input_candidates)
    found_candidates = set()
    baseline_found = False
    for s in j['scores']:
        if s.get('label') == 'tau0_baseline':
            assert s.get('tau_myr') == 0.0
            baseline_found = True
        else:
            # numeric approximate match
            if 'tau_myr' in s:
                for c in input_candidates:
                    if abs(s['tau_myr'] - c) < 1e-6:
                        found_candidates.add(c)

    assert baseline_found
    assert found_candidates == candidate_set

    # Ensure run saved in library with same run_id and contains adapter_diagnostic
    run_id = j.get('run_id')
    assert run_id
    r2 = client.get(f'/runs/{run_id}')
    assert r2.status_code == 200
    run = r2.json()
    assert run['response']['adapter_diagnostic']['dataset_hash'] == diag['dataset_hash']


def test_baseline_win_and_best_nonbaseline_reported():
    client = TestClient(app)
    payload = {
        "data": {"z": [0.0, 0.5, 1.0], "fsigma8": [0.5, 0.5, 0.5]},
        "dt_myr": 10.0,
        "tau_candidates_myr": [10.0, 50.0],
        "n_kernel": 32,
        "lam": 0.01,
    }

    r = client.post('/anamnesis/search_tau_fsigma8', json=payload)
    assert r.status_code == 200, r.text
    j = r.json()

    assert any(s.get('label') == 'tau0_baseline' for s in j['scores'])

    # Baseline should be selected when tied for best objective
    assert j.get('best_tau_myr') == 0.0

    # Best nonbaseline candidate should still be reported
    assert j.get('best_nonbaseline_tau_myr') == 10.0

    # Comparison winner may be baseline or tie when objectives match
    if j.get('comparison'):
        winner = j['comparison']['delta']['winner']
        assert winner in ("baseline", "tie")


def test_baseline_win_and_best_nonbaseline_reported_verbose():
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    payload = {
        "data": {"z": [0.0, 0.5, 1.0], "fsigma8": [0.5, 0.5, 0.5]},
        "dt_myr": 10.0,
        "tau_candidates_myr": [10.0, 50.0],
        "n_kernel": 32,
        "lam": 0.01,
    }
    r = client.post('/anamnesis/search_tau_fsigma8', json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    print('best_tau_myr:', j.get('best_tau_myr'))
    print('best_nonbaseline_tau_myr:', j.get('best_nonbaseline_tau_myr'))
    print('ris_summary:', j.get('ris_summary'))
    print('comparison:', j.get('comparison'))
    print('scores:')
    for s in j['scores'][:3]:
        print(s)
    # Find and print baseline row
    baseline = next((s for s in j['scores'] if s.get('label') == 'tau0_baseline'), None)
    print('baseline row:', baseline)


def test_preprocessing_preserves_original_scale_for_baseline():
    client = TestClient(app)
    z = [0.0, 0.1, 0.2, 0.5]
    fs8 = [0.45, 0.47, 0.50, 0.52]
    payload = {
        "data": {"z": z, "fsigma8": fs8},
        "dt_myr": 10.0,
        "tau_candidates_myr": [10.0, 30.0],
        "n_kernel": 32,
        "lam": 0.02,
        "demean": True,
        "standardize": True,
    }

    r = client.post('/anamnesis/search_tau_fsigma8', json=payload)
    assert r.status_code == 200, r.text
    j = r.json()

    # Find baseline entry and compare y_hat_original to original resampled observed values
    baseline = next((s for s in j['scores'] if s.get('label') == 'tau0_baseline'), None)
    assert baseline is not None
    y_hat_original = baseline.get('y_hat_original')
    assert y_hat_original is not None

    # Recreate resampled original observed y used by adapter
    from core.data_adapter import lookback_time_gyr, resample_uniform
    t_gyr, _ = lookback_time_gyr(z)
    dt_gyr = float(payload['dt_myr']) / 1000.0
    _, fs8_uniform = resample_uniform(t_gyr, fs8, dt_gyr)

    assert len(y_hat_original) == len(fs8_uniform)
    for a, b in zip(y_hat_original, fs8_uniform):
        # Baseline should exactly reconstruct resampled original observed signal (allow tiny numerical tolerance)
        assert abs(float(a) - float(b)) < 1e-6


def test_fsigma8_schema_snapshot():
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    payload = {
        "data": {"z": [0.0, 0.2, 0.5], "fsigma8": [0.5, 0.6, 0.7]},
        "dt_myr": 10.0,
        "tau_candidates_myr": [10.0, 30.0],
        "n_kernel": 16,
        "lam": 0.01,
    }
    r = client.post('/anamnesis/search_tau_fsigma8', json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    expected_keys = {"best_tau_myr", "best_index", "best", "best_nonbaseline_tau_myr", "scores", "ris_summary", "comparison", "adapter_diagnostic", "run_id"}
    missing = expected_keys - set(j.keys())
    if missing:
        print(f"Schema snapshot failure: response.keys()={list(j.keys())}")
        print(f"ris_summary={j.get('ris_summary')}")
        raise AssertionError(f"Missing keys: {missing}")
