#!/usr/bin/env python3
"""
Zero-Cost Multi-Agent Qualitative Data Analysis Pipeline (Med-AgentLab)
5-Stage MapReduce Pipeline: Ingestion -> Privacy Guard -> Map -> Validation -> Reduce
"""

import asyncio
import logging
import os
import sys
import re
import urllib.request
import urllib.parse
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('analysis_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Data class to store analysis results for each text chunk/entry"""
    original_text: str
    pii_redacted_text: str
    mapped_themes: str
    validation_result: str
    validation_reason: str

def chunk_text_sliding_window(text: str, max_words: int = 2250, overlap_words: int = 340) -> List[str]:
    """
    Splits long unstructured text transcripts into overlapping chunks.
    - 3000 tokens ≈ 2250 words
    - 450 tokens overlap ≈ 340 words
    """
    words = text.split()
    if len(words) <= max_words:
        return [text]
    
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_words
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start += (max_words - overlap_words)
    return chunks

class PatternGuard:
    """Regex-based Pattern Guard layer to reinforce PII scrubbing and ensure local safety"""
    
    def __init__(self):
        self.patterns = {
            "TC_NO": r"\b[1-9]\d{10}\b",
            "PHONE": r"\b(?:\+?90[- ]?)?0?[5-9]\d{2}[- ]?\d{3}[- ]?\d{4}\b",
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        }
        
    def sanitize(self, text: str) -> str:
        sanitized = text
        for label, pattern in self.patterns.items():
            sanitized = re.sub(pattern, f"[{label}_REDACTED]", sanitized)
        return sanitized

class AgentA_PrivacyScrubber:
    """Agent A: Privacy Guard - Scrubbing PII using local Ollama model & Pattern Guard"""
    
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "ollama/qwen3:4b")
        self.pattern_guard = PatternGuard()
        self.system_prompt = (
            "You are a strict HIPAA-compliance data scrubber. "
            "Read the clinical text/interview and redact all Personally Identifiable Information (PII) "
            "such as Names, Surnames, SSNs, phone numbers, and addresses. "
            "Replace them with appropriate tags like [NAME_REDACTED] or [ADDRESS_REDACTED]. "
            "Do NOT change medical details, symptoms, or other clinical content. "
            "Return ONLY the redacted text without any introductory or concluding comments."
        )
        
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def scrub_pii(self, text: str, row_num: int) -> str:
        try:
            logger.info(f"Row/Chunk {row_num} - Privacy Scrubber (Ollama) processing...")
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Text to redact:\n{text}"}
                ],
                temperature=0.0,
                max_tokens=2048
            )
            redacted = response.choices[0].message.content.strip()
            logger.info(f"Row/Chunk {row_num} - Privacy Scrubber completed.")
        except Exception as e:
            logger.warning(f"Row/Chunk {row_num} - Privacy Scrubber error: {str(e)}. Falling back to Pattern Guard.")
            redacted = text
            
        # Apply Regex Pattern Guard
        redacted = self.pattern_guard.sanitize(redacted)
        return redacted

class AgentB_ThematicMapper:
    """Agent B: Thematic Mapper - Concurrent thematic/open coding using Groq LPU"""
    
    def __init__(self):
        self.model = os.getenv("GROQ_MODEL", "groq/llama3-8b-8192")
        self.system_prompt = (
            "You are a clinical qualitative data coder. "
            "Extract psychological, physical, and behavioral themes, symptoms or side effects from the text. "
            "Provide them as a comma-separated list of short codes or keywords. "
            "Do NOT include conversational text. Return ONLY the comma-separated codes/themes."
        )
        
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(Exception)
    )
    async def extract_themes(self, text: str, row_num: int) -> str:
        try:
            logger.info(f"Row/Chunk {row_num} - Thematic Mapper (Groq) processing...")
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Redacted text:\n{text}"}
                ],
                temperature=0.2,
                max_tokens=250
            )
            themes = response.choices[0].message.content.strip()
            logger.info(f"Row/Chunk {row_num} - Thematic Mapper completed: {themes}")
            return themes
        except Exception as e:
            logger.error(f"Row/Chunk {row_num} - Thematic Mapper error: {str(e)}")
            raise

class AgentC_PubMedValidator:
    """Agent C: PubMed Validator - Cross-checks themes with PubMed medical database using Gemini"""
    
    def __init__(self):
        self.model = "gemini/gemini-1.5-flash"
        self.system_prompt = (
            "You are a senior medical reviewer and auditor. "
            "Verify whether the extracted medical themes/symptoms correspond to known medical literature. "
            "We searched PubMed database and found some reference article titles for these themes. "
            "Analyze the themes and reference titles. Decide if the themes are valid or potential hallucinations. "
            "Reply exactly in this format:\n"
            "VALIDATION: YES (or NO or PARTIAL)\n"
            "REASON: [Write one brief sentence explaining why, referencing the PubMed titles if supportive]"
        )
        
    def sync_search_pubmed(self, term: str) -> List[str]:
        """Search NCBI PubMed via standard urllib request"""
        try:
            # Clean special characters
            clean_term = re.sub(r'[^\w\s]', ' ', term).strip()
            if not clean_term:
                return []
            
            # Simple keyword construction
            query = urllib.parse.quote(clean_term)
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax=2"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    id_list = data.get("esearchresult", {}).get("idlist", [])
                    if not id_list:
                        return []
                    
                    ids = ",".join(id_list)
                    summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids}&retmode=json"
                    
                    req_sum = urllib.request.Request(summary_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_sum, timeout=4) as sum_response:
                        if sum_response.status == 200:
                            sum_data = json.loads(sum_response.read().decode())
                            results = sum_data.get("result", {})
                            titles = []
                            for uid in id_list:
                                title = results.get(uid, {}).get("title", "")
                                if title:
                                    titles.append(title)
                            return titles
        except Exception as e:
            logger.warning(f"PubMed search error for '{term}': {str(e)}")
        return []

    async def search_pubmed(self, term: str) -> List[str]:
        return await asyncio.to_thread(self.sync_search_pubmed, term)
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception)
    )
    async def validate_themes(self, themes: str, original_text: str, row_num: int) -> tuple[str, str]:
        try:
            logger.info(f"Row/Chunk {row_num} - PubMed Validator (Gemini) processing...")
            
            pubmed_titles = await self.search_pubmed(themes)
            rag_context = "\n".join([f"- {t}" for t in pubmed_titles]) if pubmed_titles else "No direct matching PubMed articles found."
            
            user_content = (
                f"Original Text snippet:\n{original_text}\n\n"
                f"Extracted Themes to Validate: {themes}\n\n"
                f"PubMed Search Results:\n{rag_context}"
            )
            
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            output = response.choices[0].message.content.strip()
            logger.info(f"Row/Chunk {row_num} - PubMed Validator completed:\n{output}")
            
            validation_result = "YES"
            validation_reason = output
            
            for line in output.split("\n"):
                if line.upper().startswith("VALIDATION:"):
                    validation_result = line.split(":", 1)[1].strip()
                elif line.upper().startswith("REASON:"):
                    validation_reason = line.split(":", 1)[1].strip()
                    
            return validation_result, validation_reason
        except Exception as e:
            logger.warning(f"Row/Chunk {row_num} - PubMed Validator error: {str(e)}")
            return "ERROR", str(e)

class AgentD_AcademicReducer:
    """Agent D: Academic Reducer - Synthesizing all qualitative themes into an academic report"""
    
    def __init__(self):
        self.model = "gemini/gemini-1.5-flash"
        self.system_prompt = (
            "You are the Lead Academic Researcher in a medical university laboratory. "
            "Your task is to synthesize the extracted and validated qualitative codes/themes into a cohesive, "
            "structured Thematic Analysis Report suitable for a medical journal publication. "
            "Group the codes into hierarchical categories, deduplicate terms, and explain the key clinical findings. "
            "Format the report beautifully in Markdown with clear sections (e.g., Executive Summary, Codebook/Theme Tree, Discussion, Conclusion)."
        )
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception)
    )
    async def synthesize_report(self, results: List[AnalysisResult]) -> str:
        try:
            logger.info("Academic Reducer starting synthesis...")
            data_summary = []
            for idx, res in enumerate(results):
                if res.mapped_themes == "ERROR":
                    continue
                data_summary.append(
                    f"Snippet {idx+1}:\n"
                    f"- Themes: {res.mapped_themes}\n"
                    f"- Validation: {res.validation_result} ({res.validation_reason})"
                )
            
            input_data = "\n\n".join(data_summary)
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Here is the qualitative analysis data to synthesize:\n\n{input_data}"}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            report = response.choices[0].message.content.strip()
            logger.info("Academic Reducer finished synthesis.")
            return report
        except Exception as e:
            logger.error(f"Academic Reducer synthesis error: {str(e)}")
            return f"Error during report synthesis: {str(e)}"

class QualitativeAnalysisPipeline:
    """Main pipeline orchestrating the 5-stage MapReduce qualitative analysis"""
    
    def __init__(self):
        self.agent_a = AgentA_PrivacyScrubber()
        self.agent_b = AgentB_ThematicMapper()
        self.agent_c = AgentC_PubMedValidator()
        self.agent_d = AgentD_AcademicReducer()
        self.results: List[AnalysisResult] = []
        self.report: str = ""
        
    async def process_single_text(self, text: str, row_num: int) -> AnalysisResult:
        try:
            # Stage 2: Privacy Guard (PII Redaction)
            redacted_text = await self.agent_a.scrub_pii(text, row_num)
            
            # Stage 3: Map Phase (Thematic Extraction)
            themes = await self.agent_b.extract_themes(redacted_text, row_num)
            
            # Stage 4: Validation (PubMed RAG check)
            val_result, val_reason = await self.agent_c.validate_themes(themes, redacted_text, row_num)
            
            return AnalysisResult(
                original_text=text,
                pii_redacted_text=redacted_text,
                mapped_themes=themes,
                validation_result=val_result,
                validation_reason=val_reason
            )
        except Exception as e:
            logger.error(f"Row/Chunk {row_num} - Pipeline failed: {str(e)}")
            return AnalysisResult(
                original_text=text,
                pii_redacted_text="ERROR",
                mapped_themes="ERROR",
                validation_result="ERROR",
                validation_reason=str(e)
            )

    async def process_batch(self, texts: List[str], batch_size: int = 5) -> None:
        """Process texts in batches to manage rate limits"""
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
            
            tasks = [
                self.process_single_text(text, i + j + 1) 
                for j, text in enumerate(batch)
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {str(result)}")
                else:
                    self.results.append(result)
            
            if i + batch_size < len(texts):
                logger.info("Waiting between batches...")
                await asyncio.sleep(2)
                
        # Stage 5: Reduce Phase (Academic Synthesis)
        if self.results:
            self.report = await self.agent_d.synthesize_report(self.results)
            
    def load_data(self, input_file: str) -> List[str]:
        """Load qualitative data from Excel file or raw text file"""
        try:
            logger.info(f"Loading data from {input_file}")
            path = Path(input_file)
            
            if path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(input_file)
                if 'text_data' not in df.columns:
                    raise ValueError("Excel file must contain a column named 'text_data'")
                return df['text_data'].dropna().tolist()
            else:
                with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                logger.info("Loaded raw text file. Performing sliding window chunking...")
                return chunk_text_sliding_window(content)
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def save_results(self, output_file: str) -> None:
        """Save results to Excel and write Academic Report to Markdown"""
        try:
            logger.info(f"Saving results to {output_file}")
            
            data = {
                'Original Text': [result.original_text for result in self.results],
                'PII Redacted Text': [result.pii_redacted_text for result in self.results],
                'Mapped Themes': [result.mapped_themes for result in self.results],
                'Validation Result': [result.validation_result for result in self.results],
                'Validation Reason': [result.validation_reason for result in self.results]
            }
            
            df = pd.DataFrame(data)
            df.to_excel(output_file, index=False, engine='openpyxl')
            logger.info(f"Excel results saved successfully to {output_file}")
            
            # Save academic report
            report_file = output_file.replace("_output.xlsx", "_report.md").replace(".xlsx", "_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(self.report)
            logger.info(f"Synthesized Academic Report saved successfully to {report_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise

    async def run(self, input_file: str, output_file: str = "output_analysis.xlsx") -> None:
        """Run the complete analysis pipeline"""
        try:
            logger.info("Starting Zero-Cost Multi-Agent Qualitative Analysis Pipeline")
            texts = self.load_data(input_file)
            
            if not texts:
                logger.warning("No texts to process")
                return
            
            await self.process_batch(texts)
            self.save_results(output_file)
            
            total_processed = len(self.results)
            successful = sum(1 for r in self.results if r.mapped_themes != "ERROR")
            logger.info(f"Pipeline completed: {successful}/{total_processed} successful")
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

async def main():
    """Main entry point"""
    load_dotenv()
    
    # Check required keys
    required_vars = ['GROQ_API_KEY', 'GEMINI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set up your .env file with the required API keys")
        return
    
    pipeline = QualitativeAnalysisPipeline()
    
    input_file = "input_data.xlsx"
    if not Path(input_file).exists():
        logger.error(f"Input file '{input_file}' not found")
        logger.info("Please create an Excel file with a 'text_data' column")
        return
        
    await pipeline.run(input_file)

if __name__ == "__main__":
    asyncio.run(main())
