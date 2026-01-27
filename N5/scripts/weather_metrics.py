#!/usr/bin/env python3
"""
Weather Metrics for Performance Dashboard v2

Fetches weather data from Open-Meteo API (no API key required).
Uses Brooklyn, NY coordinates as default location.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional

# Brooklyn, NY coordinates (V's location)
DEFAULT_LAT = 40.6782
DEFAULT_LON = -73.9442

# WMO Weather Code mapping
# See: https://open-meteo.com/en/docs
WEATHER_CODES = {
    0: ("Clear", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌧️"),
    53: ("Moderate Drizzle", "🌧️"),
    55: ("Dense Drizzle", "🌧️"),
    56: ("Freezing Drizzle", "🌧️"),
    57: ("Dense Freezing Drizzle", "🌧️"),
    61: ("Light Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    66: ("Freezing Rain", "🌧️"),
    67: ("Heavy Freezing Rain", "🌧️"),
    71: ("Light Snow", "🌨️"),
    73: ("Moderate Snow", "🌨️"),
    75: ("Heavy Snow", "🌨️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Light Showers", "🌦️"),
    81: ("Moderate Showers", "🌦️"),
    82: ("Violent Showers", "🌦️"),
    85: ("Light Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm w/ Hail", "⛈️"),
    99: ("Severe Thunderstorm", "⛈️"),
}


def fetch_weather_data(
    start_date: str, 
    end_date: str,
    latitude: float = DEFAULT_LAT,
    longitude: float = DEFAULT_LON
) -> Optional[dict]:
    """
    Fetch historical weather data from Open-Meteo API.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        latitude: Location latitude
        longitude: Location longitude
        
    Returns:
        Raw API response dict or None on error
    """
    # Open-Meteo forecast API with past_days for recent historical data
    # For dates within last 7 days, use forecast API; older dates need archive API
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days_ago = (datetime.now() - start_dt).days
    
    if days_ago <= 16:
        # Use forecast API with past_days
        base_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "temperature_unit": "fahrenheit",
            "past_days": min(days_ago + 1, 16),
            "forecast_days": 1,
            "timezone": "America/New_York"
        }
    else:
        # Use archive API for older dates
        base_url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York"
        }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Weather API error: {e}")
        return None


def get_weather_description(code: int) -> tuple[str, str]:
    """
    Convert WMO weather code to description and emoji.
    
    Returns:
        (description, emoji)
    """
    return WEATHER_CODES.get(code, ("Unknown", "❓"))


def calculate_weather_metrics(data: dict, start_date: str, end_date: str) -> dict:
    """
    Calculate weather metrics from API response.
    
    Args:
        data: Raw Open-Meteo API response
        start_date: Period start date
        end_date: Period end date
        
    Returns:
        {
            avg_high, avg_low, 
            rain_days, total_precipitation,
            conditions_summary: {condition: count},
            daily_values: [{date, high, low, precip, condition, emoji}],
            data_points
        }
    """
    if not data or 'daily' not in data:
        return {
            "avg_high": 0.0,
            "avg_low": 0.0,
            "rain_days": 0,
            "total_precipitation": 0.0,
            "conditions_summary": {},
            "daily_values": [],
            "data_points": 0
        }
    
    daily = data['daily']
    dates = daily.get('time', [])
    highs = daily.get('temperature_2m_max', [])
    lows = daily.get('temperature_2m_min', [])
    precip = daily.get('precipitation_sum', [])
    codes = daily.get('weathercode', [])
    
    # Filter to requested date range
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    daily_values = []
    conditions_count = {}
    valid_highs = []
    valid_lows = []
    total_precip = 0.0
    rain_days = 0
    
    for i, date_str in enumerate(dates):
        date_dt = datetime.strptime(date_str, '%Y-%m-%d')
        if date_dt < start_dt or date_dt > end_dt:
            continue
            
        high = highs[i] if i < len(highs) and highs[i] is not None else None
        low = lows[i] if i < len(lows) and lows[i] is not None else None
        day_precip = precip[i] if i < len(precip) and precip[i] is not None else 0.0
        code = codes[i] if i < len(codes) else 0
        
        condition, emoji = get_weather_description(code)
        
        if high is not None:
            valid_highs.append(high)
        if low is not None:
            valid_lows.append(low)
        
        total_precip += day_precip
        if day_precip > 0.1:  # More than trace precipitation
            rain_days += 1
        
        conditions_count[condition] = conditions_count.get(condition, 0) + 1
        
        daily_values.append({
            "date": date_str,
            "high": round(high, 1) if high is not None else None,
            "low": round(low, 1) if low is not None else None,
            "precip": round(day_precip, 2),
            "condition": condition,
            "emoji": emoji
        })
    
    avg_high = sum(valid_highs) / len(valid_highs) if valid_highs else 0.0
    avg_low = sum(valid_lows) / len(valid_lows) if valid_lows else 0.0
    
    return {
        "avg_high": round(avg_high, 1),
        "avg_low": round(avg_low, 1),
        "rain_days": rain_days,
        "total_precipitation": round(total_precip, 2),
        "conditions_summary": conditions_count,
        "daily_values": daily_values,
        "data_points": len(daily_values)
    }


def get_weekly_weather(days: int = 7) -> dict:
    """
    Main entry point: get weather metrics for past N days.
    
    Args:
        days: Number of days to look back
        
    Returns:
        Complete weather metrics dict
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    data = fetch_weather_data(start_str, end_str)
    metrics = calculate_weather_metrics(data, start_str, end_str)
    
    metrics['period_start'] = start_str
    metrics['period_end'] = end_str
    metrics['location'] = "Brooklyn, NY"
    
    return metrics


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Weather metrics for Performance Dashboard")
    parser.add_argument('--days', type=int, default=7, help="Days to look back")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    parser.add_argument('--test', action='store_true', help="Run test with sample output")
    args = parser.parse_args()
    
    metrics = get_weekly_weather(args.days)
    
    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        print(f"Weather: {metrics['period_start']} to {metrics['period_end']}")
        print(f"Location: {metrics['location']}")
        print(f"Avg High: {metrics['avg_high']}°F | Avg Low: {metrics['avg_low']}°F")
        print(f"Rain Days: {metrics['rain_days']} | Total Precip: {metrics['total_precipitation']}\"")
        print(f"\nConditions breakdown:")
        for condition, count in sorted(metrics['conditions_summary'].items(), key=lambda x: -x[1]):
            print(f"  {condition}: {count} days")
        print(f"\nDaily values:")
        for day in metrics['daily_values']:
            print(f"  {day['date']}: {day['emoji']} {day['condition']} | High {day['high']}° Low {day['low']}°")
