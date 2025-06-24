import streamlit as st
import requests
import time
import json
import httpx
import asyncio
from typing import Dict, Any
from pydantic import BaseModel

st.set_page_config(page_title="Gaia PRD Generator", page_icon="🤖")
st.markdown("""<style>.main .block-container { max-width: 1280px; }</style>""", unsafe_allow_html=True)

class PRDRequest(BaseModel):
    product_idea: str
    target_audience: str = ""
    timeline: str = ""
    budget_range: str = ""

class AgentResponse(BaseModel):
    analysis: str

class PRDResponse(BaseModel):
    prd: str
    dev_prompt: str
    elon_analysis: str = ""
    warren_analysis: str = ""
    peter_analysis: str = ""
    steve_analysis: str = ""

class GaiaAgent:
    def __init__(self, name: str, url: str, perspective: str):
        self.name = name
        self.url = url
        self.perspective = perspective

    async def analyze(self, product_idea: str) -> str:
        prompt = f"""You are {self.name} analyzing a product idea.

Product Idea: "{product_idea}"

Your expertise: {self.perspective}

Provide analysis covering:
1. Key opportunities and challenges
2. Strategic recommendations
3. Important considerations
4. Success factors

Keep response focused and actionable (300-400 words). Think from your unique perspective.

Respond in plain text, not JSON."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "stream": False
                    },
                    timeout=60.0
                )
                
                response_text = response.text
                
                # Handle both JSON and plain text responses
                try:
                    data = json.loads(response_text)
                    if 'choices' in data and data['choices']:
                        return data['choices'][0]['message']['content']
                    else:
                        return response_text
                except json.JSONDecodeError:
                    return response_text
                    
        except Exception as e:
            return f"Analysis from {self.name}: Due to technical issues, unable to provide detailed analysis. However, {product_idea} shows potential and should be evaluated further."

# ===== AGENT DEFINITIONS =====
agents = {
    "elon": GaiaAgent(
        "Elon Musk", 
        "https://0xf3402fdc5684b8cd331b09a37caa176ce7efb686.gaia.domains/v1/chat/completions",
        "Innovation, scaling, and disruptive technology"
    ),
    "warren": GaiaAgent(
        "Warren Buffet",
        "https://0xfd0ca669e92e705d337f05d8f5f12c4d0b9dfb9d.gaia.domains/v1/chat/completions", 
        "Business fundamentals and long-term value"
    ),
    "peter": GaiaAgent(
        "Peter Thiel",
        "https://0x7a967b4b6b1f82c6d3a4a53d2e28eae596d8d6d9.gaia.domains/v1/chat/completions",
        "Zero-to-one innovation and monopoly strategy"
    ),
    "steve": GaiaAgent(
        "Steve Jobs",
        "https://0x30650e408f4e4307cbda0a12070aaacd8f2d743f.gaia.domains/v1/chat/completions",
        "Design excellence and user experience"
    )
}

async def generate_prd(request: PRDRequest, selected_agents: Dict[str, bool]) -> PRDResponse:
    """Generate PRD by calling selected agents"""
    
    # Call only selected advisory agents
    results = {}
    tasks = []
    
    for agent_key, selected in selected_agents.items():
        if selected and agent_key in agents:
            tasks.append((agent_key, agents[agent_key].analyze(request.product_idea)))
    
    # Run all agent calls concurrently
    if tasks:
        agent_results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        for i, (agent_key, _) in enumerate(tasks):
            result = agent_results[i]
            if isinstance(result, Exception):
                results[agent_key] = f"Unable to get analysis from {agents[agent_key].name} AI"
            else:
                results[agent_key] = result
    
    # Count selected advisors
    selected_count = sum(selected_agents.values())
    advisor_names = []
    if selected_agents.get('elon'): advisor_names.append("Elon Musk")
    if selected_agents.get('warren'): advisor_names.append("Warren Buffet") 
    if selected_agents.get('peter'): advisor_names.append("Peter Thiel")
    if selected_agents.get('steve'): advisor_names.append("Steve Jobs")
    
    advisor_list = ", ".join(advisor_names[:-1]) + f" and {advisor_names[-1]}" if len(advisor_names) > 1 else advisor_names[0] if advisor_names else "No advisors"
    
    # Generate dynamic advisory panel section
    advisory_sections = []
    
    if selected_agents.get('elon') and 'elon' in results:
        advisory_sections.append(f"""### 🚀 Innovation & Scaling Perspective (Elon Musk)
{results['elon']}""")
    
    if selected_agents.get('warren') and 'warren' in results:
        advisory_sections.append(f"""### 💰 Business Fundamentals Perspective (Warren Buffet)
{results['warren']}""")
    
    if selected_agents.get('peter') and 'peter' in results:
        advisory_sections.append(f"""### 🎯 Strategic Monopoly Perspective (Peter Thiel)
{results['peter']}""")
    
    if selected_agents.get('steve') and 'steve' in results:
        advisory_sections.append(f"""### 🎨 Design Excellence Perspective (Steve Jobs)
{results['steve']}""")
    
    # Generate comprehensive PRD
    prd_content = f"""# Product Requirements Document (PRD)

**Product:** {request.product_idea}
**Target Audience:** {request.target_audience}
**Timeline:** {request.timeline}
**Budget Range:** {request.budget_range}
**Date:** {time.strftime('%Y-%m-%d')}
**Advisory Panel:** {advisor_list} ({selected_count} advisor{"s" if selected_count != 1 else ""})

## Executive Summary
This PRD synthesizes insights from {selected_count} legendary business perspective{"s" if selected_count != 1 else ""} to provide comprehensive product guidance.

## Advisory Panel Analysis

{chr(10).join(advisory_sections) if advisory_sections else "No advisory analysis available."}

## Synthesis & Recommendations

**Core Value Proposition:** Focus on solving a real user problem with elegant simplicity while building defensible competitive advantages.

**Technical Strategy:** Build scalable foundation with modern architecture, emphasizing user experience and rapid iteration capabilities.

**Business Model:** Develop sustainable revenue streams based on strong unit economics and customer retention.

**Market Approach:** Target early adopters, validate product-market fit, then scale with disciplined growth strategy.

## Product Specifications

**Target Users:** {request.target_audience}
**Development Timeline:** {request.timeline}
**Budget Allocation:** {request.budget_range}

## Next Steps
1. Validate core assumptions with target users
2. Build MVP focusing on primary value proposition  
3. Iterate based on user feedback and data
4. Scale with proven product-market fit

---
*Generated by Gaia Multi-Agent System with {selected_count} AI advisor{"s" if selected_count != 1 else ""}*"""

    dev_prompt = f"""# Development Prompt for {request.product_idea}

**Target Audience:** {request.target_audience}
**Timeline:** {request.timeline}
**Budget:** {request.budget_range}

Based on analysis from {advisor_list}, build a production-ready web application with these priorities:

## Core Requirements
- **User-Centric Design:** Tailored for {request.target_audience}
- **Timeline Considerations:** Deliverable within {request.timeline}
- **Budget Optimization:** Efficient development within {request.budget_range}

## Technical Implementation
Use React/Next.js + TypeScript + Tailwind CSS with:
- User authentication (Auth0/Supabase)
- Responsive design (mobile-first)
- Real-time features where appropriate
- Analytics and user tracking
- SEO optimization
- Accessibility compliance

## Key Features
1. Compelling landing page with clear value prop for {request.target_audience}
2. Streamlined user onboarding
3. Core functionality solving main user problem
4. Clean dashboard with actionable insights
5. Account management and settings
6. Mobile app-like experience

## Success Metrics
- User engagement and retention
- Conversion rates and revenue per user
- Performance metrics (Core Web Vitals)
- Customer satisfaction scores

Build something {request.target_audience} will love, that scales efficiently, and creates lasting value.

*Optimized for v0.dev, bolt.new, lovable.dev*
*Advisory insights from: {advisor_list}*"""

    return PRDResponse(
        prd=prd_content,
        dev_prompt=dev_prompt,
        elon_analysis=results.get('elon', '') if selected_agents.get('elon') else '',
        warren_analysis=results.get('warren', '') if selected_agents.get('warren') else '',
        peter_analysis=results.get('peter', '') if selected_agents.get('peter') else '',
        steve_analysis=results.get('steve', '') if selected_agents.get('steve') else ''
    )

st.title("🤖 Gaia Multi-Agent PRD Generator")
st.markdown("Get product insights from AI versions of legendary entrepreneurs")

st.sidebar.header("🤖 Advisory Panel Selection")
st.sidebar.markdown("Choose which AI advisors to consult:")

agent_configs = {
    "elon": {"name": "🚀 Elon Musk AI", "desc": "Innovation & Scaling", "port": 8001},
    "warren": {"name": "💰 Warren Buffet AI", "desc": "Business Fundamentals", "port": 8002},
    "peter": {"name": "🎯 Peter Thiel AI", "desc": "Strategy & Monopoly", "port": 8003},
    "steve": {"name": "🎨 Steve Jobs AI", "desc": "Design & Experience", "port": 8004}
}

selected_agents = {}
for key, config in agent_configs.items():
    selected_agents[key] = st.sidebar.checkbox(
        f"{config['name']}", 
        value=True, 
        help=f"Expertise: {config['desc']}"
    )

with st.sidebar:
    st.markdown("### 📚 Tips for Better Results")
    st.markdown("""
    **For the best PRD analysis:**
    - Be specific about your product's core functionality
    - Clearly define the problem you're solving
    - Include your target market and user personas
    - Mention any unique competitive advantages
    - Specify technical requirements or constraints
    
    **Using the Advisory Panel:**
    - **Elon Musk AI**: Best for innovative, scalable, tech-forward products
    - **Warren Buffet AI**: Focus on business fundamentals and long-term viability
    - **Peter Thiel AI**: Strategic insights for competitive differentiation
    - **Steve Jobs AI**: User experience and design excellence
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("**Built by [Harish Kotra](https://tini.ltd/hk) from Gaia** 🚀")

st.markdown("### Selected Advisory Panel:")
cols = st.columns(4)
for i, (key, config) in enumerate(agent_configs.items()):
    with cols[i]:
        if selected_agents[key]:
            st.markdown(f"**{config['name']}**\n\n{config['desc']}")
        else:
            st.markdown(f"~~**{config['name']}**~~\n*Disabled*")

st.subheader("💡 Example Prompts")
st.markdown("Click any example to auto-fill the product idea field:")

examples = [
    "A social media app for pet owners to share photos, get veterinary advice, and connect with local pet services and other pet owners in their area",
    "An AI-powered fitness coach that provides personalized workout plans, tracks progress with computer vision, and adapts routines based on user feedback and biometric data", 
    "A sustainable food delivery platform that connects consumers directly with local farms, reduces food waste through dynamic pricing, and uses electric vehicles for delivery",
    "A VR collaboration tool for remote teams featuring spatial computing, realistic avatars, interactive whiteboards, and seamless integration with existing productivity tools",
    "A personal finance app that uses AI to analyze spending patterns, automatically optimize investments, provide tax advice, and help users achieve specific financial goals"
]

cols = st.columns(2)
for i, example in enumerate(examples):
    with cols[i % 2]:
        if st.button(f"🎯 {example[:50]}{'...' if len(example) > 50 else ''}", key=f"example_{i+1}"):
            st.session_state.product_idea = example
            st.rerun()

st.markdown("---")

# Initialize session state for form fields
if 'product_idea' not in st.session_state:
    st.session_state.product_idea = ""
if 'target_audience' not in st.session_state:
    st.session_state.target_audience = "General consumers aged 25-45"
if 'timeline' not in st.session_state:
    st.session_state.timeline = "6-12 months MVP"
if 'prd_generated' not in st.session_state:
    st.session_state.prd_generated = False
if 'response_data' not in st.session_state:
    st.session_state.response_data = None

# Input form
with st.form("prd_form"):
    st.markdown("### Product Details")
    
    product_idea = st.text_area(
        "Product Idea", 
        value=st.session_state.product_idea,
        placeholder="Describe your product idea in detail...",
        height=120,
        help="💡 Describe what your product does, who it serves, and what problem it solves. Be specific about key features and benefits."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        target_audience = st.text_input(
            "Target Audience", 
            value=st.session_state.target_audience,
            help="👥 Who are your primary users? Include demographics, behaviors, and characteristics of your ideal customers."
        )
    with col2:
        timeline = st.text_input(
            "Timeline", 
            value=st.session_state.timeline,
            help="⏱️ What's your development timeline? Include key milestones like MVP, beta, and launch dates."
        )
    
    budget_range = st.selectbox(
        "Budget Range",
        ["$10K - $50K", "$50K - $100K", "$100K - $500K", "$500K - $1M", "$1M+", "Bootstrapped", "Seeking Investment"],
        index=1,
        help="💰 What's your available budget for development, marketing, and operations?"
    )
    
    submitted = st.form_submit_button("Generate PRD with Selected Advisory Panel ✨")

if submitted and product_idea:
    # Count selected agents
    selected_count = sum(selected_agents.values())
    if selected_count == 0:
        st.error("Please select at least one advisor from the sidebar!")
    else:
        with st.spinner(f"Consulting {selected_count} advisor(s) (this may take 1-2 minutes)..."):
            try:
                # Create Pydantic request object
                prd_request = PRDRequest(
                    product_idea=product_idea,
                    target_audience=target_audience,
                    timeline=timeline,
                    budget_range=budget_range
                )
                
                # Generate PRD using async function with Pydantic models
                response: PRDResponse = asyncio.run(generate_prd(prd_request, selected_agents))
                
                # Convert Pydantic model to dict for session state
                st.session_state.response_data = response.model_dump()
                st.session_state.prd_generated = True
                st.session_state.product_idea = product_idea
                st.session_state.target_audience = target_audience
                st.session_state.timeline = timeline
                
            except Exception as e:
                st.error(f"Error generating PRD: {e}")

elif submitted and not product_idea:
    st.warning("Please enter a product idea to get started!")

# Display results if available
if st.session_state.prd_generated and st.session_state.response_data:
    data = st.session_state.response_data
    
    # Display PRD with download options
    st.subheader("📋 Product Requirements Document")
    
    prd_content = data.get("prd", "No PRD generated")
    
    # PRD download/copy options
    col1, col2 = st.columns([3, 1])
    with col2:
        # Download PRD as markdown file
        st.download_button(
            label="📥 Download PRD",
            data=prd_content,
            file_name=f"PRD_{st.session_state.product_idea.replace(' ', '_')[:30]}.md",
            mime="text/markdown"
        )
    
    with col1:
        st.markdown(prd_content)
    
    # Show PRD content in expandable text area for easy copying
    with st.expander("📋 Copy PRD Content (Click to expand, then Ctrl+A to select all)"):
        st.text_area(
            "PRD Content for Copying:",
            value=prd_content,
            height=300,
            help="Click in this text area, then use Ctrl+A to select all and Ctrl+C to copy"
        )
    
    # Display Development Prompt with enhanced content and copy options  
    st.subheader("⚡ Development Prompt for AI Platforms")
    
    # Enhanced dev prompt with AI insights
    ai_insights = ""
    
    if selected_agents.get("elon") and data.get("elon_analysis"):
        ai_insights += f"""**🚀 Innovation Perspective (Elon Musk):**
{data.get("elon_analysis", "")[:500]}...

"""
    
    if selected_agents.get("warren") and data.get("warren_analysis"):
        ai_insights += f"""**💰 Business Perspective (Warren Buffet):**
{data.get("warren_analysis", "")[:500]}...

"""
    
    if selected_agents.get("peter") and data.get("peter_analysis"):
        ai_insights += f"""**🎯 Strategic Perspective (Peter Thiel):**
{data.get("peter_analysis", "")[:500]}...

"""
    
    if selected_agents.get("steve") and data.get("steve_analysis"):
        ai_insights += f"""**🎨 Design Perspective (Steve Jobs):**
{data.get("steve_analysis", "")[:500]}...

"""
    
    enhanced_dev_prompt = data.get("dev_prompt", "") + f"""

## AI Advisory Insights for Implementation

{ai_insights}
## Implementation Priority
1. Start with core functionality that delivers immediate value
2. Focus on user experience and interface design
3. Build scalable architecture from day one
4. Implement analytics to track key metrics
5. Plan for iterative improvements based on user feedback

**Copy this entire prompt and paste it into v0.dev, bolt.new, or lovable.dev for best results.**"""
    
    # Dev prompt copy options
    col1, col2 = st.columns([3, 1])
    with col2:
        # Download enhanced dev prompt
        st.download_button(
            label="📥 Download Prompt",
            data=enhanced_dev_prompt,
            file_name=f"DevPrompt_{st.session_state.product_idea.replace(' ', '_')[:30]}.md",
            mime="text/markdown"
        )
    
    with col1:
        st.code(enhanced_dev_prompt, language="markdown")
    
    # Show dev prompt in expandable text area for easy copying
    with st.expander("📋 Copy Development Prompt (Click to expand, then Ctrl+A to select all)"):
        st.text_area(
            "Development Prompt for Copying:",
            value=enhanced_dev_prompt,
            height=400,
            help="Click in this text area, then use Ctrl+A to select all and Ctrl+C to copy"
        )
    
    st.info("💡 **Tip:** Use the expandable text areas above to easily copy the PRD or development prompt. Click to expand, then Ctrl+A to select all and Ctrl+C to copy!")
    
    # Individual analyses in expanders (only for selected agents)
    if selected_agents.get("elon") and data.get("elon_analysis"):
        with st.expander("🚀 Elon Musk's Innovation Analysis"):
            st.markdown(data.get("elon_analysis"))
    
    if selected_agents.get("warren") and data.get("warren_analysis"):
        with st.expander("💰 Warren Buffet's Business Analysis"):
            st.markdown(data.get("warren_analysis"))
    
    if selected_agents.get("peter") and data.get("peter_analysis"):
        with st.expander("🎯 Peter Thiel's Strategic Analysis"):
            st.markdown(data.get("peter_analysis"))
    
    if selected_agents.get("steve") and data.get("steve_analysis"):
        with st.expander("🎨 Steve Jobs' Design Analysis"):
            st.markdown(data.get("steve_analysis"))