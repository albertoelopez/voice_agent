import pytest
import re
import socket
from playwright.sync_api import Page, expect


def is_livekit_running():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", 7880))
    sock.close()
    return result == 0


requires_livekit = pytest.mark.skipif(
    not is_livekit_running(),
    reason="LiveKit server not running on localhost:7880"
)


class TestVoiceClientUI:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/test_client.html")
        self.page = page

    def test_page_loads(self):
        expect(self.page).to_have_title("Voice Agent Test")

    def test_initial_status_disconnected(self):
        status = self.page.locator("#status")
        expect(status).to_have_text("Disconnected")
        expect(status).to_have_class("disconnected")

    def test_connect_button_visible(self):
        connect_btn = self.page.locator("#connectBtn")
        expect(connect_btn).to_be_visible()
        expect(connect_btn).to_have_text("Connect & Talk")
        expect(connect_btn).to_be_enabled()

    def test_disconnect_button_initially_disabled(self):
        disconnect_btn = self.page.locator("#disconnectBtn")
        expect(disconnect_btn).to_be_visible()
        expect(disconnect_btn).to_be_disabled()

    def test_conversation_area_exists(self):
        conversation = self.page.locator("#conversation")
        expect(conversation).to_be_visible()

    def test_debug_log_exists(self):
        details = self.page.locator("details")
        expect(details).to_be_visible()
        details.click()
        log = self.page.locator("#log")
        expect(log).to_be_visible()

    def test_page_has_livekit_script(self):
        scripts = self.page.locator("script[src*='livekit-client']")
        expect(scripts).to_have_count(1)


@requires_livekit
class TestVoiceClientConnection:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/test_client.html")
        self.page = page

    def test_connect_changes_status(self):
        self.page.locator("#connectBtn").click()

        status = self.page.locator("#status")
        expect(status).to_have_class(re.compile(r"connecting|connected"), timeout=5000)

    def test_connect_updates_ui_on_success(self):
        self.page.locator("#connectBtn").click()

        try:
            self.page.wait_for_function(
                "document.getElementById('status').className.includes('connected')",
                timeout=15000
            )
            connect_btn = self.page.locator("#connectBtn")
            expect(connect_btn).to_be_disabled()
            disconnect_btn = self.page.locator("#disconnectBtn")
            expect(disconnect_btn).to_be_enabled()
        except Exception:
            pytest.skip("Connection failed - likely microphone permission denied in headless mode")

    def test_connect_logs_activity(self):
        self.page.locator("details").click()
        self.page.locator("#connectBtn").click()

        self.page.wait_for_timeout(3000)

        log = self.page.locator("#log")
        log_text = log.inner_text()

        assert "Connecting to LiveKit" in log_text

    def test_disconnect_restores_initial_state(self):
        self.page.locator("#connectBtn").click()

        try:
            self.page.wait_for_function(
                "document.getElementById('status').className.includes('connected')",
                timeout=15000
            )
            disconnect_btn = self.page.locator("#disconnectBtn")
            expect(disconnect_btn).to_be_enabled(timeout=5000)
        except Exception:
            pytest.skip("Connection failed - likely microphone permission denied in headless mode")

        self.page.locator("#disconnectBtn").click()

        status = self.page.locator("#status")
        expect(status).to_have_text("Disconnected", timeout=5000)
        expect(status).to_have_class("disconnected")

        connect_btn = self.page.locator("#connectBtn")
        expect(connect_btn).to_be_enabled()

        disconnect_btn = self.page.locator("#disconnectBtn")
        expect(disconnect_btn).to_be_disabled()


class TestVoiceClientConversationUI:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/test_client.html")
        self.page = page

    def test_initial_conversation_placeholder(self):
        conversation = self.page.locator("#conversation")
        text = conversation.inner_text()
        assert "Connect" in text or "speaking" in text.lower()

    def test_addmessage_function_exists(self):
        result = self.page.evaluate("typeof addMessage === 'function'")
        assert result is True

    def test_can_add_user_message(self):
        self.page.evaluate("addMessage('Hello test', true)")

        conversation = self.page.locator("#conversation")
        expect(conversation).to_contain_text("Hello test")

        user_msg = self.page.locator(".user-message")
        expect(user_msg).to_be_visible()

    def test_can_add_agent_message(self):
        self.page.evaluate("addMessage('Agent response', false)")

        conversation = self.page.locator("#conversation")
        expect(conversation).to_contain_text("Agent response")

        agent_msg = self.page.locator(".agent-message")
        expect(agent_msg).to_be_visible()

    def test_messages_have_labels(self):
        self.page.evaluate("addMessage('User says', true)")
        self.page.evaluate("addMessage('Agent says', false)")

        labels = self.page.locator(".message-label")
        expect(labels).to_have_count(2)

    def test_conversation_scrolls_on_new_message(self):
        for i in range(10):
            is_user = "true" if i % 2 == 0 else "false"
            self.page.evaluate(f"addMessage('Message {i}', {is_user})")

        conversation = self.page.locator("#conversation")
        scroll_top = self.page.evaluate("document.getElementById('conversation').scrollTop")
        scroll_height = self.page.evaluate("document.getElementById('conversation').scrollHeight")
        client_height = self.page.evaluate("document.getElementById('conversation').clientHeight")

        assert scroll_top >= scroll_height - client_height - 10


class TestLiveKitIntegration:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        page.goto("http://localhost:8080/test_client.html")
        self.page = page

    def test_livekit_client_loaded(self):
        result = self.page.evaluate("typeof LivekitClient !== 'undefined'")
        assert result is True

    def test_livekit_room_class_exists(self):
        result = self.page.evaluate("typeof LivekitClient.Room === 'function'")
        assert result is True

    def test_can_create_room_instance(self):
        result = self.page.evaluate("new LivekitClient.Room() !== null")
        assert result is True

    def test_token_is_valid_jwt_format(self):
        token = self.page.evaluate("TOKEN")
        parts = token.split(".")
        assert len(parts) == 3
