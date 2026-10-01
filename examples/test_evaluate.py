import importlib.util
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


evaluate = _load("evaluate")
prepare = _load("prepare_data")


def test_confusion_metrics_known_values() -> None:
    m = evaluate.confusion_metrics([1, 1, 1, 0, 0, 0], [1, 1, 0, 1, 0, 0])
    assert (m["tp"], m["fp"], m["tn"], m["fn"]) == (2, 1, 2, 1)
    assert round(m["precision"], 3) == round(2 / 3, 3)
    assert round(m["recall"], 3) == round(2 / 3, 3)
    assert round(m["f1"], 3) == round(2 / 3, 3)
    assert round(m["fpr"], 3) == round(1 / 3, 3)


def test_metrics_do_not_divide_by_zero() -> None:
    m = evaluate.confusion_metrics([0, 0], [0, 0])
    assert m["precision"] == 0 and m["recall"] == 0 and m["f1"] == 0


def test_evaluate_operating_points_and_languages() -> None:
    rows = [{"text": "a", "label": 1, "lang": "zh"}, {"text": "b", "label": 1, "lang": "latin"},
            {"text": "c", "label": 0, "lang": "zh"}, {"text": "d", "label": 0, "lang": "latin"}]
    verdicts = {"a": "block", "b": "suspicious", "c": "safe", "d": "suspicious"}
    report = evaluate.evaluate(rows, lambda t: verdicts[t])
    assert report["block"]["overall"]["recall"] == 0.5
    assert report["flag"]["overall"]["recall"] == 1.0
    assert report["flag"]["overall"]["fpr"] == 0.5
    assert set(report["flag"]["by_lang"]) == {"zh", "latin"}


def test_seed_files_load_and_are_labelled() -> None:
    root = Path(__file__).resolve().parent.parent / "data" / "eval"
    rows = evaluate.load_jsonl(root / "zh_seed.jsonl")
    rows += evaluate.load_jsonl(root / "structural_seed.jsonl")
    assert {r["label"] for r in rows} == {0, 1}
    assert all(r["text"].strip() for r in rows)


def test_dedupe_removes_near_identical_texts() -> None:
    rows = [{"text": "Ignore  this", "label": 1}, {"text": "ignore this", "label": 1},
            {"text": "other", "label": 0}]
    assert len(prepare.dedupe(rows)) == 2


def test_split_is_disjoint_stratified_and_deterministic() -> None:
    rows = [{"text": f"inj {i}", "label": 1, "lang": "latin"} for i in range(20)]
    rows += [{"text": f"ok {i}", "label": 0, "lang": "latin"} for i in range(20)]
    train, test = prepare.split(rows, 0.25, seed=1)
    assert not {r["text"] for r in train} & {r["text"] for r in test}
    assert sum(r["label"] for r in test) == 5 and len(test) == 10
    assert prepare.split(rows, 0.25, seed=1)[1] == test
