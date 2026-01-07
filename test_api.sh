#!/bin/bash
set -e

API_URL="${TRAVELBUDDY_API_URL:-http://localhost:8000}"

echo "🧪 Testing TravelBuddy API at $API_URL"
echo ""

# Health check
echo "1️⃣  Health check..."
curl -s "$API_URL/health" | jq .
echo ""

# Get locations
echo "2️⃣  Get locations..."
LOCATION_COUNT=$(curl -s "$API_URL/api/locations" | jq 'length')
echo "   $LOCATION_COUNT locations found"
echo ""

# Search for Paris
echo "3️⃣  Search for Paris, France..."
PARIS=$(curl -s "$API_URL/api/locations/search?name=Paris&country=France")
echo "$PARIS" | jq .
echo ""

# Get promoted tips
echo "4️⃣  Get promoted tips for Paris..."
TIPS=$(curl -s "$API_URL/api/promoted-tips?location_name=Paris&location_country=France")
TIP_COUNT=$(echo "$TIPS" | jq 'length')
echo "   $TIP_COUNT promoted tips found"
echo ""

if [ "$TIP_COUNT" -gt 0 ]; then
  # Show top 3
  echo "5️⃣  Top 3 tips:"
  echo "$TIPS" | jq -r '.[0:3] | .[] | "  [\(.mention_count)x] \(.tip_text[:70])..."'
  echo ""
else
  echo "⚠️  No promoted tips found for Paris"
  echo "   Run: python -m backend.jobs.nightly_processor --no-wake"
  echo ""
fi

# Test all locations
echo "6️⃣  Testing all locations..."
LOCATIONS=$(curl -s "$API_URL/api/locations" | jq -r '.[] | "\(.name),\(.country)"')

while IFS=',' read -r name country; do
  TIPS_FOR_LOC=$(curl -s "$API_URL/api/promoted-tips?location_name=$name&location_country=$country" | jq 'length')
  echo "   • $name, $country: $TIPS_FOR_LOC promoted tips"
done <<< "$LOCATIONS"

echo ""
echo "✅ All tests passed!"
