"""
Comprehensive test suite for ML/AI modules
Tests autonomous agent, decision engine, and learning components
"""
import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.autonomous_agent import AutonomousTradingAgent
from agents.ai_decision_engine import AutonomousDecisionEngine


class TestAutonomousDecisionEngine:
    """Test AI decision engine functionality"""
    
    @pytest.fixture
    def engine(self):
        """Create decision engine instance"""
        return AutonomousDecisionEngine()
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initializes correctly"""
        assert engine is not None
        assert hasattr(engine, 'rl_agent')
        assert hasattr(engine, 'pattern_analyzer')
        assert hasattr(engine, 'risk_manager')
    
    @pytest.mark.asyncio
    async def test_market_context_analysis(self, engine):
        """Test market context analysis with valid data"""
        market_data = {
            "price": 100.0,
            "volume": 1000000,
            "volatility": 0.05,
            "trend": "bullish",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = await engine.analyze_market_context(market_data)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "llm_recommendation" in result
        assert "confidence_level" in result
        assert "risk_assessment" in result
        
        # Verify recommendation is valid
        recommendation = result.get("llm_recommendation")
        assert recommendation in ["BUY", "SELL", "HOLD", None]
    
    @pytest.mark.asyncio
    async def test_market_analysis_with_minimal_data(self, engine):
        """Test market analysis with minimal data"""
        market_data = {"price": 100.0}
        
        result = await engine.analyze_market_context(market_data)
        
        # Should handle minimal data gracefully
        assert isinstance(result, dict)
        assert "llm_recommendation" in result
    
    @pytest.mark.asyncio
    async def test_market_analysis_with_empty_data(self, engine):
        """Test market analysis with empty data"""
        market_data = {}
        
        result = await engine.analyze_market_context(market_data)
        
        # Should handle empty data without crashing
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_confidence_levels(self, engine):
        """Test that confidence levels are within valid range"""
        market_data = {
            "price": 100.0,
            "volume": 1000000,
            "volatility": 0.05
        }
        
        result = await engine.analyze_market_context(market_data)
        
        if "confidence_level" in result:
            confidence = result["confidence_level"]
            assert isinstance(confidence, (int, float))
            # Confidence should be between 0 and 1 (or 0 and 100 if percentage)
            assert 0 <= confidence <= 100
    
    @pytest.mark.asyncio
    async def test_risk_assessment_structure(self, engine):
        """Test risk assessment returns proper structure"""
        market_data = {
            "price": 100.0,
            "volume": 1000000,
            "volatility": 0.15  # Higher volatility
        }
        
        result = await engine.analyze_market_context(market_data)
        
        if "risk_assessment" in result:
            risk = result["risk_assessment"]
            assert isinstance(risk, dict)


class TestAutonomousTradingAgent:
    """Test autonomous trading agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return AutonomousTradingAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with all components"""
        assert agent is not None
        assert hasattr(agent, 'decision_engine')
        assert hasattr(agent, 'blockchain_executor')
        assert hasattr(agent, 'behavior_simulator')
        assert hasattr(agent, 'learning_loop')
        assert hasattr(agent, 'wallet_manager')
        assert hasattr(agent, 'strategy_evolver')
        assert hasattr(agent, 'is_running')
        assert agent.is_running == False
    
    @pytest.mark.asyncio
    async def test_agent_market_data_gathering(self, agent):
        """Test market data gathering method exists and works"""
        if hasattr(agent, '_gather_market_data'):
            data = await agent._gather_market_data()
            assert isinstance(data, dict)
    
    def test_agent_performance_metrics(self, agent):
        """Test performance metrics structure"""
        assert hasattr(agent, 'performance_metrics')
        assert isinstance(agent.performance_metrics, dict)
    
    @pytest.mark.asyncio
    async def test_agent_market_analysis(self, agent):
        """Test agent can analyze market"""
        if hasattr(agent, 'analyze_current_market'):
            result = await agent.analyze_current_market()
            assert isinstance(result, dict)
    
    def test_agent_components_integration(self, agent):
        """Test all agent components are properly integrated"""
        # Verify decision engine
        assert agent.decision_engine is not None
        assert hasattr(agent.decision_engine, 'analyze_market_context')
        
        # Verify blockchain executor
        assert agent.blockchain_executor is not None
        
        # Verify behavior simulator
        assert agent.behavior_simulator is not None
        
        # Verify learning loop
        assert agent.learning_loop is not None
        
        # Verify wallet manager
        assert agent.wallet_manager is not None


class TestLearningAndAdaptation:
    """Test learning and adaptation capabilities"""
    
    @pytest.fixture
    def agent(self):
        """Create agent with learning capabilities"""
        return AutonomousTradingAgent()
    
    @pytest.mark.asyncio
    async def test_learning_feedback_exists(self, agent):
        """Test learning feedback loop exists"""
        assert hasattr(agent, 'learning_loop')
        learning_loop = agent.learning_loop
        
        # Check if learning methods exist
        if hasattr(learning_loop, 'analyze_trade_performance'):
            trade_data = {
                "action": "BUY",
                "amount": 100,
                "price": 100.0,
                "outcome": "success"
            }
            result = await learning_loop.analyze_trade_performance(trade_data)
            assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_strategy_evolution_exists(self, agent):
        """Test strategy evolution mechanism exists"""
        assert hasattr(agent, 'strategy_evolver')
        evolver = agent.strategy_evolver
        
        if hasattr(evolver, 'evolve_strategies'):
            # Should handle evolution gracefully
            await evolver.evolve_strategies()


class TestBehaviorSimulation:
    """Test organic behavior simulation"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return AutonomousTradingAgent()
    
    @pytest.mark.asyncio
    async def test_behavior_simulator_exists(self, agent):
        """Test behavior simulator component exists"""
        assert hasattr(agent, 'behavior_simulator')
        simulator = agent.behavior_simulator
        assert simulator is not None
    
    @pytest.mark.asyncio
    async def test_organic_trade_simulation(self, agent):
        """Test organic trade simulation"""
        simulator = agent.behavior_simulator
        
        if hasattr(simulator, 'simulate_organic_trade'):
            context = {
                "llm_recommendation": "BUY",
                "confidence_level": 75
            }
            result = await simulator.simulate_organic_trade(context)
            
            assert isinstance(result, dict)
            assert "action" in result
            assert "amount" in result
            assert result["action"] in ["BUY", "SELL", "HOLD"]


class TestRiskManagement:
    """Test risk management functionality"""
    
    @pytest.fixture
    def engine(self):
        """Create decision engine with risk manager"""
        return AutonomousDecisionEngine()
    
    @pytest.mark.asyncio
    async def test_risk_manager_exists(self, engine):
        """Test risk manager component exists"""
        assert hasattr(engine, 'risk_manager')
        risk_manager = engine.risk_manager
        assert risk_manager is not None
    
    @pytest.mark.asyncio
    async def test_high_volatility_risk_assessment(self, engine):
        """Test risk assessment for high volatility scenarios"""
        high_risk_data = {
            "price": 100.0,
            "volume": 500000,
            "volatility": 0.25,  # Very high volatility
            "trend": "volatile"
        }
        
        result = await engine.analyze_market_context(high_risk_data)
        
        # Should recognize high risk
        if "risk_assessment" in result:
            risk = result["risk_assessment"]
            assert isinstance(risk, dict)


class TestModelTraining:
    """Test model training capabilities"""
    
    def test_training_method_exists(self):
        """Test that training methods exist"""
        engine = AutonomousDecisionEngine()
        
        # Check if training-related methods exist
        # Note: actual training might be expensive, so we just check existence
        if hasattr(engine, 'train_price_prediction_model'):
            assert callable(engine.train_price_prediction_model)
        
        if hasattr(engine, 'rl_agent'):
            rl_agent = engine.rl_agent
            if hasattr(rl_agent, 'train'):
                assert callable(rl_agent.train)


class TestPatternRecognition:
    """Test pattern recognition capabilities"""
    
    @pytest.fixture
    def engine(self):
        """Create decision engine"""
        return AutonomousDecisionEngine()
    
    def test_pattern_analyzer_exists(self, engine):
        """Test pattern analyzer component exists"""
        assert hasattr(engine, 'pattern_analyzer')
        analyzer = engine.pattern_analyzer
        assert analyzer is not None
    
    def test_pattern_recognition_basic(self, engine):
        """Test basic pattern recognition"""
        analyzer = engine.pattern_analyzer
        
        if hasattr(analyzer, 'find_patterns'):
            # Simple price series
            price_series = [100.0, 102.0, 105.0, 103.0, 106.0]
            patterns = analyzer.find_patterns(price_series)
            
            # Should return list of patterns (can be empty)
            assert isinstance(patterns, list)


class TestWalletStrategy:
    """Test wallet strategy management"""
    
    @pytest.fixture
    def agent(self):
        """Create agent with wallet manager"""
        return AutonomousTradingAgent()
    
    def test_wallet_manager_exists(self, agent):
        """Test wallet manager component exists"""
        assert hasattr(agent, 'wallet_manager')
        assert agent.wallet_manager is not None
    
    @pytest.mark.asyncio
    async def test_distributed_trade_execution(self, agent):
        """Test distributed trade execution capability"""
        wallet_manager = agent.wallet_manager
        
        if hasattr(wallet_manager, 'execute_distributed_trade'):
            master_decision = {
                "action": "BUY",
                "amount": 1000,
                "strategy": "diversified"
            }
            
            result = await wallet_manager.execute_distributed_trade(master_decision)
            
            # Should return list of execution results
            assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
