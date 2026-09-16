# AI Use Cases in Financial Services

## Purpose

This document identifies high-value applications of Artificial Intelligence,
Generative AI, Large Language Models (LLMs), Retrieval-Augmented Generation
(RAG), and AI Agents across financial services.

The objective is to identify opportunities where AI can improve:

- Credit decisioning
- Risk management
- Portfolio management
- Fraud detection and investigation
- Financial analysis
- Regulatory compliance
- Model risk management
- Operational efficiency
- Customer experience
- Financial decision intelligence

The use cases will serve as the foundation for the AI Financial Risk Lab.

# 1. Credit Underwriting

## Business Problem

Traditional underwriting requires analysts to collect, interpret, validate,
and synthesize information from multiple sources.

This may include:

- Credit bureau data
- Financial statements
- Bank transaction data
- Income information
- Business information
- Industry information
- Existing debt
- Payment history
- Fraud indicators
- Internal risk models
- Credit policy

The process can be time-consuming and inconsistent when large volumes of
applications require human review.

## AI Opportunity

AI can assist underwriting by collecting and organizing information,
identifying risk factors, retrieving relevant credit policies, explaining
risk-model outputs, identifying missing information, and preparing an
underwriting recommendation for human review.

## Potential AI Capabilities

- Applicant information extraction
- Financial statement analysis
- Bank transaction analysis
- Credit policy retrieval
- Risk-factor identification
- Credit memo generation
- Policy exception identification
- Missing-information detection
- Risk segmentation
- Human-in-the-loop decision support

## Potential Agent Tools

The future AI underwriting agent could use tools such as:

- get_applicant_data()
- get_credit_bureau_data()
- calculate_dti()
- calculate_utilization()
- calculate_pd()
- calculate_expected_loss()
- check_credit_policy()
- evaluate_policy_exception()
- calculate_recommended_limit()
- generate_credit_memo()

## Human Decision

The AI system should initially operate as a decision-support system.

A qualified credit officer or other authorized human decision maker remains
responsible for the final credit decision.

## Key Risks

- Hallucination
- Incorrect policy interpretation
- Data quality problems
- Model risk
- Bias and fair-lending concerns
- Unauthorized decisioning
- Data leakage
- Privacy concerns
- Inadequate audit trails

## Governance Requirements

The system should support:

- Human-in-the-loop review
- Audit logging
- Explainability
- Model validation
- Data lineage
- Policy version control
- Performance monitoring
- AI evaluation
- Access controls
- Change management

# 2. Credit Policy Interpretation

## Business Problem

Credit policies can contain numerous rules, thresholds, exceptions,
definitions, documentation requirements, and approval authorities.

Analysts may need to search multiple policy documents to determine which
rules apply to a particular application.

## AI Opportunity

A Retrieval-Augmented Generation (RAG) system can retrieve the relevant
sections of credit policy and provide an explanation grounded in approved
policy documents.

## Example Questions

The system could answer questions such as:

- What is the minimum credit score requirement?
- What is the maximum allowable DTI?
- What documentation is required?
- What is the maximum credit limit?
- Who can approve a policy exception?
- What conditions apply to a thin-file applicant?
- Which policy version is currently effective?

## AI Capabilities

- Document retrieval
- Semantic search
- Policy classification
- Policy interpretation
- Citation of source documents
- Effective-date identification
- Exception identification

## Key Risks

- Hallucinated policy
- Outdated policy
- Incorrect retrieval
- Incorrect interpretation
- Missing policy exceptions
- Failure to identify policy hierarchy

## Governance Requirements

The system should provide:

- Source citations
- Policy version
- Effective date
- Retrieval trace
- Confidence/evaluation metrics
- Human review for material decisions

# 3. Credit Committee Analysis

## Business Problem

Credit committees often review large amounts of information before making
material lending decisions.

## AI Opportunity

An AI assistant can organize information and prepare a structured credit
committee package.

## Potential Outputs

- Executive summary
- Borrower overview
- Financial analysis
- Credit risk assessment
- PD
- Expected loss
- Exposure
- Collateral
- Policy compliance
- Exceptions
- Key risks
- Mitigants
- Recommended conditions
- Questions for the committee

## Human Decision

The AI prepares analysis and recommendations.

The credit committee retains decision authority.

## Key Risks

- Incorrect financial interpretation
- Hallucination
- Unsupported recommendations
- Missing adverse information
- Excessive automation

## Governance Requirements

Every material recommendation should be traceable to:

1. Source data
2. Applicable policy
3. Analytical calculation
4. Model output
5. AI-generated reasoning
6. Human approval

# 4. SMB Underwriting
## Business Problem

Traditional underwriting requires analysts to collect, interpret, validate,
and synthesize information from multiple sources.

This may include:
business financial statements
bank transactions
business bureau
owner bureau
cash flow
industry
fraud
KYB
debt obligations
PD
exposure
credit limit
pricing
expected loss
## AI Opportunity

AI can assist underwriting by collecting and organizing information,
identifying risk factors, retrieving relevant credit policies, explaining
risk-model outputs, identifying missing information, and preparing an
underwriting recommendation for human review.

## Potential AI Capabilities

- Applicant information extraction
- Financial statement analysis
- Bank transaction analysis
- Credit policy retrieval
- Risk-factor identification
- Credit memo generation
- Policy exception identification
- Missing-information detection
- Risk segmentation
- Human-in-the-loop decision support

# 5. Portfolio Risk Monitoring
The future agent could monitor:
Delinquency
Roll Rates
Vintage Performance
Loss Rates
Utilization
Approval Rates
Policy Changes
Risk Segments
Early Warning Signals

The agent could answer:

"Why did 2026 Q2 losses increase?"

and investigate:

vintage
product
risk tier
geography
acquisition channel
underwriting policy
pricing
utilization
delinquency
customer segment

# 6. Fraud Investigation
Document:

transaction analysis
customer behavior
device information
merchant information
geography
velocity
prior cases
fraud scores
suspicious patterns
investigator case summary
Eventually:

Transactions
      ↓
Fraud Models
      ↓
Rules
      ↓
Customer History
      ↓
AI Investigation Agent
      ↓
Case Summary
      ↓
Human Investigator

# 7. Collections Strategy
The AI system could analyze:

delinquency
customer segment
payment behavior
balance
probability of cure
historical treatment response
contact history

Then recommend:

treatment strategy
contact channel
timing
payment plan
escalation

# 8. CCECL / Expected Loss
Document AI capabilities around:

PD
LGD
EAD
expected loss
Markov migration
delinquency transitions
macroeconomic scenarios
qualitative adjustments
segmentation
forecast analysis
model documentation
management overlays

Eventually you'll build:

AI CECL Agent

# 9. Model Risk Management
he AI system could review:

Model Documentation
        ↓
Development Evidence
        ↓
Validation Report
        ↓
Performance Metrics
        ↓
Monitoring
        ↓
Model Inventory
        ↓
Policy Requirements
        ↓
SR 11-7 Requirements
        ↓
AI Governance Agent

It could identify:

missing documentation
methodology inconsistencies
weak validation
missing monitoring
model limitations
unsupported assumptions
governance gaps

# 10. Regulatory / Compliance Analysis
Potential applications:

regulatory document retrieval
policy comparison
regulatory change monitoring
compliance impact analysis
control mapping
issue identification
regulatory response preparation

Again, human compliance/legal oversight remains critical.

# 11. AI Capability Maps

The financial-services use cases above can be organized into several
technology capabilities.

| Capability | Example |
|---|---|
| LLM | Generate credit-risk summaries |
| Prompting | Analyze borrower information |
| Structured Output | Produce standardized risk assessment |
| RAG | Retrieve credit policies |
| Tool Calling | Execute risk calculations |
| AI Agent | Perform multi-step underwriting analysis |
| Machine Learning | Predict probability of default |
| Data Analytics | Analyze portfolio performance |
| Workflow Orchestration | Coordinate underwriting steps |
| Human-in-the-Loop | Require human approval |
| Evaluation | Measure AI accuracy |
| Governance | Control AI risk |
| Observability | Monitor agent behavior |

# 12. AI Financial Risk Architecture

The long-term objective is to develop an AI-enabled financial risk
decision platform.

The conceptual architecture is:

Data
  ↓
Data Quality
  ↓
Risk Models
  ↓
Policy
  ↓
RAG / Knowledge Layer
  ↓
AI Agent
  ↓
Tools
  ↓
Decision Intelligence
  ↓
Human Review
  ↓
Action
  ↓
Monitoring
  ↓
Governance

The AI system should augment financial professionals rather than
initially replace them.

The architecture should prioritize:

- Accuracy
- Explainability
- Auditability
- Security
- Human oversight
- Data governance
- Model governance
- AI governance
- Reproducibility
- Monitoring

# Day 1 Knowledge Check

## Question 1
What is the difference between an LLM and an AI agent?
A Large Language Model (LLM) is a text-generating AI engine, while an AI agent is an autonomous system that uses an LLM as its "brain" to plan, use tools, and execute multi-step tasks in a loop

## Question 2
Why would a bank use RAG instead of simply asking an LLM about its
credit policy?
A bank uses Retrieval-Augmented Generation (RAG) instead of a standard Large Language Model (LLM) because RAG provides accurate, up-to-date, and verifiable answers from internal documents while preventing costly hallucinations

## Question 3
What is tool calling?