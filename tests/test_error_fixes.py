"""
Test that our error fixes work correctly.
"""

import sys
sys.path.append('.')

import pytest
from thespian.llm.playwright import EnhancedPlaywright
from thespian.llm.manager import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.utils.error_handling import parse_llm_json_response, validate_scene_content


class TestStoryOutlineFix:
    """Test the story outline method signature fix."""
    
    def test_create_story_outline_with_dict_requirements(self):
        """Test original signature with dict requirements."""
        playwright = EnhancedPlaywright(
            name="TestPlaywright",
            llm_manager=LLMManager(),
            memory=TheatricalMemory(),
            advisor_manager=AdvisorManager(LLMManager(), TheatricalMemory()),
            quality_control=TheatricalQualityControl()
        )
        
        # Should work with original signature
        requirements = {
            'setting': 'Victorian London',
            'style': 'Mystery',
            'period': '1890s',
            'target_audience': 'Adults'
        }
        
        # This should not raise an error
        outline = playwright.create_story_outline("Murder mystery", requirements)
        assert isinstance(outline, dict)
    
    def test_create_story_outline_with_list_themes(self):
        """Test new signature with list of themes."""
        playwright = EnhancedPlaywright(
            name="TestPlaywright",
            llm_manager=LLMManager(),
            memory=TheatricalMemory(),
            advisor_manager=AdvisorManager(LLMManager(), TheatricalMemory()),
            quality_control=TheatricalQualityControl()
        )
        
        # Should work with new signature (premise, themes)
        themes = ["justice", "redemption", "secrets"]
        
        # This should not raise an error
        outline = playwright.create_story_outline("A judge confronts their past", themes)
        assert isinstance(outline, dict)
    
    def test_create_story_outline_with_no_requirements(self):
        """Test with no requirements parameter."""
        playwright = EnhancedPlaywright(
            name="TestPlaywright",
            llm_manager=LLMManager(),
            memory=TheatricalMemory(),
            advisor_manager=AdvisorManager(LLMManager(), TheatricalMemory()),
            quality_control=TheatricalQualityControl()
        )
        
        # Should work with just premise
        outline = playwright.create_story_outline("A simple love story")
        assert isinstance(outline, dict)


class TestErrorHandlingUtils:
    """Test error handling utilities."""
    
    def test_parse_llm_json_response_valid(self):
        """Test parsing valid JSON."""
        response = '{"key": "value", "number": 42}'
        result = parse_llm_json_response(response)
        assert result == {"key": "value", "number": 42}
    
    def test_parse_llm_json_response_markdown(self):
        """Test parsing JSON wrapped in markdown."""
        response = '```json\n{"key": "value"}\n```'
        result = parse_llm_json_response(response)
        assert result == {"key": "value"}
    
    def test_parse_llm_json_response_invalid(self):
        """Test parsing invalid JSON returns fallback."""
        response = "This is not JSON"
        fallback = {"default": True}
        result = parse_llm_json_response(response, fallback)
        assert result == fallback
    
    def test_parse_llm_json_response_object(self):
        """Test parsing response object with content attribute."""
        class MockResponse:
            content = '{"test": "data"}'
        
        result = parse_llm_json_response(MockResponse())
        assert result == {"test": "data"}
    
    def test_validate_scene_content_valid(self):
        """Test validating valid scene content."""
        scene = """
        ACT 1, SCENE 1
        
        HAMLET: To be or not to be, that is the question.
        
        OPHELIA: My lord, I have remembrances of yours.
        """
        assert validate_scene_content(scene) is True
    
    def test_validate_scene_content_too_short(self):
        """Test validating short scene content."""
        scene = "Too short"
        assert validate_scene_content(scene) is False
    
    def test_validate_scene_content_no_structure(self):
        """Test validating scene without structure."""
        scene = "A" * 200  # Long enough but no structure
        assert validate_scene_content(scene) is False


if __name__ == "__main__":
    # Run tests
    print("Testing Story Outline Fix...")
    test_outline = TestStoryOutlineFix()
    
    try:
        test_outline.test_create_story_outline_with_dict_requirements()
        print("✓ Dict requirements test passed")
    except Exception as e:
        print(f"✗ Dict requirements test failed: {e}")
    
    try:
        test_outline.test_create_story_outline_with_list_themes()
        print("✓ List themes test passed")
    except Exception as e:
        print(f"✗ List themes test failed: {e}")
    
    try:
        test_outline.test_create_story_outline_with_no_requirements()
        print("✓ No requirements test passed")
    except Exception as e:
        print(f"✗ No requirements test failed: {e}")
    
    print("\nTesting Error Handling Utils...")
    test_utils = TestErrorHandlingUtils()
    
    try:
        test_utils.test_parse_llm_json_response_valid()
        print("✓ Valid JSON parsing test passed")
    except Exception as e:
        print(f"✗ Valid JSON parsing test failed: {e}")
    
    try:
        test_utils.test_parse_llm_json_response_markdown()
        print("✓ Markdown JSON parsing test passed")
    except Exception as e:
        print(f"✗ Markdown JSON parsing test failed: {e}")
    
    try:
        test_utils.test_validate_scene_content_valid()
        print("✓ Valid scene content test passed")
    except Exception as e:
        print(f"✗ Valid scene content test failed: {e}")