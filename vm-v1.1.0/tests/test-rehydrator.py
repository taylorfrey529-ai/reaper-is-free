#!/usr/bin/env python3
import hashlib
import importlib.util
import io
import json
import pathlib
import tarfile
import tempfile
import zipfile

BASE = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = BASE / "bin" / "rehydrate-offline-v1.1.0.py"

spec = importlib.util.spec_from_file_location("vm_v110_rehydrate", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def sha_bytes(blob):
    return hashlib.sha256(blob).hexdigest()


def make_metal_fixture(base, carried_derivative=None):
    staging = base / "staging"
    payload = base / "payload"
    scratch = base / "scratch"
    staging.mkdir()
    payload.mkdir()
    scratch.mkdir()

    stock = b"<control>\nset_cc48=64\n#include articulation.sfz\n"
    derived = stock.replace(b"set_cc48=64", b"set_cc48=0", 1)
    sample = b"FAKEWAVDATA"

    tree = base / "tree" / "Metal-GTX"
    programs = tree / "Programs"
    samples = tree / "Samples"
    programs.mkdir(parents=True)
    samples.mkdir(parents=True)
    (programs / "03-METAL-GTX XTracking.sfz").write_bytes(stock)
    (samples / "sample.wav").write_bytes(sample)
    if carried_derivative is not None:
        (programs / "03-METAL-GTX XTracking Clean DI.sfz").write_bytes(carried_derivative)

    archive = base / "metal-gtx.tar.gz"
    with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT) as tf:
        tf.add(tree, arcname="Metal-GTX")

    archive_blob = archive.read_bytes()
    logical_sha = sha_bytes(archive_blob)
    part_name = "metal-gtx.tar.gz.drive.part.000"
    part_zip = staging / "metal-part.zip"
    with zipfile.ZipFile(part_zip, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr(part_name, archive_blob)

    manifest_zip = staging / "metal-manifest.zip"
    sums = f"{logical_sha}  {part_name}\n"
    recovery = f"Authority archive SHA-256: {logical_sha}\n"
    with zipfile.ZipFile(manifest_zip, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("SHA256SUMS", sums)
        zf.writestr("RECOVERY.txt", recovery)

    final_sfz_bytes = len(stock) + len(derived)
    pm = {
        "samples": {"files": 1, "bytes": len(sample)},
        "sfz": {
            "files": 2,
            "bytes": final_sfz_bytes,
            "upstream_files": 1,
            "upstream_bytes": len(stock),
            "approved_clean_di_derivative_files": 1,
            "approved_clean_di_derivative_bytes": len(derived),
        },
        "stock_xtracking": {"sha256": sha_bytes(stock)},
        "clean_di_xtracking": {"sha256": sha_bytes(derived)},
    }
    asset = {
        "logical_archive_sha256": logical_sha,
        "drive_manifest": {"name": manifest_zip.name},
        "drive_objects": [{"name": part_zip.name}],
    }
    durable = {"assets": {"metal_gtx": asset}}
    permanence = {"assets": {"metal_gtx": pm}}
    return staging, payload, scratch, durable, permanence, stock, derived


def test_clean_di_reconstruction():
    with tempfile.TemporaryDirectory(prefix="vm-v110-test-metal-") as td:
        base = pathlib.Path(td)
        staging, payload, scratch, durable, permanence, stock, derived = make_metal_fixture(base)
        mod.stage_metal(staging, durable, permanence, payload, scratch)
        target = payload / "instruments" / "Metal-GTX" / "Programs"
        got_stock = target / "03-METAL-GTX XTracking.sfz"
        got_clean = target / "03-METAL-GTX XTracking Clean DI.sfz"
        assert got_stock.read_bytes() == stock
        assert got_clean.read_bytes() == derived
        assert mod.sha256(got_clean) == permanence["assets"]["metal_gtx"]["clean_di_xtracking"]["sha256"]
        print("PASS: missing Clean DI derivative reconstructed deterministically")


def test_wrong_carried_derivative_rejected():
    with tempfile.TemporaryDirectory(prefix="vm-v110-test-metal-bad-") as td:
        base = pathlib.Path(td)
        stock = b"<control>\nset_cc48=64\n#include articulation.sfz\n"
        derived = stock.replace(b"set_cc48=64", b"set_cc48=0", 1)
        bad = bytearray(derived)
        bad[-2] = ord("X") if bad[-2] != ord("X") else ord("Y")
        bad = bytes(bad)
        assert len(bad) == len(derived)
        staging, payload, scratch, durable, permanence, _, _ = make_metal_fixture(base, carried_derivative=bad)
        try:
            mod.stage_metal(staging, durable, permanence, payload, scratch)
        except RuntimeError as exc:
            assert "carried Clean DI derivative hash mismatch" in str(exc)
            print("PASS: mismatched carried Clean DI derivative rejected")
        else:
            raise AssertionError("mismatched carried Clean DI derivative was not rejected")


def test_tar_path_traversal_rejected():
    with tempfile.TemporaryDirectory(prefix="vm-v110-test-tar-") as td:
        base = pathlib.Path(td)
        tar_path = base / "evil.tar"
        payload = b"blocked"
        with tarfile.open(tar_path, "w") as tf:
            info = tarfile.TarInfo("../escape")
            info.size = len(payload)
            tf.addfile(info, io.BytesIO(payload))
        dest = base / "dest"
        dest.mkdir()
        with tarfile.open(tar_path, "r:") as tf:
            try:
                mod.safe_tar_extract(tf, dest)
            except RuntimeError as exc:
                assert "unsafe TAR path" in str(exc)
                print("PASS: TAR path traversal rejected")
            else:
                raise AssertionError("unsafe TAR path was not rejected")


def test_zip_path_traversal_rejected():
    with tempfile.TemporaryDirectory(prefix="vm-v110-test-zip-") as td:
        base = pathlib.Path(td)
        zip_path = base / "evil.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("../escape", b"blocked")
        dest = base / "dest"
        dest.mkdir()
        with zipfile.ZipFile(zip_path) as zf:
            try:
                mod.safe_zip_extract(zf, dest)
            except RuntimeError as exc:
                assert "unsafe ZIP path" in str(exc)
                print("PASS: ZIP path traversal rejected")
            else:
                raise AssertionError("unsafe ZIP path was not rejected")


def main():
    test_clean_di_reconstruction()
    test_wrong_carried_derivative_rejected()
    test_tar_path_traversal_rejected()
    test_zip_path_traversal_rejected()
    print("VM v1.1.0 offline rehydrator unit tests: PASS")


if __name__ == "__main__":
    main()
