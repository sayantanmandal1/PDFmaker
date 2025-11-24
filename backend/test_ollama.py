"""
Quick test to verify Ollama integration with Qwen model.
"""
from services.llm_service import LLMService

def test_ollama_connection():
    """Test that Ollama is working with Qwen model."""
    print("🧪 Testing Ollama connection with Qwen model...")
    
    try:
        llm = LLMService()
        print(f"✅ LLM Service initialized")
        print(f"📝 Model: {llm.model}")
        print(f"🌐 Base URL: {llm.client.base_url}")
        
        # Test a simple generation
        print("\n🔄 Testing content generation...")
        result = llm.generate_section_content(
            topic="Artificial Intelligence",
            section_header="Introduction",
            context="Brief overview for a business document"
        )
        
        print("\n✅ Generation successful!")
        print(f"\n📄 Generated content:\n{result}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

if __name__ == "__main__":
    test_ollama_connection()
