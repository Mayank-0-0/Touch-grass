import unittest
from datetime import datetime, timedelta, date
from database import Base, engine, SessionLocal
import models
from schemas import (
    PreferenceUpdate, ChallengeGenerateRequest,
    ProofSubmitRequest
)
import main

class TestTouchGrassBackend(unittest.TestCase):
    def setUp(self):
        # Reset DB tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_health_and_root(self):
        r = main.root()
        self.assertEqual(r["app"], "Touch Grass")
        h = main.health()
        self.assertEqual(h["status"], "ok")

    def test_ai_status(self):
        status_info = main.get_ai_status()
        self.assertIn("online", status_info)
        self.assertIn("server_url", status_info)

    def test_preferences(self):
        prefs = main.get_preferences(db=self.db)
        self.assertIn("Walking", prefs["selected_interests"])

        update_data = PreferenceUpdate(
            selected_interests=["Drawing", "Gardening", "Music"],
            default_duration=60,
            default_difficulty="Hard"
        )
        updated = main.update_preferences(data=update_data, db=self.db)
        self.assertEqual(updated["default_duration"], 60)
        self.assertEqual(updated["default_difficulty"], "Hard")
        self.assertEqual(updated["selected_interests"], ["Drawing", "Gardening", "Music"])

    def test_challenge_generation_and_timer_persistence(self):
        req = ChallengeGenerateRequest(
            interest="Walking",
            duration_minutes=30,
            difficulty="Easy",
            surprise_me=False
        )
        ch = main.generate_challenge(req=req, db=self.db)
        self.assertEqual(ch["status"], "draft")
        self.assertEqual(ch["duration_minutes"], 30)
        self.assertTrue(len(ch["follow_up_questions"]) > 0)
        ch_id = ch["id"]

        # Start challenge
        started = main.start_challenge(challenge_id=ch_id, db=self.db)
        self.assertEqual(started["status"], "active")
        self.assertIsNotNone(started["started_at"])
        self.assertIsNotNone(started["target_end_at"])
        self.assertGreater(started["remaining_seconds"], 1700)

        # Query active challenge (simulating browser refresh)
        active = main.get_active_challenge(db=self.db)
        self.assertIsNotNone(active)
        self.assertEqual(active["id"], ch_id)
        self.assertEqual(active["status"], "active")
        self.assertGreater(active["remaining_seconds"], 0)

    def test_proof_submission_preserves_data_and_handles_ai_offline(self):
        # Generate & start
        req = ChallengeGenerateRequest(
            interest="Drawing",
            duration_minutes=30,
            difficulty="Easy"
        )
        ch = main.generate_challenge(req=req, db=self.db)
        ch_id = ch["id"]
        main.start_challenge(challenge_id=ch_id, db=self.db)

        # Submit proof while AI is offline -> should raise HTTPException(503)
        proof_req = ProofSubmitRequest(
            proof_answers={
                "What physical object did you choose to sketch and why?": "A vintage brass key from my desk drawer.",
                "How did you approach shading the shadow cast by the object?": "Cross-hatching with a soft graphite pencil."
            },
            proof_image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )

        with self.assertRaises(main.HTTPException) as cm:
            main.submit_proof(challenge_id=ch_id, req=proof_req, db=self.db)

        self.assertEqual(cm.exception.status_code, 503)

        # Ensure user answers were preserved in SQLite!
        saved = main.get_challenge(challenge_id=ch_id, db=self.db)
        self.assertIsNotNone(saved["proof_answers"])
        self.assertIn("brass key", str(saved["proof_answers"]))
        self.assertIsNotNone(saved["proof_image"])

    def test_duplicate_submission_and_streak_logic(self):
        # Manually complete a challenge
        c = models.Challenge(
            title="Mindful Walking",
            interest="Walking",
            duration_minutes=30,
            difficulty="Easy",
            instructions="Walk outside",
            status="completed",
            score=90
        )
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)

        # Attempt to submit again
        with self.assertRaises(main.HTTPException) as cm:
            main.submit_proof(
                challenge_id=c.id,
                req=ProofSubmitRequest(proof_answers="test"),
                db=self.db
            )
        self.assertEqual(cm.exception.status_code, 400)

    def test_abandon_challenge(self):
        req = ChallengeGenerateRequest(
            interest="Gardening",
            duration_minutes=30,
            difficulty="Easy"
        )
        ch = main.generate_challenge(req=req, db=self.db)
        ch_id = ch["id"]
        main.start_challenge(challenge_id=ch_id, db=self.db)

        abandoned = main.abandon_challenge(challenge_id=ch_id, db=self.db)
        self.assertEqual(abandoned["status"], "abandoned")

        # Active challenge should now be None
        active = main.get_active_challenge(db=self.db)
        self.assertIsNone(active)

if __name__ == "__main__":
    unittest.main()
