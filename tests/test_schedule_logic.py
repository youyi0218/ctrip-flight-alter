from __future__ import annotations

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import flight_monitor


TZ = ZoneInfo("Asia/Shanghai")


class ScheduleLogicTests(unittest.TestCase):
    def test_capture_only_triggers_inside_lead_window(self) -> None:
        schedule_times = ["09:00"]
        state = {"sent_slots": []}

        before_window = datetime(2026, 3, 31, 8, 49, tzinfo=TZ)
        self.assertEqual(
            flight_monitor.get_due_capture_slots(before_window, schedule_times, state, set(), 10 * 60),
            [],
        )

        in_window = datetime(2026, 3, 31, 8, 50, tzinfo=TZ)
        due = flight_monitor.get_due_capture_slots(in_window, schedule_times, state, set(), 10 * 60)
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].slot_key, "2026-03-31 09:00")

        at_push_time = datetime(2026, 3, 31, 9, 0, tzinfo=TZ)
        self.assertEqual(
            flight_monitor.get_due_capture_slots(at_push_time, schedule_times, state, set(), 10 * 60),
            [],
        )

    def test_capture_uses_next_day_slot_when_window_crosses_midnight(self) -> None:
        now = datetime(2026, 3, 31, 23, 58, tzinfo=TZ)
        due = flight_monitor.get_due_capture_slots(now, ["00:05"], {"sent_slots": []}, set(), 10 * 60)

        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].slot_key, "2026-04-01 00:05")
        self.assertEqual(
            flight_monitor.seconds_until_next_capture(now, ["00:05"], {"sent_slots": []}, set(), 10 * 60),
            1,
        )

    def test_push_due_supports_previous_day_grace_window(self) -> None:
        now = datetime(2026, 4, 1, 0, 3, tzinfo=TZ)
        due = flight_monitor.get_due_slots(now, ["23:59"], {"sent_slots": []}, 5 * 60)

        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].slot_key, "2026-03-31 23:59")

    def test_captured_or_sent_slots_are_skipped(self) -> None:
        now = datetime(2026, 3, 31, 8, 55, tzinfo=TZ)
        slot_key = "2026-03-31 09:00"
        self.assertEqual(
            flight_monitor.get_due_capture_slots(now, ["09:00"], {"sent_slots": [slot_key]}, set(), 10 * 60),
            [],
        )
        self.assertEqual(
            flight_monitor.get_due_capture_slots(now, ["09:00"], {"sent_slots": []}, {slot_key}, 10 * 60),
            [],
        )


if __name__ == "__main__":
    unittest.main()
