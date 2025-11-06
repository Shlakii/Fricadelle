#!/usr/bin/env python3
"""
Advanced AI Analyzer with structured prompts and multi-step analysis.
This module provides improved AI interaction with better hallucination prevention.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
import ollama
from vulnerability_schema import validate_vulnerability_response, get_cvss_guidance


class AIAnalyzer:
    """
    Advanced AI analyzer with structured prompts and validation.
    """
    
    # Constants for AI configuration
    DEFAULT_NUM_PREDICT = 2000  # Increased from default 512 to allow detailed responses
    DEFAULT_VALIDATION_PREDICT = 500  # For validation responses
    
    def __init__(self, model: str = "llama3.2", temperature: float = 0.1):
        """
        Initialize the AI analyzer.
        
        Args:
            model: The Ollama model to use
            temperature: Temperature for AI responses (lower = more deterministic)
        """
        self.model = model
        self.temperature = temperature
        self.max_retries = 3
    
    def _clean_json_response(self, response_text: str) -> str:
        """
        Clean AI response to extract valid JSON.
        
        Args:
            response_text: Raw response from AI
            
        Returns:
            Cleaned JSON string
        """
        response_text = response_text.strip()
        
        # Remove markdown code blocks
        if '```' in response_text:
            # Find JSON between code blocks
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                response_text = response_text[start:end]
        
        return response_text
    
    def _build_detection_prompt(self, raw_data: str, filename: str) -> str:
        """
        Build a structured prompt for vulnerability detection.
        
        Args:
            raw_data: Raw scan data
            filename: Name of the scan file
            
        Returns:
            Structured prompt string
        """
        prompt = f"""Tu es un analyste cybersécurité expert en pentesting et analyse de vulnérabilités.

MISSION: Analyser les données ci-dessous et identifier UNIQUEMENT les vraies vulnérabilités de sécurité.

DONNÉES À ANALYSER:
Fichier: {filename}
---
{raw_data}
---

RÈGLES STRICTES DE DÉTECTION:

1. NE PAS SIGNALER comme vulnérabilité:
   - Ports ouverts standards sans service vulnérable
   - Informations techniques basiques (OS, versions sans CVE)
   - Comportements normaux du système
   - Configurations standard sécurisées

2. SIGNALER comme vulnérabilité:
   - Credentials valides découverts (password spray, brute force)
   - Mots de passe faibles ou crackés
   - Services avec CVE connus
   - Configurations dangereuses (anonymous login, partages ouverts)
   - Versions obsolètes avec vulnérabilités connues
   - Exposition de données sensibles
   - Authentification faible ou manquante
   - Privilèges excessifs

3. NIVEAU DE SÉVÉRITÉ (strictement respecter):
   - CRITICAL (9.0-10.0): Accès non autorisé immédiat, credentials valides, RCE
   - HIGH (7.0-8.9): Exploitation probable avec impact important
   - MEDIUM (4.0-6.9): Impact modéré ou exploitation complexe
   - LOW (0.1-3.9): Impact minimal ou information mineure
   - INFO (0.0): Information uniquement, pas de risque

4. CVSS SCORE GUIDANCE:
   - Évaluer: Attack Vector, Attack Complexity, Privileges Required, User Interaction
   - Impact: Confidentiality, Integrity, Availability
   - Être précis et justifié

FORMAT DE RÉPONSE OBLIGATOIRE:
Réponds UNIQUEMENT en JSON valide, sans texte additionnel.
Si aucune vulnérabilité: {{"vulnerabilities": []}}

Si vulnérabilité(s) détectée(s):
{{
  "vulnerabilities": [
    {{
      "title": "Titre clair et précis de la vulnérabilité (10-200 caractères)",
      "severity": "critical|high|medium|low|info",
      "cvss_score": 0.0-10.0,
      "cve_ids": ["CVE-YYYY-XXXXX"],
      "finding_type": "Type exact (ex: Weak Credentials, Configuration Error, etc.)",
      "description": "Description DÉTAILLÉE (minimum 100 caractères):
        - Qu'est-ce qui a été découvert exactement?
        - Comment cela a été détecté?
        - Pourquoi est-ce une vulnérabilité?
        - Quel est le vecteur d'attaque?
        - Quelles sont les conséquences techniques?",
      "remediation": "Plan de remédiation DÉTAILLÉ et ACTIONNABLE (minimum 100 caractères):
        1. Action immédiate à prendre
        2. Correction à court terme
        3. Mesures à moyen terme
        4. Recommandations à long terme
        5. Validation de la correction",
      "business_impact": "Impact métier CONCRET (minimum 50 caractères):
        - Quelles données sont à risque?
        - Quels processus métier sont affectés?
        - Quelles sont les conséquences financières potentielles?
        - Quel est l'impact réputationnel?",
      "affected_assets": ["Liste précise des assets affectés"],
      "evidence": "Preuve technique EXACTE extraite des données (logs, output, commandes)",
      "confidence_score": 0.0-1.0,
      "exploitation_complexity": "low|medium|high"
    }}
  ]
}}

IMPORTANT:
- Sois RIGOUREUX: Ne signale que des vraies vulnérabilités
- Sois PRÉCIS: Fournis des détails techniques concrets
- Sois ACTIONNABLE: Les remédiations doivent être applicables
- Sois PROFESSIONNEL: Utilise un langage technique approprié
- PAS de texte hors JSON
- PAS de suppositions: base-toi sur les données fournies

RÉPONDS MAINTENANT (JSON UNIQUEMENT):"""
        
        return prompt
    
    def _build_validation_prompt(self, vulnerability: Dict[str, Any], raw_data: str) -> str:
        """
        Build a prompt to validate a detected vulnerability.
        
        Args:
            vulnerability: The vulnerability to validate
            raw_data: Original raw data
            
        Returns:
            Validation prompt
        """
        prompt = f"""Tu es un expert en cybersécurité chargé de VALIDER une vulnérabilité détectée.

VULNÉRABILITÉ À VALIDER:
{json.dumps(vulnerability, indent=2, ensure_ascii=False)}

DONNÉES ORIGINALES:
{raw_data}

MISSION: Vérifier que cette vulnérabilité est:
1. RÉELLE: Basée sur des preuves concrètes dans les données
2. EXACTE: La description correspond aux faits
3. PERTINENTE: C'est vraiment une vulnérabilité de sécurité
4. BIEN SCORÉE: Le CVSS et la sévérité sont appropriés

RÉPONDS EN JSON:
{{
  "is_valid": true/false,
  "confidence": 0.0-1.0,
  "issues": ["Liste des problèmes détectés si is_valid=false"],
  "suggestions": ["Suggestions d'amélioration"]
}}

RÉPONDS MAINTENANT (JSON UNIQUEMENT):"""
        
        return prompt
    
    def _detect_vulnerabilities(
        self,
        raw_data: str,
        filename: str
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Detect vulnerabilities using AI analysis.
        
        Args:
            raw_data: Raw scan data to analyze
            filename: Name of the scan file
            
        Returns:
            Tuple of (vulnerabilities_list, errors_list)
        """
        errors = []
        
        for attempt in range(self.max_retries):
            try:
                detection_prompt = self._build_detection_prompt(raw_data, filename)
                
                response = ollama.generate(
                    model=self.model,
                    prompt=detection_prompt,
                    stream=False,
                    options={
                        "temperature": self.temperature,
                        "num_predict": self.DEFAULT_NUM_PREDICT,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                )
                
                response_text = response['response'].strip()
                cleaned_response = self._clean_json_response(response_text)
                
                # Try to parse JSON
                if not cleaned_response.startswith('{'):
                    # Try to find JSON in the response
                    start = cleaned_response.find('{')
                    end = cleaned_response.rfind('}') + 1
                    if start != -1 and end > start:
                        cleaned_response = cleaned_response[start:end]
                    else:
                        raise ValueError("No valid JSON found in response")
                
                result = json.loads(cleaned_response)
                
                # Validate response structure
                is_valid, error_msg = validate_vulnerability_response(result)
                
                if not is_valid:
                    errors.append(f"Validation error on attempt {attempt + 1}: {error_msg}")
                    if attempt < self.max_retries - 1:
                        continue
                    else:
                        return [], errors
                
                return result.get('vulnerabilities', []), errors
                
            except json.JSONDecodeError as e:
                errors.append(f"JSON parsing error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    continue
            except Exception as e:
                errors.append(f"Analysis error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    continue
        
        return [], errors
    
    def _validate_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]],
        raw_data: str
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Validate detected vulnerabilities.
        
        Args:
            vulnerabilities: List of vulnerabilities to validate
            raw_data: Original raw data
            
        Returns:
            Tuple of (validated_vulnerabilities, errors_list)
        """
        validated_vulns = []
        errors = []
        
        for vuln in vulnerabilities:
            validation_result = self._validate_vulnerability(vuln, raw_data)
            if validation_result['is_valid']:
                # Add confidence score
                vuln['confidence_score'] = validation_result.get('confidence', 0.8)
                validated_vulns.append(vuln)
            else:
                errors.append(
                    f"Vulnerability '{vuln.get('title', 'Unknown')}' failed validation: "
                    f"{', '.join(validation_result.get('issues', []))}"
                )
        
        return validated_vulns, errors
    
    def analyze_scan_data(
        self,
        raw_data: str,
        filename: str,
        validate: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Analyze scan data with structured multi-step approach.
        
        Args:
            raw_data: Raw scan data to analyze
            filename: Name of the scan file
            validate: Whether to validate detected vulnerabilities
            
        Returns:
            Tuple of (vulnerabilities_list, errors_list)
        """
        # Step 1: Initial detection
        vulnerabilities, errors = self._detect_vulnerabilities(raw_data, filename)
        
        if not vulnerabilities:
            return [], errors
        
        # Step 2: Validate each vulnerability if requested
        if validate:
            validated_vulns, validation_errors = self._validate_vulnerabilities(
                vulnerabilities, raw_data
            )
            errors.extend(validation_errors)
            return validated_vulns, errors
        
        return vulnerabilities, errors
    
    def _validate_vulnerability(
        self,
        vulnerability: Dict[str, Any],
        raw_data: str
    ) -> Dict[str, Any]:
        """
        Validate a detected vulnerability.
        
        Args:
            vulnerability: The vulnerability to validate
            raw_data: Original raw data
            
        Returns:
            Validation result dictionary
        """
        try:
            validation_prompt = self._build_validation_prompt(vulnerability, raw_data)
            
            response = ollama.generate(
                model=self.model,
                prompt=validation_prompt,
                stream=False,
                options={
                    "temperature": 0.1,
                    "num_predict": self.DEFAULT_VALIDATION_PREDICT
                }
            )
            
            response_text = response['response'].strip()
            cleaned_response = self._clean_json_response(response_text)
            
            result = json.loads(cleaned_response)
            return result
            
        except Exception as e:
            # If validation fails, assume it's valid but with lower confidence
            return {
                "is_valid": True,
                "confidence": 0.6,
                "issues": [f"Validation error: {str(e)}"],
                "suggestions": []
            }
    
    def enrich_vulnerability(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a vulnerability with additional analysis.
        
        Args:
            vulnerability: The vulnerability to enrich
            
        Returns:
            Enriched vulnerability
        """
        # Add CVSS breakdown if not present
        if 'cvss_breakdown' not in vulnerability:
            severity = vulnerability.get('severity', 'medium')
            cvss_score = vulnerability.get('cvss_score', 5.0)
            
            vulnerability['cvss_breakdown'] = {
                'score': cvss_score,
                'severity': severity,
                'guidance': get_cvss_guidance(severity)
            }
        
        # Ensure confidence score exists
        if 'confidence_score' not in vulnerability:
            vulnerability['confidence_score'] = 0.7  # Default moderate confidence
        
        # Add exploitation complexity if not present
        if 'exploitation_complexity' not in vulnerability:
            cvss_score = vulnerability.get('cvss_score', 5.0)
            if cvss_score >= 9.0:
                vulnerability['exploitation_complexity'] = 'low'
            elif cvss_score >= 7.0:
                vulnerability['exploitation_complexity'] = 'medium'
            else:
                vulnerability['exploitation_complexity'] = 'high'
        
        return vulnerability
