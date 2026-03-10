"""
Keyword extraction service for resume optimization.

This module provides dynamic keyword extraction using regex patterns to identify
technical terms, business keywords, action verbs, and quantitative metrics from
resume bullet points.
"""

import re
from typing import List, Set, Final


class KeywordExtractor:
    """Dynamic keyword extraction using regex patterns for resume optimization."""
    
    # Maximum keyword limits for filtering
    MAX_TECH_KEYWORD_LENGTH: Final[int] = 20
    MAX_ACTION_KEYWORD_LENGTH: Final[int] = 15
    MAX_BUSINESS_KEYWORD_LENGTH: Final[int] = 20
    MAX_METRIC_KEYWORD_LENGTH: Final[int] = 15
    
    # Keyword count limits
    MIN_KEYWORDS: Final[int] = 4
    MAX_KEYWORDS: Final[int] = 8
    
    def __init__(self) -> None:
        """Initialize keyword extractor with compiled regex patterns."""
        self.tech_patterns = self._get_technology_patterns()
        self.action_patterns = self._get_action_patterns()
        self.business_patterns = self._get_business_patterns()
        self.metric_patterns = self._get_metric_patterns()
        
        self._compile_patterns()
    
    def _get_technology_patterns(self) -> List[str]:
        """Get regex patterns for technology keywords."""
        return [
            r'\b(?:React|Angular|Vue|Node|Python|Java|JavaScript|TypeScript|Go|Rust|C\+\+|C#|PHP|Ruby|Scala|Kotlin)\b',
            r'\b(?:Django|Flask|FastAPI|Express|Spring|Rails|Laravel|ASP\.NET|Symfony)\b',
            r'\b(?:MongoDB|PostgreSQL|MySQL|Redis|Cassandra|DynamoDB|SQLite|Oracle)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|GitLab|CircleCI|Terraform|Ansible)\b',
            r'\b(?:Git|SVN|Mercurial|Perforce)\b',
            r'\b(?:REST|GraphQL|gRPC|SOAP|API|SDK|CLI)\b',
            r'\b(?:pandas|NumPy|scikit-learn|TensorFlow|PyTorch|Matplotlib|Seaborn)\b',
            r'\b(?:Jest|Mocha|Cypress|Selenium|Pytest|JUnit|TestNG)\b',
            r'\b(?:Webpack|Vite|Rollup|Parcel|Babel|ESLint|Prettier)\b',
            r'\b(?:Next\.js|Nuxt\.js|Gatsby)\b',
            r'\b[A-Z][a-z]+(?:\.js|\.py|Script|SQL|DB)\b',
        ]
    
    def _get_action_patterns(self) -> List[str]:
        """Get regex patterns for action verbs."""
        return [
            r'\b(?:developed|implemented|built|created|designed|architected|engineered|constructed)\b',
            r'\b(?:optimized|improved|enhanced|streamlined|automated|modernized|refactored|upgraded)\b',
            r'\b(?:led|managed|coordinated|supervised|mentored|guided|facilitated|directed)\b',
            r'\b(?:reduced|increased|enhanced|boosted|accelerated|minimized|maximized|scaled)\b',
            r'\b(?:deployed|launched|released|shipped|delivered|migrated|integrated|configured)\b',
            r'\b(?:analyzed|researched|investigated|evaluated|assessed|monitored|tracked)\b',
            r'\b(?:collaborated|partnered|worked|contributed|participated|supported|assisted)\b'
        ]
    
    def _get_business_patterns(self) -> List[str]:
        """Get regex patterns for business and product keywords."""
        return [
            r'\b(?:user|customer|client|stakeholder|product|feature|solution|platform)\b',
            r'\b(?:conversion|engagement|retention|acquisition|growth|revenue|ROI|KPI)\b',
            r'\b(?:performance|scalability|reliability|availability|security|compliance)\b',
            r'\b(?:agile|scrum|kanban|sprint|backlog|requirement|specification)\b',
            r'\b(?:analytics|metrics|dashboard|reporting|insights|data|intelligence)\b',
            r'\b(?:microservices|architecture|infrastructure|pipeline|workflow|automation)\b',
            r'\b(?:testing|deployment|monitoring|logging|debugging|troubleshooting)\b',
            r'\b(?:cross-functional|full-stack|end-to-end|real-time|enterprise|production)\b'
        ]
    
    def _get_metric_patterns(self) -> List[str]:
        """Get regex patterns for quantitative metrics."""
        return [
            r'\d+(?:\.\d+)?%',  # Percentages
            r'\d+(?:,\d{3})*\+?(?:\s*(?:users|requests|lines|transactions|records|sessions))?',  # Numbers with context
            r'\b(?:twice|double|triple|quadruple|half|quarter)\b',  # Multipliers
            r'\b\d+(?:x|X)\s*(?:faster|slower|more|less|improvement)\b',  # Performance multipliers
            r'\b(?:sub-\d+ms|\d+ms|\d+s|\d+min|\d+hour)\b',  # Time measurements
            r'\b\d+(?:\.\d+)?(?:GB|MB|KB|TB|PB)\b'  # Data sizes
        ]
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for better performance."""
        self.compiled_tech = [re.compile(pattern, re.IGNORECASE) for pattern in self.tech_patterns]
        self.compiled_actions = [re.compile(pattern, re.IGNORECASE) for pattern in self.action_patterns]
        self.compiled_business = [re.compile(pattern, re.IGNORECASE) for pattern in self.business_patterns]
        self.compiled_metrics = [re.compile(pattern, re.IGNORECASE) for pattern in self.metric_patterns]
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords dynamically using regex patterns.
        
        Args:
            text: Input text to extract keywords from
            
        Returns:
            List of 4-8 most relevant keywords sorted by relevance
        """
        if not text or not text.strip():
            return []
        
        keywords: Set[str] = set()
        
        # Extract different types of keywords
        keywords.update(self._extract_pattern_matches(self.compiled_tech, text, self.MAX_TECH_KEYWORD_LENGTH))
        keywords.update(self._extract_pattern_matches(self.compiled_actions, text, self.MAX_ACTION_KEYWORD_LENGTH))
        keywords.update(self._extract_pattern_matches(self.compiled_business, text, self.MAX_BUSINESS_KEYWORD_LENGTH))
        keywords.update(self._extract_pattern_matches(self.compiled_metrics, text, self.MAX_METRIC_KEYWORD_LENGTH))
        
        return self._sort_and_limit_keywords(list(keywords))
    
    def _extract_pattern_matches(self, patterns: List[re.Pattern], text: str, max_length: int) -> Set[str]:
        """Extract matches from patterns with length filtering."""
        matches: Set[str] = set()
        for pattern in patterns:
            pattern_matches = pattern.findall(text)
            for match in pattern_matches:
                cleaned_match = match.strip()
                if cleaned_match and len(cleaned_match) <= max_length:
                    matches.add(cleaned_match)
        return matches
    
    def _sort_and_limit_keywords(self, keywords: List[str]) -> List[str]:
        """Sort keywords by relevance and limit to 4-8 keywords."""
        if not keywords:
            return []
        
        # Sort by relevance (longer terms first, then alphabetically)
        keywords.sort(key=lambda x: (-len(x), x.lower()))
        
        # Return 4-8 most relevant keywords
        return keywords[:min(self.MAX_KEYWORDS, max(self.MIN_KEYWORDS, len(keywords)))]
    
    def categorize_content(self, text: str, keywords: List[str]) -> str:
        """
        Automatically categorize bullet point based on content and keywords.
        
        Args:
            text: Original bullet point text
            keywords: Extracted keywords (currently unused but kept for future enhancement)
            
        Returns:
            Category: 'technical', 'leadership', 'achievement', or 'collaboration'
        """
        text_lower = text.lower()
        
        # Define category indicators
        leadership_indicators = {'led', 'managed', 'supervised', 'mentored', 'guided', 'coordinated', 'directed'}
        achievement_indicators = {'%', 'reduced', 'increased', 'improved', 'optimized', 'enhanced'}
        collaboration_indicators = {'collaborated', 'partnered', 'cross-functional', 'stakeholder', 'team'}
        
        # Check for category indicators in order of priority
        if any(indicator in text_lower for indicator in leadership_indicators):
            return 'leadership'
        
        if any(indicator in text_lower for indicator in achievement_indicators):
            return 'achievement'
        
        if any(indicator in text_lower for indicator in collaboration_indicators):
            return 'collaboration'
        
        # Default to technical
        return 'technical'
    
    def extract_technologies_from_keywords(self, keywords: List[str]) -> Set[str]:
        """
        Extract technology-specific keywords from a keyword list.
        
        Args:
            keywords: List of keywords to filter for technologies
            
        Returns:
            Set of technology keywords found in the input list
        """
        if not keywords:
            return set()
        
        technologies: Set[str] = set()
        keywords_text = ' '.join(keywords)
        
        for pattern in self.compiled_tech:
            matches = pattern.findall(keywords_text)
            technologies.update(match.strip() for match in matches if match.strip())
        
        return technologies
