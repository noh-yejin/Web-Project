from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# FastMCP 서버 초기화
mcp = FastMCP("weather")

# 상수
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# National Weather Service API에서 데이터를 쿼리하고 형식을 지정하는 헬퍼 함수를 추가

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """NWS API에 적절한 오류 처리로 요청합니다."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """알림 기능을 읽기 쉬운 문자열로 형식화합니다."""
    props = feature["properties"]
    return f"""
이벤트: {props.get('event', '알 수 없음')}
지역: {props.get('areaDesc', '알 수 없음')}
심각도: {props.get('severity', '알 수 없음')}
설명: {props.get('description', '설명 없음')}
지침: {props.get('instruction', '특별한 지침 없음')}
"""



@mcp.tool()
async def get_alerts(state: str) -> str:
    """미국 주의 기상 알림을 가져옵니다.

    Args:
        state: 두 글자 미국 주 코드 (예: CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "알림을 가져올 수 없거나 알림이 없습니다."

    if not data["features"]:
        return "이 주에 대한 활성 알림이 없습니다."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """위치에 대한 기상 예보를 가져옵니다.

    Args:
        latitude: 위치의 위도
        longitude: 위치의 경도
    """
    # 먼저 예보 그리드 엔드포인트 가져오기
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "이 위치에 대한 예보 데이터를 가져올 수 없습니다."

    # 포인트 응답에서 예보 URL 가져오기
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "상세 예보를 가져올 수 없습니다."

    # 기간을 읽기 쉬운 예보로 포맷팅
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # 다음 5개 기간만 표시
        forecast = f"""
{period['name']}:
온도: {period['temperature']}°{period['temperatureUnit']}
바람: {period['windSpeed']} {period['windDirection']}
예보: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    # 서버 초기화 및 실행
    mcp.run(transport='stdio')