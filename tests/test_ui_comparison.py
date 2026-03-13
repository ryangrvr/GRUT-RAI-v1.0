from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_search_tau_includes_winner_and_baseline():
    payload = {
        'y_obs': [0,0,0,1,0,0,0,0,0,0],
        'dt_s': 1.0,
        'tau_candidates_s': [1.0, 2.0, 5.0, 10.0],
        'n_kernel': 16,
        'lam': 0.05,
        'max_iter': 500,
        'tol': 1e-6,
        'nonnegative': True,
        'emd_warn': 2.0,
        'emd_fail': 5.0,
        'residual_warn': 0.10,
        'residual_fail': 0.25
    }

    r = client.post('/anamnesis/search_tau', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert 'comparison' in data, 'comparison block should be present'
    cmp = data['comparison']
    assert 'baseline' in cmp and cmp['baseline']['name'] == 'tau0_baseline'
    assert 'delta' in cmp and 'winner' in cmp['delta']
    assert cmp['delta']['winner'] in ('best', 'baseline', 'tie')


def test_run_compare_winner_present():
    # construct a minimal RunRequest that triggers compare
    body = {
        'engine': {'z_grid': [0.0, 0.5], 'eps_t_myr': 0.1},
        'observer': {'profile': 'participant', 'v_obs_m_s': 1.0, 'ui_window': {'ui_actions': 1, 'window_s': 1, 'avg_param_delta': 0.1}, 'sensor': {'mode': 'off'}, 'info_cfg': {'eta': 1.0}, 'enable_observer_modulation': False},
        'compare': {'enabled': True, 'models': ['lcdm'], 'metric': 'l2'}
    }

    r = client.post('/runs', json=body)
    assert r.status_code == 200
    data = r.json()
    assert 'comparison' in data
    cmp = data['comparison']
    assert 'delta' in cmp and 'winner' in cmp['delta']
    assert cmp['delta']['winner'] in ('best', 'baseline', 'tie')
