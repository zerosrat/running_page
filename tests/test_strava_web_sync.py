import datetime
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "run_page"))
import strava_web_sync as sync


class WebSyncTests(unittest.TestCase):
    def test_resume_covers_outage(self):
        session = MagicMock()
        session.query.return_value.scalar.return_value = "2026-06-21 13:07:46+00:00"
        latest = datetime.datetime(2026, 6, 21, 13, 7, 46, tzinfo=datetime.UTC).timestamp()
        self.assertEqual(sync._sync_cutoff(session, None), latest - 7 * 86400)

    def test_empty_database_imports_history(self):
        session = MagicMock()
        session.query.return_value.scalar.return_value = None
        self.assertEqual(sync._sync_cutoff(session, None), 0)
        self.assertEqual(sync._sync_cutoff(session, 7, now=1000000), 395200)
        with self.assertRaises(ValueError):
            sync._sync_cutoff(session, 0)

    def test_last_partial_page_and_run_filter(self):
        run = {"id": 1, "sport_type": "Run", "start_date_local_raw": 2000000000}
        pages = [{"models": [run] * 20, "total": 21},
                 {"models": [run, {**run, "sport_type": "Swim"}], "total": 22},
                 {"models": [], "total": 22}]
        with patch.object(sync, "WebClient"), patch.object(sync, "init_db"), \
             patch.object(sync, "_sync_cutoff", return_value=0), \
             patch.object(sync, "_fetch_json", side_effect=pages), \
             patch.object(sync, "_sync_one") as one, \
             patch.object(sync, "_finalize") as finalize, patch.object(sync.time, "sleep"):
            sync.run_strava_web_sync("test", only_run=True)
        self.assertEqual(one.call_count, 21)
        self.assertEqual(finalize.call_args.args[1:], (21, True))

    def test_failed_streams_do_not_overwrite_existing_activity(self):
        with patch.object(sync, "_fetch_streams", side_effect=RuntimeError("HTTP error")), \
             patch.object(sync, "update_or_create_activity") as update:
            with self.assertRaises(RuntimeError):
                sync._sync_one(MagicMock(), MagicMock(), {"id": 123})
        update.assert_not_called()

    def test_activity_is_saved_in_real_database(self):
        session = sync.init_db(":memory:")
        raw = {"id": 123, "sport_type": "Run", "name": "Evening run",
               "distance_raw": 1000, "moving_time_raw": 300,
               "start_date_local_raw": 1770000000}
        with patch.object(sync, "_fetch_streams", return_value={}):
            sync._sync_one(MagicMock(), session, raw)
        saved = session.get(sync.Activity, 123)
        self.assertEqual(saved.name, "Evening run")
        self.assertEqual(saved.distance, 1000)
        self.assertEqual(saved.start_date_local, "2026-02-02 02:40:00")
        session.close()

    def test_local_wall_clock_does_not_shift_evening_to_next_day(self):
        ts = int(datetime.datetime(2026, 10, 16, 21, 28, 7,
                                   tzinfo=datetime.UTC).timestamp())
        activity = sync.WebActivity({"id": 1, "start_date_local_raw": ts})
        self.assertEqual(activity.start_date_local, "2026-10-16 21:28:07")
        self.assertEqual(activity.start_date, "2026-10-16 13:28:07+00:00")

    def test_adapter_units_dates_and_route(self):
        raw = {"id": "123", "sport_type": "Run", "distance_raw": 1000,
               "moving_time_raw": 300, "start_date_local_raw": 0}
        activity = sync.WebActivity(raw, {"latlng": [[38.5, -120.2], [40.7, -120.95]],
                                         "heartrate": [120, None, 140]})
        self.assertEqual(activity.distance, 1000)
        self.assertEqual(activity.moving_time, datetime.timedelta(seconds=300))
        self.assertEqual(activity.average_heartrate, 130)
        self.assertEqual(activity.start_date, "1969-12-31 16:00:00+00:00")
        self.assertEqual(sync._fmt_local_date(1770000000), "2026-02-02 02:40:00")
        self.assertEqual(activity.summary_polyline, "_p~iF~ps|U_ulLnnqC")


if __name__ == "__main__":
    unittest.main()
