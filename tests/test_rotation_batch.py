from tools.run_rotation_batch import run_rotation_batch


def test_rotation_batch_summary(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data1 = data_dir / "g1.csv"
    data2 = data_dir / "g2.csv"
    header = "r_kpc,v_obs,v_err,v_gas,v_star\n"
    data1.write_text(header + "1,100,5,60,80\n2,100,5,60,80\n")
    data2.write_text(header + "1,90,5,50,70\n2,90,5,50,70\n")

    outdir = tmp_path / "batch"
    summary = run_rotation_batch(
        [data1, data2],
        {"response_model": "identity", "r0_policy": "median_radius"},
        outdir,
    )
    assert summary["summary_sha256"]
