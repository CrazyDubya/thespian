import pytest
from thespian.llm.config import LLMConfig
from thespian.llm.models import LLMManager


def test_llmconfig_defaults():
    config = LLMConfig()
    assert config.ollama_base_url == "http://localhost:11434"
    assert config.ollama_model == "long-gemma"
    assert config.grok_api_base == "https://api.x.ai/v1"
    assert config.grok_model == "grok-3-beta"
    assert config.ollama_usage_percentage == 0.5


def test_llmconfig_should_use_ollama():
    config = LLMConfig()
    # If no grok_api_key, should always use ollama
    assert config.should_use_ollama("any_agent") is True
    # If grok_api_key is set, should return a bool
    config.grok_api_key = "dummy"
    result = config.should_use_ollama("agent1")
    assert isinstance(result, bool)


def test_llmconfig_get_model_config():
    config = LLMConfig()
    ollama_conf = config.get_model_config("ollama")
    assert ollama_conf["base_url"] == config.ollama_base_url
    assert ollama_conf["model"] == config.ollama_model
    grok_conf = config.get_model_config("grok")
    assert grok_conf["api_base"] == config.grok_api_base
    assert grok_conf["model"] == config.grok_model
    with pytest.raises(ValueError):
        config.get_model_config("unknown")


def test_llmmanager_init_and_model_info():
    manager = LLMManager()
    info = manager.get_model_info("agent1")
    assert "type" in info and "model" in info
    # Should default to ollama if grok is not available
    assert info["type"] == "ollama"


def test_llmmanager_generate_response(monkeypatch):
    manager = LLMManager()
    # Patch _generate_ollama_response to avoid real HTTP call
    manager._generate_ollama_response = lambda prompt, **kwargs: {"response": "test", "model": "long-gemma"}
    resp = manager.generate_response("hello", "agent1")
    assert resp["response"] == "test"
    assert resp["model"] == "long-gemma" 