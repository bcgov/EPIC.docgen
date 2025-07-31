# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Bring in the common JWT Manager."""
from functools import wraps

from flask import g, request, current_app
from flask_jwt_oidc import JwtManager


jwt = (
    JwtManager()
)  # pylint: disable=invalid-name; lower case name as used by convention in most Flask apps


class Auth:  # pylint: disable=too-few-public-methods
    """Extending JwtManager to include additional functionalities."""

    @classmethod
    def require(cls, f):
        """Validate the Bearer Token."""

        @jwt.requires_auth
        @wraps(f)
        def decorated(*args, **kwargs):
            g.authorization_header = request.headers.get("Authorization", None)
            g.token_info = g.jwt_oidc_token_info

            return f(*args, **kwargs)

        return decorated

    @classmethod
    def require_api_key_or_jwt(cls, f):
        """Validate either API Key (X-API-Key header) OR JWT token (Authorization header)."""

        @wraps(f)
        def decorated(*args, **kwargs):
            # Check for X-API-Key header
            api_key = request.headers.get("X-API-Key")
            if api_key:
                if cls._is_valid_api_key(api_key):
                    g.authorization_header = f"X-API-Key {api_key}"
                    g.token_info = g.jwt_oidc_token_info = {
                        "sub": "github-actions",
                        "client_id": "api-key-client",
                        "preferred_username": "github-actions",
                        "auth_type": "api_key"
                    }
                    return f(*args, **kwargs)
                else:
                    return {"message": "Invalid API key"}, 403

            # Check for Authorization header (JWT)
            auth_header = request.headers.get("Authorization")
            if auth_header:
                @jwt.requires_auth
                @wraps(f)
                def jwt_decorated(*args, **kwargs):
                    g.authorization_header = auth_header
                    g.token_info = g.jwt_oidc_token_info
                    g.token_info["auth_type"] = "jwt"
                    return f(*args, **kwargs)

                return jwt_decorated(*args, **kwargs)

            return {"message": "Either X-API-Key or Authorization header required"}, 401

        return decorated

    @classmethod
    def _is_valid_api_key(cls, api_key):
        """Check if the API key is valid."""
        if not api_key or not api_key.strip():
            return False

        # Get comma-separated API keys from environment variable
        api_keys_env = current_app.config['DOCGEN_API_KEYS']
        if not api_keys_env:
            return False

        # Split by comma and clean up whitespace
        valid_api_keys = [key.strip() for key in api_keys_env.split(",") if key.strip()]

        return api_key.strip() in valid_api_keys


auth = (
    Auth()
)
