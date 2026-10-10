import threading
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

class MockLlamaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/health", "/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/completion":
            content_length = int(self.headers.get("Content-Length", 0))
            req_body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(req_body)
            prompt = data.get("prompt", "")

            # Decide whether this is a generation prompt or an evaluation prompt
            if "impartial, supportive offline activity evaluator" in prompt:
                # Evaluation response
                eval_payload = {
                    "relevance": "Direct and thorough response relating to plant care and soil aeration.",
                    "quality": "Exceptional sensory observations noted regarding leaf texture and emerging node tip.",
                    "completion_score": 95,
                    "feedback": "Outstanding dedication to hands-on gardening! Your mindful inspection revealed fine details you would have missed on a screen.",
                    "final_score": 96
                }
                res_content = json.dumps(eval_payload)
            else:
                # Challenge generation response
                gen_payload = {
                    "title": "Acoustic Melody Transcription",
                    "interest": "Music",
                    "duration_minutes": 30,
                    "difficulty": "Medium",
                    "instructions": "Pick up an acoustic instrument or sit quietly. Hum or play 4-note melodies by ear without digital sheets.",
                    "materials": ["Acoustic instrument or voice"],
                    "expected_result": "A 4-note melody transcribed or committed to muscle memory.",
                    "proof_instructions": "Describe the notes or intervals you practiced and how your auditory focus changed.",
                    "follow_up_questions": [
                        "What acoustic melody or interval did you focus on?",
                        "What sensory challenge arose when matching pitches without a digital tuner?",
                        "How did your listening awareness feel after 30 minutes?"
                    ],
                    "rubric": "Score based on acoustic attentiveness and honest effort."
                }
                res_content = json.dumps(gen_payload)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"content": res_content}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # quiet

def run_test():
    # Start mock llama server on 8081
    server = HTTPServer(("127.0.0.1", 8081), MockLlamaHandler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()
    time.sleep(0.5)

    print("Mock llama.cpp server running on port 8081")

    # 1. Test AI status endpoint
    ai_status = requests.get("http://127.0.0.1:8000/api/ai/status").json()
    print("AI status online:", ai_status["online"])
    assert ai_status["online"] == True

    # 2. Generate challenge with local AI
    gen_resp = requests.post("http://127.0.0.1:8000/api/challenges/generate", json={
        "interest": "Music",
        "duration_minutes": 30,
        "difficulty": "Medium",
        "surprise_me": False
    }).json()
    ch_id = gen_resp["id"]
    print(f"Generated Challenge via AI: ID={ch_id}, Title='{gen_resp['title']}', is_fallback={gen_resp['is_fallback']}")
    assert gen_resp["is_fallback"] == False
    assert gen_resp["title"] == "Acoustic Melody Transcription"

    # 3. Start challenge
    started = requests.post(f"http://127.0.0.1:8000/api/challenges/{ch_id}/start").json()
    print("Challenge started. Status:", started["status"], "Remaining seconds:", started["remaining_seconds"])
    assert started["status"] == "active"
    assert started["remaining_seconds"] > 0

    # 4. Submit proof and get AI evaluation
    eval_resp = requests.post(f"http://127.0.0.1:8000/api/challenges/{ch_id}/submit", json={
        "proof_answers": {
            "What acoustic melody or interval did you focus on?": "A major third interval on acoustic guitar (C to E) and hummed the resonance.",
            "What sensory challenge arose when matching pitches without a digital tuner?": "Noticed the natural beating of the strings and had to tune by ear.",
            "How did your listening awareness feel after 30 minutes?": "My hearing felt much more sensitive to room acoustic reverb."
        },
        "proof_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    })

    print("Submission status code:", eval_resp.status_code)
    assert eval_resp.status_code == 200
    res_data = eval_resp.json()
    print(f"Evaluation: Score={res_data['score']}, Current Streak={res_data['current_streak']}, Total Completed={res_data['total_completed']}")
    print(f"AI Feedback: {res_data['feedback']}")
    assert res_data["score"] == 96
    assert res_data["current_streak"] >= 1
    assert res_data["total_completed"] >= 1

    # 5. Check History endpoint
    history = requests.get("http://127.0.0.1:8000/api/history").json()
    print(f"History contains {len(history)} items. Latest score: {history[0]['score']}")
    assert len(history) >= 1
    assert history[0]["id"] == ch_id

    # 6. Check Stats endpoint
    stats = requests.get("http://127.0.0.1:8000/api/stats").json()
    print("User stats:", stats)
    assert stats["total_completed"] >= 1

    server.shutdown()
    print("\nALL END-TO-END AI TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_test()
