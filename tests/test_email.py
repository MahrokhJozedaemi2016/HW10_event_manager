import pytest
import os
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

# Skip the test if running in GitHub Actions
if os.getenv("GITHUB_ACTIONS"):
    pytestmark = pytest.mark.skip(reason="Skipping due to SMTP connection issue in GitHub Actions")

@pytest.mark.asyncio
async def test_send_markdown_email(email_service):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, 'email_verification')
    # Manual verification in Mailtrap
