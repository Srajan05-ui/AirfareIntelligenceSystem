import logging
from datetime import date, timedelta
from typing import List, Optional
from fast_flights import FlightQuery, Passengers, get_flights, create_query

from ingestion.models import RawFareObservation
from ingestion.rate_limiter import PoliteScraper

logger = logging.getLogger(__name__)

class FastFlightsCollector:
    def __init__(self):
        # Enforce exactly 1.5 requests per second as per VayuSutra guidelines
        self.scraper = PoliteScraper(requests_per_second=1.5, max_burst=2)
        
        # Hardcoded configs for prototype
        self.ROUTES = [("DEL", "BOM"), ("BOM", "BLR"), ("DEL", "BLR")]
        self.WINDOWS = [3, 7, 14, 30]
        
    def _parse_price(self, price_raw) -> Optional[float]:
        if price_raw is None: return None
        if isinstance(price_raw, (int, float)): return float(price_raw)
        digits = "".join(ch for ch in str(price_raw) if ch.isdigit() or ch == ".")
        try:
            return float(digits) if digits else None
        except ValueError:
            return None

    def fetch_route(self, origin: str, destination: str, departure_date: date) -> List[RawFareObservation]:
        with self.scraper:
            logger.info(f"Querying {origin}->{destination} for {departure_date}")
            query = create_query(
                flights=[
                    FlightQuery(
                        date=departure_date.isoformat(),
                        from_airport=origin,
                        to_airport=destination,
                    )
                ],
                trip="one-way",
                seat="economy",
                passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
                currency="INR", # Fixes the USD bug
            )
            
            try:
                result = get_flights(query)
            except Exception as e:
                logger.error(f"Failed to fetch {origin}->{destination}: {e}")
                return []
                
            flights = result if isinstance(result, list) else (getattr(result, "flights", None) or [])
            observations = []
            
            for f in flights:
                price_raw = getattr(f, "price", None)
                price = self._parse_price(price_raw)
                
                # Sanitize the USD Bug (USD_TO_INR approx 84)
                if price and price < 500:
                    price = round(price * 84.0)
                    
                if not price: continue
                
                airlines = getattr(f, "airlines", [])
                airline = airlines[0] if airlines else (getattr(f, "name", "") or getattr(f, "airline", "") or "Unknown")
                
                try:
                    # STRICT PYDANTIC VALIDATION
                    obs = RawFareObservation(
                        source_tier="tier1_googleflights",
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date.isoformat(),
                        airline=airline,
                        departure_time="00:00", # Mocked for prototype simplification
                        arrival_time="00:00",
                        price=price
                    )
                    observations.append(obs)
                except Exception as e:
                    logger.warning(f"Validation failed for flight {airline} {price}: {e}")
            
            return observations

    def run_all(self):
        all_results = []
        for origin, destination in self.ROUTES:
            for window in self.WINDOWS:
                target_date = date.today() + timedelta(days=window)
                obs = self.fetch_route(origin, destination, target_date)
                all_results.extend(obs)
                
        return all_results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = FastFlightsCollector()
    results = collector.run_all()
    print(f"Collected {len(results)} valid observations.")
    if results:
        print("Sample:", results[0].model_dump_json(indent=2))
