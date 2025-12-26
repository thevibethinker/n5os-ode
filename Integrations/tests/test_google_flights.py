import unittest
from pathlib import Path
import sys

# Add parent dir to path to import script
sys.path.append(str(Path(__file__).parent.parent))
from google_flights import normalize_airport_code, FlightPreferences, score_flight

class TestGoogleFlights(unittest.TestCase):
    def test_normalize_airport_code(self):
        self.assertEqual(normalize_airport_code("JFK"), "JFK")
        self.assertEqual(normalize_airport_code("San Diego"), "SAN")
        self.assertEqual(normalize_airport_code("London"), "LHR")
        self.assertEqual(normalize_airport_code("  sfo  "), "SFO")

    def test_score_flight_basic(self):
        prefs = FlightPreferences()
        prefs.departure_airports = ["JFK", "LGA", "EWR"]
        prefs.preferred_airlines = ["B6"]
        
        flight = {
            "flights": [{"airline": "JetBlue", "flight_number": "B6 123"}]
        }
        
        # JFK + JetBlue bonus
        score = score_flight(flight, "JFK", prefs)
        self.assertGreater(score, 100)

if __name__ == "__main__":
    unittest.main()

