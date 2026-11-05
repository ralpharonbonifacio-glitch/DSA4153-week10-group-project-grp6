import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import main as main_module  # noqa: E402
from src import pipeline  # noqa: E402
from src.configuration import load_config  # noqa: E402

DATA = os.path.join(ROOT, "data")
COLUMNS = ["country", "continent", "year", "lifeExp", "pop", "gdpPercap"]
FINAL_FILES = ["canonical.csv", "asia_selected_year.csv", "validation.csv"]


class PipelineTest(unittest.TestCase):
    """Helpers: a temp folder holding a copy of the manifest, configs, and readers."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.input_dir = os.path.join(self.tmp, "data")
        os.makedirs(self.input_dir)
        shutil.copy(os.path.join(DATA, "manifest.json"), self.input_dir)
        self.out = os.path.join(self.tmp, "output")

    # ---- fixtures
    def clean_rows(self) -> pd.DataFrame:
        """1,704 clean canonical rows as text (conflicting_key.csv minus the conflict)."""
        df = pd.read_csv(os.path.join(DATA, "conflicting_key.csv"),
                         dtype=str, keep_default_na=False)
        return df.drop_duplicates(["country", "year"]).reset_index(drop=True)

    def save(self, df: pd.DataFrame, name: str = "fixture.csv") -> str:
        """Save a fixture CSV in the temp input folder and return its file name."""
        df.to_csv(os.path.join(self.input_dir, name), index=False)
        return name

    def copy_case(self, name: str) -> str:
        """Copy a supplied case file into the temp input folder."""
        shutil.copy(os.path.join(DATA, name), self.input_dir)
        return name

    # ---- configs
    def config_for(self, filename: str, fmt: str = "csv", out: str = None) -> dict:
        """Config for one UTF-8, comma-separated, canonical-name file."""
        return {
            "input_directory": self.input_dir,
            "output_directory": out or self.out,
            "reporting_year": 2007,
            "supported_formats": ["csv", "xlsx", "json", "parquet"],
            "check_controls": False,
            "inputs": [{"file": filename, "format": fmt, "encoding": "utf-8",
                        "separator": ",", "mapping": {c: c for c in COLUMNS}}],
        }

    def real_config(self, year: int = 2007) -> dict:
        """Config for the four real inputs, taken from the project's config.json."""
        with open(os.path.join(ROOT, "config.json"), encoding="utf-8") as file:
            config = json.load(file)
        config["input_directory"] = DATA
        config["output_directory"] = self.out
        config["reporting_year"] = year
        return config

    # ---- readers and assertions
    def read_report(self, name: str, out: str = None) -> pd.DataFrame:
        """Read a report CSV (comma, UTF-8) as text."""
        return pd.read_csv(os.path.join(out or self.out, name),
                           dtype=str, keep_default_na=False)

    def read_canonical(self, out: str = None) -> pd.DataFrame:
        """Read canonical.csv in the dialect the exporter writes."""
        return pd.read_csv(os.path.join(out or self.out, "canonical.csv"),
                           **pipeline.CSV_EXPORT_SETTINGS)

    def assert_failed(self, code: int) -> None:
        """Nonzero exit, failure report saved, no final files, staging removed."""
        self.assertNotEqual(code, 0)
        self.assertTrue(os.path.isfile(os.path.join(self.out, "failed_validation_report.csv")))
        for name in FINAL_FILES:
            self.assertFalse(os.path.exists(os.path.join(self.out, name)), name)
        self.assertFalse(os.path.exists(self.out + "_staging"))


class TestTwelveCategories(PipelineTest):
    def test_01_normal_four_format_recovery(self) -> None:
        self.assertEqual(pipeline.run_pipeline(self.real_config()), 0)
        quarantine = self.read_report("quarantine.csv")
        self.assertEqual(len(quarantine), 24)
        self.assertEqual(quarantine["source_file"].value_counts().tolist(), [6, 6, 6, 6])
        self.assertEqual(len(self.read_report("duplicate_log.csv")), 8)
        self.assertEqual(len(self.read_canonical()), 1704)
        self.assertEqual(len(self.read_report("asia_selected_year.csv")), 33)
        self.assertTrue((self.read_report("validation.csv")["pass"] == "True").all())

    def test_02_missing_file(self) -> None:
        self.assert_failed(pipeline.run_pipeline(self.config_for("does_not_exist.csv")))

    def test_03_existing_unsupported_format(self) -> None:
        name = self.copy_case("unsupported.txt")
        self.assert_failed(pipeline.run_pipeline(self.config_for(name, fmt="txt")))
        report = self.read_report("failed_validation_report.csv")
        self.assertIn("unsupported", report["actual"].iloc[-1])

    def test_04_missing_column(self) -> None:
        name = self.copy_case("missing_column.csv")
        self.assert_failed(pipeline.run_pipeline(self.config_for(name)))
        report = self.read_report("failed_validation_report.csv")
        self.assertIn("pop", report["actual"].iloc[-1])

    def test_05_missing_key_column(self) -> None:
        name = self.save(self.clean_rows().drop(columns=["year"]))
        self.assert_failed(pipeline.run_pipeline(self.config_for(name)))

    def test_06_unparseable_number(self) -> None:
        df = self.clean_rows()
        df.loc[0, "lifeExp"] = "abc"
        self.assertEqual(pipeline.run_pipeline(self.config_for(self.save(df))), 0)
        quarantine = self.read_report("quarantine.csv")
        self.assertEqual(len(quarantine), 1)
        self.assertEqual(quarantine.loc[0, "source_record"], "1")
        self.assertIn("lifeExp", quarantine.loc[0, "reason"])
        self.assertEqual(len(self.read_canonical()), 1703)

    def test_07_fractional_year_and_population(self) -> None:
        df = self.clean_rows()
        df.loc[1, "year"] = "1997.5"
        df.loc[2, "pop"] = "100.5"
        self.assertEqual(pipeline.run_pipeline(self.config_for(self.save(df))), 0)
        quarantine = self.read_report("quarantine.csv")
        self.assertEqual(set(quarantine["source_record"]), {"2", "3"})
        self.assertTrue(quarantine["reason"].str.contains("whole number").all())

    def test_08_non_finite_and_out_of_range(self) -> None:
        df = self.clean_rows()
        df.loc[0, "lifeExp"] = "nan"
        df.loc[1, "lifeExp"] = "inf"
        df.loc[2, "lifeExp"] = "150"
        df.loc[3, "gdpPercap"] = "-5"
        df.loc[4, "year"] = "1800"
        self.assertEqual(pipeline.run_pipeline(self.config_for(self.save(df))), 0)
        self.assertEqual(len(self.read_report("quarantine.csv")), 5)
        self.assertEqual(len(self.read_canonical()), 1699)

    def test_09_exact_duplicates(self) -> None:
        df = self.clean_rows()
        df = pd.concat([df, df.iloc[[10]]], ignore_index=True)
        self.assertEqual(pipeline.run_pipeline(self.config_for(self.save(df))), 0)
        duplicates = self.read_report("duplicate_log.csv")
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates.loc[0, "source_record"], "1705")
        self.assertEqual(len(self.read_canonical()), 1704)

    def test_10_conflicting_keys_stop_processing(self) -> None:
        name = self.copy_case("conflicting_key.csv")
        self.assert_failed(pipeline.run_pipeline(self.config_for(name)))
        report = self.read_report("failed_validation_report.csv")
        self.assertIn("conflicting", report["actual"].iloc[-1])

    def test_11_reordered_records(self) -> None:
        df = self.clean_rows()
        shuffled = df.sample(frac=1, random_state=0).reset_index(drop=True)
        out_a, out_b = os.path.join(self.tmp, "a"), os.path.join(self.tmp, "b")
        self.assertEqual(pipeline.run_pipeline(
            self.config_for(self.save(df, "x.csv"), out=out_a)), 0)
        self.assertEqual(pipeline.run_pipeline(
            self.config_for(self.save(shuffled, "y.csv"), out=out_b)), 0)
        with open(os.path.join(out_a, "canonical.csv"), "rb") as a, \
                open(os.path.join(out_b, "canonical.csv"), "rb") as b:
            self.assertEqual(a.read(), b.read())

    def run_with_corrupted_export(self, fmt: str) -> int:
        """Run the pipeline while one export is altered right after it is written."""
        if fmt == "json":
            target, real = "export_to_json", pipeline.export_to_json

            def corrupt(canonical, path):
                real(canonical, path)
                with open(path, encoding="utf-8") as file:
                    records = json.load(file)
                records[0]["lifeExp"] += 1.0
                with open(path, "w", encoding="utf-8") as file:
                    json.dump(records, file)
        else:
            target, real = "export_to_csv", pipeline.export_to_csv

            def corrupt(canonical, path):
                real(canonical, path)
                table = pd.read_csv(path, **pipeline.CSV_EXPORT_SETTINGS)
                table.loc[0, "lifeExp"] += 1.0
                table.to_csv(path, index=False, **pipeline.CSV_EXPORT_SETTINGS)

        config = self.config_for(self.save(self.clean_rows()))
        with mock.patch.object(pipeline, target, corrupt):
            return pipeline.run_pipeline(config)

    def assert_round_trip_failed(self, fmt: str) -> None:
        """The failure report must name the failed round-trip check for this format."""
        report = self.read_report("failed_validation_report.csv")
        failed = report[(report["pass"] == "False") & (report["check"] != "run_error")]
        self.assertTrue(failed["check"].str.contains(f"round trip {fmt}").any())

    def test_12_corrupted_json_export_fails_comparison(self) -> None:
        self.assert_failed(self.run_with_corrupted_export("json"))
        self.assert_round_trip_failed("json")

    def test_12b_corrupted_csv_export_fails_comparison(self) -> None:
        self.assert_failed(self.run_with_corrupted_export("csv"))
        self.assert_round_trip_failed("csv")


class TestIntegration(PipelineTest):
    def test_reporting_year_1997_needs_no_code_change(self) -> None:
        self.assertEqual(pipeline.run_pipeline(self.real_config(year=1997)), 0)
        self.assertEqual(set(self.read_report("asia_selected_year.csv")["year"]), {"1997"})

    def test_failed_run_keeps_earlier_outputs(self) -> None:
        self.assertEqual(
            pipeline.run_pipeline(self.config_for(self.save(self.clean_rows()))), 0)
        with open(os.path.join(self.out, "canonical.csv"), "rb") as file:
            before = file.read()
        name = self.copy_case("conflicting_key.csv")
        self.assertNotEqual(pipeline.run_pipeline(self.config_for(name)), 0)
        with open(os.path.join(self.out, "canonical.csv"), "rb") as file:
            self.assertEqual(file.read(), before)

    def test_matrix_selection_comes_from_config(self) -> None:
        config = self.config_for(self.save(self.clean_rows()))
        config["analysis"] = {"matrix_countries": ["Philippines", "Japan"],
                              "matrix_years": [1982, 1992, 2002]}
        self.assertEqual(pipeline.run_pipeline(config), 0)
        index = self.read_report("population_index.csv")
        self.assertEqual(list(index["country"]), ["Philippines", "Japan"])
        self.assertEqual(list(index.columns), ["country", "1982", "1992", "2002"])

    def test_main_returns_2_for_missing_config(self) -> None:
        with mock.patch.object(sys, "argv", ["main.py", "--config", "nope.json"]):
            self.assertEqual(main_module.main(), 2)

    def test_main_returns_2_when_config_has_no_inputs(self) -> None:
        path = os.path.join(self.tmp, "no_inputs.json")
        with open(path, "w", encoding="utf-8") as file:
            json.dump({"reporting_year": 2007}, file)
        with mock.patch.object(sys, "argv", ["main.py", "--config", path]):
            self.assertEqual(main_module.main(), 2)

    def test_year_not_in_manifest_stops_the_run(self) -> None:
        config = self.config_for(self.save(self.clean_rows()))
        config["reporting_year"] = 2010
        self.assert_failed(pipeline.run_pipeline(config))

    def test_bad_baseline_year_stops_the_run(self) -> None:
        config = self.config_for(self.save(self.clean_rows()))
        config["analysis"] = {"matrix_years": [1987, 1992], "baseline_year": 1982}
        self.assert_failed(pipeline.run_pipeline(config))
        report = self.read_report("failed_validation_report.csv")
        self.assertIn("baseline", report["actual"].iloc[-1].lower())

    def test_config_validation_rejects_bad_settings(self) -> None:
        spec = {"file": "a.csv", "mapping": {"a": "country"}}
        bad_configs = [{"reporting_year": "2007", "inputs": [spec]},
                       {"reporting_year": True, "inputs": [spec]},
                       {"supported_formats": [], "inputs": [spec]},
                       {"inputs": [{"file": "a.csv"}]},
                       {"inputs": [{"file": "a.csv", "mapping": {}}]},
                       {"inputs": []}]
        for position, bad in enumerate(bad_configs):
            path = os.path.join(self.tmp, f"bad_{position}.json")
            with open(path, "w", encoding="utf-8") as file:
                json.dump(bad, file)
            with self.subTest(config=bad), self.assertRaises(ValueError):
                load_config(path)

    def test_config_defaults(self) -> None:
        path = os.path.join(self.tmp, "ok.json")
        with open(path, "w", encoding="utf-8") as file:
            json.dump({"inputs": [{"file": "a.csv", "mapping": {"a": "country"}}]}, file)
        config = load_config(path)
        self.assertEqual(config["reporting_year"], 2007)
        self.assertEqual(config["output_directory"], "output")

    def test_main_without_config_value_exits_2(self) -> None:
        with mock.patch.object(sys, "argv", ["main.py", "--config"]), \
                mock.patch.object(sys, "stderr", mock.MagicMock()):
            with self.assertRaises(SystemExit) as caught:
                main_module.main()
        self.assertEqual(caught.exception.code, 2)

    def test_check_tolerance(self) -> None:
        run = pipeline.PipelineRun({})
        self.assertTrue(run.check("within", 0.0, 5e-9, 1e-8))
        self.assertFalse(run.check("outside", 0.0, 2e-8, 1e-8))
        self.assertTrue(run.check("exact", 3, 3))
        self.assertFalse(run.passed())


def run_and_record(path: str = os.path.join(ROOT, "test_results.txt")) -> int:
    """Run every test in tests/ and write the outcomes to test_results.txt."""
    suite = unittest.defaultTestLoader.discover(os.path.join(ROOT, "tests"))
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(f"Test run: {pd.Timestamp.now().isoformat(timespec='seconds')}\n\n")
        result = unittest.TextTestRunner(stream=handle, verbosity=2).run(suite)
        handle.write(f"\nSummary: ran={result.testsRun} failures={len(result.failures)} "
                     f"errors={len(result.errors)} skipped={len(result.skipped)}\n")
    print(f"Results written to {path}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_and_record())