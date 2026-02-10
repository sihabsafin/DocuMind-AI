"""
LLM Manager - Handles model initialization and routing
Supports Groq (Gemma-2, LLaMA-3) and Ollama (local models)
"""
from typing import Optional, Dict, Any
from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
from langchain.callbacks import StreamingStdOutCallbackHandler

from config.settings import settings, MODEL_CONFIGS


class LLMManager:
    """Manages LLM instances and model routing"""
    
    def __init__(self):
        self.groq_api_key = settings.groq_api_key
        self.models_cache = {}
    
    def get_model(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        streaming: bool = False
    ):
        """
        Get an LLM instance
        
        Args:
            model_name: Name of the model (uses default if None)
            temperature: Model temperature (0.0 - 1.0)
            streaming: Enable streaming output
        
        Returns:
            LangChain LLM instance
        """
        if model_name is None:
            model_name = settings.default_model
        
        # Check cache
        cache_key = f"{model_name}_{temperature}_{streaming}"
        if cache_key in self.models_cache:
            return self.models_cache[cache_key]
        
        # Get model config
        config = MODEL_CONFIGS.get(model_name)
        if not config:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Initialize based on provider
        if config['provider'] == 'groq':
            model = self._get_groq_model(model_name, temperature, streaming)
        elif config['provider'] == 'ollama':
            model = self._get_ollama_model(model_name, temperature, streaming)
        else:
            raise ValueError(f"Unknown provider: {config['provider']}")
        
        # Cache the model
        self.models_cache[cache_key] = model
        return model
    
    def _get_groq_model(
        self,
        model_name: str,
        temperature: float,
        streaming: bool
    ) -> ChatGroq:
        """Initialize a Groq model"""
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else None
        
        return ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name=model_name,
            temperature=temperature,
            streaming=streaming,
            callbacks=callbacks,
            max_tokens=None  # Let model decide
        )
    
    def _get_ollama_model(
        self,
        model_name: str,
        temperature: float,
        streaming: bool
    ) -> Ollama:
        """Initialize an Ollama model"""
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else None
        
        return Ollama(
            base_url=settings.ollama_base_url,
            model=model_name,
            temperature=temperature,
            callbacks=callbacks
        )
    
    def get_fast_model(self, **kwargs):
        """Get the fastest available model"""
        return self.get_model(settings.fast_model, **kwargs)
    
    def get_default_model(self, **kwargs):
        """Get the default model"""
        return self.get_model(settings.default_model, **kwargs)
    
    def get_premium_model(self, **kwargs):
        """Get the premium (highest quality) model"""
        return self.get_model(settings.premium_model, **kwargs)
    
    def get_model_for_task(self, task_type: str, **kwargs):
        """
        Get appropriate model based on task type
        
        Task types:
        - quick_summary: Fast model for initial summaries
        - detailed_summary: Default model for detailed work
        - premium_summary: Premium model for executive summaries
        - refinement: Premium model for refinement passes
        """
        task_model_mapping = {
            'quick_summary': settings.fast_model,
            'detailed_summary': settings.default_model,
            'premium_summary': settings.premium_model,
            'refinement': settings.premium_model,
        }
        
        model_name = task_model_mapping.get(task_type, settings.default_model)
        return self.get_model(model_name, **kwargs)
    
    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a model call
        
        Note: Groq models are currently free, but this is here for future paid tiers
        """
        config = MODEL_CONFIGS.get(model_name)
        if config and config['cost'] == 'free':
            return 0.0
        
        # Placeholder for future pricing
        # pricing = {
        #     'input': 0.0001,  # per token
        #     'output': 0.0002
        # }
        # return (input_tokens * pricing['input']) + (output_tokens * pricing['output'])
        
        return 0.0
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a model"""
        if model_name is None:
            model_name = settings.default_model
        
        config = MODEL_CONFIGS.get(model_name)
        if not config:
            raise ValueError(f"Unknown model: {model_name}")
        
        return {
            'name': model_name,
            'provider': config['provider'],
            'context_window': config['context_window'],
            'speed': config['speed'],
            'quality': config['quality'],
            'cost': config['cost']
        }
    
    def list_available_models(self) -> Dict[str, Dict]:
        """List all available models and their configurations"""
        return MODEL_CONFIGS.copy()
    
    def clear_cache(self):
        """Clear the model cache"""
        self.models_cache.clear()


# Global LLM manager instance
llm_manager = LLMManager()
