import json
import time
import logging

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("apps.audit")


class AuditMiddleware(MiddlewareMixin):
    SAFE_PATHS = ("/api/v1/auth/login", "/api/v1/auth/logout", "/health/")
    AUDIT_METHODS = ("POST", "PUT", "PATCH", "DELETE")

    def process_request(self, request):
        request._audit_start_time = time.time()
        request._audit_body = None
        if request.method in self.AUDIT_METHODS and request.content_type == "application/json":
            try:
                request._audit_body = json.loads(request.body) if request.body else None
            except (json.JSONDecodeError, ValueError):
                request._audit_body = None

    def process_response(self, request, response):
        if not hasattr(request, "_audit_start_time"):
            return response

        duration_ms = int((time.time() - request._audit_start_time) * 1000)
        path = request.path

        if any(path.startswith(sp) for sp in self.SAFE_PATHS):
            return response

        if path.startswith("/api/") and request.method in self.AUDIT_METHODS:
            try:
                from apps.audit.models import AuditLog

                user = request.user if hasattr(request, "user") and request.user.is_authenticated else None
                tenant = getattr(request, "tenant", None)

                action_map = {
                    "POST": AuditLog.ActionType.CREATE,
                    "PUT": AuditLog.ActionType.UPDATE,
                    "PATCH": AuditLog.ActionType.UPDATE,
                    "DELETE": AuditLog.ActionType.DELETE,
                }

                entity_type = self._extract_entity_type(path)

                old_value = None
                new_value = None
                if request.method in ("PUT", "PATCH"):
                    new_value = request._audit_body
                elif request.method == "POST":
                    new_value = request._audit_body
                elif request.method == "DELETE":
                    old_value = {"deleted": True}

                AuditLog.objects.create(
                    tenant=tenant,
                    user=user,
                    action_type=action_map.get(request.method, AuditLog.ActionType.READ),
                    entity_type=entity_type,
                    entity_id=self._extract_entity_id(path),
                    description=f"{request.method} {path}",
                    old_value=old_value,
                    new_value=new_value,
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                    request_method=request.method,
                    request_path=path,
                    response_status=response.status_code,
                    duration_ms=duration_ms,
                    is_success=200 <= response.status_code < 400,
                )
            except Exception as e:
                logger.warning(f"Audit log failed: {e}")

        return response

    def _extract_entity_type(self, path):
        parts = [p for p in path.strip("/").split("/") if p and p != "api" and p != "v1"]
        if parts:
            return parts[0]
        return "unknown"

    def _extract_entity_id(self, path):
        import uuid
        parts = path.strip("/").split("/")
        for part in parts:
            try:
                return uuid.UUID(part)
            except (ValueError, AttributeError):
                continue
        return None

    def _get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
