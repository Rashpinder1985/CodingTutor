#!/usr/bin/env python3
"""
Test script to verify Gemini integration and fallback mechanism.
"""

import os
import sys

def test_gemini_sdk():
    """Test if Gemini SDK is installed."""
    print("=" * 60)
    print("🧪 Testing Gemini SDK Installation")
    print("=" * 60)
    
    try:
        import google.generativeai as genai
        print("✓ Gemini SDK installed successfully!")
        print(f"  Version: {genai.__version__ if hasattr(genai, '__version__') else 'Unknown'}")
        return True
    except ImportError:
        print("✗ Gemini SDK not installed")
        print("  Run: pip3 install google-generativeai --break-system-packages")
        return False

def test_api_key():
    """Test if API key is set."""
    print("\n" + "=" * 60)
    print("🔑 Checking API Keys")
    print("=" * 60)
    
    # Check Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✓ GEMINI_API_KEY set: {gemini_key[:10]}...{gemini_key[-4:]}")
    else:
        print("✗ GEMINI_API_KEY not set")
        print("  Get key: https://makersuite.google.com/app/apikey")
        print("  Set: export GEMINI_API_KEY='your-key-here'")
    
    # Check OpenAI (optional)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"✓ OPENAI_API_KEY set: {openai_key[:10]}...{openai_key[-4:]}")
    else:
        print("ℹ OPENAI_API_KEY not set (optional)")
    
    return gemini_key is not None

def test_config():
    """Test if config.yaml has fallback enabled."""
    print("\n" + "=" * 60)
    print("⚙️  Checking Configuration")
    print("=" * 60)
    
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        llm_config = config.get('llm', {})
        fallback_enabled = llm_config.get('fallback_enabled', False)
        fallback_providers = llm_config.get('fallback_providers', [])
        
        print(f"Primary provider: {llm_config.get('provider', 'unknown')}")
        print(f"Primary model: {llm_config.get('model', 'unknown')}")
        print(f"Fallback enabled: {fallback_enabled}")
        
        if fallback_enabled:
            print(f"Fallback providers ({len(fallback_providers)}):")
            for i, fb in enumerate(fallback_providers, 1):
                print(f"  {i}. {fb.get('provider')} ({fb.get('model')})")
        
        return fallback_enabled
    
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False

def test_llm_generator():
    """Test if LLM generator can load."""
    print("\n" + "=" * 60)
    print("🤖 Testing LLM Generator")
    print("=" * 60)
    
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        from src.llm_generator import LLMGenerator
        
        generator = LLMGenerator(config)
        
        print(f"✓ LLM Generator initialized")
        print(f"  Primary provider: {generator.provider}")
        print(f"  Primary model: {generator.model}")
        print(f"  Fallback enabled: {generator.fallback_enabled}")
        
        if generator.fallback_enabled:
            print(f"  Fallback chain: {len(generator.fallback_providers)} provider(s)")
        
        return True
    
    except Exception as e:
        print(f"✗ Error loading LLM generator: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 Gemini Fallback System Test")
    print("=" * 60)
    print()
    
    results = {
        "SDK": test_gemini_sdk(),
        "API Key": test_api_key(),
        "Config": test_config(),
        "LLM Generator": test_llm_generator()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! System is ready.")
        print("=" * 60)
        print("\n💡 Next steps:")
        print("   1. Start server: python3 app.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Upload exit ticket and generate questions")
        print("   4. Watch terminal for fallback messages")
        return 0
    else:
        print("❌ Some tests failed. Check messages above.")
        print("=" * 60)
        print("\n💡 To fix:")
        print("   - Install SDK: pip3 install google-generativeai")
        print("   - Set API key: export GEMINI_API_KEY='your-key'")
        print("   - Check GEMINI_SETUP.md for detailed guide")
        return 1

if __name__ == "__main__":
    sys.exit(main())

