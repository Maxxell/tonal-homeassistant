import requests

AUTH0_DOMAIN = "tonal.auth0.com"
CLIENT_ID = "ERCyexW-xoVG_Yy3RDe-eV4xsOnRHP6L"
API_BASE = "https://api.tonal.com"


class TonalAPI:
    """
    A clean, Home Assistant–friendly wrapper around Tonal’s API.
    Handles:
      - authentication
      - user ID lookup
      - strength score retrieval
    """

    def __init__(self, email: str, password: str):
        self._email = email
        self._password = password
        self._access_token = None
        self._id_token = None
        self._token_type = None
        self._user_id = None

    # ------------------------------------------------------------
    # AUTHENTICATION
    # ------------------------------------------------------------
    def _authenticate(self):
        response = requests.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            json={
                "grant_type": "password",
                "client_id": CLIENT_ID,
                "username": self._email,
                "password": self._password,
                "scope": "openid profile email offline_access",
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception(
                f"Authentication failed: {response.status_code} - {response.text}"
            )

        data = response.json()
        self._access_token = data["access_token"]
        self._id_token = data["id_token"]
        self._token_type = data.get("token_type", "Bearer")

    def _get_headers(self):
        """Return headers with a valid token."""
        if not self._id_token:
            self._authenticate()

        return {
            "Authorization": f"Bearer {self._id_token}",
            "Accept": "application/json",
        }

    # ------------------------------------------------------------
    # USER INFO (GET USER ID)
    # ------------------------------------------------------------
    def _ensure_user_id(self):
        if self._user_id:
            return

        if not self._id_token:
            self._authenticate()

        headers = {"Authorization": f"Bearer {self._id_token}"}

        response = requests.get(
            f"{API_BASE}/v6/users/userinfo",
            headers=headers,
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to get user info: {response.status_code} - {response.text}"
            )

        data = response.json()
        self._user_id = data.get("userId") or data.get("id")

        if not self._user_id:
            raise Exception("Tonal API did not return a userId")

    # ------------------------------------------------------------
    # STRENGTH SCORES
    # ------------------------------------------------------------
    def get_current_strength_scores(self) -> dict:
        """Return muscle strength scores in a Home Assistant–friendly format."""
        self._ensure_user_id()

        url = f"{API_BASE}/v6/users/{self._user_id}/strength-scores/current"

        response = requests.get(url, headers=self._get_headers(), timeout=30)

        if response.status_code != 200:
            raise Exception(
                f"Strength score fetch failed: {response.status_code} - {response.text}"
            )

        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            return {}

        muscles = {}

        for region in data:
            region_name = region.get("strengthBodyRegion", "Unknown")

            for muscle in region.get("familyActivity", []):
                muscle_name = muscle.get("strengthFamily", "Unknown")
                muscles[muscle_name] = {
                    "score": round(muscle.get("score", 0)),
                    "region": region_name,
                    "updatedAt": muscle.get("updatedAt"),
                }

        return muscles

    # ------------------------------------------------------------
    # HOME ASSISTANT ENTRY POINT
    # ------------------------------------------------------------
    def fetch_data(self):
        """Fetch user ID and strength scores."""
        self._ensure_user_id()
        return self.get_current_strength_scores()