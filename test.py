import json
import sys
import os

# Přidání cesty k modulu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'cz_air_quality'))

# Přímý import air_quality_data modulu
from air_quality_data import CHMUAirQuality


def test_new_api():
    """Test zjednodušeného API."""
    print("Testing simplified CHMUAirQuality class...")
    print("=" * 80)

    # Test 1: Získání všech kódů stanic
    print("\n1. Testing get_all_station_codes():")
    print("-" * 80)
    try:
        station_codes = CHMUAirQuality.get_all_station_codes()
        print(f"Total stations available: {len(station_codes)}")
        print(f"\nFirst 10 station codes:")
        for i, code in enumerate(station_codes[:10], 1):
            print(f"  {i}. {code}")
        print(f"\nLast 5 station codes:")
        for i, code in enumerate(station_codes[-5:], len(station_codes)-4):
            print(f"  {i}. {code}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 80)

    # Test 2: Získání dat pro konkrétní stanici podle názvu
    print("\n2. Testing get_station_data() with station name:")
    print("-" * 80)

    test_stations = ["Praha", "Brno", "Ostrava", "Plzeň", "Liberec"]

    for station_name in test_stations:
        print(f"\n  Searching for: '{station_name}'")
        try:
            result = CHMUAirQuality.get_station_data(station_name)

            if result["station_data"]:
                data = result["station_data"]
                print(f"  ✓ Found: {data['station_code']} - {data['station_name']}")
                print(f"    Region: {data['region']}")
                print(f"    AQI: {data['air_quality_index']}")
                print(f"    Updated: {result['updated']}")

                # Vypsat dostupné měření
                measurements = []
                if data['no2_1h'] is not None:
                    measurements.append(f"NO2: {data['no2_1h']} µg/m³")
                if data['pm10_24h'] is not None:
                    measurements.append(f"PM10(24h): {data['pm10_24h']} µg/m³")
                if data['pm25_1h'] is not None:
                    measurements.append(f"PM2.5: {data['pm25_1h']} µg/m³")
                if data['o3_1h'] is not None:
                    measurements.append(f"O3: {data['o3_1h']} µg/m³")

                if measurements:
                    print(f"    Measurements: {', '.join(measurements)}")
            else:
                print(f"  ✗ No station found for '{station_name}'")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n" + "=" * 80)

    # Test 3: Test konkrétního kódu stanice
    print("\n3. Testing get_station_data() with specific station code:")
    print("-" * 80)

    # Nejprve získáme nějaký kód stanice
    codes = CHMUAirQuality.get_all_station_codes()
    if codes:
        test_code = codes[0]  # Vezmeme první kód
        print(f"\n  Testing with code: '{test_code}'")
        try:
            result = CHMUAirQuality.get_station_data(test_code)

            if result["station_data"]:
                print(f"  ✓ Success!")
                print(f"\n  Full station data:")
                print(json.dumps(result["station_data"], indent=4, ensure_ascii=False))
            else:
                print(f"  ✗ Failed to get data")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n" + "=" * 80)

    # Test 4: Test neexistující stanice
    print("\n4. Testing with non-existent station:")
    print("-" * 80)
    try:
        result = CHMUAirQuality.get_station_data("NonExistentStation123")
        if result["station_data"] is None:
            print("  ✓ Correctly returned None for non-existent station")
        else:
            print("  ✗ Should have returned None")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\n" + "=" * 80)

    # Test 5: Test struktury dat pro hub.py
    print("\n5. Testing data structure for hub.py integration:")
    print("-" * 80)
    try:
        result = CHMUAirQuality.get_station_data("Praha")

        if result["station_data"]:
            data = result["station_data"]
            print("\n  Checking all required fields for hub.py:")

            fields = [
                ("station_code", data.get("station_code")),
                ("station_name", data.get("station_name")),
                ("region", data.get("region")),
                ("classification", data.get("classification")),
                ("owner", data.get("owner")),
                ("air_quality_index", data.get("air_quality_index")),
                ("datetime", data.get("datetime")),
                ("so2_1h", data.get("so2_1h")),
                ("no2_1h", data.get("no2_1h")),
                ("co_8h", data.get("co_8h")),
                ("pm10_1h", data.get("pm10_1h")),
                ("pm10_24h", data.get("pm10_24h")),
                ("pm25_1h", data.get("pm25_1h")),
                ("o3_1h", data.get("o3_1h")),
                ("limitPassedColor_aqi", data.get("limitPassedColor_aqi")),
            ]

            for field_name, field_value in fields:
                status = "✓" if field_value is not None or field_name in ["so2_1h", "co_8h", "pm25_1h", "o3_1h"] else "?"
                print(f"    {status} {field_name}: {field_value}")

            print("\n  ✓ Data structure is compatible with hub.py")
        else:
            print("  ✗ Failed to get data")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\n" + "=" * 80)
    print("\nAll tests completed!")


if __name__ == "__main__":
    test_new_api()



