# Dime Product Discovery Session Results

**Date**: 2025-01-30  
**Status**: Discovery Complete - Ready for Strategic Questions  
**Conducted by**: Product-Manager-Analyst Agent

## Project Overview

**Vision**: Content creation system specifically for Acts of Defiance, built with generalizable architecture that can be adapted for other organizations by changing prompts.

**Key Insight**: "Most content production pipelines are similar" - building for reusability across domains.

## Complete Workflow Specification

### Phase 1: Human Input
1. **Topic Selection**: Human-driven decision making
2. **Research Document**: Human-created markdown with footnote citations
3. **Input Methods**: 
   - Direct paste into conversation
   - Google Docs import
   - File system pickup

### Phase 2: AI Agent Pipeline

#### 1. Fact Checker Agent
- **Input**: Research markdown document with footnotes
- **Process**: Validates three aspects with 1-10 scoring:
  - Source credibility verification
  - Bias assessment 
  - Claim verification against sources
- **Output**: Separate markdown report with detailed analysis and scores
- **Quality Gate**: Articles with average score <5 flagged for human review
- **Integration**: Scores influence Writer agent's source prioritization

#### 2. Writer Agent
- **Input**: Original research + fact-checking report
- **Content Requirements**:
  - Length: 5-10 paragraphs
  - Tone: Casual, hip, intelligent
  - Target Audience: 25-40 year olds, educated but not politics junkies
  - Strategy: Prioritizes high-credibility sources, downplays low-scoring ones
- **Citation Format**: References back to research document title and links
- **Output**: Article draft in markdown

#### 3. Editor Agent
- **Input**: Writer's article draft + fact-checking report
- **Functions**:
  - Style consistency enforcement (casual/hip/intelligent tone)
  - Fact-checking validation (double-check citations match claims)
  - Readability optimization for target audience
  - Citation formatting standardization
- **Output**: Polished article ready for graphics

#### 4. Graphics Agent
- **Input**: Final article content
- **Process**: Agent + Human interaction required
- **Outputs**:
  - Large header/feature image for article
  - Thumbnail version of header image
- **Integration**: Image references included in final document

#### 5. Document Assembly Agent
- **Input**: All previous outputs (research, article, fact-check report, images)
- **Output**: Single markdown document containing:
  - Frontmatter metadata (YAML/TOML format)
  - Original research document
  - Final polished article
  - Image references/paths
  - Fact-checking summary and scores
- **Structure**: Template-based (to be developed later)

## Technical Specifications Discovered

### Input Format Requirements
- **Research Format**: Markdown with footnote citations `[^1]`
- **Footnote Content**: Whatever information comes in original document (flexible)
- **Citation Style**: `[^1]: Source information` at document bottom

### Quality Thresholds
- **Fact-Check Threshold**: Average score below 5/10 triggers human review
- **Scoring Metrics**: Each rated 1-10 (1=worst, 10=best)
  - Source credibility
  - Bias level 
  - Claim verification accuracy

### Agent Communication
- **Flow**: Linear pipeline with structured handoffs
- **Data Format**: Markdown documents with structured metadata
- **Quality Gates**: Human review triggered by fact-check scores
- **Error Handling**: Human review required for low-scoring content

## Key Design Decisions Made

1. **Architecture**: Generalizable agent system with configurable prompts
2. **Input Flexibility**: Multiple input methods (paste/Google Docs/file system)
3. **Quality Control**: Automated fact-checking with human oversight
4. **Output Format**: Single consolidated markdown document
5. **Human Touchpoints**: Topic selection, research creation, low-score review, graphics approval

## Strategic Questions for Next Session

### Error Handling & Recovery
- What happens if an agent fails mid-pipeline?
- Should there be ability to re-run individual agents?
- Do you need versioning for iterations?

### Performance & Scale
- Expected volume of articles per day/week?
- Acceptable processing time per article?
- Will agents run in parallel where possible or strictly sequential?

### Human Oversight & Control
- Beyond the fact-check threshold, any other automatic flags needed?
- Should humans be able to override agent decisions?
- Need for audit trail of agent actions/decisions?

### Integration Considerations
- Any existing systems this needs to integrate with?
- Publishing platforms or CMS requirements?
- Analytics or monitoring needs?

### Content Management
- How will you handle article updates/revisions?
- Archive or version control requirements?
- Metadata standards or SEO requirements for frontmatter?

## Next Steps

1. **Strategic Questions Session**: Address remaining questions above
2. **Technical Specification**: Define detailed agent requirements and APIs
3. **Architecture Design**: System design with component interactions
4. **Implementation Planning**: Development phases and milestones
5. **Template Creation**: Final output document template design

## Discovery Session Summary

**Duration**: 1 session  
**Key Achievement**: Complete workflow definition with all agent roles specified  
**Critical Insights**: 
- Clear quality gate at fact-checking (avg <5 = human review)
- Target audience well-defined (25-40, educated, topic-interested)
- Generalizable architecture for multiple organizations
- Linear pipeline with structured handoffs between agents

**Ready for**: Strategic planning and technical specification phase

---

**Status**: Discovery Complete ✓  
**Next Session**: Strategic Questions & Technical Requirements  
**Document Owner**: Product-Manager-Analyst Agent